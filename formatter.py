
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


def code_blockify(title='', content='', footer=''):
    """Creates a code block through discord markdown"""
    code_block = f"```py\n" \
                 f"{title}\n" \
                 f" \n" \
                 f"{content}\n" \
                 f" \n" \
                 f"{footer}```"
    return code_block


def prettify_list(element_list):
    """Takes in a list of tuple containing (number, element_name) and formats them into '[number] : element_name"""
    pretty_list = []
    for element in element_list:
        number, element_name = element
        pretty_list.append(f" [{number}] : {element_name}")
    return "\n".join(pretty_list)


def prettify_bulk_list(element_list):
    """Takes a list of elements and formats them into '`element`, '"""
    pretty_bulk_list = []
    for element in element_list:
        pretty_bulk_list.append(f"`{element}`")
    return ", ".join(pretty_bulk_list)



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
