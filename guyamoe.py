import aiohttp
import re
import models

from source import Source
from collections import namedtuple


class Manga(models.Manga):
    PATH = "read/manga/{self.slug}"

    def __init__(self, *, data):
        super().__init__(data=data)
        self.slug = data.pop("slug")


class Chapter(models.Chapter):
    PATH = "read/manga/{self.slug}/{self.chapter}"

    def __init__(self, *, data):
        super().__init__(data=data)
        self.slug = data.pop("slug")


class GuyaMoe(Source, color=0x862220, code='gm', factory=[Manga, Chapter]):
    BASE = "https://guya.moe/"

    async def fetch(self, path, **kwargs):
        resp = await self.session.get(self.BASE + "api/" + path, **kwargs)
        data = await resp.json()
        return data

    async def get_manga(self, *, slug):
        path = "series/{slug}".format(slug=slug)
        data = await self.fetch(path)
        return self.factory('manga', data=data)

    async def get_chapters(self, *, slug, check=lambda *args: True):
        path = "series/{slug}".format(slug=slug)
        data = await self.fetch(path)
        for c, item in data['chapters'].items():
            c_data = {
                "chapter": c,
                "title": item['title'],
                "timestamp": item['release_data']['1']
            }
            if check(c_data):
                yield self.factory('chapter', data=c_data)

    async def search_titles(self, title):
        path = "get_all_series"
        data = await self.fetch(path)
        dummy = namedtuple("dummy", ['title', 'slug'])
        for t, item in data.items():
            if re.search(title, t, re.IGNORECASE):
                yield dummy(t, item['slug'])


async def setup(bot):
    src = GuyaMoe(bot.session)
    return src
