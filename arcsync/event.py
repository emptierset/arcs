import abc
import dataclasses
import typing

# This file will need to import most of the game's concepts, but only as type annotations. We'll
# import them as TYPE_CHECKING only to avoid circular imports. This means that many of the type
# annotations in this file will be ugly string forward references.
if typing.TYPE_CHECKING:
    from arcsync.ambition import Ambition
    from arcsync.color import Color
    from arcsync.piece import DamageablePiece


@dataclasses.dataclass(frozen=True)
class Event(object, metaclass=abc.ABCMeta):
    pass


@dataclasses.dataclass(frozen=True)
class AmbitionDeclaredEvent(Event):
    player: "Color"
    ambition: "Ambition"


@dataclasses.dataclass(frozen=True)
class InitiativeGainedEvent(Event):
    player: "Color"


@dataclasses.dataclass(frozen=True)
class PlayerDestroyedPieceEvent(Event):
    player: "Color"
    piece: "DamageablePiece"


if __name__ == "__main__":
    pass
