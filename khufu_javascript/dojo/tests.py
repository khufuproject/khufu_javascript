import unittest
from pyramid.testing import setUp as setUpPyramid, DummyRequest
from khufu_javascript.testing import Mock
try:
    import webtest
except ImportError:
    webtest = None


class DojoTests(unittest.TestCase):

    def setUp(self):
        self.config = setUpPyramid()
        self.request = DummyRequest()
        self.request.registry = self.config.registry

    def test_generate_dj_config(self):
        from khufu_javascript.dojo import generate_dj_config
        self.config.include('khufu_javascript.dojo')
        self.config.register_script('khufu_javascript.dojo:testscript.js')

        dj_config = generate_dj_config(self.request)
        app_url = self.request.application_url
        if not app_url.endswith('/'):
            app_url += '/'

        self.assertEqual(dj_config['modulePaths'],
                         {'foo': '../foo'})

    def test_register_script(self):
        from khufu_javascript.dojo import register_script
        self.assertRaises(IOError, register_script, self.request, '')

    def test_register_script_dir(self):
        from khufu_javascript.dojo import register_script_dir
        register_script_dir(self.request, '')

    def test_get_script_registry(self):
        from khufu_javascript.dojo import get_script_registry
        self.assertTrue(get_script_registry(self.request) is not None)


class MockOpen(list):
    def close(self):
        pass


class DojoScriptRegistryTests(unittest.TestCase):
    def get_script_registry(self, *args, **kwargs):
        from khufu_javascript.dojo import ScriptRegistry
        return ScriptRegistry(*args, **kwargs)

    def test_init(self):
        registry = self.get_script_registry({})
        self.assertTrue(hasattr(registry, 'settings'))
        self.assertTrue(hasattr(registry, 'dj_config'))

    def test_get_scripts(self):
        registry = self.get_script_registry({})
        self.assertEqual(registry.get_scripts(), [])

    def test_get_script_filename(self):
        registry = self.get_script_registry({})
        self.assertEqual(registry.get_script_filename('foobar'), None)

        registry.parent = Mock(scripts={})
        self.assertEqual(registry.get_script_filename('foobar'), None)

        obj = object()
        registry.scripts['foobar'] = obj
        self.assertEqual(registry.get_script_filename('foobar'), obj)

    def test_register_script(self):
        registry = self.get_script_registry({})
        registry._open = lambda x: MockOpen(['a', 'b', 'c'])
        self.assertRaises(ValueError, registry.register_script, 'foobar')

    def test_register_script_dir(self):
        registry = self.get_script_registry({})
        registry._listdir = lambda x: ['foo.js']
        self.assertRaises(IOError, registry.register_script_dir, 'foobar')


if webtest is not None:
    class DojoWebTests(unittest.TestCase):

        def test_includeme(self):
            self.config.include('khufu_javascript.dojo')
            self.config.register_script('khufu_javascript.dojo:testscript.js')

            app = webtest.TestApp(self.config.make_wsgi_app())
            res = app.get('/dojo/foo/bar.js')
            self.assertTrue(res.status.startswith('200'))
