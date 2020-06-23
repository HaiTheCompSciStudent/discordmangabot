from discord.ext import commands
import dbl


class TopGG(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._token = bot.config["DBL_TOKEN"]
        self._client = dbl.DBLClient(self.bot, self._token, autopost=True)

    async def on_guild_post(self):
        print(f"{self.bot} guild count updated")

def setup(bot):
    bot.add_cog(TopGG(bot))