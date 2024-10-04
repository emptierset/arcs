import dataclasses
import random
import typing
from collections import Counter
from collections.abc import Collection, MutableSequence, Sequence
from typing import Callable, Final

from arcsync.card import Deck
from arcsync.color import Color
from arcsync.courtcard import CourtCard
from arcsync.event import CardRemovedFromCourtEvent, CourtRefillNeededEvent
from arcsync.eventbus import EventBus
from arcsync.util import assert_never

CardName = str
Index = int
SlotKey = CardName | Index | CourtCard


@dataclasses.dataclass
class CardWithAgents(object):
    card: CourtCard
    agents: Counter[Color] = dataclasses.field(init=False, default_factory=Counter[Color])


# Court should not be inherited from because we are calling a staticmethod inside it using the raw
# class name, not self.
@typing.final
class Court(object):
    # TODO(base): Make these private.
    deck: Final[Deck[CourtCard]]
    discard_pile: Final[Deck[CourtCard]]

    # `_slots` should never be appended to or popped from. It should always have the same
    # number of elements, forever.
    # TODO(base): We can probably enforce this with mypy with some type, somehow. Maybe it's a 3 or
    # 4-tuple?
    _slots: Final[MutableSequence[CardWithAgents | None]]

    _event_bus: Final[EventBus]

    @property
    def slots_contents(self) -> Sequence[CourtCard | None]:
        return [None if slot is None else slot.card for slot in self._slots]

    def __init__(
        self,
        deck: Collection[CourtCard],
        *,
        num_slots: int,
        seed: int | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        if seed is not None:
            random.seed(seed)
        self.deck = Deck[CourtCard](deck)
        self.deck.shuffle()
        self.discard_pile = Deck[CourtCard]()
        initial_flop = self.deck.draw(num_slots)
        self._slots = [CardWithAgents(card) for card in initial_flop]

        # For convenience, if you are unit testing one component and don't need an event bus, you
        # can skip it. One will be created, but it won't be very useful because it won't be linked
        # to anything else.
        if event_bus is None:
            event_bus = EventBus()
        self._event_bus = event_bus

        def handle_court_refill_needed_event(e: CourtRefillNeededEvent) -> None:
            self.refill_court()

        self._event_bus.subscribe(CourtRefillNeededEvent, handle_court_refill_needed_event)

    def refill_court(self) -> None:
        # We might never need to refill more than one card in base game, but some campaign things
        # can require it. For example, Breaking Worlds.
        for i, slot in enumerate(self._slots):
            if slot is None:
                card = self.deck.draw()
                self._slots[i] = CardWithAgents(card)

    def card(self, key: SlotKey) -> CourtCard:
        slot, _ = self._get_slot_with_card(key)
        return slot.card

    def agents_on_card(self, key: SlotKey) -> Counter[Color]:
        slot, _ = self._get_slot_with_card(key)
        return slot.agents

    # NOTE: This function removes the card from the court before it is returned. If you drop the
    # reference to the returned card, it will be lost from the gamestate.
    def take_card(self, key: SlotKey) -> tuple[CourtCard, Counter[Color]]:
        slot, index = self._get_slot_with_card(key)
        card_with_agents = slot
        self._slots[index] = None
        return card_with_agents.card, card_with_agents.agents

    def discard_card(self, key: SlotKey) -> None:
        self._remove_card(key, self.discard_pile.put_on_top)

    def bury_card(self, key: SlotKey) -> None:
        self._remove_card(key, self.deck.put_on_bottom)

    def _remove_card(self, key: SlotKey, card_movement_fn: Callable[[CourtCard], None]) -> None:
        slot, index = self._get_slot_with_card(key)
        card_with_agents = slot
        self._slots[index] = None
        card_movement_fn(card_with_agents.card)
        # Let the players know that they can reclaim the agents on the removed card.
        self._event_bus.publish(CardRemovedFromCourtEvent(card_with_agents.agents))

    def unbury_to_empty_slot(self, slot_index: int) -> None:
        cwa = self._slots[slot_index]
        if cwa is not None:
            raise ValueError(f"Cannot unbury card to slot already containing {cwa}.")
        card = self.deck.draw_from_bottom()
        self._slots[slot_index] = CardWithAgents(card)

    def recover_discarded_card_to_empty_slot(self, card_name: CardName, slot_index: int) -> None:
        cwa = self._slots[slot_index]
        if cwa is not None:
            raise ValueError(f"Cannot recover discarded card to slot already containing {cwa}.")
        card = self._recover_discarded_card(card_name)
        self._slots[slot_index] = CardWithAgents(card)

    def _recover_discarded_card(self, card_name: CardName) -> CourtCard:
        return Court._draw_from_card_deck_by_name(self.discard_pile, card_name)

    # TODO(campaign): Duplicate card names are common in campaign, so this needs to be some other
    # identifier in the future.
    @staticmethod
    def _draw_from_card_deck_by_name(deck: Deck[CourtCard], card_name: str) -> CourtCard:
        found_card: CourtCard
        for card in deck._cards:
            if card.name == card_name:
                found_card = card
                break
        else:
            raise ValueError(f"Card {card_name} not found in searched Deck.")
        deck._cards.remove(found_card)
        return found_card

    def add_agents(self, player: Color, key: SlotKey, num_agents: int) -> None:
        if num_agents < 0:
            raise ValueError(f"Cannot add negative number ({num_agents}) of agents to card.")
        self._modify_agent_count(player, key, delta=num_agents)

    def remove_agents(self, player: Color, key: SlotKey, num_agents: int) -> None:
        if num_agents < 0:
            raise ValueError(f"Cannot remove negative number ({num_agents}) of agents from card.")
        self._modify_agent_count(player, key, delta=-1 * num_agents)

    def _modify_agent_count(self, player: Color, key: SlotKey, *, delta: int) -> None:
        slot, _ = self._get_slot_with_card(key)
        if slot.agents[player] + delta < 0:
            raise ValueError(
                f"Cannot apply negative delta ({delta}) agents to card with only"
                f" {slot.agents[player]} agents."
            )
        slot.agents[player] += delta

    def _get_slot_with_card(self, key: SlotKey) -> tuple[CardWithAgents, Index]:
        slot, index = self._get_slot(key)
        if slot is None:
            raise ValueError(
                f"No card found in slot keyed by {key}, but _get_slot_with_card requires a card to"
                " be found."
            )
        return slot, index

    def _get_slot(self, key: SlotKey) -> tuple[CardWithAgents | None, Index]:
        if isinstance(key, str) or isinstance(key, CourtCard):
            return self._find_slot_containing(key)
        elif isinstance(key, int):
            return self._slots[key], key
        else:  # pragma: no cover
            assert_never(key)

    def _find_slot_containing(
        self, card_identifier: CardName | CourtCard
    ) -> tuple[CardWithAgents, Index]:
        lookup_name = card_identifier if isinstance(card_identifier, str) else card_identifier.name
        names = [None if slot is None else slot.card.name for slot in self._slots]
        for i, name in enumerate(names):
            if name is not None and name == lookup_name:
                # Cast here is safe because `names` and `self._slots` are parallel -- the same
                # length and mutually `None` when they are `None`.
                return typing.cast(CardWithAgents, self._slots[i]), i
        raise ValueError(f"Card {card_identifier} not in court ({self.slots_contents}).")


if __name__ == "__main__":  # pragma: no cover
    pass
