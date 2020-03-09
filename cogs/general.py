import util
from util import _prefix_callable, get_prefix

from discord.ext import commands
import discord
from database import database

from config import FEEDBACK_CHANNEL


class General(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def format_cmds(self, cmd):
        return

    @commands.command(name="prefix",
                      usage="[Prefix]",
                      description="Changes the command prefix.",
                      help="[Prefix]\n"
                           "#Prefix to be changed to\n"
                           " \n"
                           "Example:"
                           "{prefix}prefix !\n"
                           "#Changes the prefix to `!`")
    async def change_prefix(self, ctx, prefix):
        guild = database.get_guild(ctx.guild.id)
        guild.prefix = prefix

        database.update_guild(guild)
        self.bot.command_prefix = _prefix_callable

        embed = discord.Embed(description=f"☑ **Success:** Prefix has been changed to `{prefix}`", color=0x00aaff)
        await ctx.send(embed=embed)

    @commands.command(name="help",
                      usage="[Command]",
                      description="Shows detailed help for a specified command or list out all the commands",
                      help="[Command]\n"
                           "#Command you want detailed help on, can be left blank to show all the commands\n"
                           " \n"
                           "Example:\n"
                           "{prefix}help sub\n"
                           "#Shows detailed help about the 'sub' command")
    async def help(self, ctx, cmd=None):
        prefix = get_prefix(ctx.guild.id)
        embed = discord.Embed(color=0x00aaff)
        if cmd is None:
            embed.description = f"**Haibot** is a bot that fetches manga updates from Mangadex.org on a 20 minute cycle, " \
                                f"use `{prefix}here` on a channel to get started.\n \u200b"
            cogs = self.bot.cogs
            for cog_name, cog in cogs.items():
                embed.add_field(name=cog_name.upper(),
                                value=", ".join([f"**`{cmd.name}`**" for cmd in cog.get_commands()]),
                                inline=False)
            embed.add_field(name="\u200b",
                            value=f"**Use `{prefix}help [Command]` to find out more about a command.**",
                            inline=False)
            return await ctx.send(embed=embed)

        if cmd:

            if cmd not in self.bot.all_commands:
                raise commands.UserInputError

            cmd = self.bot.all_commands[cmd]
            embed.description = f"**Usage:** `{prefix}{cmd} {cmd.usage}`\n"
            embed.add_field(name=cmd.description,
                            value=util.code_blockify(cmd.help, prefix="```py").format(prefix=prefix))
            return await ctx.send(embed=embed)

    @commands.command(name="feedback",
                      usage="[Message]",
                      description="Sends a message to the creator of this bot.",
                      help="Hint:\n"
                           "#All types of feedback even complaints are welcomed, "
                           "if you have a feature that you would like to be implemented "
                           "please don't hesitate to use this command.")
    async def feedback(self, ctx, *message):
        if len(message) <= 0:
            raise commands.UserInputError
        message = " ".join(message)
        fb_embed = discord.Embed(color=0x00aaff)
        fb_embed.set_author(name=f"Name: {ctx.author} Guild: {ctx.guild.name}")
        fb_embed.description = message
        await self.bot.get_channel(FEEDBACK_CHANNEL).send(embed=fb_embed)
        embed = discord.Embed(color=0x00aaff,
                              description=f"☑ **Success:** Your feedback has been successfully sent. Thank you!")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))
