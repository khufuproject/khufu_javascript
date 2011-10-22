import unittest

from khufu_javascript.testing import Mock, MockRegistryHolder

class ResourceHelperTests(unittest.TestCase):

    def get_resource_helper(self, *args, **kwargs):
        from khufu_javascript import ResourceHelper
        return ResourceHelper(*args, **kwargs)

    def test_init(self):
        helper = self.get_resource_helper(config=MockRegistryHolder())
        self.assertTrue(helper._settings is \
                            MockRegistryHolder.registry.settings)
        helper = self.get_resource_helper(request=MockRegistryHolder())
        self.assertTrue(helper._settings is \
                            MockRegistryHolder.registry.settings)

    def test_settings(self):
        helper = self.get_resource_helper(MockRegistryHolder())
        self.assertTrue('khufu_javascript.javascript_resources' in \
                            helper.settings)
        self.assertTrue('khufu_javascript.css_resources' in \
                            helper.settings)

    def test_add_resources(self):
        helper = self.get_resource_helper(MockRegistryHolder())
        settings = helper.settings

        helper.add_javascript('foo', 'foobar:static/some.js')
        self.assertTrue(
            ('foo', 'foobar:static/some.js') in \
                settings['khufu_javascript.javascript_resources'])

        helper.add_stylesheet('bar', 'foobar:static/some.css')
        self.assertTrue(
            ('bar', 'foobar:static/some.css')in \
                settings['khufu_javascript.css_resources'])

    def test_render(self):
        helper = self.get_resource_helper(MockRegistryHolder())
        helper.add_javascript('foo', 'foobar:static/some.js')
        helper.add_stylesheet('bar', 'foobar:static/some.css')

        rendered = helper.render(Mock(static_url=lambda x: x))
        self.assertTrue('some.js' in rendered)
        self.assertTrue('some.css' in rendered)


class MainTests(unittest.TestCase):
    def test_setup_globals(self):
        from khufu_javascript import setup_globals
        d = {'request': Mock(registry=Mock(settings={}))}
        setup_globals(d)
        self.assertTrue('resource_helper' in d)

    def test_includeme(self):
        from khufu_javascript import includeme
        holder = MockRegistryHolder()
        includeme(holder)
        self.assertTrue('get_resource_helper' in holder.directives)
        self.assertTrue(len(holder.subscribers) > 0)


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
