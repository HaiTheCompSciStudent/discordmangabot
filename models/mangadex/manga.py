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

    def populate(self, data):
        for attr, value in vars(self).items():
            try:
                setattr(self, attr, data[attr])
            except KeyError:
                continue
        return self

    def serialize(self):
        return self.__dict__

    @classmethod
    def from_json(cls, data):
        return cls(data["id"]).populate(data)
