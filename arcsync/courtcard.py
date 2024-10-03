import enum
import typing
from abc import ABCMeta

from arcsync.card import Card



class CourtCard(Card, metaclass=ABCMeta):
    id: str
    name: str
    text: str

    def __init__(self, name: str, id_: str, text: str = "") -> None:
        self.name = name
        self.id = id_
        self.text = text

    def __eq__(self, other: "CourtCard") -> bool:  # type: ignore[override]
        return self.id == other.id


@typing.final
class Suit(enum.Enum):
    MATERIAL = 1
    FUEL = 2
    WEAPON = 3
    RELIC = 4
    PSIONIC = 5


NumKeys = int


class GuildCard(CourtCard):
    suit: Suit
    raid_cost: NumKeys

    def __init__(
        self, name: str, id_: str, suit: Suit, *, raid_cost: NumKeys, text: str = ""
    ) -> None:
        super().__init__(name, id_, text)
        self.suit = suit
        self.raid_cost = raid_cost


@typing.final
class LoreCard(CourtCard):
    def __init__(self, name: str, id_: str, text: str = "") -> None:
        super().__init__(name, id_, text)


class VoxCard(CourtCard):
    def __init__(self, name: str, id_: str, text: str = "") -> None:
        super().__init__(name, id_, text)


if __name__ == "__main__":
    pass
