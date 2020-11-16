import discord
import asyncio
import aiohttp

import collections
import importlib.util
import sys
import re

from discord.ext import commands
from contextlib import contextmanager


class SourceError(Exception):

    def __init__(self, *args, color):
        self.color = color
        super().__init__(*args)


class Sources:

    def __init__(self, bot, *, names):
        self.bot = bot
        self.names = names
        self._sources = {}
        self._patterns = {}

    def __iter__(self):
        return iter(self._sources.values())

    def get(self, code):
        for source in self:
            if source.code is code:
                return source
        else:
            raise LookupError

    def parse_code(self, code):
        for s_code, patterns in self._patterns.items():
            for pattern in patterns:
                m = re.search(pattern, code)
                if m is not None:
                    return s_code, m.groupdict()
        else:
            raise SourceError

    async def _load_source(self, name):
        spec = importlib.util.find_spec(name)
        lib = importlib.util.module_from_spec(spec)
        sys.modules[name] = lib
        try:
            spec.loader.exec_module(lib)
            setup = getattr(lib, 'setup')
            source = await setup(self.bot)
        except Exception as e:
            del sys.modules[name]
            raise e
        else:
            self._sources[name] = source

    def _unload_source(self, name):
        try:
            self._sources[name]
        except AttributeError:
            pass
        else:
            self._sources.pop(name)
            del sys.modules[name]

    def _get_patterns(self):
        patterns = dict()
        for source in self:
            patterns[source.code] = source.patterns
        return patterns

    async def start(self):
        for name in self.names:
            await self._load_source(name)
        self._patterns = self._get_patterns()


class Index(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = aiohttp.ClientSession()
        self.sources = Sources(self, names=["mangadex", "guyamoe"])

    @contextmanager
    def get_source(self, code):
        # The safe 'get_source'
        try:
            source = self.sources.get(code)
        except KeyError:
            raise

        try:
            yield source
        except Exception as e:
            raise SourceError(e.args, color=source.color)

    async def get_manga(self, id):
        code, kwargs = self.sources.parse_code(id)
        with self.get_source(code) as source:
            manga = await source.get_manga(**kwargs)
            return manga

    async def get_chapter(self, id):
        code, kwargs = self.sources.parse_code(id)
        with self.get_source(code) as source:
            chapter = await source.get_chapter(**kwargs)
            return chapter

    async def get_chapters(self, id, *, check=lambda *args: True):
        code, kwargs = self.sources.parse_code(id)
        with self.get_source(code) as source:
            async for chapter in source.get_chapters(**kwargs, check=check):
                yield chapter

    async def search_titles(self, title, *, code=None):
        if code is None:
            # We are doing global search baby
            async def task(s, t):
                return [dummy async for dummy in s.search_titles(t)]

            tasks = [task(source, title) for source in self.sources]

            while tasks:
                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                tasks = pending

                titles = done.pop().result()

                if not titles:
                    continue

                yield titles

        else:

            with self.get_source(code) as source:
                yield [dummy async for dummy in source.search_titles(title)]

    async def start(self, *args, **kwargs):
        await self.sources.start()
        await super().start(*args, **kwargs)
