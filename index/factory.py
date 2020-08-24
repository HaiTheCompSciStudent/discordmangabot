class FactoryMeta(type):

    def __new__(mcs, *args, **kwargs):
        name, bases, attrs = args
        for key, value in kwargs.items():
            attrs[key] = value
        cls = super().__new__(mcs, name, bases, attrs)
        cls.__factory_name__ = kwargs.pop("name", name.lower())
        return cls

    def inject(cls, src):
        kwargs = src.__factory_kwargs__.get(cls.__factory_name__)
        kwargs["source"] = src.name

        class injected_factory(cls, **kwargs):
            pass

        return injected_factory


class Factory(metaclass=FactoryMeta):
    pass

