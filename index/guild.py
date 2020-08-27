import discord

from . import model



class Guild(model.Model):
    id: str
    prefix: str = model.field(default="m!")
    subscription: str = model.field(default=[])
    notification_channel: discord.TextChannel = model.field(name="channel_id", default=None)
