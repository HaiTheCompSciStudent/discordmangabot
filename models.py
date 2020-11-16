

class Manga:
    PATH = ""

    def __init__(self, *, data):
        self.id = data.get('id', None)
        self.title = data.get('title', None)
        self.description = data.get('description', None)
        self.artist = data.get('artist', None)
        self.author = data.get('author', None)

    @property
    def url(self):
        return self.BASE + self.PATH.format(self=self)


class Chapter:
    PATH = ""

    def __init__(self, *, data):
        self.id = data.get('id', None)
        self.chapter = data.get('chapter', None)
        self.title = data.get('title', None)
        self.timestamp = data.get('timestamp', None)


    @property
    def url(self):
        return self.BASE + self.PATH.format(self=self)
