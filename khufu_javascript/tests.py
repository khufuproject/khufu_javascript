import unittest


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
