import typing
from collections import Counter
from collections.abc import Collection, Sequence
from typing import Final

from arcsync.card import Deck
from arcsync.color import Color
from arcsync.courtcard import CourtCard

AgentsOnCard = Counter[Color]


@typing.final
class CardInCourt(object):
    card: CourtCard
    agents: AgentsOnCard

    def __init__(self, card: CourtCard) -> None:
        self.card = card
        self.agents = Counter()


@typing.final
class Court(object):
    deck: Final[Deck[CourtCard]]

    # `cards` should never be appended to or popped from. It should always have the same number of
    # elements, forever.
    # TODO(base): We can probably enforce this with mypy.
    cards: Final[Sequence[CardInCourt]]

    def __init__(self, deck: Collection[CourtCard], *, num_slots: int) -> None:
        self.deck = Deck[CourtCard](deck)
        self.deck.shuffle()
        initial_flop = self.deck.draw(num_slots)
        self.cards = [CardInCourt(card) for card in initial_flop]


if __name__ == "__main__":
    pass
