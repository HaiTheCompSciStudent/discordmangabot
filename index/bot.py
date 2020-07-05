import discord
from discord.ext import commands
from discord.utils import get
import aiohttp
import asyncio
import importlib.util
import sys
import time

from .dataio import DataIO
from .server import Server
from .errors import EmbedError


class BotError(EmbedError):
    COLOR = 0x000000

def _prefix_callable(bot, ctx):
    return bot.dataio.fetch("test_guilds", ctx.guild.id).get("prefix")

class Index(commands.Bot):

    def __init__(self, *args, **kwargs):
        self.config = kwargs.pop("config")
        self.session = aiohttp.ClientSession()
        self.dataio = DataIO(
            self.config["MONGO_URI"])
        self.__libs = {}
        super().__init__(*args, **kwargs)
        self.command_prefix = _prefix_callable

    async def send_feedback(self, *, embed):
        await self.feedback_channel.send(embed=embed)

    async def load_lib(self, name):
        spec = importlib.util.find_spec(name)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        try:
            spec.loader.exec_module(module)
            setup = getattr(module, "setup")
            lib = await setup(self)
        except Exception as err:
            print(err)
            del sys.modules[name]
        else:
            print("Library [{.name}] has been successfully loaded.".format(lib))
            self.__libs[name] = lib

    async def unload_lib(self, name):
        try:
            lib = self.__libs[name]
            teardown = getattr(lib, "teardown")
            await teardown(self)
        except AttributeError:
            pass
        finally:
            self.__libs.pop(name)
            del sys.modules[name]

    async def reload_libs(self):
        for name, lib in self.__libs.copy().items():
            try:
                self.__libs[name] = await lib.recreate(self)
            except Exception as err:
                print("Library [{0.name}] has failed to reload: {1}".format(lib, err))
                # Rollback the changes
                self.__libs[name] = lib

    def get_lib(self, name_or_alias):
        name_or_alias = name_or_alias.lower()
        for lib in self.libs:
            if name_or_alias in lib.name_or_aliases:
                return lib
        raise BotError("No library with name or alias '{0}' can be found.".format(name_or_alias))

    async def get_manga(self, reference, lib_name=None):
        if lib_name:
            # Do a database search first
            lib = self.get_lib(lib_name)
            id = lib.split_id(reference)
            data = self.dataio.fetch("test_manga", id)
            if data:
                return lib.manga_factory(id, data=data)
            else:
                manga = await lib.fetch_manga(id)
                self.dataio.insert("test_manga", manga.serialized)
                return manga
        else:
            for lib in self.libs:
                try:
                    id = lib.split_id(reference)
                except Exception:
                    continue
                data = self.dataio.fetch("test_manga", id)
                if data:
                    return lib.manga_factory(id, data=data)
                else:
                    try:
                        manga = await lib.fetch_manga(id)
                    except Exception:
                        continue
                    else:
                        self.dataio.insert("test_manga", manga.serialized)
                        print("Yes")
                        return manga
        raise BotError("Can't find any manga with the reference specified.")

    async def search_manga(self, query, *, lib_name=None):
        if lib_name:
            lib = self.get_lib(lib_name)
            return [manga async for manga in lib.search_manga(query)]
        else:
            results = []

            async def _add_list(lib):
                async for manga in lib.search_manga(query):
                    results.append(manga)

            await asyncio.gather(*(_add_list(lib) for lib in self.libs))

            return results

    async def fetch_chapters(self, origin, id, timestamp):
        lib = self.get_lib(origin)
        async for chapter in lib.fetch_chapters(id):
            if self._check_chapter_validity(chapter, timestamp):
                yield chapter
            else:
                break

    def _check_chapter_validity(self, chapter, timestamp):
        return all((
            timestamp - chapter.timestamp <= 20 * 60,
            chapter.lang_code == "gb",
            chapter.timestamp <= timestamp
        ))

    def get_server(self, id):
        data = self.dataio.fetch("test_guilds", id)
        return Server(data=data)

    def get_role(self, ctx, id):
        return get(ctx.guild.roles, id=id)

    def update_server(self, server):
        self.dataio.update("test_guilds", server.serialized)

    async def start(self, *args, **kwargs):
        for name in ["lib.mangadex", "lib.guyamoe"]:
            await self.load_lib(name)
        await super().start(*args, **kwargs)

    async def close(self):
        for name in self.__libs.keys():
            await self.unload_lib(name)
        await self.session.close()
        await super().close()

    @property
    def libs(self):
        return self.__libs.values()

    @property
    def servers(self):
        for guild in self.guilds:
            yield self.get_server(guild.id)

    @property
    def feedback_channel(self):
        return self.get_channel(self.config.get("feedback_channel"))
