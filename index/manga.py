from index.abc import Hashable


class MangaMeta(type):

    def __new__(cls, *args, **kwargs):
        name, bases, attrs = args
        settings = kwargs.pop("settings", {})
        for attr_name, value in settings.items():
            attrs[attr_name] = value
        new_cls = super().__new__(cls, name, bases, attrs)
        return new_cls


class Manga(Hashable, metaclass=MangaMeta):
    ORIGIN = "None"
    PAGE_BASE = "{0}"
    COVER_BASE = "{0}"
    GENRE_ENUM = {}

    def __init__(self, id, *, data):
        self.id = id
        self.origin = self.ORIGIN
        self._cover_url = data.get("cover_url", None)
        self.title = data.get("title", None)
        self.description = data.get("description", None)
        self.author = data.get("author", None)
        self.artist = data.get("artist", None)
        self._genres = data.get("genres", [])

    def __repr__(self):
        attrs = ("origin", "id", "title")
        return "<" + ", ".join(["%s=%s" % (attr, getattr(self, attr)) for attr in attrs]) + ">"

    @property
    def page_url(self):
        return self.PAGE_BASE.format(self.id)

    @property
    def cover_url(self):
        return self.COVER_BASE.format(self._cover_url)

    @property
    def genres(self):
        return (self.GENRE_ENUM[genre] if self.GENRE_ENUM else genre for genre in self._genres)

    @property
    def serialized(self):
        data = {}
        for attr_name, value in vars(self).items():
            data[attr_name.lstrip("_")] = value
        return data

    @property
    def dataform(self):
        data = {}
        for attr in ("id", "origin", "cover_url", "title", "description", "author", "artist", "page_url", "genres"):
            data[attr] = getattr(self, attr)
        return data



def factory(settings):
    class Factory(Manga, settings=settings):
        pass

    return Factory
