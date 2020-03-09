class Manga:

    def __init__(self, id):
        self.id = id
        self.cover_url = None
        self.descriptions = None
        self.title = None
        self.artist = None
        self.author = None
        self.status = None
        self.genres = None
        self.last_chapter = None
        self.lang_name = None
        self.lang_flag = None
        self.hentai = None
        self.links = None

    @classmethod
    def populate(cls, data):
        manga = cls(data["id"])
        for key, value in data.items():
            setattr(manga, key, value)
        return manga

    @property
    def serialized(self):
        return self.__dict__

    @property
    def url(self):
        return f"https://mangadex.org/title/{self.id}"

    @property
    def api_url(self):
        return f"https://mangadex.org/api/manga/{self.id}"
