import time


class ChapterMeta(type):

    def __new__(cls, *args, **kwargs):
        name, bases, attrs = args
        settings = kwargs.pop("settings", {})
        for key, value in settings.items():
            attrs[key] = value

        new_cls = super().__new__(cls, name, bases, attrs)
        return new_cls


class Chapter(metaclass=ChapterMeta):
    ORIGIN = "None"
    PAGE_BASE = "{0}"

    def __init__(self, id, *, data=None):
        self.id = id
        self.origin = self.ORIGIN
        self.chapter = data.get("chapter", None)
        self.title = data.get("title", None)
        self.timestamp = data.get("description", None)
        self.lang_code = data.get("lang_code", None)

    @property
    def page_url(self):
        return self.PAGE_BASE.format(self.id)

    @property
    def time_since_released(self):
        return time.time() - self.timestamp


def factory(settings):
    class Factory(Chapter, settings=settings):
        pass

    return Factory
