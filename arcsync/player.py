import typing
from collections.abc import MutableSequence
from typing import Final, NewType, Sequence

import arcsync.piece
from arcsync.actioncard import ActionCard
from arcsync.color import Color
from arcsync.courtcard import GuildCard
from arcsync.piece import DamageablePiece
from arcsync.resource import Resource
from arcsync.util import DunderDictReprMixin

SlotRaidCost = NewType("SlotRaidCost", int)


@typing.final
class Slot(DunderDictReprMixin):
    contents: Resource | None
    is_unlocked: bool
    raid_cost: Final[SlotRaidCost]

    def __init__(
        self, raid_cost: SlotRaidCost, is_unlocked: bool, contents: Resource | None = None
    ) -> None:
        self.contents = contents
        self.is_unlocked = is_unlocked
        self.raid_cost = raid_cost


@typing.final
class Player(object):
    color: Final[Color]

    hand: MutableSequence[ActionCard]
    tableau: MutableSequence[GuildCard]
    slots: Sequence[Slot]

    ships: int
    agents: int
    starports: int
    cities: int

    # TODO(campaign): Favors
    # TODO(campaign): Titles
    # TODO(L&L): Leader/Fate

    def __init__(self, color: Color) -> None:
        self.color = color

        self.hand = []
        self.tableau = []
        self.slots = [
            Slot(SlotRaidCost(3), True),
            Slot(SlotRaidCost(1), True),
            Slot(SlotRaidCost(1), False),
            Slot(SlotRaidCost(2), False),
            Slot(SlotRaidCost(1), False),
            Slot(SlotRaidCost(3), False),
        ]

        self.ships = 15
        self.agents = 10
        self.starports = 5
        self.cities = 5

    def hit_piece(self, p: DamageablePiece, num_hits: int = 1) -> None:
        arcsync.piece.hit(self.color, p, num_hits=num_hits)


if __name__ == "__main__":
    pass
