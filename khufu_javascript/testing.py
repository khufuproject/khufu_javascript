class Mock(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class MockRegistryHolder(object):
    registry = Mock(settings={})

    def __init__(self):
        self.directives = {}
        self.subscribers = []

    def add_directive(self, name, o):
        self.directives[name] = o

    def add_subscriber(self, f, o):
        self.subscribers.append((f, o))
