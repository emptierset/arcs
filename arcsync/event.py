import abc
import dataclasses
import typing
from collections import Counter

# This file will need to import most of the game's concepts, but only as type annotations. We'll
# import them as TYPE_CHECKING only to avoid circular imports. This means that many of the type
# annotations in this file will be ugly string forward references.
if typing.TYPE_CHECKING:  # pragma: no cover
    from arcsync.ambition import Ambition
    from arcsync.color import Color
    from arcsync.piece import DamageablePiece


# TODO(cleanup): These events need to be named according to what actually happened, not what they
# want a listener to do. For example, AmbitionDeclaredEvent should be LeadCardDeclaredAmbition.
# AmbitionDeclaredEvent makes it sound like it's AmbitionManager announcing to everyone else that
# an ambition was declared, not someone else announcing to AmbitionManager that they should declare
# an ambition.


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
class RoundCompleteEvent(Event):
    pass


@dataclasses.dataclass(frozen=True)
class CardRemovedFromCourtEvent(Event):
    agents: Counter["Color"]


# NOTE: Do not use this yet. Secure must be automated before automatic refill is possible
@dataclasses.dataclass(frozen=True)
class CourtRefillNeededEvent(Event):
    def __init__(self) -> None:
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class PlayerDestroyedPieceEvent(Event):
    player: "Color"
    piece: "DamageablePiece"


if __name__ == "__main__":  # pragma: no cover
    pass
