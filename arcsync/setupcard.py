import abc
import dataclasses
from collections.abc import Collection, Sequence
from typing import Final

from arcsync.reach import Cluster, SystemID


@dataclasses.dataclass(kw_only=True, frozen=True)
class PlayerSetupSystems(object):
    a: SystemID
    b: SystemID
    c: SystemID | tuple[SystemID, SystemID]


@dataclasses.dataclass(frozen=True)
class SetupCard(object, metaclass=abc.ABCMeta):
    name: str
    in_play_clusters: Collection[Cluster]


@dataclasses.dataclass(frozen=True)
class TwoPlayerSetupCard(SetupCard):
    name: str
    _: dataclasses.KW_ONLY
    in_play_clusters: Collection[Cluster]
    player1: PlayerSetupSystems
    player2: PlayerSetupSystems


@dataclasses.dataclass(frozen=True)
class ThreePlayerSetupCard(SetupCard):
    name: str
    _: dataclasses.KW_ONLY
    in_play_clusters: Collection[Cluster]
    player1: PlayerSetupSystems
    player2: PlayerSetupSystems
    player3: PlayerSetupSystems


@dataclasses.dataclass(frozen=True)
class FourPlayerSetupCard(SetupCard):
    name: str
    _: dataclasses.KW_ONLY
    in_play_clusters: Collection[Cluster]
    player1: PlayerSetupSystems
    player2: PlayerSetupSystems
    player3: PlayerSetupSystems
    player4: PlayerSetupSystems


two_player_setup_cards: Final[Sequence[TwoPlayerSetupCard]] = [
    TwoPlayerSetupCard(
        "Frontiers",
        in_play_clusters=[Cluster(2), Cluster(3), Cluster(4), Cluster(5)],
        player1=PlayerSetupSystems(
            a=SystemID("5H"), b=SystemID("4H"), c=(SystemID("3H"), SystemID("3G"))
        ),
        player2=PlayerSetupSystems(
            a=SystemID("3A"), b=SystemID("5A"), c=(SystemID("4A"), SystemID("5G"))
        ),
    ),
    # TODO(base): Mix Up 1
    # TODO(base): Homelands
    # TODO(base): Mix Up 2
]

three_player_setup_cards: Final[Sequence[ThreePlayerSetupCard]] = [
    ThreePlayerSetupCard(
        "Mix Up",
        in_play_clusters=[Cluster(2), Cluster(3), Cluster(5), Cluster(6)],
        player1=PlayerSetupSystems(
            a=SystemID("3H"),
            b=SystemID("5C"),
            c=SystemID("2G"),
        ),
        player2=PlayerSetupSystems(
            a=SystemID("5H"),
            b=SystemID("2A"),
            c=SystemID("3G"),
        ),
        player3=PlayerSetupSystems(
            a=SystemID("2H"),
            b=SystemID("3A"),
            c=SystemID("4G"),
        ),
    ),
    # TODO(base): Frontiers
    # TODO(base): Homelands
    # TODO(base): Core Conflict
]

four_player_setup_cards: Final[Sequence[FourPlayerSetupCard]] = [
    FourPlayerSetupCard(
        "Mix Up 1",
        in_play_clusters=[Cluster(1), Cluster(2), Cluster(4), Cluster(5), Cluster(6)],
        player1=PlayerSetupSystems(
            a=SystemID("4A"),
            b=SystemID("6H"),
            c=SystemID("1G"),
        ),
        player2=PlayerSetupSystems(
            a=SystemID("4H"),
            b=SystemID("5H"),
            c=SystemID("6G"),
        ),
        player3=PlayerSetupSystems(
            a=SystemID("5A"),
            b=SystemID("1H"),
            c=SystemID("4G"),
        ),
        player4=PlayerSetupSystems(
            a=SystemID("6A"),
            b=SystemID("1A"),
            c=SystemID("5G"),
        ),
    ),
    # TODO(base): Mix Up 2
    # TODO(base): Frontiers
    # TODO(base): Mix Up 3
]

if __name__ == "__main__":
    pass
