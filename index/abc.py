class Hashable:

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id


class IndexedDict:

    def __init__(self, data):
        self.data = data
        self.index_key_map = dict((i, key) for i, key in enumerate(data.keys()))

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.data[self.index_key_map[item]]
        elif isinstance(item, str):
            return self.data[item]
