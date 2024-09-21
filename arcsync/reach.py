import abc
import enum
import re
import typing
from collections.abc import Collection, Mapping, MutableMapping, MutableSet
from typing import Final, NewType

from arcsync.piece import Piece
from arcsync.util import DunderDictReprTruncatedSequencesMixin

if typing.TYPE_CHECKING:
    from arcsync.setupcard import SetupCard


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


class System(DunderDictReprTruncatedSequencesMixin, metaclass=abc.ABCMeta):
    # cluster is conceptually final; can't figure out how to make mypy happy, though.
    cluster: Cluster

    adjacencies: MutableSet[SystemID]
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
    systems: Final[Mapping[SystemID, System]]

    excluded_system_ids: Final[Collection[SystemID]]

    def __init__(self, setup_card: "SetupCard") -> None:
        m: MutableMapping[SystemID, System] = dict()

        def init_gate_to_adjacent_gate_edges(g: Gate) -> None:
            def get_next_in_play_gate(g: Gate) -> System:
                def get_next_cluster(c: Cluster) -> Cluster:
                    if c == 6:
                        return Cluster(1)
                    return Cluster(c + 1)

                def get_next_in_play_cluster(c: Cluster) -> Cluster:
                    # Only consider skipping two clusters, because no more than two consecutive
                    # clusters can be out of play.
                    next_cluster = get_next_cluster(c)
                    if next_cluster not in setup_card.in_play_clusters:
                        next_cluster = get_next_cluster(next_cluster)
                    if next_cluster not in setup_card.in_play_clusters:
                        next_cluster = get_next_cluster(next_cluster)
                    return next_cluster

                cluster_of_next_gate = get_next_in_play_cluster(g.cluster)
                system_id = SystemID(f"{cluster_of_next_gate}.G")
                return m[system_id]

            def get_previous_in_play_gate(g: Gate) -> System:
                def get_previous_cluster(c: Cluster) -> Cluster:
                    if c == 1:
                        return Cluster(6)
                    return Cluster(c - 1)

                def get_previous_in_play_cluster(c: Cluster) -> Cluster:
                    # Only consider skipping two clusters, because no more than two consecutive
                    # clusters can be out of play.
                    previous_cluster = get_previous_cluster(c)
                    if previous_cluster not in setup_card.in_play_clusters:
                        previous_cluster = get_previous_cluster(previous_cluster)
                    if previous_cluster not in setup_card.in_play_clusters:
                        previous_cluster = get_previous_cluster(previous_cluster)
                    return previous_cluster

                cluster_of_previous_gate = get_previous_in_play_cluster(g.cluster)
                system_id = SystemID(f"{cluster_of_previous_gate}.G")
                return m[system_id]

                # It's OK to miss here, because some gates that we need to create edges to might
                # not exist yet. We are checking all of the gates, so we'll create the edge in the
                # future.

            try:
                next_gate = get_next_in_play_gate(g)
                Reach.add_edge(g, next_gate)
            except KeyError:
                pass
            try:
                previous_gate = get_previous_in_play_gate(g)
                Reach.add_edge(g, previous_gate)
            except KeyError:
                pass

        excluded_system_ids: list[SystemID] = []

        if Cluster(1) in setup_card.in_play_clusters:
            g1 = Gate(Cluster(1))
            m["1.G"] = g1
            m["1.1"] = Planet("1.1", PlanetType.WEAPON, num_slots=2)
            m["1.2"] = Planet("1.2", PlanetType.FUEL, num_slots=1)
            m["1.3"] = Planet("1.3", PlanetType.MATERIAL, num_slots=2)
            init_gate_to_adjacent_gate_edges(g1)
            Reach.add_edges(m["1.G"], [m["1.1"], m["1.2"], m["1.3"]])
        else:
            excluded_system_ids.extend(["1.G", "1.1", "1.2", "1.3"])

        if Cluster(2) in setup_card.in_play_clusters:
            g2 = Gate(Cluster(2))
            m["2.G"] = g2
            m["2.1"] = Planet("2.1", PlanetType.PSIONIC, num_slots=1)
            m["2.2"] = Planet("2.2", PlanetType.WEAPON, num_slots=1)
            m["2.3"] = Planet("2.3", PlanetType.RELIC, num_slots=2)
            init_gate_to_adjacent_gate_edges(g2)
            Reach.add_edges(m["2.G"], [m["2.1"], m["2.2"], m["2.3"]])
        else:
            excluded_system_ids.extend(["2.G", "2.1", "2.2", "2.3"])

        if Cluster(3) in setup_card.in_play_clusters:
            g3 = Gate(Cluster(3))
            m["3.G"] = g3
            m["3.1"] = Planet("3.1", PlanetType.MATERIAL, num_slots=1)
            m["3.2"] = Planet("3.2", PlanetType.FUEL, num_slots=1)
            m["3.3"] = Planet("3.3", PlanetType.WEAPON, num_slots=2)
            init_gate_to_adjacent_gate_edges(g3)
            Reach.add_edges(m["3.G"], [m["3.1"], m["3.2"], m["3.3"]])
        else:
            excluded_system_ids.extend(["3.G", "3.1", "3.2", "3.3"])

        if Cluster(4) in setup_card.in_play_clusters:
            g4 = Gate(Cluster(4))
            m["4.G"] = g4
            m["4.1"] = Planet("4.1", PlanetType.RELIC, num_slots=2)
            m["4.2"] = Planet("4.2", PlanetType.FUEL, num_slots=2)
            m["4.3"] = Planet("4.3", PlanetType.MATERIAL, num_slots=1)
            init_gate_to_adjacent_gate_edges(g4)
            Reach.add_edges(m["4.G"], [m["4.1"], m["4.2"], m["4.3"]])
        else:
            excluded_system_ids.extend(["4.G", "4.1", "4.2", "4.3"])

        if Cluster(5) in setup_card.in_play_clusters:
            g5 = Gate(Cluster(5))
            m["5.G"] = g5
            m["5.1"] = Planet("5.1", PlanetType.WEAPON, num_slots=1)
            m["5.2"] = Planet("5.2", PlanetType.RELIC, num_slots=1)
            m["5.3"] = Planet("5.3", PlanetType.PSIONIC, num_slots=2)
            init_gate_to_adjacent_gate_edges(g5)
            Reach.add_edges(m["5.G"], [m["5.1"], m["5.2"], m["5.3"]])
        else:
            excluded_system_ids.extend(["5.G", "5.1", "5.2", "5.3"])

        if Cluster(6) in setup_card.in_play_clusters:
            g6 = Gate(Cluster(6))
            m["6.G"] = g6
            m["6.1"] = Planet("6.1", PlanetType.MATERIAL, num_slots=1)
            m["6.2"] = Planet("6.2", PlanetType.FUEL, num_slots=2)
            m["6.3"] = Planet("6.3", PlanetType.PSIONIC, num_slots=1)
            init_gate_to_adjacent_gate_edges(g6)
            Reach.add_edges(m["6.G"], [m["6.1"], m["6.2"], m["6.3"]])
        else:
            excluded_system_ids.extend(["6.G", "6.1", "6.2", "6.3"])

        # These are "edge case" (ha!) edges between two pairs of clusters if they are both in the
        # game.
        if Cluster(2) in setup_card.in_play_clusters and Cluster(3) in setup_card.in_play_clusters:
            Reach.add_edge(m["2.3"], m["3.1"])
        if Cluster(5) in setup_card.in_play_clusters and Cluster(6) in setup_card.in_play_clusters:
            Reach.add_edge(m["5.3"], m["6.1"])

        self.systems = m
        self.excluded_system_ids = excluded_system_ids

    # Adjacency is always bidirectional (until Gate Wraith.......).
    @staticmethod
    def add_edge(s1: System, s2: System) -> None:
        s1.adjacencies.add(s2.id)
        s2.adjacencies.add(s1.id)

    @staticmethod
    def add_edges(s: System, ss: Collection[System]) -> None:
        for adjacent_system in ss:
            Reach.add_edge(s, adjacent_system)


if __name__ == "__main__":
    pass
