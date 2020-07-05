class HashableIterator:

    def __init__(self, iterator):
        self.map = dict(((item.id, item) for item in iterator))

    def __iter__(self):
        self._iterator = iter(self.map.values())
        return self

    def __len__(self):
        return len(self.map)

    def __next__(self):
        return next(self._iterator)

    def __setitem__(self, id, item):
        self.map[id] = item

    def __getitem__(self, id):
        return self.map[id]

    def __delitem__(self, id):
        del self.map[id]

    def __contains__(self, item):
        return item.id in list(self.map.keys())