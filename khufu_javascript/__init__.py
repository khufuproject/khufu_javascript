from pyramid.events import subscriber, BeforeRender


class ResourceHelper(object):

    js_key = 'khufu_javascript.javascript_resources'
    css_key = 'khufu_javascript.css_resources'

    css_html = '<link type="text/css" rel="stylesheet" href="%s" />\n'
    js_html = '<script type="text/javascript" href="%s" />\n'

    def __init__(self, config=None, request=None):
        self.config = config
        self.request = request
        if config is not None:
            registry = config.registry
        else:
            registry = request.registry
        self._settings = registry.settings

    @property
    def settings(self):
        for key in (self.js_key, self.css_key):
            d = self._settings.get(key, None)
            if d is None:
                self._settings[key] = set()
        return self._settings

    def add_javascript(self, name, path):
        self.settings[self.js_key].add((name, path))

    def add_stylesheet(self, name, path):
        self.settings[self.css_key].add((name, path))

    def render(self, request=None):
        request = request or self.request
        s = u''
        for name, path in self.settings[self.css_key]:
            s += self.css_html % request.static_url(path)
        for name, path in self.settings[self.js_key]:
            s += self.js_html % request.static_url(path)
        return s


def setup_globals(event):
    request = event['request']
    event['resource_helper'] = ResourceHelper(request=request)


def includeme(c):
    c.add_directive('get_resource_helper', ResourceHelper)
    c.add_subscriber(setup_globals, BeforeRender)
