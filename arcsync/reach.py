import abc
import enum
import re
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

    def alphabetic_abbreviation(self) -> str:
        match self:
            case PlanetSymbol.ARROW:
                return "A"
            case PlanetSymbol.CRESCENT:
                return "C"
            case PlanetSymbol.HEXAGON:
                return "H"

    def numeric_abbreviation(self) -> str:
        match self:
            case PlanetSymbol.ARROW:
                return "1"
            case PlanetSymbol.CRESCENT:
                return "2"
            case PlanetSymbol.HEXAGON:
                return "3"

    @staticmethod
    def from_string(s: str) -> "PlanetSymbol":
        match s:
            case "A" | "1":
                return PlanetSymbol.ARROW
            case "C" | "2":
                return PlanetSymbol.CRESCENT
            case "H" | "3":
                return PlanetSymbol.HEXAGON
        raise ValueError(f"Input '{s}' could not be converted to PlanetSymbol.")


Cluster = NewType("Cluster", int)

SystemID = str


def _decompose_system_id(system_id: SystemID) -> tuple[Cluster, PlanetSymbol | None]:
    m = re.match(r"^([1-6])([ACHG])$", system_id)
    if m is None:
        m = re.match(r"^([1-6])\.([1-3G])$", system_id)
        if m is None:
            raise ValueError(f"Input '{system_id}' did not match any known SystemID regex.")

    cluster = int(m.group(1))
    planet_or_gate_string = m.group(2)

    planet_symbol: PlanetSymbol | None = None
    if planet_or_gate_string != "G":
        planet_symbol = PlanetSymbol.from_string(planet_or_gate_string)

    return Cluster(cluster), planet_symbol


class System(object, metaclass=abc.ABCMeta):
    # cluster is conceptually final; can't figure out how to make mypy happy, though.
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

    adjacencies: MutableSet[SystemID]
    pieces: MutableSet[Piece]

    def __init__(
        self,
        cluster: Cluster,
    ) -> None:
        self.cluster = cluster
        self.adjacencies = set()

        self.pieces = set()

    @property
    def id(self) -> SystemID:
        return f"{self.cluster}G"


@typing.final
class Planet(System):
    cluster: Cluster
    symbol: Final[PlanetSymbol]
    type: Final[PlanetType]
    num_slots: int

    adjacencies: MutableSet[SystemID]
    pieces: MutableSet[Piece]

    # TODO(base): Move all @propertys to before __init__, so they are more like normal attributes.
    @property
    def id(self) -> SystemID:
        return f"{self.cluster}{self.symbol.alphabetic_abbreviation()}"

    def __init__(
        self,
        system_id: SystemID,
        planet_type: PlanetType,
        *,
        num_slots: int,
    ) -> None:
        cluster, planet_symbol = _decompose_system_id(system_id)
        if planet_symbol is None:
            raise ValueError(f"SystemID {system_id} does not decompose to a planet symbol.")

        self.cluster = cluster
        self.symbol = planet_symbol
        self.type = planet_type
        self.num_slots = num_slots
        self.adjacencies = set()

        self.pieces = set()

    # def add_piece
    # def remove_piece


@typing.final
class Reach(object):
    systems: Final[Collection[System]]

    def __init__(self, systems: Collection[System]):
        self.systems = systems


if __name__ == "__main__":
    pass
