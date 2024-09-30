import os

from statemachine.contrib.diagram import DotGraphMachine
from arcsync.round import Round
from arcsync.game import Game

def make_diagram(cls):
    graph = DotGraphMachine(cls)
    dot = graph()
    try:
        os.mkdir("diagrams")
    except FileExistsError:
        pass
    dot.write_png(f"diagrams/{cls.__name__.lower()}.png")


clses = [Game, Round]

for cls in clses:
    make_diagram(cls)
