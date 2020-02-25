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

    def populate(self, data):
        for attr, value in vars(self).items():
            try:
                setattr(self, attr, data[attr])
            except KeyError:
                continue
        return self
