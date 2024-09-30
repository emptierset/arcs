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

    # TODO(base): make most of these private and final.

    hand: MutableSequence[ActionCard]
    tableau: MutableSequence[GuildCard]
    slots: Sequence[Slot]
    # TODO(base): Add some holding area for excess resources during rearrange.
    # excess: Final[list[Resource]]

    power: int

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

        self.power = 0

        self.ships = 15
        self.agents = 10
        self.starports = 5
        self.cities = 5

    def count_for_ambition(self, ambition: Ambition) -> int:
        match ambition:
            case Ambition.TYCOON:
                return (
                    self._count_resources_of_type(Resource.MATERIAL)
                    + self._count_resources_of_type(Resource.FUEL)
                    + self._count_guild_cards_of_suit(GuildCardSuit.MATERIAL)
                    + self._count_guild_cards_of_suit(GuildCardSuit.FUEL)
                )
            case Ambition.EDENGUARD:  # pragma: no cover
                raise NotImplementedError()
            case Ambition.TYRANT:
                raise NotImplementedError()
            case Ambition.WARLORD:
                raise NotImplementedError()
            case Ambition.KEEPER:
                return self._count_resources_of_type(
                    Resource.RELIC
                ) + self._count_guild_cards_of_suit(GuildCardSuit.RELIC)
            case Ambition.EMPATH:
                return self._count_resources_of_type(
                    Resource.PSIONIC
                ) + self._count_guild_cards_of_suit(GuildCardSuit.PSIONIC)
            case Ambition.BLIGHTKIN:  # pragma: no cover
                raise NotImplementedError()
            case _ as unreachable:  # pragma: no cover
                assert_never(unreachable)

    def _count_resources_of_type(self, resource: Resource) -> int:
        return sum(1 for s in self.slots if s.contents == resource)

    def _count_guild_cards_of_suit(self, suit: GuildCardSuit) -> int:
        return sum(1 for card in self.tableau if card.suit == suit)

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
