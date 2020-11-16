import re


class SourceMeta(type):

    def __new__(mcs, *args, **kwargs):
        name, bases, attrs = args
        attrs['color'] = kwargs.pop('color', 0x666666)
        attrs['code'] = kwargs.pop('code', '??')

        cls = super().__new__(mcs, name, bases, attrs)

        cls.__factory__ = kwargs.pop('factory', None)

        return cls


class Source(metaclass=SourceMeta):
    BASE = ""

    def __init__(self, session):
        self.session = session
        self._factory = self._get_factory()
        self.patterns = self.get_match_patterns()

    def _get_factory(self):
        factory = dict()
        for item in self.__class__.__factory__:
            name = item.__name__.lower()
            item.BASE = self.BASE
            factory[name] = item
        return factory

    def factory(self, name, *args, **kwargs):
        cls = self._factory[name]
        return cls(*args, **kwargs)

    def get_match_patterns(self):
        patterns = [self.code + r'(?P<id>.*)']
        for item in self._factory.values():
            regex = item.BASE + item.PATH
            for i, match in enumerate(re.finditer(r'\{(.*?)\}', item.BASE + item.PATH)):
                start, end = match.span()
                group = match.group()
                regex = regex[:start + i] + '(?P<{field}>.*)'.format(field=group[6:-1]) + regex[end + i:]
            patterns.append(regex)
        return patterns
