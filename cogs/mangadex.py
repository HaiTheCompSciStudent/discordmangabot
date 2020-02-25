import asyncio
import discord
import math
import os
import time
from discord.ext import commands, tasks

import aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv

import formatter
from cogs.exceptions import *
from database import database
from models.discord.guild import Guild
from models.mangadex.chapter import Chapter
from models.mangadex.manga import Manga

# TODO: add a config file
load_dotenv()

USERNAME = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
UPDATE_INTERVAL = os.getenv('UPDATE_INTERVAL')


class Mangadex(commands.Cog, name="Mangadex"):

    def __init__(self, bot, session, is_auth):
        self.bot = bot
        self.session = session
        self.is_auth = is_auth
        self.manga_update_task.start()

    @staticmethod
    async def login(username, password):
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

        session = aiohttp.ClientSession()
        await session.post(url, headers=headers, data=payload)
        return session

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
                raise MangadexError(f"❌ **Error:** **[`{manga_id}`]** isn't a valid Manga ID.")
            else:
                raise MangadexError(f"❌ **Error:"
                                    f"** **HTTP Error** encountered when accessing Mangadex API : **[`{err.status}`]**")
        else:
            return Manga(manga_id).populate(manga)

    async def fetch_chapter(self, chapter_id):
        url = f"https://mangadex.org/api/chapter/{chapter_id}"
        try:
            chapter = await self.fetch_json(url)
        except aiohttp.ClientResponseError as err:
            if err.status == 404:
                raise MangadexError(f"❌ **Error:** **[`{chapter_id}`]** isn't a valid Chapter ID.")
            raise MangadexError(f"❌ **Error:"
                                f"** **HTTP Error** encountered when accessing Mangadex API : **[`{err.status}`]**")
        else:
            return Chapter(chapter_id).populate(chapter)

    async def fetch_chapters(self, manga_id, time_limit, current_time, lang_code="gb"):
        url = f"https://mangadex.org/api/manga/{manga_id}"
        try:
            data = await self.fetch_json(url)
            title = data["manga"]["title"]
            chapters = data["chapter"]
        except aiohttp.ClientResponseError as err:
            if err.status == 404:
                raise MangadexError(f"❌ **Error:** **[`{manga_id}`]** isn't a valid Manga ID.")
            else:
                raise MangadexError(f"❌ **Error:"
                                    f"** **HTTP Error** encountered when accessing Mangadex API : **[`{err.status}`]**")
        except KeyError:
            raise MangadexError(f"{title} doesn't have any chapters!")
        else:
            fetched_chapters = []
            for chapter_id in chapters:
                chapter = chapters[chapter_id]
                if chapter["lang_code"] == lang_code:
                    if current_time - chapter["timestamp"] < time_limit:
                        fetched_chapters.append(Chapter(chapter_id).populate(chapter))
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
                "title": title
            }
            results.append(Manga(manga_id).populate(manga_data))
            if i == max_results - 1:
                break
        return results

    @commands.command(name="sub", usage="[Manga ID] [@Member]")
    async def sub(self, ctx, manga_id: str, member: discord.Member = None):

        member = ctx.author if member is None else member

        guild = database.get_guild(ctx.guild.id)
        manga = database.get_manga(manga_id)

        if not manga:
            manga = await self.fetch_manga(manga_id)
            database.insert_manga(manga)

        if not guild.check_subscription(manga_id):
            guild.insert_subscription(manga_id)

        subscription = guild.get_subscription(manga_id)

        try:
            subscription.insert_subscriber(member.id)
        except EntryError:
            raise EntryError(f"❌ **Error:** **{member}** is already subscribed to **[{manga.title}]**.")

        database.update_guild(ctx.guild.id, guild.serialize())
        success_msg = f"☑ **{member}** has successfully subscribed to **[{manga.title}]**."

        await ctx.channel.send(embed=formatter.pretty_embed(success_msg))

    @commands.command(name="unsub", usage="[Manga ID] [@Member]")
    async def unsub(self, ctx, manga_id: str, member: discord.Member = None):

        member = ctx.author if member is None else member

        guild = database.get_guild(ctx.guild.id)
        manga = database.get_manga(manga_id)

        subscription = guild.get_subscription(manga_id)

        if not subscription:
            raise EntryError("❌ **Error:** No such subscription found!")

        try:
            subscription.remove_subscriber(member.id)
        except EntryError:
            raise EntryError(f"❌ **Error:** **{member}** is not subscribed to **[{manga.title}]**.")

        success_msg = f"☑ **{member}** has successfully unsubscribed from **[{manga.title}]**."
        await ctx.channel.send(embed=formatter.pretty_embed(success_msg))

    @commands.command(name="addsub", usage="[Manga ID]")
    async def add_sub(self, ctx, manga_id: str):

        guild = database.get_guild(ctx.guild.id)
        manga = database.get_manga(manga_id)

        if not manga:
            manga = await self.fetch_manga(manga_id)
            database.insert_manga(manga)

        try:
            guild.insert_subscription(manga_id)
        except EntryError:
            raise EntryError(f"❌ **Error:** **[{manga.title}]** is already on the subscription list!")

        database.update_guild(ctx.guild.id, guild.serialize())
        success_msg = f"☑ **[{manga.title}]** has successfully been added to the subscription list!."
        await ctx.channel.send(embed=formatter.pretty_embed(success_msg))

    @commands.command(name="removesub", usage="[Manga ID]")
    async def remove_sub(self, ctx, manga_id: str):

        guild = database.get_guild(ctx.guild.id)
        manga = database.get_manga(manga_id)

        if not manga:
            manga = await self.fetch_manga(manga_id)
            database.insert_manga(manga)

        try:
            guild.remove_subscription(manga_id)
        except EntryError:
            raise EntryError(f"❌ **Error:** **[{manga.title}]** is not on the subscription list!")

        database.update_guild(ctx.guild.id, guild.serialize())
        success_msg = f"☑ **[{manga.title}]** has successfully been removed from the subscription list!."
        await ctx.channel.send(embed=formatter.pretty_embed(success_msg))

    @commands.command(name="list", usage="[Page Number]")
    async def list_manga(self, ctx, page: int = 1):

        guild = database.get_guild(ctx.guild.id)
        id_list = guild.get_subscription_ids()

        if not id_list:
            raise MangadexError(f"❌ **Error:** **[`{ctx.guild}`]** doesn't have any subscriptions!")

        length = len(id_list)
        total_page = math.ceil(len(id_list) / 9)

        if page < 0 or page > total_page:
            raise UsageError(f"❌ **Error:** **[`{page}`]** is not a valid page number! [`{total_page}`] total pages.")

        id_list = id_list[(page - 1) * 9:]
        manga_list = []

        for i, manga_id in enumerate(id_list):
            manga_list.append(database.get_manga(manga_id))
            if i == 8:
                break

        embed = discord.Embed(title=ctx.guild.name, color=0x00aaff)
        embed.add_field(name=f"**Tracking [{length}] manga.**", value=formatter.pretty_list_menu(
            (page - 1) * 9,
            manga_list,
            page,
            total_page
        ))

        await ctx.channel.send(embed=embed)

    @commands.command(name="search", usage="[Keywords]")
    async def quick_search(self, ctx, *key: str):
        if not self.is_auth:
            raise MangadexError(f"❌ **Error:** Search function is not available as agent is not authenticated.")
        regex = "%20".join(list(key))
        print(f"regex: {regex}")

        if not regex:
            raise UsageError

        results = await self.search(regex)

        if not results:
            raise IndexbotExceptions(f"No results found!")

        embed = discord.Embed(title=f"**Showing [{len(results)}] results**", color=0x00aaff)
        embed.add_field(name="**Input `1~5` to select a manga to add, `x` to cancel.**",
                        value=formatter.pretty_list_menu(0, results, 1, 1))
        prompt = await ctx.channel.send(embed=embed)
        print(prompt.id)

        def check(m):
            crr_choice = [str(i + 1) for i in range(len(results))]
            crr_choice.append("x")

            return m.author == ctx.author \
                and m.content in crr_choice \
                and m.channel == ctx.channel

        try:
            choice = await self.bot.wait_for('message', timeout=30, check=check)
        except asyncio.TimeoutError:
            raise IndexbotExceptions("❌ **Timeout!**")
        else:
            if choice.content == "x":
                await prompt.delete(delay=0.5)
                await ctx.channel.send(embed=formatter.pretty_embed("❌ Search **cancelled!**"))

            manga_id = results[int(choice.content) - 1].id

            guild = database.get_guild(ctx.guild.id)
            manga = database.get_manga(manga_id)

            if not manga:
                manga = await self.fetch_manga(manga_id)
                database.insert_manga(manga)

            try:
                guild.insert_subscription(manga_id)
            except EntryError:
                raise EntryError(f"❌ **Error:** **[{manga.title}]** is already on the subscription list!")

            database.update_guild(ctx.guild.id, guild.serialize())
            success_msg = f"☑ **[{manga.title}]** has successfully been added to the subscription list!"
            await ctx.channel.send(embed=formatter.pretty_embed(success_msg))

    @commands.command(name="here")
    async def here(self, ctx):
        guild = database.get_guild(ctx.guild.id)
        guild.set_channel(ctx.channel.id)
        database.update_guild(ctx.guild.id, guild.serialize())
        success_msg = f"☑ **[{ctx.channel}]** has been designated as the update channel!"
        await ctx.channel.send(embed=formatter.pretty_embed(success_msg))

    @tasks.loop(minutes=20)
    async def manga_update_task(self):
        # TODO: CLEAN UP
        print("Starting update loop!")
        current_time = time.time()
        manga_pool = {}
        for guild_data in database.guild_objs:
            guild = Guild.from_json(guild_data)
            if guild.channel is not None:
                channel = self.bot.get_channel(guild.channel)
                for subscription in guild.subscriptions:
                    chapter_links = []
                    try:
                        chapter_links = manga_pool[subscription.manga_id]
                    except KeyError:
                        try:
                            manga_pool[subscription.manga_id] = await self.fetch_chapters(subscription.manga_id,
                                                                                          20 * 60, current_time)
                            chapter_links = manga_pool[subscription.manga_id]
                        except Exception as err:
                            print(
                                f"Guild: [{guild.guild_id}] Manga: [{subscription.manga_id}] Error: {type(err)} {err}")

                    if chapter_links:
                        notified_members = " ".join([f"<@{subscriber}>" for subscriber in subscription.subscribers])
                        chapter_links = "\n".join([chapter.url for chapter in manga_pool[subscription.manga_id]])
                        await channel.send(notified_members + "\n" + chapter_links)

        print(manga_pool)
        print("Update loop ended!")

    @manga_update_task.before_loop
    async def bfr_update(self):
        await self.bot.wait_until_ready()

def setup(bot):
    # TODO: Add checks if the session is authenticated or not
    loop = asyncio.get_event_loop()
    session = loop.run_until_complete(Mangadex.login(USERNAME, PASSWORD))
    bot.add_cog(Mangadex(bot, session, True))
