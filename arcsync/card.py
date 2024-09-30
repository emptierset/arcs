import collections
import random
from collections.abc import Collection
from typing import Generic, TypeVar

from arcsync.util import DunderDictReprMixin


class Card(DunderDictReprMixin):
    pass


CardT = TypeVar("CardT", bound=Card)


class Deck(Generic[CardT]):
    _cards: collections.deque[CardT]

    def __init__(self, cards: Collection[CardT]) -> None:
        self._cards = collections.deque(cards)

    def __len__(self) -> int:
        return len(self._cards)

    def shuffle(self) -> None:
        to_shuffle = list(self._cards)
        random.shuffle(to_shuffle)
        self._cards = collections.deque(to_shuffle)

    def add(self, cards: Collection[CardT]) -> None:
        self._cards.extend(cards)
        self.shuffle()

    def put_on_top(self, card: CardT) -> None:
        self._cards.appendleft(card)

    def draw(self, num: int = 1) -> list[CardT]:
        if len(self._cards) < num:
            raise ValueError(
                f"Cannot draw {num} cards from a deck with only {len(self._cards)} cards."
            )
        cs: list[CardT] = []
        for _ in range(num):
            cs.append(self._cards.popleft())
        return cs

    def put_on_bottom(self, card: CardT) -> None:
        self._cards.append(card)

    def draw_from_bottom(self, num: int = 1) -> list[CardT]:
        if len(self._cards) < num:
            raise ValueError(
                f"Cannot draw {num} cards from the bottom of a deck with only "
                f"{len(self._cards)} cards."
            )
        cs: list[CardT] = []
        for _ in range(num):
            cs.append(self._cards.pop())
        return cs

    def draw_all(self) -> list[CardT]:
        return self.draw(len(self))


if __name__ == "__main__":
    pass
