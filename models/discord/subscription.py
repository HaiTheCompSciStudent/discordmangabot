from cogs.exceptions import *

class Subscription:

    def __init__(self, manga_id, subscribers=None):
        if subscribers is None:
            subscribers = []
        self.manga_id = manga_id
        self.subscribers = subscribers

    def insert_subscriber(self, subscriber_id):
        if subscriber_id not in self.subscribers:
            self.subscribers.append(subscriber_id)
        else:
            raise EntryError("Member is already subscribed!")

    def remove_subscriber(self, subscriber_id):
        if subscriber_id in self.subscribers:
            self.subscribers.remove(subscriber_id)
        else:
            raise EntryError("Member is not subscribed!")

    def serialize(self):
        return self.__dict__

    @classmethod
    def from_json(cls, data):
        manga_id = data["manga_id"]
        subscribers = data["subscribers"]
        return cls(manga_id, subscribers)
