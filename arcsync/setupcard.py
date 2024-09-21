import dataclasses
from collections.abc import Collection
from typing import Final

from arcsync.reach import SystemID


@dataclasses.dataclass(kw_only=True, frozen=True)
class PlayerSetupSystems(object):
    a: SystemID
    b: SystemID
    c: SystemID | tuple[SystemID, SystemID]


@dataclasses.dataclass(frozen=True)
class SetupCard(object):
    name: str
    out_of_play_clusters: Collection[int]


@dataclasses.dataclass(frozen=True)
class TwoPlayerSetupCard(SetupCard):
    name: str
    out_of_play_clusters: Collection[int]
    _: dataclasses.KW_ONLY
    player1: PlayerSetupSystems
    player2: PlayerSetupSystems


@dataclasses.dataclass(frozen=True)
class ThreePlayerSetupCard(SetupCard):
    name: str
    out_of_play_clusters: Collection[int]
    _: dataclasses.KW_ONLY
    player1: PlayerSetupSystems
    player2: PlayerSetupSystems
    player3: PlayerSetupSystems


@dataclasses.dataclass(frozen=True)
class FourPlayerSetupCard(SetupCard):
    name: str
    out_of_play_clusters: Collection[int]
    _: dataclasses.KW_ONLY
    player1: PlayerSetupSystems
    player2: PlayerSetupSystems
    player3: PlayerSetupSystems
    player4: PlayerSetupSystems


two_player_setup_cards: Final[Collection[TwoPlayerSetupCard]] = [
    TwoPlayerSetupCard(
        "Frontiers",
        [1, 6],
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

three_player_setup_cards: Final[Collection[ThreePlayerSetupCard]] = [
    ThreePlayerSetupCard(
        "Mix Up",
        [1, 4],
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

four_player_setup_cards: Final[Collection[FourPlayerSetupCard]] = [
    FourPlayerSetupCard(
        "Mix Up 1",
        [3],
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
