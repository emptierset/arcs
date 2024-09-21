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

    # TODO(base): Make aliases for these, maybe using numbers for one set of aliases and pretty
    # unicode for another.
    def abbreviation(self) -> str:
        match self:
            case PlanetSymbol.ARROW:
                return "A"
            case PlanetSymbol.CRESCENT:
                return "C"
            case PlanetSymbol.HEXAGON:
                return "H"


Cluster = NewType("Cluster", int)

SystemID = NewType("SystemID", str)


class System(object, metaclass=abc.ABCMeta):
    # Conceptually final; can't figure out how to make mypy happy, though.
    cluster: Cluster

    adjacencies: Collection["System"]
    pieces: MutableSet[Piece]

    @abc.abstractmethod
    def __init__(self, cluster: Cluster) -> None: ...

    @property
    @abc.abstractmethod
    def id(self) -> SystemID: ...


@typing.final
class Gate(System):
    cluster: Cluster

    adjacencies: Collection[System]
    pieces: MutableSet[Piece]

    def __init__(self, cluster: Cluster) -> None:
        self.cluster = cluster

        self.pieces = set()
        self.adjacencies = []

    @property
    def id(self) -> SystemID:
        return SystemID(f"{self.cluster}G")


@typing.final
class Planet(System):
    cluster: Cluster
    symbol: Final[PlanetSymbol]
    type: Final[PlanetType]
    num_slots: int

    adjacencies: Collection[System]
    pieces: MutableSet[Piece]

    # TODO(base): Move all @propertys to before __init__, so they are more like normal attributes.
    @property
    def id(self) -> SystemID:
        return SystemID(f"{self.cluster}{self.symbol.abbreviation()}")

    def __init__(
        self,
        cluster: Cluster,
        planet_symbol: PlanetSymbol,
        planet_type: PlanetType,
        *,
        num_slots: int,
    ) -> None:
        self.cluster = cluster
        self.symbol = planet_symbol
        self.type = planet_type
        self.num_slots = num_slots

        self.pieces = set()
        self.adjacencies = []

    # def add_piece
    # def remove_piece


@typing.final
class Reach(object):
    systems: Final[Collection[System]]

    def __init__(self, systems: Collection[System]):
        self.systems = systems


if __name__ == "__main__":
    pass
