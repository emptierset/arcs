import typing
from collections.abc import MutableSequence
from typing import Final, NewType, Sequence

import arcsync.piece
from arcsync.actioncard import ActionCard
from arcsync.ambition import Ambition
from arcsync.color import Color
from arcsync.courtcard import GuildCard
from arcsync.courtcard import Suit as GuildCardSuit
from arcsync.event import CardRemovedFromCourtEvent
from arcsync.eventbus import EventBus
from arcsync.piece import Agent, City, DamageablePiece, PlayerPiece, Ship, Starport
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

    trophies: list[PlayerPiece]
    captives: list[PlayerPiece]

    # TODO(campaign): Favors
    # TODO(campaign): Titles
    # TODO(L&L): Leader/Fate

    _event_bus: Final[EventBus]

    def __init__(self, color: Color, event_bus: EventBus | None = None) -> None:
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

        # For convenience, if you are unit testing one component and don't need an event bus, you
        # can skip it. One will be created, but it won't be very useful because it won't be linked
        # to anything else.
        if event_bus is None:
            event_bus = EventBus()
        self._event_bus = event_bus

        def handle_card_removed_from_court_event(e: CardRemovedFromCourtEvent) -> None:
            if self.color not in e.agents:
                return
            for _ in range(e.agents[self.color]):
                # TODO(cleanup): Creating an Agent to return it is jank.
                self.receive_returned_piece(Agent(self.color))

        # TODO(cleanup): is there a way to subscribe to events and create the callback inline?
        self._event_bus.subscribe(CardRemovedFromCourtEvent, handle_card_removed_from_court_event)

    def acquire_card(self, card: GuildCard) -> None:
        self.tableau.append(card)

    def capture(self, piece: PlayerPiece) -> None:
        if piece.loyalty == self.color:
            raise ValueError(
                f"Cannot capture returned piece of loyalty {piece.loyalty} because it matches my"
                f" color ({self.color})."
            )
        self.captives.append(piece)

    def receive_returned_piece(self, piece: PlayerPiece) -> None:
        if piece.loyalty != self.color:
            raise ValueError(
                f"Cannot receive returned piece of loyalty {piece.loyalty} because it does not"
                f" match my color ({self.color})."
            )
        match piece:
            case Ship():
                self.ships += 1
            case Agent():
                self.agents += 1
            case Starport():
                self.starports += 1
            case City():
                self.cities += 1
                # TODO(base): Handle resource rearrangement.

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


if __name__ == "__main__":  # pragma: no cover
    pass
