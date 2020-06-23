from index.library import Library
from index.errors import LibraryError
import aiohttp
import bs4


class MangadexError(LibraryError):
    COLOR = 0xf7931e


class Mangadex(Library):
    color = 0xf7931e
    def __init__(self, *args, **kwargs):
        self.credentials = kwargs.pop("credentials")
        super().__init__(*args, **kwargs)

    def split_id(self, reference):
        if reference.isdigit():
            return reference
        elif reference.startswith("https://mangadex.org/title"):
            return reference.split("/")[4]
        raise MangadexError("Invalid URL or ID provided.")

    async def request(self, url):
        try:
            return await self.bot.session.get(url)
        except aiohttp.ClientResponseError as err:
            if err.status in (503, 502, 403):
                raise MangadexError("Mangadex.org is currently undergoing DDOS mitigation.")
            if err.status == 404:
                raise MangadexError("Invalid URL of ID provided.")
            if err.status >= 500:
                raise MangadexError("Mangadex.org is currently unavailable. **[{0.status}]**".format(err))

    async def fetch_manga(self, id):
        resp = await self.request("https://mangadex.org/api/manga/{0}".format(id))
        data = await resp.json()
        return self.manga_factory(id, data=data["manga"])

    async def fetch_chapters(self, manga_id):
        resp = await self.request("https://mangadex.org/api/manga/{0}".format(manga_id))
        data = await resp.json()
        for id, chapter in data.get("chapter", {}).items():
            yield self.chapter_factory(id, data=chapter)

    async def search_manga(self, *args, max_results=5):
        if not self.logged_on:
            raise MangadexError("Search is currently unavailable as the bot can't authenticate with Mangadex.org.")
        query = "%20".join(args)
        resp = await self.request("https://mangadex.org/search?title={0}".format(query))
        html = await resp.text()
        soup = bs4.BeautifulSoup(html, "html.parser")
        for i, entry in enumerate(soup.find_all("div", {"class": "manga-entry col-lg-6 border-bottom pl-0 my-1"})):
            if i >= max_results:
                break
            id = entry.get("data-id")
            yield await self.fetch_manga(id)

    async def login(self):
        username, password = self.credentials
        await self.bot.session.post(
            url="https://mangadex.org/ajax/actions.ajax.php?function=login",
            headers={
                "x-requested-with": "XMLHttpRequest",
                "user-agent": "index-discord-bot"
            },
            data={
                "login_username": username,
                "login_password": password,
                "remember_me": 1
            })

    @property
    def logged_on(self):
        return "mangadex_session" in (cookie.key for cookie in self.bot.session.cookie_jar)

    @classmethod
    async def recreate(cls, bot):
        lib = cls(bot, **bot.config["LIBRARIES"]["mangadex"])
        await lib.login()
        return lib


async def setup(bot):
    return await Mangadex.recreate(bot)
