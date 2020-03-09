class BotException(Exception):
    """Base class for all bot exceptions"""
    def __init__(self, message, timeout=None):
        super().__init__(message)
        self._message = message
        self.timeout = timeout

    @property
    def message(self):
        return f"❌ **Error:** {self._message}"


class MangadexError(BotException):
    """Raised when there is error accessing Mangadex API"""
    pass


class EntryError(BotException):
    """Raised when there is duplicate entries or no entries in the database"""
    pass


class EmptyError(BotException):
    """Raised when there if something is empty found"""
    pass


class SilentError(Exception):
    """Base class for all errors that fall silently"""


class NoChoiceError(SilentError):
    """Raised when there is no choice selected"""
    pass
