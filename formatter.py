
from discord.embeds import Embed
from cogs.general import get_prefix


def pretty_manga_str(start_pos, manga_list):
    fmt_manga_list = []
    for i, manga in enumerate(manga_list):
        i = start_pos + i + 1
        fmt_manga_list.append(f" [{i}] : {manga.title} {manga.id}\n")
    return "".join(fmt_manga_list)


def pretty_list_menu(start_pos, manga_list, page=1, total_page=1):
    """TODO: make it more general"""
    fmt_manga_list = pretty_manga_str(start_pos, manga_list)
    content = "```py\n" \
              " \n" \
              f"{fmt_manga_list}" \
              " \n" \
              f"Page {page} of {total_page}```"
    return content


def pretty_embed(content):
    """pretty useless imo"""
    embed = Embed(description=content, color=0x00aaff)
    return embed


def pretty_help(cog_list):
    embed = Embed(description="For further help please contact: <@250997040169877504>\n", color=0x00aaff)
    embed.set_author(name="Here are all the commands!")
    for cog_name in cog_list:
        cog_cmds = cog_list[cog_name]
        cog_cmds = [f"**`{cmd.name}`**" for cmd in cog_cmds]
        cog_cmds = ", ".join(cog_cmds)
        embed.add_field(name=f"{cog_name.upper()}", value=cog_cmds, inline=False)
    return embed
