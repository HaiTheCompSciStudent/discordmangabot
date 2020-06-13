from config import DEFAULT_PREFIX
from models.subscription import Subscription


class Guild:

    def __init__(self, id_, prefix=DEFAULT_PREFIX, channel=None, subscriptions=None):
        self.id = id_
        self.prefix = prefix
        self.channel = channel
        self.subscriptions = [] if subscriptions is None else subscriptions

    @property
    def id_list(self):
        """Returns the manga IDs of every subscription"""
        return [subscription.manga_id for subscription in self.subscriptions]

    def get_subscription(self, manga_id):
        return self.subscriptions[self.id_list.index(manga_id)]

    @classmethod
    def deserialize(cls, data):
        print(data)
        id_ = data["guild_id"]
        prefix = data["prefix"]
        channel = data["channel"]
        subscriptions = list(map(Subscription.deserialize, data["subscriptions"]))
        return cls(id_, prefix, channel, subscriptions)

    @property
    def serialized(self):
        return {
            "guild_id": self.id,
            "prefix": self.prefix,
            "channel": self.channel,
            "subscriptions": list(map(lambda s: s.serialized, self.subscriptions)),
        }
