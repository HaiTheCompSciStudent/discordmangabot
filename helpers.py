import discord

LIGHT_BLUE = 0x03A9F4


def success_message(message):
    return discord.Embed(description=message, color=LIGHT_BLUE)


def update_message(record, chapters):
    message = """New chapter{s} for [{title}] is out!\n{chapters}\n{mentions}"""
    return message.format(s='s' if len(chapters) > 1 else '',
                          chapters="\n".join([chapter.url for chapter in chapters]),
                          mentions=" ".join(["<@%s>" % id for id in record.members]))
