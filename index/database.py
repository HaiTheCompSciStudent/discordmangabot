from redis.client import Redis

import json
import os


class DatabaseMeta(type):
    # Singleton instance
    __instance__ = None

    def __call__(cls, *args, **kwargs):
        if cls.__instance__ is None:
            cls.__instance__ = super().__call__(*args, **kwargs)
        return cls.__instance__


class Database(metaclass=DatabaseMeta):

    def __init__(self):
        host, port, password = " : : ".split(":")
        self.redis = Redis(host=host, port=port, password=password)
        self._models = {}

    def add_model(self, cls):
        self._models[cls.__hash_name__] = cls

    def get(self, prefix, id):
        model = self._models[prefix]
        text = self.redis.get(prefix + ':' + id).decode('utf8')
        data = json.loads(text)
        return model(data)

    def set(self, model):
        data = model.to_data()
        text = json.dumps(data)
        hash = "{0.__hash_prefix__}:{0.id}".format(model)
        self.redis.hset(hash, text)

    def delete(self, prefix, id):
        self.redis.delete(prefix + ":" + id)

    def get_all(self, prefix):
        for h in self.redis.scan_iter(prefix + ":*"):
            prefix, id = h.split(":")
            yield self.get(prefix, id)
