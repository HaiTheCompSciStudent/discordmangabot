from .manga import factory as manga_factory
from .chapter import factory as chapter_factory


class Library:
    color = 0x000000

    def __init__(self, bot, **kwargs):
        self.bot = bot
        self.name = kwargs.pop("name")
        self.aliases = kwargs.pop("aliases", [])
        self.description = kwargs.pop("description")
        self.url = kwargs.pop("url")
        self.icon_url = kwargs.pop("icon_url")
        self.explanation = kwargs.pop("explanation")
        self.manga_factory = manga_factory(kwargs.pop("manga"))
        self.chapter_factory = chapter_factory(kwargs.pop("chapter"))

    @property
    def name_or_aliases(self):
        return (self.name.lower(), *(alias.lower() for alias in self.aliases))
