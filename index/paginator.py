import discord
import asyncio

from contextlib import suppress





FIRST_EMOJI = "\u23EE"  # [:track_previous:]
LEFT_EMOJI = "\u25C0"  # [:arrow_backward:]
RIGHT_EMOJI = "\u25B6"  # [:arrow_forward:]
LAST_EMOJI = "\u23ED"  # [:track_next:]
DELETE_EMOJI = "\u274C"  # [:x:]
PAGINATION_EMOJI = [FIRST_EMOJI, LEFT_EMOJI, RIGHT_EMOJI, LAST_EMOJI, DELETE_EMOJI]


class Paginator:

    def __init__(self, prefix="```", suffix="```", max_lines=10, width=55, fill_empty=False):
        self.prefix = prefix
        self.suffix = suffix
        self.max_lines = max_lines
        self.width = width
        self.fill_empty = fill_empty
        self._linecount = 0
        self._current_page = [] if self.prefix is None else [self.prefix]
        self._pages = []

    def add_line(self, line):
        if self._linecount >= self.max_lines:
            self.close_page()
        self._current_page.append(line)
        self._linecount += 1

    def close_page(self):
        if self.suffix is not None:
            self._current_page.append(self.suffix)
        self._pages.append("\n".join(self._current_page))
        self._linecount = 0
        if self.prefix is not None:
            self._current_page = [self.prefix]
        else:
            self._current_page = []

    def _shorten_line(self, line):
        if len(line) > self.width:
            print(self.width)
            return line[:(self.width - 3)] + "..."
        return line

    @property
    def pages(self):
        if len(self._current_page) > (0 if self.prefix is None else 1):
            if self.fill_empty:
                for _ in range(self.max_lines - self._linecount):
                    self._current_page.append(" ")
            self.close_page()
        return self._pages

    @classmethod
    async def paginate(cls,
                       ctx,
                       embed,
                       lines,
                       prefix="```",
                       suffix="```",
                       max_lines=10,
                       width=55,
                       fill_empty=True,
                       timeout=90):

        def event_check(reaction_, user_):
            return all((reaction_.message.id == message.id,
                        str(reaction_.emoji) in PAGINATION_EMOJI,
                        user_.id != ctx.bot.user.id))

        paginator = cls(prefix, suffix, max_lines, width, fill_empty)

        for line in lines:
            paginator.add_line(paginator._shorten_line(line))

        current_page = 0
        embed.description = paginator.pages[current_page]
        embed.set_footer(text=f"Page {current_page + 1} of {len(paginator.pages)}")

        if len(paginator.pages) <= 1:
            await ctx.send(embed=embed)
        else:
            message = await ctx.send(embed=embed)

            for emoji in PAGINATION_EMOJI:
                await message.add_reaction(emoji)

            while True:
                try:
                    reaction, user = await ctx.bot.wait_for("reaction_add", timeout=timeout, check=event_check)
                except asyncio.TimeoutError:
                    break

                await message.remove_reaction(reaction.emoji, user)

                if str(reaction.emoji) == FIRST_EMOJI:
                    if current_page == 0:
                        continue

                    current_page = 0

                    embed.description = paginator.pages[current_page]
                    embed.set_footer(text=f"Page {current_page + 1} of {len(paginator.pages)}")

                    await message.edit(embed=embed)

                if str(reaction.emoji) == LEFT_EMOJI:
                    if current_page == 0:
                        continue

                    current_page -= 1

                    embed.description = paginator.pages[current_page]
                    embed.set_footer(text=f"Page {current_page + 1} of {len(paginator.pages)}")

                    await message.edit(embed=embed)

                if str(reaction.emoji) == RIGHT_EMOJI:
                    if current_page == len(paginator.pages) - 1:
                        continue

                    current_page += 1

                    embed.description = paginator.pages[current_page]
                    embed.set_footer(text=f"Page {current_page + 1} of {len(paginator.pages)}")

                    await message.edit(embed=embed)

                if str(reaction.emoji) == LAST_EMOJI:
                    if current_page == len(paginator.pages) - 1:
                        continue

                    current_page = len(paginator.pages) - 1

                    embed.description = paginator.pages[current_page]
                    embed.set_footer(text=f"Page {current_page + 1} of {len(paginator.pages)}")

                    await message.edit(embed=embed)

                if str(reaction.emoji) == DELETE_EMOJI:
                    return await message.delete()

            with suppress(discord.NotFound):
                await message.clear_reactions()


class MangaPaginator(Paginator):

    def _shorten_line(self, line):
        """
        Shorten only the title part of a line to fit within :attr: width
        Eg: [1] : Kaguya-sama wa Kokurasetai: Tensai-tachi no Renai Zunousen 17274
        ->  [1] : Kaguya-sama wa Kokurasetai: Tensai-ta... 17274
        """
        order, _, *title, id_ = line.split(" ")
        if len(" ".join(title)) >= self.width - (len(order) + len(id_) + 4):  # four spaces in-between
            print(title)
            return " ".join([order, _, " ".join(title)[:(self.width - (len(order) + len(id_) + 7))] + "...", id_])
            # probably the shittiest code i ever written
        return line


ONE_EMOJI = "1\ufe0f\u20e3"
TWO_EMOJI = "2\ufe0f\u20e3"
THREE_EMOJI = "3\ufe0f\u20e3"
FOUR_EMOJI = "4\ufe0f\u20e3"
FIVE_EMOJI = "5\ufe0f\u20e3"

CHOICE_EMOJI = [ONE_EMOJI, TWO_EMOJI, THREE_EMOJI, FOUR_EMOJI, FIVE_EMOJI, DELETE_EMOJI]


class ChoiceMenu(MangaPaginator):

    def __init__(self, prefix="```", suffix="```", max_lines=10, width=55, fill_empty=False):
        super().__init__(prefix, suffix, max_lines, width, fill_empty)
        self._choice = []

    @property
    def _choice_emoji(self):
        choice_emoji_ = []
        for i, emoji in enumerate(CHOICE_EMOJI):
            if i >= len(self._choice):
                break
            choice_emoji_.append(emoji)
        choice_emoji_.append(DELETE_EMOJI)
        return choice_emoji_

    @classmethod
    async def prompt(cls,
                     ctx,
                     embed,
                     choices,
                     prefix="```",
                     suffix="```",
                     max_lines=5,
                     width=55,
                     fill_empty=True,
                     timeout=90):

        def event_check(reaction_, user_):
            return all((reaction_.message.id == message.id,
                        str(reaction_.emoji) in menu._choice_emoji,
                        user_.id != ctx.bot.user.id))

        menu = cls(prefix, suffix, max_lines, width, fill_empty)

        for choice, line in choices:
            menu.add_line(menu._shorten_line(line))
            menu._choice.append(choice)

        embed.description = menu.pages[0]

        message = await ctx.send(embed=embed)

        for emoji in menu._choice_emoji:
            await message.add_reaction(emoji)

        try:
            reaction, user = await ctx.bot.wait_for("reaction_add", timeout=timeout, check=event_check)
        except asyncio.TimeoutError:
            await message.delete()
            return None

        await message.remove_reaction(reaction.emoji, user)

        if str(reaction.emoji) == DELETE_EMOJI:
            await message.delete()
            return None
        else:
            choice = menu._choice[int(str(reaction.emoji)[0]) - 1]
            await message.delete()
            return choice