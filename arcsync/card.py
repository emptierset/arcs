import collections
import random
import typing
from collections.abc import Collection
from typing import Generic, TypeVar

from arcsync.util import DunderDictReprMixin


class Card(DunderDictReprMixin):
    pass


CardT = TypeVar("CardT", bound=Card)


class Deck(Generic[CardT]):
    _cards: collections.deque[CardT]

    def __init__(self, cards: Collection[CardT], seed: int | None = None) -> None:
        if seed is not None:
            random.seed(seed)
        self._cards = collections.deque(cards)

    def __len__(self) -> int:
        return len(self._cards)

    # Not interesting for base game, but a nontrivial part of campaign strategy is seeing the
    # cardback for the card on top of the deck.
    def peek_top(self) -> CardT:
        if not self._cards:
            raise ValueError("Cannot peek the top card of an empty deck.")
        # 0 is the correct index (not -1), because `draw` uses `popleft`, not `pop`.
        return self._cards[0]

    def shuffle(self) -> None:
        to_shuffle = list(self._cards)
        random.shuffle(to_shuffle)
        self._cards = collections.deque(to_shuffle)

    def add(self, cards: Collection[CardT]) -> None:
        self._cards.extend(cards)
        self.shuffle()

    def put_on_top(self, card: CardT) -> None:
        self._cards.appendleft(card)

    @typing.overload
    def draw(self) -> CardT: ...

    @typing.overload
    def draw(self, num: int) -> list[CardT]: ...

    def draw(self, num: int | None = None) -> list[CardT] | CardT:
        if num is None:
            num = 1
        if len(self._cards) < num:
            raise ValueError(
                f"Cannot draw {num} cards from a deck with only {len(self._cards)} cards."
            )
        if num == 1:
            return self._cards.popleft()
        return [self._cards.popleft() for _ in range(num)]

    def put_on_bottom(self, card: CardT) -> None:
        self._cards.append(card)

    @typing.overload
    def draw_from_bottom(self) -> CardT: ...

    @typing.overload
    def draw_from_bottom(self, num: int) -> list[CardT]: ...

    def draw_from_bottom(self, num: int | None = None) -> list[CardT] | CardT:
        if num is None:
            num = 1
        if len(self._cards) < num:
            raise ValueError(
                f"Cannot draw {num} cards from bottom of deck with only {len(self._cards)} cards."
            )
        if num == 1:
            return self._cards.pop()
        return [self._cards.pop() for _ in range(num)]

    def draw_all(self) -> list[CardT]:
        return self.draw(len(self))


if __name__ == "__main__":
    pass
