import inspect


def wrapper(func):
    def wrapped(self, *args, **kwargs):
        print(self.l)
        return func(self, *args, **kwargs)

    return wrapped


class FooMeta(type):

    def __new__(cls, *args, **kwargs):
        new_cls = super().__new__(cls, *args, **kwargs)
        func = getattr(new_cls, "foo")
        setattr(new_cls, "foo", wrapper(func))
        return new_cls


class Foo(metaclass=FooMeta):

    def __init__(self):
        self.l = "foo"

    def foo(self, id):
        print(self.l)
        print(id)
        print("what")


f = Foo()
f.foo(2)