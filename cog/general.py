from discord.ext import commands
import discord


class General(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="prefix",
                      usage="[Prefix]",
                      description="Changes the prefix.",
                      help="[Prefix]\n"
                           "Prefix to be changed to."
                           "Example:\n"
                           "{0.prefix}prefix m!\n"
                           "#Changes the prefix to 'm!'.")
    async def _prefix_command(self, ctx, prefix):
        server = self.bot.get_server(ctx.guild.id)
        server.prefix = prefix
        self.bot.update_server(server)
        embed = discord.Embed(color=0x00aaff, description="Prefix has been changed to **`{0}`**".format(prefix))
        await ctx.send(embed=embed)

    @commands.command(name="feedback",
                      usage="[Message]",
                      description="Sends a feedback to the creator of this bot.",
                      help="All feedbacks are welcome even complaints are welcomed"
                           "if you have a feature that you would like to be implemented"
                           "please don't hesitate to use this command.")
    async def _feedback_command(self, ctx, *args):
        feedback = " ".join(args)
        embed = discord.Embed()
        embed.set_author(name="{0} : {1.name} {1.id}".format(str(ctx.author), ctx.guild))
        embed.description = feedback
        await self.bot.send_feedback(embed=embed)
        embed = discord.Embed(color=0x00aaff)
        embed.description = "Thanks for the sending in the feedback!"
        await ctx.send(embed=embed)

    @commands.command(name="help",
                      usage="[Command]",
                      description="Displays detailed help about a specific command or provides general help.",
                      help="[Command]\n"
                           "#Command you want detailed help on, can be left blank to show general help."
                           " \n"
                           "Example:\n"
                           "{0.prefix}help sub"
                           "#Shows detailed help on the command 'sub'.")
    async def _help_command(self, ctx, command_name=None):
        if command_name:
            if command_name not in self.bot.all_commands:
                raise commands.UserInputError
            command = self.bot.all_commands[command_name]
            embed = discord.Embed(description="**Usage:** `{0.prefix}{1} {1.usage}`\n".format(ctx, command),
                                  color=0x00aaff)
            embed.add_field(name=command.description,
                            value="```py\n{0}\n```".format(command.help.format(ctx)))
            return await ctx.send(embed=embed)

        embed = discord.Embed(title="Hello and thanks for using the bot!", color=0x00aaff)
        embed.add_field(name="Getting started",
                        value="Use **`{0.prefix}here`** to choose where it will post the updates.\n"
                              "Use **`{0.prefix}sub`** or **`{0.prefix}search`** to start subscribing manga.\n"
                              "Use **`{0.prefix}help [Command]`** to get detailed help on a command.\n"
                              " \n"
                              "**Below is all the commands available:**".format(ctx))
        for cog in self.bot.cogs.values():
            _commands = cog.get_commands()
            if not _commands:
                continue
            embed.add_field(name=cog.qualified_name.upper(),
                            value=", ".join(("**`{0}`**".format(command) for command in _commands)),
                            inline=False)
        embed.set_footer(text="Happy reading!")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))
