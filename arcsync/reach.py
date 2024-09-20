import abc
import enum
import typing
from collections.abc import Collection, Mapping, MutableMapping, MutableSet
from typing import Final, NewType

from arcsync.piece import Piece


@typing.final
class PlanetType(enum.Enum):
    MATERIAL = enum.auto()
    FUEL = enum.auto()
    WEAPON = enum.auto()
    RELIC = enum.auto()
    PSIONIC = enum.auto()


@typing.final
class PlanetSymbol(enum.Enum):
    ARROW = enum.auto()
    CRESCENT = enum.auto()
    HEXAGON = enum.auto()


class System(object, metaclass=abc.ABCMeta):
    # Conceptually final; can't figure out how to make mypy happy, though.
    cluster_number: int

    adjacencies: Collection["System"]
    pieces: MutableSet[Piece]

    @abc.abstractmethod
    def __init__(self, cluster_number: int) -> None: ...


@typing.final
class Gate(System):
    cluster_number: int

    adjacencies: Collection[System]
    pieces: MutableSet[Piece]

    def __init__(self, cluster_number: int) -> None:
        self.cluster_number = cluster_number

        self.pieces = set()
        self.adjacencies = []


@typing.final
class Planet(System):
    cluster_number: int
    symbol: Final[PlanetSymbol]
    type: Final[PlanetType]

    adjacencies: Collection[System]
    pieces: MutableSet[Piece]

    _num_slots: int

    def __init__(
        self,
        cluster_number: int,
        planet_symbol: PlanetSymbol,
        planet_type: PlanetType,
        *,
        num_slots: int,
    ) -> None:
        self.cluster_number = cluster_number
        self.symbol = planet_symbol
        self.type = planet_type

        self.pieces = set()
        self.adjacencies = []

        self._num_slots = num_slots

    # def add_piece
    # def remove_piece


@typing.final
class Reach(object):
    systems: Final[Collection[System]]

    def __init__(self, systems: Collection[System]):
        self.systems = systems


if __name__ == "__main__":
    reach = Reach([Planet(1, PlanetSymbol.ARROW, PlanetType.WEAPON, num_slots=2)])
