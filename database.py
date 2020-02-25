from pymongo import MongoClient
from models.discord.guild import Guild
from models.mangadex.manga import Manga

from dotenv import load_dotenv
import os

class Database:

    def __init__(self, db_path):
        self.client = MongoClient(MONGODB_URI)
        self.database = self.client["discord-bot"]
        self.guilds = self.database["guilds"]
        self.manga = self.database["manga"]

    def update_guild(self, guild_id, guild_data):
        self.guilds.find_one_and_replace({"guild_id": guild_id}, guild_data)

    def get_guild(self, guild_id):
        json_data = self.guilds.find_one({"guild_id": guild_id})
        if json_data is None:
            self.insert_guild(guild_id)
            return Guild(guild_id)
        else:
            return Guild.from_json(json_data)

    def insert_guild(self, guild_id):
        self.guilds.insert_one(Guild(guild_id).serialize())

    def remove_guild(self, guild_id):
        self.guilds.find_one_and_delete({"guild_id": guild_id})

    def get_manga(self, manga_id):
        data = self.manga.find_one({"id": manga_id})
        if not data:
            return None
        else:
            return Manga(manga_id).populate(data)

    def insert_manga(self, manga):
        self.manga.insert_one(manga.serialize())

    @property
    def guild_objs(self):
        return self.guilds.find({})

load_dotenv()

DB_PATH = os.getenv("DB_PATH")
database = Database(DB_PATH)