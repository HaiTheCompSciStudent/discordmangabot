import aiohttp
import models

from source import Source

import bs4

from collections import namedtuple


class Manga(models.Manga):
    PATH = "title/{self.id}"


class Chapter(models.Chapter):
    PATH = "chapter/{self.id}"


class MangadexError(Exception):
    pass


class Mangadex(Source, color=0xf69e38, code='md', factory=[Manga, Chapter]):
    BASE = "https://mangadex.org/"

    def __init__(self, session):
        super().__init__(session)
        self.logged_on = False

    async def login(self, username, password, retries=3):
        path = "ajax/actions.ajax.php?function=login"
        headers = {
            'x-requested-with': "XMLHttpRequest",
            'user-agent': 'dedicatus545-discord'
        }
        data = {
            'login_username': username,
            'login_password': password,
            'remember_me': 1
        }
        while self.logged_on is False and retries > 0:
            retries -= 1
            resp = await self.session.post(self.BASE + path, headers=headers, data=data)
            self.logged_on = 'mangadex_session' in list(resp.cookies.keys())

    async def fetch(self, path, **kwargs):
        resp = await self.session.get(self.BASE + "api/v2/" + path, **kwargs)
        payload = await resp.json()

        try:
            resp.raise_for_status()
        except aiohttp.ClientResponseError:
            message = payload.get("message")
            raise MangadexError(message)

        return payload.get("data")

    async def get_manga(self, id):
        path = "manga/{id}".format(id=id)
        data = await self.fetch(path)
        return self.factory('manga', data=data)

    async def get_chapter(self, id):
        path = "chapter/{id}".format(id=id)
        data = await self.fetch(path)
        return self.factory('chapter', data=data)

    async def get_chapters(self, id, *, check=lambda *args: True, **kwargs):
        path = "manga/{id}/chapters".format(id=id)
        data = await self.fetch(path, **kwargs)
        for c_data in data.get("chapters"):
            if check(c_data):
                yield self.factory('chapter', data=c_data)

    async def search_titles(self, title):
        if not self.logged_on:
            raise MangadexError
        path = "search?title={title}".format(title=title)
        resp = await self.session.get(self.BASE + path)
        text = await resp.text()
        soup = bs4.BeautifulSoup(text, "html.parser")
        dummy = namedtuple("dummy", ['title', 'id'])
        for idx, entry in enumerate(
                soup.find_all('div', attrs={'class': 'manga-entry col-lg-6 border-bottom pl-0 my-1'})):
            t = entry.find('a', attrs={'class': 'ml-1 manga_title text-truncate'}).get('title')
            id = entry.get('data-id')
            yield dummy(t, id)


async def setup(bot):
    src = Mangadex(bot.session)
    await src.login("Tokubetsu", "ng yu yue123")
    return src
