import doctest
import unittest
import os

from khufu_javascript.testing import Mock, MockRegistryHolder


class RootTests(unittest.TestCase):
    def test_includeme(self):
        from khufu_javascript import includeme
        # doesn't currently do anything
        includeme(None)


class ResourceRegistryTests(unittest.TestCase):

    def get_resource_registry(self, *args, **kwargs):
        from khufu_javascript._api import ResourceRegistry
        return ResourceRegistry(*args, **kwargs)

    def test_resource(self):
        from khufu_javascript._api import Resource
        r = Resource('foo.js', use_static_url=True)
        self.assertTrue('foo.js' in r.render(Mock(static_url=lambda x: x)))

    def test_add_resources(self):
        helper = self.get_resource_registry(MockRegistryHolder())
        helper.add_javascript('somepath.js')
        self.assertTrue('somepath.js' in helper._js)
        helper.add_stylesheet('some.css')
        self.assertTrue('some.css' in helper._css)

        self.assertRaises(ValueError, helper.add_stylesheet, 'some.css')

    def test_render(self):
        helper = self.get_resource_registry(parent=Mock(_js={}, _css={}))
        helper.add_javascript('some.js')
        helper.add_stylesheet('some.css')

        rendered = helper.render(Mock(static_url=lambda x: x))
        self.assertTrue('some.js' in rendered)
        self.assertTrue('some.css' in rendered)

    def test_get_resource_registry(self):
        from khufu_javascript import get_resource_registry
        r = get_resource_registry(Mock(registry=Mock(settings={})))
        self.assertEqual(r.parent, None)
        r = get_resource_registry(Mock(environ={}, registry=Mock(settings={'khufu_javascript.resource_registry': Mock()})))
        self.assertNotEqual(r.parent, None)


    def test_request_renderable(self):
        from khufu_javascript._api import RequestRenderable
        rr = RequestRenderable(Mock(render=lambda request: u'foo'), None)
        rr.render()

class PrefixedDictTests(unittest.TestCase):
    def test_setitem(self):
        from khufu_javascript.utils import PrefixedDict
        d = {}
        prefixed = PrefixedDict('foo.', d)
        prefixed['grr'] = 'abc'

        self.assertTrue('grr' in prefixed)
        self.assertTrue('foo.grr' in d)

    def test_contains(self):
        from khufu_javascript.utils import PrefixedDict
        d = {'foo': 'bar',
             'foo.abc': 'xyz',
             'foo.abc.grr': '123'}

        prefixed1 = PrefixedDict('foo.', d)
        self.assertTrue('abc' in prefixed1)

        prefixed2 = PrefixedDict('abc.', prefixed1)
        self.assertTrue('grr' in prefixed2)


class SourcedDictTests(unittest.TestCase):
    def test_it(self):
        from khufu_javascript.utils import SourcedDict

        d1 = {'foo': 'bar'}
        d2 = {'abc': 'xyz'}
        sourced = SourcedDict(d1, d2)

        self.assertEqual(sorted(sourced.keys()),
                         ['abc', 'foo'])


class MockIter(object):
    def abc(self):
        return

    def iterabc(self):
        return iter([])

    def __len__(self):
        return 0


class DictViewTests(unittest.TestCase):
    def test_it(self):
        from khufu_javascript.utils import _DictView
        m = MockIter()
        v = _DictView(m, 'abc')
        for x in v:
            break
        self.assertEqual(len(v), 0)
        self.assertTrue('foo' not in v)
        repr(v)
