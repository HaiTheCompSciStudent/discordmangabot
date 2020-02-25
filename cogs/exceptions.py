class IndexbotExceptions(Exception):

    def __init__(self, message, *, expire_in=60):
        super().__init__(message)
        self._message = message
        self.expire_in = expire_in

    @property
    def message(self):
        return self._message


class MangadexError(IndexbotExceptions):
    """Raised when encountering error accessing Mangadex API"""
    pass


class DatabaseError(IndexbotExceptions):
    """Raised when encountering saving or updating database"""
    pass


class EntryError(IndexbotExceptions):
    """Raised when there is duplicate or no entries in a model in a database"""
    pass

class UsageError(Exception):
    """Raised when a incorrect usage of a command is called"""
    pass
