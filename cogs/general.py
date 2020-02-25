from discord.ext import commands
from database import database
import formatter


def prefix_callable(bot, m):
    guild = database.get_guild(m.guild.id)
    return guild.prefix


def get_prefix(guild_id):
    guild = database.get_guild(guild_id)
    return guild.prefix


class General(commands.Cog, name="General"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="prefix", usage="[Prefix]", help="Change the server's prefix.")
    async def change_prefix(self, ctx, prefix):

        guild = database.get_guild(ctx.guild.id)
        guild.change_prefix(prefix)

        self.bot.command_prefix = prefix_callable

        database.update_guild(ctx.guild.id, guild.serialize())
        success_msg = f"☑ **Prefix** has been changed to `{prefix}`."
        await ctx.channel.send(embed=formatter.pretty_embed(success_msg))

    @commands.command(name="help", help="Shows help")
    async def help(self, ctx, cmd=None):
        if not cmd:
            prefix = get_prefix(ctx.guild.id)
            cogs = self.bot.cogs
            cmds = {}
            for cog_name in cogs:
                cog = cogs[cog_name]
                cog_cmds = cog.get_commands()
                cmds[cog_name] = cog_cmds
            embed = formatter.pretty_help(cmds)
            embed.add_field(name="\u200b",
                            value=f"**Use `{prefix}help <Command>` for more information about the command.**\n",
                            inline=False)
            await ctx.channel.send(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))