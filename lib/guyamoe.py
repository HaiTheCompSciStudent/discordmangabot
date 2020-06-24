from index.library import Library
from index.manga import Manga
from index.chapter import Chapter
from index.errors import LibraryError
import random
import aiohttp
import re

SLUG_ID_TABLE = {
    "Kaguya-Wants-To-Be-Confessed-To": "gm1",
    "Kaguya-Wants-To-Be-Confessed-To-Official-Doujin": "gm2",
    "We-Want-To-Talk-About-Kaguya": "gm3"
}

ID_SLUG_TABLE = {
    "gm1": "Kaguya-Wants-To-Be-Confessed-To",
    "gm2": "Kaguya-Wants-To-Be-Confessed-To-Official-Doujin",
    "gm3": "We-Want-To-Talk-About-Kaguya",
}


class GuyaError(LibraryError):
    COLOR = 0xc71025


class GuyaMoe(Library):
    color = 0xc71025
    def __init__(self, bot, **kwargs):
        manga = kwargs.get("manga")
        super().__init__(bot, **kwargs)

        class MangaFactory(Manga, settings=manga):

            def __init__(self, slug, *, data):
                self.slug = slug
                id = SLUG_ID_TABLE.get(self.slug)
                super().__init__(id, data=data)

            @property
            def page_url(self):
                return self.PAGE_BASE.format(self.slug)

        self.manga_factory = MangaFactory

    async def request(self, url):
        try:
            return await self.bot.session.get(url)
        except aiohttp.ClientResponseError as err:
            if err.status == 500:
                raise GuyaError("Invalid URL or ID provided.")
            raise GuyaError("Guya.moe is currently unavailable. **[{0.status}]**".format(err))

    def split_id(self, reference):
        if reference.startswith("https://guya.moe/"):
            return SLUG_ID_TABLE.get(reference.split("/")[5])
        elif reference in ID_SLUG_TABLE:
            return reference
        elif reference in SLUG_ID_TABLE:
            return SLUG_ID_TABLE.get(reference)
        raise GuyaError("Invalid URL or ID provided.")

    async def fetch_manga(self, id):
        slug = ID_SLUG_TABLE.get(id)
        url = "https://guya.moe/api/series/{0}".format(slug)
        resp = await self.request(url)
        data = await resp.json()

        data["cover_url"] = data.pop("cover")

        return self.manga_factory(id, data=data)

    async def fetch_chapters(self, id):
        slug = ID_SLUG_TABLE.get(id)
        url = "https://guya.moe/api/series/{0}".format(slug)
        resp = await self.request(url)
        data = await resp.json()
        # Sort by the second item (value) in the key-value pair first entry in the 'release date' key
        for _chapter, _data in sorted(data["chapters"].items(),
                                      key=lambda p: next(p[1].get("release_date").values()),
                                      reverse=True):
            _data["id"] = "{0}/{1}/1".format(slug, _chapter)
            _data["chapter"] = _chapter
            _data["timestamp"] = next(_data.pop("release_date").values())
            _data["lang_code"] = "gb"
            yield self.chapter_factory(_data["id"], data=_data)

    async def search_manga(self, *args, max_results=5):
        url = "https://guya.moe/api/get_all_series/"
        resp = await self.request(url)
        data = await resp.json()

        for i, pair in enumerate(data.items()):
            title, manga = pair
            if i >= max_results:
                break
            if any((key.lower() in title.lower() for key in args)):
                yield await self.fetch_manga(manga["slug"])

    @classmethod
    async def recreate(cls, bot):
        lib = cls(bot, **bot.config["LIBRARIES"]["guyamoe"])
        return lib


async def setup(bot):
    return await GuyaMoe.recreate(bot)
