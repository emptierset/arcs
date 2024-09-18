import abc
import dataclasses

import arcsync.ambition
from arcsync.color import Color
from arcsync.piece import DamageablePiece


@dataclasses.dataclass(frozen=True)
class Event(object, metaclass=abc.ABCMeta):
    pass


@dataclasses.dataclass(frozen=True)
class AmbitionDeclaredEvent(Event):
    player: Color
    ambition: arcsync.ambition.Ambition


@dataclasses.dataclass(frozen=True)
class InitiativeSeizedEvent(Event):
    player: Color


@dataclasses.dataclass(frozen=True)
class PlayerDestroyedPieceEvent(Event):
    player: Color
    piece: DamageablePiece


if __name__ == "__main__":
    pass
