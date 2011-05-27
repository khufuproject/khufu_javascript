import os
import re
import json

from zope.interface import Interface, implements
from pyramid.asset import abspath_from_asset_spec
from paste.urlparser import StaticURLParser

from ..utils import PrefixedDict, SourcedDict

DEFAULT_DJCONFIG = {
    'isDebug': False,
    'debugAtAllCosts': False,
    #baseUrl: '',
    #modulePaths: {},
}

provides_re = re.compile(
    r'dojo.provides *\( *["\']([a-zA-Z0-9 _.-]+)["\'] *\) *;.*')


class IScriptRegistry(Interface):
    pass


class ScriptRegistry(object):
    implements(IScriptRegistry)

    def __init__(self, settings=None, default_package=None, parent=None):
        self.scripts = {}
        self.default_package = default_package or '__main__'
        self.parent = parent

        sources = [settings]
        if parent is not None:
            sources.append(parent.settings)
        self.settings = SourcedDict(*sources)
        self.dj_config = PrefixedDict('djconfig.', self.settings)

    def get_scripts(self):
        scripts = {}
        if self.parent is not None:
            scripts.update(self.parent.scripts)
        scripts.update(self.scripts)
        return scripts.items()

    def get_script_filename(self, provides):
        if provides in self.scripts:
            return self.scripts[provides]
        if self.parent is not None:
            return self.parent.scripts.get(provides)
        return None

    def register_script(self, fname, provides=None):
        filename = abspath_from_asset_spec(fname, self.default_package)
        if provides is None:
            with open(filename) as f:
                for line in f:
                    match = provides_re.match(line.strip())
                    if match:
                        provides = match.group(1)
                        break

        if not provides:
            raise ValueError('%s does not contain a "dojo.provides()" entry')

        self.scripts[provides] = filename

    def register_script_dir(self, dirspec):
        dirname = abspath_from_asset_spec(dirspec, self.default_package)
        for x in os.listdir(dirname):
            if x.endswith('.js'):
                self.register_script(os.path.join(dirname, x))


def register_script(config_or_request, fname, provides=None):
    registry = get_script_registry(config_or_request)
    registry.register_script(fname, provides)


def register_script_dir(config_or_request, dirspec):
    registry = get_script_registry(config_or_request)
    registry.register_script_dir(dirspec)


def get_script_registry(config_or_request, create=True):
    r = config_or_request.registry

    global_registry = registry = r.queryUtility(IScriptRegistry)
    if global_registry is None and create:
        app_settings = r.settings
        settings = PrefixedDict('khufu.dojo.', app_settings)
        dj_config = PrefixedDict('djconfig.', settings)
        for k, v in DEFAULT_DJCONFIG.items():
            if k not in dj_config:
                dj_config[k] = v
        registry = global_registry = ScriptRegistry(settings=settings)
        r.registerUtility(global_registry, IScriptRegistry)

    if hasattr(config_or_request, 'environ'):
        environ = config_or_request.environ
        k = 'khufu.dojo.registry'
        if k in environ:
            registry = environ[k]
        elif create:
            registry = environ[k] = ScriptRegistry(parent=global_registry)

    return registry


def generate_dj_config(request):
    registry = get_script_registry(request)
    dj_config = registry.dj_config.as_dict()
    module_paths = dj_config.get('modulePaths')
    if module_paths is None:
        dj_config['modulePaths'] = module_paths = {}

    app_url = request.application_url
    if not app_url.endswith('/'):
        app_url += '/'
    for provides, fname in registry.get_scripts():
        parts = provides.rsplit('.', 1)
        main = parts[0]
        module_paths[main] = app_url + 'dojo/' + main
    return dj_config


def render_header(request):
    dojo_base = u'http://ajax.googleapis.com/ajax/libs/dojo/1.6'
    dj_config = generate_dj_config(request)
    registry = get_script_registry(request)
    dijit_html = u''
    dijit_theme = registry.settings.get('dijit_theme')

    if dijit_theme:
        dijit_html = u'''\
  <link rel="stylesheet"
        type="text/css"
        href="%(dojo_base)s/dijit/themes/%(dijit_theme)s/%(dijit_theme)s.css">
''' % {'dijit_theme': dijit_theme.decode('utf-8'),
       'dojo_base': dojo_base}

    return u'''\
%(dijit_html)s
  <script type="text/javascript">
    djConfig = %(dj_config)s;
  </script>
  <script src="%(dojo_base)s/dojo/dojo.xd.js"
          type="text/javascript"></script>
''' % {'dj_config': json.dumps(dj_config).decode('utf-8'),
       'dojo_base': dojo_base,
       'dijit_html': dijit_html}


class ScriptView(object):

    def __call__(self, request):
        provides = '.'.join(request.matchdict['provides'])
        provides = provides.rsplit('.', 1)[0]

        registry = get_script_registry(request)
        fname = registry.get_script_filename(provides)

        app = StaticURLParser(os.path.dirname(fname))
        request_copy = request.copy()
        # Fix up PATH_INFO to get rid of everything but the "subpath"
        # (the actual path to the file relative to the root dir).
        request_copy.environ['PATH_INFO'] = '/' + os.path.basename(fname)
        # Zero out SCRIPT_NAME for good measure.
        request_copy.environ['SCRIPT_NAME'] = ''
        return request_copy.get_response(app)


def includeme(config):
    config.add_directive('register_script', register_script)
    config.add_directive('register_script_dir', register_script_dir)
    view = ScriptView()
    config.add_route('dojo', '/dojo', view=view)
    config.add_route('dojo', '/dojo/*provides', view=view)
