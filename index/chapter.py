from .factory import Factory

class Chapter(Factory):

    def __init__(self, *, data):
        self.id = data.pop("id", None)
        self.chapter = data.get("chapter", None)
        self.title = data.get("title", None)
        self.timestamp = data.get("timestamp", None)
        self.lang_code = data.get("lang_code", None)

    @property
    def page_url(self):
        return self.page.format(self)