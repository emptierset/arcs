import enum
import typing

from arcsync.card import Card


class CourtCard(Card):
    pass


@typing.final
class Suit(enum.Enum):
    MATERIAL = 1
    FUEL = 2
    WEAPON = 3
    RELIC = 4
    PSIONIC = 5


NumKeys = int


@typing.final
class GuildCard(CourtCard):
    name: str
    suit: Suit
    raid_cost: NumKeys
    text: str

    def __init__(self, name: str, suit: Suit, raid_cost: NumKeys, text: str) -> None:
        self.name = name
        self.suit = suit
        self.raid_cost = raid_cost
        self.text = text


@typing.final
class LoreCard(CourtCard):
    name: str
    text: str

    def __init__(self, name: str, raid_cost: NumKeys, text: str) -> None:
        self.name = name
        self.text = text


@typing.final
class VoxCard(CourtCard):
    name: str
    text: str

    def __init__(self, name: str, raid_cost: NumKeys, text: str) -> None:
        self.name = name
        self.text = text


if __name__ == "__main__":
    pass
