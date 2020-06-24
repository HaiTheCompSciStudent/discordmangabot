from discord.ext import commands, tasks
import discord

import asyncio
import inspect
import time

from index.paginator import MangaPaginator
from index.pick import Pick
from index.errors import CogError


class Core(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.refresh_libs_loops.start()
        self.update_loop.start()

    @commands.command(name="addsub",
                      usage="[Manga Reference] [Source Alias]",
                      description="Adds a manga to the subscription list.",
                      help="[Manga Reference]\n"
                           "#Reference to a specific manga, usually a ID or URL.\n"
                           " \n"
                           "[Source Alias]\n"
                           "#Alias of a source currently supported by the bot, defaulted to 'Mangadex'.\n"
                           " \n"
                           "Example:"
                           "{0.prefix}addsub https://mangadex.org/title/39/One-Piece Mangadex\n"
                           "{0.prefix}addsub 39 Mangadex\n"
                           "#Adds [One Piece] to the subscription list.\n"
                           "{0.prefix}addsub gm1 Guya\n"
                           "#Adds [Kaguya-sama: Love is War] to the subscription list.\n")
    async def _add_command(self, ctx, reference: str, lib_name="mangadex"):
        server = self.bot.get_server(ctx.guild.id)
        manga = await self.bot.get_manga(reference, lib_name)
        if manga not in server.subscriptions:
            server.subscriptions.add(manga)
        else:
            raise CogError("**[{0.title}]** is already in the subscription list.".format(manga))
        self.bot.update_server(server)
        embed = discord.Embed(description="**[{0}]** has been added to the subscriptions list!".format(manga.title))
        await ctx.send(embed=embed)

    @commands.command(name="sub",
                      usage="[Manga Reference] [@Members] [@Roles] [Source Alias]",
                      description="Subscribes multiple users and roles to a manga and pings them if there is a new chapter.",
                      help="[Manga Reference]\n"
                           "#Reference to a specific manga, usually a ID or URL.\n"
                           " \n"
                           "[@Members]\n"
                           "#Must be one or multiple mentions of members in a guild, defaulted to the user if there "
                           "is no members and no roles specified.\n"
                           " \n"
                           "[@Roles]\n"
                           "#Must be one or multiple mentions of roles in a guild.\n"
                           " \n"
                           "[Source Alias]\n"
                           "#Alias of a source currently supported by the bot, defaulted to 'Mangadex'.\n"
                           " \n"
                           "Example:"
                           "{0.prefix}sub 39 @member @role\n"
                           "#Subscribes @member and @role to [One Piece]"
                           "{0.prefix}sub 39 @member1 @member2\n"
                           "#Subscribes @member1 and @member2 to [One Piece]")
    async def _sub_command(self, ctx, reference : str,
                           members: commands.Greedy[discord.Member] = None,
                           roles: commands.Greedy[discord.Role] = None,
                           lib_name="mangadex"):
        members = members if members else [ctx.author] if (not members and not roles) else []
        roles = roles if roles else []
        server = self.bot.get_server(ctx.guild.id)
        manga = await self.bot.get_manga(reference, lib_name)
        _members = []
        _roles = []
        if manga not in server.subscriptions:
            server.subscriptions.add(manga)
        subscription = server.subscriptions.get(manga)
        for member in members:
            if member.id not in subscription.members:
                _members.append(str(member))
                subscription.members.append(member.id)
        for role in roles:
            if role.id not in subscription.roles:
                _roles.append(str(role))
                subscription.roles.append(role.id)
        self.bot.update_server(server)
        embed = discord.Embed(
            title="The following members and roles have successfully subscribed from **[{0.title}]**".format(manga),
            description="```\nMembers: {0}\nRoles: {1}\n```".format(", ".join(_members), ", ".join(_roles))
        )
        await ctx.send(embed=embed)

    @commands.command(name="removesub",
                      usage="[Manga Reference] [Source Alias]",
                      description="Removes a manga to the subscription list.",
                      help="[Manga Reference]\n"
                           "#Reference to a specific manga, usually a ID or URL.\n"
                           " \n"
                           "[Source Alias]\n"
                           "#Alias of a source currently supported by the bot, defaulted to 'Mangadex'.\n"
                           " \n"
                           "Example:"
                           "{0.prefix}removesub https://mangadex.org/title/39/One-Piece Mangadex\n"
                           "{0.prefix}removesub 39 Mangadex\n"
                           "#Removes [One Piece] to the subscription list.\n"
                           "{0.prefix}removesub gm1 Guya\n"
                           "#Removes [Kaguya-sama: Love is War] to the subscription list.\n")
    async def _remove_command(self, ctx, reference: str, lib_name="mangadex"):
        server = self.bot.get_server(ctx.guild.id)
        manga = await self.bot.get_manga(reference, lib_name)
        if manga in server.subscriptions:
            server.subscriptions.pop(manga)
        else:
            raise CogError("**[{0.title}]** is not in the subscription list.".format(manga))
        self.bot.update_server(server)
        embed = discord.Embed(description="**{0}** has been removed from the subscriptions list!".format(manga.title))
        await ctx.send(embed=embed)

    @commands.command(name="unsub",
                      usage="[Manga Reference] [@Members] [@Roles] [Source Alias]",
                      description="Unsubscribes members and roles from a manga.",
                      help="[Manga Reference]\n"
                           "#Reference to a specific manga, usually a ID or URL.\n"
                           " \n"
                           "[@Members]\n"
                           "#Must be one or multiple mentions of members in a guild, defaulted to the user if there "
                           "is no members and no roles specified.\n"
                           " \n"
                           "[@Roles]\n"
                           "#Must be one or multiple mentions of roles in a guild.\n"
                           " \n"
                           "[Source Alias]\n"
                           "#Alias of a source currently supported by the bot, defaulted to 'Mangadex'.\n"
                           " \n"
                           "Example:"
                           "{0.prefix}unsub 39 @member @role\n"
                           "#Unsubscribes @member and @role from [One Piece]"
                           "{0.prefix}unsub 39 @member1 @member2\n"
                           "#Unsubscribes @member1 and @member2 from [One Piece]")
    async def _unsub_command(self, ctx, reference: str,
                             members: commands.Greedy[discord.Member] = None,
                             roles: commands.Greedy[discord.Role] = None,
                             lib_name="mangadex"):
        members = members if members else [ctx.author]
        roles = roles if roles else []
        _members = []
        _roles = []
        server = self.bot.get_server(ctx.guild.id)
        manga = await self.bot.get_manga(reference, lib_name)
        if manga not in server.subscriptions:
            raise CogError("**[{0.title}]** is not in the subscription list.".format(manga))
        subscription = server.subscriptions.get(manga)
        for member in members:
            if member.id in subscription.members:
                _members.append(str(member))
                subscription.members.remove(member.id)
        for role in roles:
            if role.id in subscription.roles:
                _roles.append(str(role))
                subscription.roles.remove(role.id)
        self.bot.update_server(server)
        embed = discord.Embed(
            title="The following members and roles have successfully unsubscribed from **[{0.title}]**".format(manga),
            description="```\nMembers: {0}\nRoles: {1}\n```".format(", ".join(_members), ", ".join(_roles))
        )
        await ctx.send(embed=embed)

    @commands.command(name="list",
                      usage="",
                      description="List all the subscriptions in the guild.",
                      help="Use the emojis the switch pages.")
    async def _list_command(self, ctx):
        server = self.bot.get_server(ctx.guild.id)
        bot = self.bot
        lines = []

        if len(server.subscriptions) <= 0:
            raise CogError("The guild doesn't have any subscriptions.")

        async def _to_line(i, id):
            await asyncio.sleep(i * 0.2)
            manga = await bot.get_manga(id)
            lines.append("[{1}] : {0.title} {0.id}".format(manga, i + 1))

        await asyncio.gather(*[_to_line(i, subscription.id) for i, subscription in enumerate(server.subscriptions)])
        embed = discord.Embed(color=0x00aaff)
        await MangaPaginator.paginate(ctx, embed, lines, fill_empty=True)

    @commands.command(name="search",
                      usage="[Keywords] [--Source Alias]",
                      description="Search manga from keywords given and adds them should the user choose to.",
                      help="[Keywords]\n"
                           "#Keywords to be searched.\n"
                           " \n"
                           "[--Source Alias]\n"
                           "#Alias of a source currently supported by the bot, must be prefixed with '--', "
                           "if no source is specified, the bot will do a global search.\n"
                           " \n"
                           "Example:\n"
                           "{0.prefix}search One Piece --Mangadex\n"
                           "#Searches the keywords 'One Piece' on Mangadex.org."
                           " \n"
                           "Use left and right emojis to change source and number emojis to choose a manga to add.")
    async def _search_command(self, ctx, *args):
        if args[-1].startswith("--"):
            lib_name = args[-1].lstrip("--")
            args = args[:-1]
        else:
            lib_name = None
        results = await self.bot.search_manga(*args, lib_name=lib_name)
        embed = discord.Embed()
        manga = await Pick.display(ctx, embed, results)
        if not manga:
            raise CogError("Timeout!")
        server = self.bot.get_server(ctx.guild.id)
        if manga not in server.subscriptions:
            server.subscriptions.add(manga)
        self.bot.update_server(server)
        embed = discord.Embed(description="**[{0}]** has been added to the subscriptions list!".format(manga.title))
        await ctx.send(embed=embed)

    @commands.command(name="info",
                      usage="[Manga Reference]",
                      description="Displays basic information and subscribers of a manga.",
                      help="[Manga Reference]\n"
                           "#Reference to a specific manga, usually a ID or URL.\n"
                           " \n"
                           "Example:\n"
                           "{0.prefix}info 39\n"
                           "#Display basic information about [One Piece].\n"
                      )
    async def _info_command(self, ctx, reference):
        server = self.bot.get_server(ctx.guild.id)
        manga = await self.bot.get_manga(reference)
        print(manga.__dict__)
        embed = discord.Embed(title="[{0.origin}]  :  {0.title} [{0.id}]".format(manga))
        embed.set_thumbnail(url=manga.cover_url)
        embed.add_field(name="Author", value=manga.author, inline=True)
        embed.add_field(name="Artist", value=manga.artist, inline=True)
        embed.add_field(name="Description", value=manga.description, inline=False)
        subscription = server.subscriptions.get(manga)
        if subscription:
            embed.add_field(name="Subscribers",
                            value="```\nMembers: {0}\nRoles: {1}\n```"
                            .format(", ".join(str(self.bot.get_user(member)) for member in subscription.members),
                                    ", ".join(str(self.bot.get_role(ctx, role)) for role in subscription.roles)),
                            inline=False)
        embed.add_field(name="Link", value="**[Click Here]({0.page_url})**".format(manga), inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="here",
                      usage="",
                      description="Sets the channel as the update channel.",
                      help="#Make sure the bot can post in that channel, without this command being called once,"
                           "the bot is useless.")
    async def _here_command(self, ctx):
        server = self.bot.get_server(ctx.guild.id)
        server.channel_id = ctx.channel.id
        self.bot.update_server(server)
        await ctx.send("**`{0.channel}`** has been set as the update channel.\n"
                       "Updates from subscribed manga will be posted here."
                       .format(ctx))

    @commands.command(name="srcs",
                      usage="",
                      description="List all the sources currently supported by the bot.",
                      help="#More sources will be added later.")
    async def _srcs_command(self, ctx):
        embed = discord.Embed(title="Here all are the websites currently supported.",
                              description="Sources: {0}".format(
                                  ", ".join(("**[{0.name}]({0.url})**".format(lib) for lib in self.bot.libs))
                              ))
        await ctx.send(embed=embed)

    @commands.command(name="srcinfo",
                      usage="[Source Alias]",
                      description="Display basic information about a source currently supported by the bot.",
                      help="[Source Alias]\n"
                           "#Alias of a source currently supported by the bot.\n,"
                           " \n"
                           "Example:\n"
                           "{0.prefix}srcinfo Mangadex\n"
                           "#Shows basic information about Mangadex.org")
    async def _src_command(self, ctx, name_or_alias):
        lib = self.bot.get_lib(name_or_alias)
        embed = discord.Embed(color=lib.color)
        embed.set_author(name=lib.name, icon_url=lib.icon_url)
        embed.add_field(name="Aliases", value=", ".join("**`{0}`**".format(alias) for alias in lib.aliases), inline=False)
        embed.add_field(name="Description", value=lib.description, inline=False)
        embed.add_field(name="Usage", value="```py\n{0}```".format(lib.explanation.format(ctx)), inline=False)
        embed.add_field(name="Link", value="**[Click Here]({.url})**".format(lib))
        await ctx.send(embed=embed)

    @tasks.loop(minutes=20)
    async def update_loop(self):
        print("Starting Update Loop.")
        pool = {}
        timestamp = time.time()
        for server in self.bot.servers:
            channel = self.bot.get_channel(server.channel_id)
            if channel:
                for subscription in server.subscriptions:
                    try:
                        chapters = pool[subscription.id]
                    except KeyError:
                        try:
                            chapters = [chapter async for chapter in self.bot.fetch_chapters(subscription.origin, subscription.id, timestamp)]
                            if chapters:
                                print("Got chapters for manga of ID '{0.id}' from source '{0.origin}'.".format(subscription))
                            pool[subscription.id] = chapters
                        except Exception as err:
                            chapters = pool[subscription.id] = []
                            print("Error upon fetching update from a manga of id '{0}': {1}".format(subscription.id, err))
                    if chapters:
                        await channel.send("{0}\n{1}"
                                           .format(" ".join(subscription.mentions),
                                                   "\n".join((chapter.page_url for chapter in chapters))))
        print("Update loop ended")

    @update_loop.before_loop
    async def before_update_loop(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=30)
    async def refresh_libs_loops(self):
        await self.bot.reload_libs()

    @refresh_libs_loops.before_loop
    async def before_refresh_loop(self):
        # Delay cause the libs are created at startup
        await self.bot.wait_until_ready()
        await asyncio.sleep(delay=30 * 60)

def setup(bot):
    bot.add_cog(Core(bot))
