from .factory import Factory

class Manga(Factory):

    def __init__(self, *, data):
        self.id = data.pop("id", None)
        self.title = data.get("title", None)
        self.description = data.get("description", None)
        self.author = data.get("author", None)
        self.artist = data.get("artist", None)

    @property
    def page_url(self):
        return self.page.format(self)

    @property
    def cover_url(self):
        return self.cover.format(self)
