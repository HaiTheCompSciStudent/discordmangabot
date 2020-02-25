from models.discord.subscription import Subscription
from cogs.exceptions import *

class Guild:

    def __init__(self, guild_id, prefix="-", channel=None, subscriptions=None):
        if subscriptions is None:
            subscriptions = []
        self.guild_id = guild_id
        self.prefix = prefix
        self.channel = channel
        self.subscriptions = subscriptions

    def change_prefix(self, prefix):
        self.prefix = prefix

    def set_channel(self, channel_id):
        self.channel = channel_id

    def check_subscription(self, manga_id):
        id_list = [sub.manga_id for sub in self.subscriptions]
        return manga_id in id_list

    def get_subscription_index(self, manga_id):
        id_list = [sub.manga_id for sub in self.subscriptions]
        if manga_id:
            return id_list.index(manga_id)
        else:
            raise EntryError("No such subscription in list!")

    def get_subscription(self, manga_id):
        try:
            return self.subscriptions[self.get_subscription_index(manga_id)]
        except ValueError:
            raise EntryError("No such subscription in list!")

    def insert_subscription(self, manga_id):
        if self.check_subscription(manga_id):
            raise EntryError("There is already such subscription!")
        else:
            self.subscriptions.append(Subscription(manga_id))

    def remove_subscription(self, manga_id):
        if self.check_subscription(manga_id):
            self.subscriptions.remove(self.get_subscription(manga_id))
        else:
            raise EntryError("There is no such subscription!")

    def get_subscription_ids(self):
        id_list = [sub.manga_id for sub in self.subscriptions]
        return id_list

    def serialize(self):
        return {
            "guild_id": self.guild_id,
            "prefix": self.prefix,
            "channel": self.channel,
            "subscriptions": list(map(lambda x: x.__dict__, self.subscriptions))
        }

    @classmethod
    def from_json(cls, data):
        id = data["guild_id"]
        prefix = data["prefix"]
        channel = data["channel"]
        subscriptions = list(map(Subscription.from_json, data["subscriptions"]))
        return cls(id, prefix, channel, subscriptions)