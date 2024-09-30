import random
import typing
from collections.abc import Mapping, MutableSequence, MutableSet, Sequence
from enum import Enum
from typing import Any, Callable, Final

from statemachine import State
from statemachine.transition_list import TransitionList

import arcsync.setupcard
from arcsync.actioncard import ActionCard, ActionCardDeck, ActionCardDiscard
from arcsync.ambition import Ambition, AmbitionManager, Power
from arcsync.color import Color
from arcsync.court import Court
from arcsync.event import InitiativeGainedEvent, RoundCompleteEvent
from arcsync.eventbus import EventBus
from arcsync.helpers.enumstatemachine import EnumStateMachine, EnumStates
from arcsync.play import Copy, CouldNotFollow, Lead, PassInitiative, Pivot, Surpass
from arcsync.player import Player
from arcsync.reach import Reach
from arcsync.round import Round
from arcsync.setupcard import SetupCard

AnyFunc = Callable[..., Any]


class Phase(Enum):
    INIT = 1
    SETUP = 2
    PLAY_A_ROUND = 3
    CHAPTER_END = 4
    GAME_END = 5


# TODO(cleanup): StateMachine-level getattr in the stub pollutes the world with a lot of Any.


@typing.final
class Game(EnumStateMachine[Phase]):
    players: Mapping[Color, Player]
    ambition_manager: AmbitionManager
    reach: Reach
    court: Court

    action_card_deck: ActionCardDeck
    action_card_discard: ActionCardDeck

    _player_count: Final[int]
    _event_bus: Final[EventBus]
    _rounds_this_chapter: MutableSequence[Round]

    initiative: Color
    chapter: int
    round: Round

    winner: Color | None

    @property
    def turn_order(self) -> Sequence[Color]:
        order = []
        current_index = self._turn_order.index(self.initiative)
        for _ in range(self._player_count):
            order.append(self._turn_order[current_index])
            current_index = (current_index + 1) % self._player_count
        return order

    def __init__(self, *, player_count: int) -> None:
        if player_count < 3 or player_count > 4:
            raise ValueError(f"Only player counts 3 and 4 are supported, not {player_count}.")
        self._player_count = player_count

        super().__init__()

        self._rounds_this_chapter: MutableSequence[Round] = []

        self._event_bus = EventBus()

        # Initialize event handlers below this.

        def handle_initiative_gained_event(e: InitiativeGainedEvent) -> None:
            self.initiative = e.player

        self._event_bus.subscribe(InitiativeGainedEvent, handle_initiative_gained_event)

        def handle_round_complete_event(e: RoundCompleteEvent) -> None:
            self._discard_cards_played_this_round()
            self._rounds_this_chapter.append(self.round)
            self._end_current_round()

        self._event_bus.subscribe(RoundCompleteEvent, handle_round_complete_event)

    # State machine logic

    s = EnumStates[Phase](Phase, Phase.INIT, final=Phase.GAME_END)

    @s.PLAY_A_ROUND.enter
    def _on_round_start(self, source: State) -> None:
        self.round = Round(self.turn_order, self._event_bus)

    @s.PLAY_A_ROUND.exit
    def _on_round_end(self, target: State) -> None:
        if target.value == Phase.CHAPTER_END:
            # If we are going to CHAPTER_END, then we are done with the chapter and no longer need
            # the round history.
            self._rounds_this_chapter: MutableSequence[Round] = []

    setup: AnyFunc = s.INIT.to(s.SETUP)

    @s.SETUP.enter
    def _setup_game(self) -> None:
        self.chapter = 1
        self.winner = None

        self.ambition_manager = AmbitionManager(self._event_bus)

        self.action_card_deck = ActionCardDeck(player_count=self._player_count)
        self.action_card_discard = ActionCardDiscard()

        # TODO(base): Remove this try/catch when we have actual court cards to put in. Add a sanity
        # check assertion to tests too.
        try:
            self.court = Court([], num_slots=4)
        except ValueError:
            pass

        # TODO(base): Allow setup card to be specified?
        setup_cards: Sequence[SetupCard]
        if self._player_count == 4:
            setup_cards = arcsync.setupcard.four_player_setup_cards
        elif self._player_count == 3:
            setup_cards = arcsync.setupcard.three_player_setup_cards
        # TODO(base2p): 2p setup cards.
        setup_card: SetupCard = random.choice(setup_cards)
        self.reach = Reach(setup_card)

        # Randomly assign player colors and initiative.
        # self.players = OrderedDict()
        # for color in random.sample(Color.values(), self._player_count):
        #    self.players[color] = Player(color)
        self.players = {
            color: Player(color) for color in random.sample(Color.values(), self._player_count)
        }
        self._turn_order = [color for color in self.players.keys()]
        self.initiative = self._turn_order[0]

        # TODO(base2p): Add 1 resource to the relevant ambition boxes for each out of play planet
        # (2p only).
        # TODO(L&L): perform draft.
        # TODO(base): Place pieces on the map according to setup card (or leader cards).
        # TODO(base): Each player gains the 2 resource tokens matching their A and B planets (or
        # leader card) into their leftmost and next leftmost slots.
        # TODO(L&L): perform extra leader setup in turn order.

        self.deal_starting_hands()

        # TODO(base2p): The player without initiative may mulligan their hand (2p only).

        self.discard_deck()

        self._end_setup()

    _end_setup: AnyFunc = s.SETUP.to(s.PLAY_A_ROUND)

    _to_chapter_end: AnyFunc = s.PLAY_A_ROUND.to(s.CHAPTER_END)

    @_to_chapter_end.cond  # type: ignore[misc, attr-defined]
    def _all_players_with_cards_have_passed_consecutively(self) -> bool:
        players_with_cards = {p.color for p in self.players.values() if p.hand}
        consecutively_passing_players: MutableSet[Color] = set()
        for r in reversed(self._rounds_this_chapter):
            if not isinstance(r._lead_play, PassInitiative):
                break
            consecutively_passing_players.add(r._lead_play.player)
        return players_with_cards == consecutively_passing_players

    _end_current_round: AnyFunc = _to_chapter_end | s.PLAY_A_ROUND.to(s.PLAY_A_ROUND)

    @s.CHAPTER_END.enter
    def _handle_chapter_end(self) -> None:
        self._score_ambitions()
        self.ambition_manager.clear()
        self.ambition_manager.most_valuable_available_marker.flip()
        self._end_game_or_go_to_next_chapter()

    _end_game: TransitionList = s.CHAPTER_END.to(s.GAME_END)

    @_end_game.cond
    def _game_is_ending(self) -> bool:
        return (
            self.chapter == 5
            or (
                self._player_count == 4
                and any(p.power >= Power(27) for p in self.players.values())
            )
            or (
                self._player_count == 3
                and any(p.power >= Power(30) for p in self.players.values())
            )
            or (
                self._player_count == 2
                and any(p.power >= Power(33) for p in self.players.values())
            )
        )

    _next_chapter: TransitionList = s.CHAPTER_END.to(s.PLAY_A_ROUND)

    @_next_chapter.on
    def _prepare_next_chapter(self) -> None:
        self.chapter += 1
        self.discard_all_player_hands()
        self.shuffle_discard_into_deck()
        self.deal_starting_hands()
        self.discard_deck()

    _end_game_or_go_to_next_chapter: AnyFunc = _end_game | _next_chapter

    @s.GAME_END.enter
    def determine_winner(self) -> None:
        max_power = max(p.power for p in self.players.values())
        for color in self.turn_order:
            if self.players[color].power == max_power:
                self.winner = color
                break

    def _discard_cards_played_this_round(self) -> None:
        discarded_cards = [play._card for play in self.round.card_plays]
        random.shuffle(discarded_cards)
        for card in discarded_cards:
            self.action_card_discard.put_on_top(card)

    # Managing the action card deck and discard

    def deal_action_cards(self, p: Player, num: int) -> None:
        p.hand.extend(self.action_card_deck.draw(num))

    def deal_starting_hands(self) -> None:
        for p in self.players.values():
            self.deal_action_cards(p, 6)

    def discard_deck(self) -> None:
        self.action_card_discard.add(self.action_card_deck.draw_all())

    def discard_all_player_hands(self) -> None:
        self.action_card_discard.add(self.action_card_deck.draw_all())
        for p in self.players.values():
            self.action_card_discard.add(p.hand)
            p.hand = []

    def shuffle_discard_into_deck(self) -> None:
        self.action_card_deck.add(self.action_card_discard.draw_all())

    # Control the player turn

    def lead(self, player: Color, card: ActionCard, ambition: Ambition | None = None) -> None:
        if card not in self.players[player].hand:
            raise ValueError(f"Cannot lead {card} because it is not in {player}'s hand.")
        self.round.begin_turn(Lead(player, card, ambition))
        self.players[player].hand.remove(card)

    def pass_initiative(self, player: Color) -> None:
        self.round.begin_turn(PassInitiative(player))

    def surpass(
        self,
        player: Color,
        card: ActionCard,
        seize_card: ActionCard | None = None,
    ) -> None:
        self._follow(Surpass, player, card, seize_card)

    def copy(
        self,
        player: Color,
        card: ActionCard,
        seize_card: ActionCard | None = None,
    ) -> None:
        self._follow(Copy, player, card, seize_card)

    def pivot(
        self,
        player: Color,
        card: ActionCard,
        seize_card: ActionCard | None = None,
    ) -> None:
        self._follow(Pivot, player, card, seize_card)

    def _follow(
        self,
        follow_type: type[Surpass] | type[Copy] | type[Pivot],
        player: Color,
        card: ActionCard,
        seize_card: ActionCard | None = None,
    ) -> None:
        if card not in self.players[player].hand:
            raise ValueError(f"Cannot follow with {card} because it is not in {player}'s hand.")
        if seize_card is not None and seize_card not in self.players[player].hand:
            raise ValueError(
                f"Cannot seize initiative with {card} because it is not in {player}'s hand."
            )
        self.round.begin_turn(follow_type(player, card, seize_card=seize_card))
        self.players[player].hand.remove(card)

    def cannot_follow_due_to_lack_of_cards(self, player: Color) -> None:
        self.round.begin_turn(CouldNotFollow(player))

    def end_prelude(self) -> None:
        self.round.end_prelude()

    def end_pips(self) -> None:
        self.round.end_pips()

    # Scoring

    def _score_ambitions(self) -> None:
        for ambition, markers in self.ambition_manager.boxes.items():
            if markers:
                self._score_ambition(ambition)

    def _score_ambition(self, ambition: Ambition) -> None:
        ranking = self._rank_players(ambition)
        for color, rank in ranking.items():
            if rank == 1:
                # TODO(base): publish that a player won a particular ambition.
                self.players[color].power += self.ambition_manager.first_place_value(ambition)
            elif rank == 2:
                self.players[color].power += self.ambition_manager.second_place_value(ambition)

    def _rank_players(self, ambition: Ambition) -> dict[Color, int]:
        ambition_counts = {
            color: player.count_for_ambition(ambition) for color, player in self.players.items()
        }

        # Players are only eligible to score for an ambition if they have at least 1 of the thing
        # the ambition wants.
        eligible_players = [color for color in self.players.keys() if ambition_counts[color] > 0]
        if not eligible_players:
            return dict()
        elif len(eligible_players) == 1:
            return {eligible_players[0]: 1}

        def key(player: Color) -> int:
            return ambition_counts[player]

        ranking = sorted(eligible_players, key=key, reverse=True)

        player_to_rank: dict[Color, int] = dict()
        left = 0
        right = 0
        current_rank = 1
        while right < len(ranking):
            # Seek right until we find either the end of the list, or the last player with the same
            # count towards the ambition.
            while (
                right + 1 < len(ranking)
                and ambition_counts[ranking[left]] == ambition_counts[ranking[right + 1]]
            ):
                right += 1
            if left == right:
                # If only one player has a unique count towards the ambition, their rank is the
                # current rank and the next player(s) are at least one rank lower.
                player_to_rank[ranking[left]] = current_rank
                left += 1
                right += 1
                current_rank += 1
            else:
                # If more one player shares count towards the ambition, they all have the rank
                # below the current rank.
                current_rank += 1
                for color in ranking[left : right + 1]:
                    player_to_rank[color] = current_rank
                left = right + 1
                right += 1
        return player_to_rank


if __name__ == "__main__":
    g = Game(player_count=4)
