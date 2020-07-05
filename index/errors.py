import discord


class IndexError(Exception):
    """Base class for all Index related errors"""
    pass


class EmbedError(IndexError):
    """Base class for all errors that need to be displayed using embeds"""
    COLOR = 0x00aaff

    def __init__(self, message):
        super().__init__(message)
        self._message = message

    @property
    def embed(self):
        return discord.Embed(color=self.COLOR, description="**Error:** {0}".format(self._message))


class CogError(EmbedError):
    """Base class for all cog related errors"""
    pass


class LibraryError(EmbedError):
    """Base class for all Library related errors"""
    pass
