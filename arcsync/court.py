import typing
from collections import Counter
from typing import Final, Sequence

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
    cards: Sequence[CardInCourt | None]
    _num_slots: Final[int]

    def __init__(self, *, num_slots: int) -> None:
        self.cards = [None] * num_slots
        self._num_slots = num_slots


if __name__ == "__main__":
    pass
