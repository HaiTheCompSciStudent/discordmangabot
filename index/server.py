from .iterator import HashableIterator


class Subscription:

    def __init__(self, id, origin, members=None, roles=None):
        self.id = id
        self.origin = origin
        self.members = members if members else []
        self.roles = roles if members else []

    def __repr__(self):
        return "{0}".format(self.id)

    @property
    def mentions(self):
        return [*["<@{0}>".format(member) for member in self.members], *["<@{0}>".format(role) for role in self.roles]]

    @property
    def serialized(self):
        return dict(
            id=self.id,
            origin=self.origin,
            members=self.members,
            roles=self.roles
        )


class Server:

    def __init__(self, *, data):
        self.id = data.get("id")
        self.prefix = data.get("prefix", "-")
        self.channel_id = data.get("channel_id", None)
        self.subscriptions = SubscriptionIterator(data.get("subscriptions", []))

    @property
    def serialized(self):
        return dict(
            id=self.id,
            prefix=self.prefix,
            channel_id=self.channel_id,
            subscriptions=self.subscriptions.serialized
        )


class SubscriptionIterator(HashableIterator):

    def __init__(self, data):
        subscriptions = [Subscription(_data["id"], _data["origin"], _data["members"], _data["roles"]) for _data in data]
        super().__init__(subscriptions)

    def add(self, manga):
        self.map[manga.id] = Subscription(manga.id, manga.origin)

    def get(self, manga, default=None):
        return self.map.get(manga.id, default)

    def pop(self, manga):
        self.map.pop(manga.id)

    @property
    def serialized(self):
        return [subscription.serialized for subscription in self]
