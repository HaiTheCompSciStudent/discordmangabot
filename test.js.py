import aiohttp
import asyncio
from cogs.exceptions import *
from models.mangadex.chapter import Chapter
import time
import requests

resp = requests.get("https://mangadex.org/api/manga/39")
print(resp.text)