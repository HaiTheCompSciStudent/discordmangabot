import discord
from discord.ext import commands
from config import TOKEN
from exceptions import *
from util import _prefix_callable, get_prefix

bot = commands.Bot(command_prefix=_prefix_callable)
bot.remove_command("help")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"Serving {len(bot.guilds)} guilds!")
    print(f"-------------------------")


@bot.event
async def on_command_error(ctx, error):
    error = getattr(error, "original", error)
    if isinstance(error, BotException):
        embed = discord.Embed(color=0x00aaff, description=error.message)
        await ctx.send(embed=embed)
    if isinstance(error, commands.UserInputError):
        embed = discord.Embed(color=0x00aaff,
                              description=f"**Usage:** **`{get_prefix(ctx.guild.id)}{ctx.command} {ctx.command.usage}`**")
        await ctx.send(embed=embed)

cogs = [
    "cogs.mangadex",
    "cogs.general"
]

for cog in cogs:
    bot.load_extension(cog)

bot.run(TOKEN)
