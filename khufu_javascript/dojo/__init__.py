import os
import re
import json
import mimetypes

from zope.interface import Interface, implements
from pyramid.asset import abspath_from_asset_spec
from paste.urlparser import StaticURLParser
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.exceptions import NotFound
from pyramid.response import Response

from ..utils import PrefixedDict, SourcedDict

DEFAULT_DJCONFIG = {
    #'isDebug': False,
    #'debugAtAllCosts': False,
    #baseUrl: '',
    #modulePaths: {},
}

provide_re = re.compile(
    r'dojo.provide *\( *["\']([a-zA-Z0-9 _.-]+)["\'] *\) *;.*')


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

    def get_script_filename(self, provide):
        if provide in self.scripts:
            return self.scripts[provide]
        if self.parent is not None:
            return self.parent.scripts.get(provide)
        return None

    def register_script(self, fname, provide=None):
        filename = abspath_from_asset_spec(fname, self.default_package)
        if provide is None:
            with open(filename) as f:
                for line in f:
                    match = provide_re.match(line.strip())
                    if match:
                        provide = match.group(1)
                        break

        if not provide:
            raise ValueError('%s does not contain a '
                             '"dojo.provide()" entry' % fname)

        self.scripts[provide] = filename

    def register_script_dir(self, dirspec):
        dirname = abspath_from_asset_spec(dirspec, self.default_package)
        for x in os.listdir(dirname):
            if x.endswith('.js'):
                self.register_script(os.path.join(dirname, x))


def register_script(config_or_request, fname, provide=None):
    registry = get_script_registry(config_or_request)
    registry.register_script(fname, provide)


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

    if request.registry.settings.get('DEBUG'):
        if 'isDebug' not in dj_config:
            dj_config['isDebug'] = True
        if 'debugAtAllCosts' not in dj_config:
            dj_config['debugAtAllCosts'] = True

    module_paths = dj_config.get('modulePaths')
    if module_paths is None:
        dj_config['modulePaths'] = module_paths = {}
    for provide, fname in registry.get_scripts():
        parts = provide.rsplit('.', 1)
        p = parts[0]
        if os.path.exists('dojo'):
            module_paths[p] = '../' + p
        else:
            module_paths[p] = p

    base_url = request.application_url
    if not base_url.endswith('/'):
        base_url += '/'
    base_url += 'dojo/'

    if not os.path.exists('dojo'):
        dj_config['baseUrl'] = base_url

    return dj_config


def render_header(request):
    dojo_base = u'http://ajax.googleapis.com/ajax/libs/dojo/1.6.0'
    dojo_script = dojo_base + u'/dojo/dojo.xd.js'

    if os.path.exists('dojo'):
        dojo_base = request.application_url
        if not dojo_base.endswith('/'):
            dojo_base += '/'
        dojo_base += 'dojo'
        dojo_script = dojo_base + u'/dojo/dojo.js'

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
  <script src="%(dojo_script)s"
          type="text/javascript"></script>
''' % {'dj_config': json.dumps(dj_config).decode('utf-8'),
       'dojo_base': dojo_base,
       'dojo_script': dojo_script,
       'dijit_html': dijit_html}


class ScriptView(object):

    def __init__(self):
        self._apps = {}

    def get_static_url_parser(self, dirname):
        if dirname in self._apps:
            return self._apps[dirname]

        self._apps[dirname] = app = StaticURLParser(dirname)
        return app

    def __call__(self, request):
        m = request.matchdict['provide']
        if len(m) > 1 and m[0] in (u'dojo', u'dijit',
                                   u'dojox', u'_base'):
            return self._local_file(request, m)

        provide = '.'.join(m)
        provide = provide.rsplit('.', 1)[0]

        if not provide:
            return self.dojo_listing(request)

        registry = get_script_registry(request)
        fname = registry.get_script_filename(provide)

        if not fname:
            s = request.url[len(request.application_url):]
            raise NotFound(message=s)

        app = self.get_static_url_parser(os.path.dirname(fname))

        request_copy = request.copy()
        # Fix up PATH_INFO to get rid of everything but the "subpath"
        # (the actual path to the file relative to the root dir).
        request_copy.environ['PATH_INFO'] = '/' + os.path.basename(fname)
        # Zero out SCRIPT_NAME for good measure.
        request_copy.environ['SCRIPT_NAME'] = ''
        return request_copy.get_response(app)

    def _abort(self, request):
        s = request.url[len(request.application_url):]
        raise NotFound(message=s)

    def _local_file(self, request, path):
        if not os.path.exists('dojo'):
            self._abort(request)

        for part in path:
            if part[0] == '.' and part[-1] == '.':
                self._abort(request)

        local = os.path.join('dojo',
                             os.path.sep.join(path))
        if not os.path.isfile(local):
            self._abort(request)

        response = Response()
        response.headers['Content-Type'] = mimetypes.guess_type(local)[0] \
            or 'application/octet-stream'
        response.headers['Content-Length'] = os.path.getsize(local)
        response.app_iter = open(local)
        return response

    def _listing_html(self, request):
        registry = get_script_registry(request)
        base_url = request.application_url
        if not base_url.endswith('/'):
            base_url += '/'
        base_url += 'dojo'

        yield u'<ul>'
        for k, v in registry.get_scripts():
            yield u'<li>'
            fname = k.replace('.', '/')
            yield u'<a href="%s/%s.js">%s.js</a>\n' % (base_url, fname, fname)
            yield u'</li>'
        yield u'</ul>'

    def dojo_listing(self, request):
        response = Response()
        response.headers['Content-Type'] = 'text/html'
        response.charset = 'utf-8'
        response.app_iter = self._listing_html(request)
        return response


def slash_redirect(request):
    return HTTPSeeOther(location=request.url + '/')


def includeme(config):
    config.add_directive('register_script', register_script)
    config.add_directive('register_script_dir', register_script_dir)
    config.add_route('dojo', '/dojo/*provide', view=ScriptView())
    config.add_route('dojo_redirect', '/dojo', slash_redirect)
