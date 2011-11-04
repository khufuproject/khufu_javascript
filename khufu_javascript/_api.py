from collections import OrderedDict
from zope.interface import implements, Interface


def get_or_set_obj(provides, factory, config_or_request, create=True):
    r = config_or_request.registry

    global_obj = obj = r.queryUtility(provides)
    if global_obj is None and create:
        obj = global_obj = factory(settings=r.settings)
        r.registerUtility(global_obj, provides)

    if hasattr(config_or_request, 'environ'):
        environ = config_or_request.environ
        k = 'khufu.dojo.registry'
        if k in environ:
            obj = environ[k]
        elif create:
            obj = environ[k] = factory(parent=global_obj)

    return obj


class IResource(Interface):
    def render(request):
        pass


class Resource(object):
    implements(IResource)

    html = u'%(path)s\n'

    def __init__(self, path):
        self.path = path

    def render(self, request):
        return self.html % {'path': request.static_url(self.path)}


class JavascriptResource(object):
    html = (u'<script type="text/javascript"\n'
            u'        href="%(path)s" />\n')


class StylesheetResource(object):
    html = (u'<link type="text/css"\n'
            u'      rel="stylesheet"\n'
            u'      href="%(path)s" />\n')


class ResourceHelper(object):
    '''Provides a central location for registering
    stylesheets and javascripts.
    '''

    js_key = 'khufu_javascript.javascript_resources'
    css_key = 'khufu_javascript.css_resources'

    def __init__(self, config=None, request=None, parent=None):
        self.config = config
        self.request = request
        self.parent = parent

        if config is not None:
            registry = config.registry
        else:
            registry = request.registry
        self.registry = registry
        self._settings = registry.settings

    @property
    def settings(self):
        for key in (self.js_key, self.css_key):
            d = self._settings.get(key, None)
            if d is None:
                self._settings[key] = OrderedDict()
        return self._settings

    def add_javascript(self, name, path):
        self.settings[self.js_key][name] = JavascriptResource(path)

    def add_stylesheet(self, name, path):
        self.settings[self.css_key][name] = StylesheetResource(path)

    def render(self, request=None):
        request = request or self.request

        if request is None:
            raise ValueError('Please specify the active request '
                             'either as an attribute on this '
                             'resourcehelper or as an argument to '
                             'the render method')

        rendered = u''
        for key in (self.css_key, self.js_key):
            for name, resource in self.settings[key].items():
                rendered += resource.render(request)
        return rendered
