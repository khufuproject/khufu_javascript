class _DictView(object):
    def __init__(self, data, attr):
        self.data = data
        self.attr = attr

    def __iter__(self):
        return getattr(self.data, 'iter' + self.attr)()

    def __len__(self):
        return len(self.data)

    def __contain__(self, k):
        return k in getattr(self.data, self.attr)()

    def __repr__(self):
        return repr(getattr(self.data, self.attr)())


class _DictMixin(dict):

    def viewkeys(self):
        return _DictView(self, 'keys')

    def viewvalues(self):
        return _DictView(self, 'values')

    def viewitems(self):
        return _DictView(self, 'items')

    def __len__(self):
        return len(self.keys())

    def items(self):
        return [(k, self[k]) for k in self.iterkeys()]

    def iteritems(self):
        for k in self.iterkeys():
            yield (k, self[k])

    def itervalues(self):
        for k in self.iterkeys():
            yield self[k]

    def values(self):
        return [x for x in self.itervalues()]

    def __iter__(self):
        return iter(self.iterkeys())

    def __contains__(self, k):
        return k in self.keys()

    def has_key(self, k):
        return k in self

    def keys(self):
        return [x for x in self.iterkeys()]

    def get(self, k, default=None):
        if k in self:
            return self[k]
        return default

    def __repr__(self):
        mname = self.__class__.__module__
        items = ', '.join(map('%r: %r'.__mod__, self.items()))
        return '%s.%s({%s})' % (mname,
                                self.__class__.__name__,
                                items)

    def as_dict(self):
        d = {}
        for k, v in self.iteritems():
            d[k] = v
        return d


class PrefixedDict(_DictMixin):

    def __init__(self, prefix, data=None):
        self.prefix = prefix
        if data is None:
            data = {}
        self.data = data

    def __setitem__(self, k, v):
        self.data.__setitem__(self.prefix + k, v)

    def __getitem__(self, k):
        return self.data.__getitem__(self.prefix + k)

    def __delitem__(self, k):
        self.data.__detitem__(self.prefix + k)

    def iterkeys(self):
        return (x[len(self.prefix):]
                for x in self.data.keys()
                if x.startswith(self.prefix))


class ImmutableDict(_DictMixin):
    def __setitem__(self, k, v):
        raise NotImplemented('dict is immutable')

    def __delitem__(self, k):
        raise NotImplemented('dict is immutable')


class SourcedDict(_DictMixin):
    def __init__(self, primary, *extra_sources):
        self.primary = primary
        self.extra_sources = extra_sources

    @property
    def sources(self):
        res = [self.primary]
        res.extend(self.extra_sources)
        return res

    def __getitem__(self, k):
        for source in self.sources:
            if source is not None and k in source:
                return source[k]
        raise KeyError(k)

    def iterkeys(self):
        keys = []
        for source in self.sources:
            if source is None:
                continue
            for k in source.keys():
                if k not in keys:
                    keys.append(k)
                    yield k

    def __setitem__(self, k, v):
        self.primary.__setitem__(k, v)
