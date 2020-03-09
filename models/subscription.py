

class Subscription:

    def __init__(self, manga_id, subscribers=None):
        self.manga_id = manga_id
        self.subscribers = [] if subscribers is None else subscribers

    @classmethod
    def deserialize(cls, data):
        manga_id = data["manga_id"]
        subscribers = data["subscribers"]
        return cls(manga_id, subscribers)

    @property
    def serialized(self):
        return self.__dict__
