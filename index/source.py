import functools
import aiohttp

from .manga import Manga
from .chapter import Chapter


def wrapper(coro):
    @functools.wraps(coro)
    async def wrapped(self, *args, **kwargs):
        return await coro(self, *args, **kwargs)

    return wrapped


# Defaults
ABSTRACT_METHODS = ("get_manga", "get_chapter", "search_manga")
FACTORY = (Manga, Chapter)


class SourceMeta(type):

    def __new__(mcs, *args, **kwargs):

        name, bases, attrs = args
        attrs["color"] = kwargs.pop("color", 0x000000)
        attrs["name"] = kwargs.pop("name", name)
        attrs["url"] = kwargs.pop("url")
        cls = super().__new__(mcs, name, bases, attrs)

        cls.__factory_attrs__ = kwargs.pop("factory_attrs", {})
        cls.__factory__ = {factory.name: factory.inject(cls) for factory in kwargs.pop("factory", FACTORY)}

        for name in ABSTRACT_METHODS:
            try:
                coro = getattr(cls, name)
            except AttributeError:
                pass
            else:
                setattr(cls, name, wrapper(coro))

        return cls



class Source(metaclass=SourceMeta):

    @classmethod
    def factory(cls, name, *args, **kwargs):
        factory = cls.__factory__.get(name)
        return factory(*args, **kwargs)



