import discord
from discord.ext import commands
from cogs.exceptions import *
import formatter
from database import database


def prefix_callable(bot, msg):
    guild = database.get_guild(msg.guild.id)
    return guild.prefix


def get_prefix(guild_id):
    guild = database.get_guild(guild_id)
    return guild.prefix


bot = commands.Bot(command_prefix=prefix_callable)
bot.remove_command("help")

@bot.event
async def on_command_error(ctx, error):
    error = getattr(error, "original", error)
    if isinstance(error, IndexbotExceptions):
        await ctx.channel.send(embed=formatter.pretty_embed(error.message))
    if isinstance(error, (UsageError, commands.MissingRequiredArgument, commands.BadArgument)):
        usage_msg = f"**Usage:** **`{get_prefix(ctx.guild.id)}{ctx.command} {ctx.command.usage}`**"
        await ctx.channel.send(embed=formatter.pretty_embed(usage_msg))

@bot.event
async def on_ready():
    print(len(bot.guilds))
    game = discord.Game("It works now use -help")
    await bot.change_presence(status=discord.Status.idle, activity=game)

COGS = [
    'cogs.mangadex',
    'cogs.general'
]

for cog in COGS:
    bot.load_extension(cog)

bot.run('NjU1ODA0MjcyNjcxNDU3MzE2.XlOrpw.JSLNk5u6AfsH4HUaPgon3vET1N0')
