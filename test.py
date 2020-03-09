import re



def _shorten_line(line):
    order, _, *title, id_ = line.split(" ")
    print(id_)

_shorten_line("[1] : Kaguya-sama wa Kokurasetai: Tensai-tachi no Renai Zunousen 17274")