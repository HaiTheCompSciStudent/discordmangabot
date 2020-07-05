import asyncio
import discord
from index.errors import CogError
from contextlib import suppress

LEFT_EMOJI = "\u23EE"  # [:track_previous:]
ONE_EMOJI = "1\ufe0f\u20e3"
TWO_EMOJI = "2\ufe0f\u20e3"
THREE_EMOJI = "3\ufe0f\u20e3"
FOUR_EMOJI = "4\ufe0f\u20e3"
FIVE_EMOJI = "5\ufe0f\u20e3"
RIGHT_EMOJI = "\u23ED"  # [:track_next:]
DELETE_EMOJI = "\u274C"  # [:x:]
PICK_EMOJIS = (LEFT_EMOJI, ONE_EMOJI, TWO_EMOJI, THREE_EMOJI, FOUR_EMOJI, FIVE_EMOJI, RIGHT_EMOJI, DELETE_EMOJI)


class Pick:

    def __init__(self, prefix, suffix, width=60, fill_empty=True):
        self.fill_empty = fill_empty
        self.prefix = prefix
        self.suffix = suffix
        self.width = width
        self._manga = {}
        self._current_page = []
        self._pages = {}

    def add_manga(self, manga):
        if manga.origin in self._manga:
            self._manga[manga.origin].append(manga)
        else:
            self._manga[manga.origin] = [manga]

    def _format_manga(self, index, manga):
        _format_str = "[{0}] : {1.title} {1.id}".format(index, manga)
        if len(_format_str) <= self.width:
            return _format_str
        else:
            short_title = manga.title[:-(len(_format_str) - self.width + 3)] + "..."
            return "[{0}] : {1} {2.id}".format(index, short_title, manga)

    def _populate_pages(self):
        for origin, manga in self._manga.items():
            self._current_page.append(self.prefix)
            for i, m in enumerate(manga):
                self._current_page.append(self._format_manga(i + 1, m))
            self._current_page.append(self.suffix)
            self._pages[origin] = "\n".join(self._current_page)
            self._current_page = []

    @property
    def manga(self):
        return list(m for manga_list in self._manga.values() for m in manga_list)

    @property
    def key_enum(self):
        return dict((i, origin) for i, origin in enumerate(self._manga.keys()))

    @property
    def pages(self):
        return list(self._pages.values())

    @classmethod
    async def display(cls, ctx, embed, manga, timeout=1239, fill_empty=True):
        picker = cls("```", "```")

        for _manga in manga:
            picker.add_manga(_manga)
        picker._populate_pages()
        current_page = 0

        def event_check(reaction_, user_):
            return all((reaction_.message.id == message.id,
                        str(reaction_.emoji) in PICK_EMOJIS,
                        user_.id != ctx.bot.user.id))

        embed.title = "Showing results from {0}:".format(picker.key_enum.get(current_page))
        embed.description = picker.pages[current_page]
        embed.set_footer(text="Page {0} of {1}".format(current_page + 1, len(picker.pages)))

        message = await ctx.send(embed=embed)

        for emoji in PICK_EMOJIS:
            await message.add_reaction(emoji)

        while True:
            try:
                reaction, user = await ctx.bot.wait_for("reaction_add", timeout=timeout, check=event_check)
            except asyncio.TimeoutError:
                await message.delete()
                raise CogError("Timeout!")

            await message.remove_reaction(reaction.emoji, user)

            if str(reaction.emoji) == DELETE_EMOJI:
                return await message.delete()

            if str(reaction.emoji) == LEFT_EMOJI:
                if current_page == 0:
                    continue

                current_page -= 1

                embed.title = "Showing results from {0}:".format(picker.key_enum.get(current_page))
                embed.description = picker.pages[current_page]
                embed.set_footer(text=f"Page {current_page + 1} of {len(picker.pages)}")

                await message.edit(embed=embed)
                continue

            if str(reaction.emoji) == RIGHT_EMOJI:
                if current_page == len(picker.pages) - 1:
                    continue

                current_page += 1

                embed.title = "Showing results from {0}:".format(picker.key_enum.get(current_page))
                embed.description = picker.pages[current_page]
                embed.set_footer(text=f"Page {current_page + 1} of {len(picker.pages)}")

                await message.edit(embed=embed)
                continue

            index = int(str(reaction.emoji)[0]) - 1  # '[N]\ufe0f\u20e3'

            if index >= len(picker._manga.get((picker.key_enum[current_page]))):
                continue
            #   Finds the absolute index of a choice by doing the following:
            #   Sum up all the lengths of the list of every key in the manga dictionary
            #   that is before the current page
            #   using the key_enum to find what key is
            #   before the current page

            abs_index = sum(len(picker._manga.get(picker.key_enum[i])) for i in range(current_page)) + index

            try:
                return picker.manga[abs_index]
            except IndexError:
                continue
