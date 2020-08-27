from redis.client import Redis
from .database import Database
import json
import os


def field(**kwargs):
    return kwargs


class ModelField:

    def __init__(self, **kwargs):
        self.name = kwargs.pop("name", None)
        self.func = kwargs.pop("func", None)
        self.default = kwargs.pop("default", None)
        self.value = None

    def __get__(self, instance, owner):
        data = instance.__data__.get(self.name, self.default)
        if self.value is None:
            self.value = data if self.func is None else self.func(owner.__database__, data)
        return self.value

    def __set__(self, instance, value):
        instance.__data__[self.name] = value
        # Do the database update shit here


class ModelMeta(type):

    def __new__(mcs, *args, **kwargs):
        name, bases, attrs = args
        attrs["__hash_name__"] = kwargs.pop("name", name.lower())
        return super().__new__(mcs, name, bases, attrs)


class Model(metaclass=ModelMeta):
    __database__: Database = Database()

    def __new__(cls, *args, **kwargs):
        for attr in cls.__annotations__.keys():
            # Skip special class variables (specifically '__database__')
            if attr.startswith("__"):
                continue
            kwargs = cls.__dict__.get(attr, dict(name=attr))
            setattr(cls, attr, ModelField(**kwargs))
        cls.__database__.add_model(cls)
        return super().__new__(cls)

    def __init__(self, data):
        self.__data__ = data
