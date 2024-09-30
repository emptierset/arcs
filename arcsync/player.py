import typing
from collections.abc import MutableSequence
from typing import Final, NewType, Sequence

import arcsync.piece
from arcsync.actioncard import ActionCard
from arcsync.ambition import Ambition
from arcsync.color import Color
from arcsync.courtcard import GuildCard
from arcsync.courtcard import Suit as GuildCardSuit
from arcsync.piece import DamageablePiece
from arcsync.resource import Resource
from arcsync.util import DunderDictReprMixin, assert_never

SlotRaidCost = NewType("SlotRaidCost", int)


@typing.final
class Slot(DunderDictReprMixin):
    contents: Resource | None
    raid_cost: Final[SlotRaidCost]

    def __init__(self, raid_cost: SlotRaidCost, contents: Resource | None = None) -> None:
        self.contents = contents
        self.raid_cost = raid_cost


@typing.final
class Player(DunderDictReprMixin):
    color: Final[Color]

    # TODO(base): make most of these private.

    hand: MutableSequence[ActionCard]
    tableau: MutableSequence[GuildCard]
    slots: Sequence[Slot]

    ships: int
    agents: int
    starports: int
    cities: int

    # trophies
    # captives

    # TODO(campaign): Favors
    # TODO(campaign): Titles
    # TODO(L&L): Leader/Fate

    def __init__(self, color: Color) -> None:
        self.color = color

        self.hand = []
        self.tableau = []
        self.slots = [
            Slot(SlotRaidCost(3)),
            Slot(SlotRaidCost(1)),
            Slot(SlotRaidCost(1)),
            Slot(SlotRaidCost(2)),
            Slot(SlotRaidCost(1)),
            Slot(SlotRaidCost(3)),
        ]

        self.ships = 15
        self.agents = 10
        self.starports = 5
        self.cities = 5

    def hit_piece(self, p: DamageablePiece, num_hits: int = 1) -> None:
        arcsync.piece.hit(self.color, p, num_hits=num_hits)

    # TODO(base): Support rearranging. Probably on an event handle.

    def gain_resource(self, r: Resource, *, slot_index: int) -> None:
        if self._is_slot_covered_by_city(slot_index):
            raise ValueError(
                f"Cannot gain resource to slot index {slot_index} because it is covered by a city."
            )
        self.slots[slot_index].contents = r
        # TODO(base): If something was in the slot, shift it somewhere else.

    def _is_slot_covered_by_city(self, slot_index: int) -> bool:
        covered = [False, False, True, True, True, True]
        if self.cities <= 4:
            covered[2] = False
        if self.cities <= 3:
            covered[3] = False
        if self.cities <= 2:
            covered[4] = False
            covered[5] = False
        return covered[slot_index]


if __name__ == "__main__":
    pass
