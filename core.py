from discord.ext import commands, tasks
import time

from helpers import success_message, update_message
from menu import Menu


class Core(commands.Cog):
    TIME_BETWEEN_LOOP = 30

    def __init__(self, bot):
        self.bot = bot
        self._internal_loop.start()

    @commands.command(name='add')
    async def add_command(self, ctx, id):
        manga = await self.bot.get_manga(id)
        async with self.bot.database.fetch_records(ctx.guild.id) as records:
            records.add(manga)
        embed = success_message("[{title}] has been added.".format(title=manga.title))
        await ctx.send(embed=embed)

    @commands.command(name='rm')
    async def rm_command(self, ctx, id):
        manga = await self.bot.get_manga(id)
        async with self.bot.database.fetch_records(ctx.guild.id) as records:
            records.remove(manga)
        embed = success_message("[{title}] has been removed.".format(title=manga.title))
        await ctx.send(embed=embed)

    @commands.command(name='search')
    async def search_command(self, ctx, *keywords):
        pass

    @commands.command(name='list')
    async def list_command(self, ctx, page=1):
        records = await self.bot.database.fetch_records(ctx.guild.id)
        menu = Menu(records)
        await menu.start()

    @tasks.loop(minutes=TIME_BETWEEN_LOOP)
    async def _internal_loop(self):

        t = time.time()
        updated = dict()

        def check(data):
            return all((data['timestamp'] - t <= self.TIME_BETWEEN_LOOP,
                        data['lang_code'] == 'gb',
                        data['timestamp'] <= t))

        for record in self.bot.database:
            chapters = []
            try:
                chapters = updated[record.code]
            except KeyError:
                try:
                    chapters = updated[record.code] = await self.bot.get_chapters(record.code, check=check)
                except Exception as e:
                    print(e.args)
                    pass
            finally:
                if chapters:
                    guild = await self.bot.database.fetch('guild', record.id)
                    channel = self.bot.get_channel(guild.channel)
                    message = update_message(record, chapters)
                    await channel.send(message)
