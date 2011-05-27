import unittest
from pyramid.testing import setUp as setUpPyramid, DummyRequest


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
                         {'foo': app_url + 'dojo/foo'})

    def test_includeme(self):
        self.config.include('khufu_javascript.dojo')
        self.config.register_script('khufu_javascript.dojo:testscript.js')

        from webtest import TestApp
        app = TestApp(self.config.make_wsgi_app())
        res = app.get('/dojo/foo/bar.js')
        self.assertTrue(res.status.startswith('200'))
