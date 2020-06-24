import json
from index.bot import Index
from index.server import Server
from index import errors
import discord
from discord.ext import commands

with open("config.json", "r") as f:
    config = json.load(f)

bot = Index(command_prefix="!", config=config)
bot.remove_command("help")


@bot.event
async def on_ready():
    print("I am ready")
    game = discord.Game("-help")
    await bot.change_presence(activity=game)


@bot.event
async def on_guild_join(guild):
    bot.dataio.insert("test_guilds", Server(data={"id": guild.id}))


@bot.event
async def on_guild_remove(guild):
    bot.dataio.remove("test_guilds", guild.id)


@bot.event
async def on_command_error(ctx, error):
    error = getattr(error, "original", error)
    if isinstance(error, errors.EmbedError):
        await ctx.send(embed=error.embed)
    elif isinstance(error, commands.UserInputError):
        embed = discord.Embed(color=0x00aaff,
                              description="**Usage:** `{0.prefix}{0.command} {0.command.usage}`".format(ctx))
        await ctx.send(embed=embed)
    else:
        print(error)


bot.load_extension("cog.core")
bot.load_extension("cog.general")

bot.run(bot.config.get("BOT_TOKEN"))

