class Chapter:

    def __init__(self, id):
        self.id = id
        self.timestamp = None
        self.hash = None
        self.volume = None
        self.chapter = None
        self.title = None
        self.lang_name = None
        self.lang_code = None
        self.manga_id = None
        self.group_id = None
        self.group_id_2 = None
        self.group_id_3 = None
        self.comments = None
        self.server = None
        self.page_array = None
        self.long_strip = None

    @classmethod
    def populate(cls, data):
        chapter = cls(data["id"])
        for key, value in data.items():
            setattr(chapter, key, value)
        return chapter

    @property
    def serialized(self):
        return self.__dict__

    @property
    def url(self):
        return f"https://mangadex.org/chapter/{self.id}"

    @property
    def api_url(self):
        return f"https://mangadex.org/api/chapter/{self.id}"
