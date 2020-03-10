import aiohttp
import discord
from discord.ext import commands, tasks
from bs4 import BeautifulSoup

from database import database
from exceptions import MangadexError, EntryError, NoChoiceError, EmptyError
import util
from util import MangaPaginator, ChoiceMenu

from models.manga import Manga
from models.chapter import Chapter
from models.subscription import Subscription

from config import LOGIN_CRED, UPDATE_INTERVAL, AUTH_INTERVAL

import time


class Mangadex(commands.Cog):

    def __init__(self, bot, session=None, is_auth=False):
        self.bot = bot
        self.session = aiohttp.ClientSession() if session is None else session
        self._manga_update_task.start()
        self.is_auth = is_auth
        self._auth_task.start()

    async def login(self, username, password):
        if not username or not password:
            raise ValueError("No username or password!")
        url = "https://mangadex.org/ajax/actions.ajax.php?function=login"
        headers = {
            "x-requested-with": "XMLHttpRequest"
        }
        payload = {
            "login_username": username,
            "login_password": password
        }
        await self.session.post(url, headers=headers, data=payload)

    async def fetch_html(self, url):
        async with self.session.get(url) as resp:
            resp.raise_for_status()
            return await resp.text()

    async def fetch_json(self, url):
        async with self.session.get(url) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def fetch_manga(self, manga_id):
        url = f"https://mangadex.org/api/manga/{manga_id}"
        try:
            data = await self.fetch_json(url)
            manga = data["manga"]
        except aiohttp.ClientResponseError as err:
            if err.status == 404:
                raise MangadexError(f"**[`{manga_id}`]** isn't a valid Manga ID.")
            else:
                raise MangadexError(f"**HTTP Error** encountered when accessing Mangadex API : **[`{err.status}`]**")
        else:
            manga["id"] = manga_id
            return Manga.populate(manga)

    async def fetch_chapter(self, chapter_id):
        url = f"https://mangadex.org/api/chapter/{chapter_id}"
        try:
            chapter = await self.fetch_json(url)
        except aiohttp.ClientResponseError as err:
            if err.status == 404:
                raise MangadexError(f"**[`{chapter_id}`]** isn't a valid Chapter ID.")
            raise MangadexError(f"** **HTTP Error** encountered when accessing Mangadex API : **[`{err.status}`]**")
        else:
            chapter["id"] = chapter_id
            return Chapter.populate(chapter)

    async def fetch_chapters(self, manga_id, time_limit, current_time, lang_code="gb"):
        url = f"https://mangadex.org/api/manga/{manga_id}"
        try:
            data = await self.fetch_json(url)
            title = data["manga"]["title"]
            chapters = data["chapter"]
        except aiohttp.ClientResponseError as err:
            if err.status == 404:
                raise MangadexError(f"**[`{manga_id}`]** isn't a valid Manga ID.")
            else:
                raise MangadexError(f"** **HTTP Error** encountered when accessing Mangadex API : **[`{err.status}`]**")
        except KeyError:
            raise MangadexError(f"{title} doesn't have any chapters!")
        else:
            fetched_chapters = []
            for chapter_id in chapters:
                chapter = chapters[chapter_id]
                if chapter["lang_code"] == lang_code:
                    if current_time - chapter["timestamp"] < time_limit:
                        chapter["id"] = chapter_id
                        fetched_chapters.append(Chapter.populate(chapter))
                    else:
                        break
            return fetched_chapters

    async def search(self, title, max_results=5):
        url = f"https://mangadex.org/search?title={title}"
        print(url)
        try:
            html = await self.fetch_html(url)
        except aiohttp.ClientResponseError as err:
            raise MangadexError(f"HTTP Error encountered when accessing Mangadex API : [{err.status}]")
        soup = BeautifulSoup(html, "html.parser")
        queries = soup.find_all("div", {"class": "manga-entry col-lg-6 border-bottom pl-0 my-1"})
        results = []
        for i, query in enumerate(queries):
            title = query.find("a", {"class": "ml-1 manga_title text-truncate"}).get("title")
            print(title)
            manga_id = query.get("data-id")
            manga_data = {
                "id": manga_id,
                "title": title
            }
            results.append(Manga.populate(manga_data))
            if i == max_results - 1:
                break
        return results

    @commands.command(name="sub",
                      usage="[Manga ID||Manga URL] [@Member]",
                      description="Subscribe the user to a manga and pings them when there is a new chapter.",
                      help="[Manga ID||Manga URL]:\n"
                           "#Reference to the manga, could be a Mangadex.org link or a id\n"
                           "[@Member]:\n"
                           "#Must be a ping to a member of the guild, defaulted to the user\n"
                           " \n"
                           "Example:\n"
                           "{prefix}sub 39 @dude\n"
                           "#Subscribes @dude to [One Piece] (https://mangadex.org/title/39)")
    async def sub(self, ctx, manga_ref, member: discord.Member = None):
        member = ctx.author if member is None else member
        guild = database.get_guild(ctx.guild.id)

        manga_id = util.split_id(manga_ref)
        manga = database.get_manga(manga_id)

        if manga is None:
            manga = await self.fetch_manga(manga_id)
            database.add_manga(manga)

        if manga_id not in guild.id_list:
            guild.subscriptions.append(Subscription(manga_id))

        subscription = guild.get_subscription(manga_id)

        if member.id in subscription.subscribers:
            raise EntryError(f"**{member}** is already subscribed to **[{manga.title}]**.")

        subscription.subscribers.append(member.id)

        database.update_guild(guild)

        embed = discord.Embed(color=0x00aaff,
                              description=f"☑ **Success:** **{member}** has successfully subscribed to **[{manga.title}].**")
        await ctx.send(embed=embed)

    @commands.command(name="unsub",
                      usage="[Manga ID||Manga URL] [@Member]",
                      description="Unsubscribe the user from a manga.",
                      help="[Manga ID||Manga URL]:\n"
                           "#Reference to the manga, could be a Mangadex.org link or a id\n"
                           "[@Member]:\n"
                           "#Must be a ping to a member of the guild, defaulted to the user\n"
                           " \n"
                           "Example:\n"
                           "{prefix}unsub 39 @dude\n"
                           "#Unubscribes @dude from [One Piece] (https://mangadex.org/title/39)")
    async def unsub(self, ctx, manga_ref, member: discord.Member = None):
        member = ctx.author if member is None else member
        guild = database.get_guild(ctx.guild.id)

        manga_id = util.split_id(manga_ref)
        manga = database.get_manga(manga_id)

        if manga is None:
            manga = await self.fetch_manga(manga_id)
            database.add_manga(manga)

        if manga_id not in guild.id_list:
            raise EntryError(f"**[{manga.title}]** is not on the subscription list.")

        subscription = guild.get_subscription(manga_id)

        if member.id not in subscription.subscribers:
            raise EntryError(f"**{member}** is already subscribed to **[{manga.title}]**.")

        subscription.subscribers.remove(member.id)

        database.update_guild(guild)

        embed = discord.Embed(color=0x00aaff,
                              description=f"☑ **Success:** **{member}** has successfully unsubscribed from **[{manga.title}]**.")
        await ctx.send(embed=embed)

    @commands.command(name="addsub",
                      usage="[Manga ID||Manga URL]",
                      description="Add a manga to the subscription list.",
                      help="[Manga ID||Manga URL]:\n"
                           "#Reference to the manga, could be a Mangadex.org link or a id\n"
                           " \n"
                           "Example:\n"
                           "{prefix}addsub 39\n"
                           "#Adds [One Piece] to the subscription list (https://mangadex.org/title/39)")
    async def add_sub(self, ctx, manga_ref):
        guild = database.get_guild(ctx.guild.id)

        manga_id = util.split_id(manga_ref)
        manga = database.get_manga(manga_id)

        if manga is None:
            manga = await self.fetch_manga(manga_id)
            database.add_manga(manga)

        if manga_id in guild.id_list:
            raise EntryError(f"**[{manga.title}]** is already on the subscription list.")

        guild.subscriptions.append(Subscription(manga_id))

        database.update_guild(guild)

        embed = discord.Embed(color=0x00aaff,
                              description=f"☑ **Success:** **[{manga.title}]** has successfully been added to the subscription list.")
        await ctx.send(embed=embed)

    @commands.command(name="removesub",
                      usage="[Manga ID||Manga URL]",
                      description="Add a manga to the subscription list.",
                      help="[Manga ID||Manga URL]:\n"
                           "#Reference to the manga, could be a Mangadex.org link or a id\n"
                           " \n"
                           "Example:\n"
                           "{prefix}removesub 39\n"
                           "#Removes [One Piece] from the subscription list (https://mangadex.org/title/39)")
    async def remove_sub(self, ctx, manga_ref):
        guild = database.get_guild(ctx.guild.id)

        manga_id = util.split_id(manga_ref)
        manga = database.get_manga(manga_id)

        if manga is None:
            manga = await self.fetch_manga(manga_id)
            database.add_manga(manga_id)

        if manga_id not in guild.id_list:
            EntryError(f"**[{manga.title}]** is not on the subscription list.")

        subscription = guild.get_subscription(manga_id)
        guild.subscriptions.remove(subscription)

        database.update_guild(guild)

        embed = discord.Embed(color=0x00aaff,
                              description=f"☑ **Success:** **[{manga.title}]** has successfully been removed to the subscription list.")
        await ctx.send(embed=embed)

    @commands.command(name="list",
                      usage="",
                      description="List all the manga currently subscribed in the server.",
                      help="Hint:\n"
                           "#Use reaction to switch pages.")
    async def list(self, ctx):
        guild = database.get_guild(ctx.guild.id)
        lines = []
        for i, manga_id in enumerate(guild.id_list):
            manga = database.get_manga(manga_id)
            lines.append(f"[{(i + 1)}] : {manga.title} [{manga.id}]")
        if not lines:
            raise EmptyError(f"**[`{ctx.guild.name}`]** doesn't have any any subscriptions.")
        embed = discord.Embed(color=0x00aaff)
        embed.set_author(name=ctx.guild.name)
        await MangaPaginator.paginate(ctx, embed, lines, fill_empty=True)

    @commands.command(name="info",
                      usage="[Manga ID||Manga URL]",
                      description="Shows all the subscribers of a manga.",
                      help="[Manga ID||Manga URL]:\n"
                           "#Reference to the manga, could be a Mangadex.org link or a id\n"
                           " \n"
                           "Example:\n"
                           "{prefix}info 39\n"
                           "#Shows [One Piece] subscribers. (https://mangadex.org/title/39)")
    async def info(self, ctx, manga_ref):
        guild = database.get_guild(ctx.guild.id)
        manga_id = util.split_id(manga_ref)
        manga = database.get_manga(manga_id)

        if manga is None:
            manga = await self.fetch_manga(manga_id)
            database.add_manga(manga)

        if manga_id not in guild.id_list:
            raise EntryError(f"**[{manga.title}]** is not on the subscription list.")

        subscription = guild.get_subscription(manga_id)

        if not subscription.subscribers:
            raise EmptyError(f"There is members currently subscribed to **[{manga.title}]**.")

        members = ", ".join([f"{str(self.bot.get_user(subscriber))}" for subscriber in subscription.subscribers])

        embed = discord.Embed(color=0x00aaff)
        embed.set_author(name=util.shorten_text(manga.title, 55))
        embed.add_field(name="Subscribers", value=util.code_blockify(members))

        await ctx.send(embed=embed)

    @commands.command(name="here",
                      usage="",
                      description="Designate the channel where the command is called as the update channel.",
                      help="Hint:\n"
                           "#Make sure bots can post in the channel you want to designate,"
                           "without this command being called the bot is pretty much useless.")
    async def here(self, ctx):
        guild = database.get_guild(ctx.guild.id)
        guild.channel = ctx.channel.id
        database.update_guild(guild)

        embed = discord.Embed(color=0x00aaff,
                              description=f"☑ **Success:** **[{ctx.channel}]** has be designated as the update channel.")
        await ctx.channel.send(embed=embed)

    @commands.command(name="search",
                      usage="[Keywords]",
                      description="Search manga based on the keywords on mangadex.org and adds them if given a choice.",
                      help="[Keywords]:\n"
                           "#Keywords to be searched on Mangadex.org\n"
                           " \n"
                           "Example:\n"
                           "{prefix}search One Piece\n"
                           "#Searches [One Piece] on Mangadex.org\n"
                           " \n"
                           "Hint:\n"
                           "#Use reaction to pick the results and add it to the subscription list.")
    async def quick_search(self, ctx, *key):
        if not self.is_auth:
            raise MangadexError("Search function is currently unavailable, please try again later.")

        guild = database.get_guild(ctx.guild.id)

        if len(key) <= 0:
            raise commands.UserInputError
        regex = "%20".join(key)

        results = await self.search(regex)

        if len(results) <= 0:
            raise EmptyError("No results found!")

        choices = []
        for i, manga in enumerate(results):
            choices.append((manga.id, f"[{i + 1}] : {manga.title} {manga.id}"))

        embed = discord.Embed(color=0x00aaff)
        embed.set_author(name=f"Showing {len(results)} results.")

        manga_id = await ChoiceMenu.prompt(ctx, embed, choices, max_lines=5, fill_empty=True)

        if manga_id is None:
            raise NoChoiceError

        manga = database.get_manga(manga_id)

        if manga is None:
            manga = await self.fetch_manga(manga_id)
            database.add_manga(manga)

        if manga_id in guild.id_list:
            raise EntryError(f"**[{manga.title}]** is already on the subscription list.")

        guild.subscriptions.append(Subscription(manga_id))

        database.update_guild(guild)

        embed = discord.Embed(color=0x00aaff,
                              description=f"☑ **Success:** **[{manga.title}]** has successfully been added to the subscription list.")
        await ctx.send(embed=embed)

    @tasks.loop(seconds=UPDATE_INTERVAL)
    async def _manga_update_task(self):
        print("Starting update loop")
        current_time = time.time()
        fetched_chapter_pool = {}
        for guild in database.guilds:
            try:
                channel = self.bot.get_channel(guild.channel)
                if channel is not None:
                    for manga_id in guild.id_list:
                        subscription = guild.get_subscription(manga_id)
                        try:
                            fetched_chapters = fetched_chapter_pool[manga_id]
                        except KeyError:
                            fetched_chapter_pool[manga_id] = await self.fetch_chapters(manga_id, UPDATE_INTERVAL,
                                                                                       current_time)
                            fetched_chapters = fetched_chapter_pool[manga_id]
                        ping_members = " ".join([f"<@{subscriber}>" for subscriber in subscription.subscribers])
                        fetched_chapter_links = "\n".join([chapter.url for chapter in fetched_chapters])
                        if fetched_chapter_links:
                            await channel.send("\n".join([ping_members, fetched_chapter_links]))

            except Exception as err:
                # CATCHES ALL THE ERRORS BECAUSE IT FREQUENTLY BREAKS
                print(err)
        print(f"{len(fetched_chapter_pool)} tracked, update loop ended")

    @_manga_update_task.before_loop
    async def _before_update_task(self):
        await self.bot.wait_until_ready()

    @tasks.loop(seconds=AUTH_INTERVAL)
    async def _auth_task(self):
        print("Starting authenticate task.")
        await self.login(LOGIN_CRED["USERNAME"], LOGIN_CRED["PASSWORD"])
        self.is_auth = False if not await self.search("komi") else True
        print(f"Authenticate task ended, authentication status: {self.is_auth}")

    @_auth_task.before_loop
    async def _before_auth_task(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Mangadex(bot))
