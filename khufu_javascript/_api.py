from collections import OrderedDict
from zope.interface import implements, Interface


class IRenderable(Interface):
    def render(request):
        '''Render (normally to html) this object
        '''


class IResource(Interface):
    def render(request):
        '''Render the given resource'''


class Resource(object):
    implements(IResource, IRenderable)

    html = u'%(path)s\n'

    def __init__(self, path, use_static_url=False):
        self.path = path
        self.use_static_url = use_static_url

    def render(self, request):
        path = self.path
        if self.use_static_url:
            path = request.static_url(path)
        return self.html % {'path': path}

    def __unicode__(self):
        return u'<%s path=%s>' % (self.__class__.__name__, self.path)


class JavascriptResource(Resource):
    html = (u'<script type="text/javascript"\n'
            u'        href="%(path)s" />\n')


class StylesheetResource(Resource):
    html = (u'<link type="text/css"\n'
            u'      rel="stylesheet"\n'
            u'      href="%(path)s" />\n')


class ResourceRegistry(object):
    '''Provides a central location for registering
    stylesheets and javascripts.
    '''

    implements(IRenderable)

    def __init__(self, parent=None, default_package=None):
        self._js = OrderedDict()
        self._css = OrderedDict()
        self.default_package = default_package or '__main__'
        self.parent = parent

    def _get_resources(self, attr):
        resources = OrderedDict()
        if self.parent is not None:
            resources.update(getattr(self.parent, attr))
        resources.update(getattr(self, attr))
        return resources

    def get_javascripts(self):
        return self._get_resources('_js').values()

    def get_stylesheets(self):
        return self._get_resources('_css').values()

    def _add(self, obj, attr):
        container = getattr(self, attr)
        if obj.path in container:
            raise ValueError(obj.path + ' already exists')
        container[obj.path] = obj

    def add_javascript(self, javascript):
        o = javascript
        if isinstance(javascript, basestring):
            o = JavascriptResource(javascript)

        if not isinstance(o, JavascriptResource):
            raise TypeError('stylesheet arg must either be a string '
                            'or StylesheetResource instance')
        self._add(o, '_js')

    def add_stylesheet(self, stylesheet):
        o = stylesheet
        if isinstance(stylesheet, basestring):
            o = StylesheetResource(stylesheet)

        if not isinstance(o, StylesheetResource):
            raise TypeError('stylesheet arg must either be a string '
                            'or StylesheetResource instance')
        self._add(o, '_css')

    def render(self, request):
        rendered = u''
        for js in self.get_javascripts():
            rendered += js.render(request)
        for css in self.get_stylesheets():
            rendered += css.render(request)
        return rendered


KEY = 'khufu_javascript.resource_registry'


def get_resource_registry(config_or_request):
    '''Get the appropriate resource registry.

    If config_or_request is a config object, then this adds
    scripts to the global pool that will be used on any page.

    If config_or_request is a request object, then this adds
    scripts to the request-scope pool that will only be used
    for the active request.  Rendering this registry will use
    the master (ie config) level pool plus the local pool.
    '''

    source = None
    if hasattr(config_or_request, 'environ'):
        source = config_or_request.environ
        parent = config_or_request.registry.settings[KEY]
    else:
        source = config_or_request.registry.settings
        parent = None

    if KEY not in source:
        source[KEY] = ResourceRegistry(parent=parent)

    return source[KEY]


class RequestRenderable(object):
    '''Provides a renderable that doesn't require a request.
    '''

    implements(IRenderable)

    def __init__(self, renderable, request):
        self.renderable = renderable
        self.request = request

    def render(self, request=None):
        request = request
        if request is None:
            request = self.request

        return self.renderable.render(request=request)
