from pymongo import MongoClient
from config import MONGO_URI

from models.guild import Guild
from models.manga import Manga


class Database:
    """Represents a database storing guild and manga information using MongoDB."""

    def __init__(self):
        self._client = MongoClient(MONGO_URI)
        self._database = self._client["discord-bot"]
        self._guilds = self._database["guilds"]
        self._manga = self._database["manga"]

    @property
    def guilds(self):
        return list(map(Guild.deserialize, self._guilds.find({})))

    def update_guild(self, guild):
        self._guilds.find_one_and_replace({"guild_id": guild.id}, guild.serialized)

    def add_guild(self, guild_id):
        self._guilds.insert(Guild(guild_id).serialized)

    def remove_guild(self, guild_id):
        self._guilds.find_one_and_delete({"guild_id": guild_id})

    def get_guild(self, guild_id):
        guild_data = self._guilds.find_one({"guild_id": guild_id})
        if not guild_data:
            self.add_guild(guild_id)
        return Guild.deserialize(self._guilds.find_one({"guild_id": guild_id}))

    def add_manga(self, manga):
        self._manga.insert_one(manga.serialized)

    def get_manga(self, manga_id):
        manga_data = self._manga.find_one({"id": manga_id})
        return None if manga_data is None else Manga.populate(manga_data)


database = Database()
