from collections import OrderedDict
import functools
import discord




def button(emote, position=None, remove_after=True):
    def wrapper(func):
        data = {
            "func": func,
            "emote": emote,
            "position": position,
            "remove_after": remove_after
        }
        func.__button_data__ = data

    return wrapper


class Button:

    def __init__(self, data):
        self.func = data.pop("func")
        self.emote = data.pop("emote")
        self.position = data.pop("position")
        self.remove_after = data.pop("remove_after")


class MenuMeta(type):

    def __new__(cls, *args, **kwargs):
        name, bases, attrs = args
        new_cls = super().__new__(cls, name, bases, attrs)
        buttons = []
        for base in reversed(new_cls.__mro__):
            for elem, value in base.__dict__.items():
                try:
                    data = value.__button_data__
                except AttributeError:
                    continue
                else:
                    button = Button(data)
                    buttons.append(button)
        new_cls.__buttons__ = buttons
        return new_cls

    def get_buttons(cls):
        buttons = OrderedDict()
        for button in sorted(cls.__buttons__, key=lambda b: b.position if button.position is not None else 1):
            buttons[button.emote] = button
        return buttons

class Menu(metaclass=MenuMeta):

    def __init__(self, ctx, embed=None, timeout=None):
        self.ctx = ctx
        self.embed = embed if embed else discord.Embed()
        self.timeout = timeout
        self._buttons = self.__class__.get_buttons()
        self._running = False

    async def start(self):
        message = await self.ctx.send(embed=self.embed)

    async def _run_loop(self, message):
