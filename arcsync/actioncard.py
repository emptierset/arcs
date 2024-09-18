import enum
import typing
from collections.abc import Mapping
from typing import Final

from arcsync.card import Card, Deck


@typing.final
class Suit(enum.Enum):
    ADMINISTRATION = enum.auto()
    CONSTRUCTION = enum.auto()
    MOBILIZATION = enum.auto()
    AGGRESSION = enum.auto()
    # TODO(campaign): FAITHFUL_ZEAL, FAITHFUL_WISDOM.


Rank = int

Pips = int


@typing.final
class ActionCard(Card):
    suit: Suit
    rank: Rank
    pips: Pips

    def __init__(self, suit: Suit, *, rank: Rank, pips: Pips) -> None:
        self.suit = suit
        self.rank = rank
        self.pips = pips


# TODO(campaign): Event cards.


class ActionCardDeck(Deck[ActionCard]):
    def __init__(self, *, player_count: int) -> None:
        if 2 <= player_count <= 3:
            super().__init__(basic_2_3p_action_cards)
        elif player_count == 4:
            super().__init__(basic_4p_action_cards)
        else:
            raise ValueError(f"only 2, 3, and 4 player games are supported, not {player_count}")


@typing.final
class ActionCardDiscard(ActionCardDeck):
    def __init__(self) -> None:
        super(ActionCardDeck, self).__init__([])


basic_action_cards: Final[Mapping[Suit, Mapping[Rank, ActionCard]]] = {
    Suit.ADMINISTRATION: {
        1: ActionCard(Suit.ADMINISTRATION, rank=1, pips=4),
        2: ActionCard(Suit.ADMINISTRATION, rank=2, pips=4),
        3: ActionCard(Suit.ADMINISTRATION, rank=3, pips=3),
        4: ActionCard(Suit.ADMINISTRATION, rank=4, pips=3),
        5: ActionCard(Suit.ADMINISTRATION, rank=5, pips=3),
        6: ActionCard(Suit.ADMINISTRATION, rank=6, pips=2),
        7: ActionCard(Suit.ADMINISTRATION, rank=7, pips=1),
    },
    Suit.CONSTRUCTION: {
        1: ActionCard(Suit.CONSTRUCTION, rank=1, pips=4),
        2: ActionCard(Suit.CONSTRUCTION, rank=2, pips=4),
        3: ActionCard(Suit.CONSTRUCTION, rank=3, pips=3),
        4: ActionCard(Suit.CONSTRUCTION, rank=4, pips=3),
        5: ActionCard(Suit.CONSTRUCTION, rank=5, pips=2),
        6: ActionCard(Suit.CONSTRUCTION, rank=6, pips=2),
        7: ActionCard(Suit.CONSTRUCTION, rank=7, pips=1),
    },
    Suit.MOBILIZATION: {
        1: ActionCard(Suit.MOBILIZATION, rank=1, pips=4),
        2: ActionCard(Suit.MOBILIZATION, rank=2, pips=4),
        3: ActionCard(Suit.MOBILIZATION, rank=3, pips=3),
        4: ActionCard(Suit.MOBILIZATION, rank=4, pips=3),
        5: ActionCard(Suit.MOBILIZATION, rank=5, pips=2),
        6: ActionCard(Suit.MOBILIZATION, rank=6, pips=2),
        7: ActionCard(Suit.MOBILIZATION, rank=7, pips=1),
    },
    Suit.AGGRESSION: {
        1: ActionCard(Suit.AGGRESSION, rank=1, pips=3),
        2: ActionCard(Suit.AGGRESSION, rank=2, pips=3),
        3: ActionCard(Suit.AGGRESSION, rank=3, pips=2),
        4: ActionCard(Suit.AGGRESSION, rank=4, pips=2),
        5: ActionCard(Suit.AGGRESSION, rank=5, pips=2),
        6: ActionCard(Suit.AGGRESSION, rank=6, pips=2),
        7: ActionCard(Suit.AGGRESSION, rank=7, pips=1),
    },
}


# TODO(base): Make this a Collection.
basic_2_3p_action_cards: Final[frozenset[ActionCard]] = frozenset(
    [
        basic_action_cards[Suit.ADMINISTRATION][2],
        basic_action_cards[Suit.ADMINISTRATION][3],
        basic_action_cards[Suit.ADMINISTRATION][4],
        basic_action_cards[Suit.ADMINISTRATION][5],
        basic_action_cards[Suit.ADMINISTRATION][6],
        basic_action_cards[Suit.CONSTRUCTION][2],
        basic_action_cards[Suit.CONSTRUCTION][3],
        basic_action_cards[Suit.CONSTRUCTION][4],
        basic_action_cards[Suit.CONSTRUCTION][5],
        basic_action_cards[Suit.CONSTRUCTION][6],
        basic_action_cards[Suit.MOBILIZATION][2],
        basic_action_cards[Suit.MOBILIZATION][3],
        basic_action_cards[Suit.MOBILIZATION][4],
        basic_action_cards[Suit.MOBILIZATION][5],
        basic_action_cards[Suit.MOBILIZATION][6],
        basic_action_cards[Suit.AGGRESSION][2],
        basic_action_cards[Suit.AGGRESSION][3],
        basic_action_cards[Suit.AGGRESSION][4],
        basic_action_cards[Suit.AGGRESSION][5],
        basic_action_cards[Suit.AGGRESSION][6],
    ]
)


basic_4p_action_cards: Final[frozenset[ActionCard]] = frozenset(
    [
        basic_action_cards[Suit.ADMINISTRATION][1],
        basic_action_cards[Suit.ADMINISTRATION][2],
        basic_action_cards[Suit.ADMINISTRATION][3],
        basic_action_cards[Suit.ADMINISTRATION][4],
        basic_action_cards[Suit.ADMINISTRATION][5],
        basic_action_cards[Suit.ADMINISTRATION][6],
        basic_action_cards[Suit.ADMINISTRATION][7],
        basic_action_cards[Suit.CONSTRUCTION][1],
        basic_action_cards[Suit.CONSTRUCTION][2],
        basic_action_cards[Suit.CONSTRUCTION][3],
        basic_action_cards[Suit.CONSTRUCTION][4],
        basic_action_cards[Suit.CONSTRUCTION][5],
        basic_action_cards[Suit.CONSTRUCTION][6],
        basic_action_cards[Suit.CONSTRUCTION][7],
        basic_action_cards[Suit.MOBILIZATION][1],
        basic_action_cards[Suit.MOBILIZATION][2],
        basic_action_cards[Suit.MOBILIZATION][3],
        basic_action_cards[Suit.MOBILIZATION][4],
        basic_action_cards[Suit.MOBILIZATION][5],
        basic_action_cards[Suit.MOBILIZATION][6],
        basic_action_cards[Suit.MOBILIZATION][7],
        basic_action_cards[Suit.AGGRESSION][1],
        basic_action_cards[Suit.AGGRESSION][2],
        basic_action_cards[Suit.AGGRESSION][3],
        basic_action_cards[Suit.AGGRESSION][4],
        basic_action_cards[Suit.AGGRESSION][5],
        basic_action_cards[Suit.AGGRESSION][6],
        basic_action_cards[Suit.AGGRESSION][7],
    ]
)

if __name__ == "__main__":
    pass
