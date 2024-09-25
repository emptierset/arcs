import enum
import typing
from collections.abc import MutableSequence, Sequence
from typing import Any, Callable, Final, cast

from statemachine.transition_list import TransitionList

from arcsync.color import Color
from arcsync.event import AmbitionDeclaredEvent, InitiativeGainedEvent
from arcsync.eventbus import EventBus
from arcsync.helpers.enumstatemachine import EnumStateMachine, EnumStates
from arcsync.play import (
    ActionCardPlay,
    Copy,
    CouldNotFollow,
    Follow,
    InitiativePlay,
    Lead,
    NonInitiativePlay,
    PassInitiative,
    Pivot,
    Play,
    Surpass,
)
from arcsync.util import DunderDictReprMixin

AnyFunc = Callable[..., Any]

# DynamicallySetEvent is a TransitionList when defining the class, but is overridden by a function
# when the StateMachine metaclass is doing its thing. When a user is using the state machine, it is
# a function that sends the event described by the transition list.
# TODO(cleanup): Instead of AnyFunc, this could be a more specific type, based on which event is
# it. Basically, the parameters could be specified, rather than anything goes.
DynamicallySetEvent = TransitionList | AnyFunc


@typing.final
class Step(enum.Enum):
    CARD_PLAY = 1
    PRELUDE = 2
    PIPS = 3
    COMPLETE = 4


# TODO(base): Make some prettier print representation of this.
@typing.final
class Round(DunderDictReprMixin, EnumStateMachine[Step]):
    turn_order: Final[Sequence[Color]]

    s = EnumStates[Step](Step, Step.CARD_PLAY, final=Step.COMPLETE)

    # Validation

    def _validate_play(self, play: Play) -> None:
        if play.player != self.current_player:
            raise ValueError(
                f"Cannot begin a turn because it is not {play.player}'s turn; current player is"
                f" {self.current_player}."
            )
        match play:
            case InitiativePlay():
                self._validate_initiative_play(play)
            case NonInitiativePlay():
                self._validate_non_initiative_play(play)
            case _:  # pragma: no cover
                raise ValueError(f"Unhandled subclass of `Play`: {type(play)}.")

    def _validate_initiative_play(self, play: InitiativePlay) -> None:
        # TODO(campaign): You cannot lead event cards.
        if play.player != self._first_player:
            raise ValueError(
                f"{play.player} cannot perform an initiative play because"
                f" {self._first_player} started with initiative this round."
            )

    def _validate_non_initiative_play(self, play: NonInitiativePlay) -> None:
        if play.player == self._first_player:
            raise ValueError(
                f"{play.player} cannot perform a non-initiative play because they did not start"
                f" with initiative this round ({self._first_player} did)."
            )
        if isinstance(play, Follow):
            self._validate_follow(play)

    def _validate_follow(self, play: Follow) -> None:
        if play.seize_card is not None and self._seized:
            raise ValueError(
                f"{play.player} cannot seize initiative because it was already seized by"
                f" {play.player} this round."
            )
        # TODO(campaign): Validate that event cards are not played face down or discarded. There is
        # some new fourth mode for playing event cards.
        match play:
            case Surpass():
                self._validate_surpass(play)
            case Copy():
                self._validate_copy(play)
            case Pivot():
                self._validate_pivot(play)
            case _:  # pragma: no cover
                raise ValueError(f"Unhandled subclass of `Follow`: {type(play)}.")

    def _validate_surpass(self, play: Surpass) -> None:
        if play.suit != self.lead_card_play.suit:
            raise ValueError(
                f"Cannot surpass because played card's suit ({play.suit}) does not match lead"
                f" card's suit ({self.lead_card_play.suit})."
            )
        # TODO(base): Not happy with these asserts needing to exist. See the comments in `Lead` for
        # more details.
        assert self.lead_card_play.rank is not None
        assert play.rank is not None
        if play.rank <= self.lead_card_play.rank:
            raise ValueError(
                f"Cannot surpass because played card's rank ({play.rank}) does not exceed lead"
                f" card's rank ({self.lead_card_play.rank})."
            )

    def _validate_copy(self, play: Copy) -> None:
        # TODO(campaign): Validate that event cards are not played face down or discarded.
        pass

    def _validate_pivot(self, play: Pivot) -> None:
        if play.suit == self.lead_card_play.suit:
            raise ValueError(
                f"Cannot pivot because played card's suit ({play.suit}) matches lead card's suit"
                f" ({self.lead_card_play.suit})."
            )

    # State actions

    def on_enter_PIPS(self) -> None:
        self._pips_remaining = self.current_card_play.pips

    def on_enter_COMPLETE(self) -> None:
        if not self._seized:
            self._assign_initative_to_highest_surpass()

    def _assign_initative_to_highest_surpass(self) -> None:
        highest_surpass = self._highest_surpass
        if highest_surpass is not None:
            self._event_bus.publish(InitiativeGainedEvent(highest_surpass.player))

    # Events

    _lead: DynamicallySetEvent = s.CARD_PLAY.to(
        s.PRELUDE,
        cond=lambda play: isinstance(play, Lead),
        validators="_validate_play",
        on=["_handle_initiative_play", "_handle_lead"],
    )

    def _handle_initiative_play(self, play: InitiativePlay) -> None:
        self._lead_play = play

    def _handle_lead(self, play: Lead) -> None:
        if play.ambition is not None:
            self._event_bus.publish(AmbitionDeclaredEvent(play.player, play.ambition))

    _pass_initiative: DynamicallySetEvent = s.CARD_PLAY.to(
        s.COMPLETE,
        cond=lambda play: isinstance(play, PassInitiative),
        validators="_validate_play",
        on=["_handle_pass_initiative", "_handle_initiative_play"],
    )

    def _handle_pass_initiative(self, play: PassInitiative) -> None:
        # TODO(base): This is technically wrong, because you pass initiative to the next player
        # _with cards_. It often doesn't really make a difference, but it can in certain
        # situations.
        self._event_bus.publish(InitiativeGainedEvent(self.next_player))

    _could_not_follow: DynamicallySetEvent = s.CARD_PLAY.to(
        s.CARD_PLAY,
        cond=lambda play: isinstance(play, CouldNotFollow),
        validators="_validate_play",
        on="_handle_non_initiative_play",
        after="_end_turn",
    )

    def _handle_non_initiative_play(self, play: NonInitiativePlay) -> None:
        self._non_initiative_plays.append(play)

    _follow: DynamicallySetEvent = s.CARD_PLAY.to(
        s.PRELUDE,
        cond=lambda play: isinstance(play, Follow),
        validators="_validate_play",
        on=["_handle_non_initiative_play", "_handle_follow"],
    )

    def _handle_follow(self, play: Follow) -> None:
        if not self._seized:
            if play.seize_card is not None or (isinstance(play, Surpass) and play.rank == 7):
                self._event_bus.publish(InitiativeGainedEvent(play.player))
                self._seized = True

    _play_card: DynamicallySetEvent = cast(TransitionList, _lead) | cast(TransitionList, _follow)

    _begin_turn: DynamicallySetEvent = (
        cast(TransitionList, _could_not_follow)
        | cast(TransitionList, _pass_initiative)
        | cast(TransitionList, _play_card)
    )

    # Events for voluntarily ending steps.

    _next_turn: DynamicallySetEvent = (
        s.CARD_PLAY.to(s.CARD_PLAY) | s.PRELUDE.to(s.CARD_PLAY) | s.PIPS.to(s.CARD_PLAY)
    )

    @cast(TransitionList, _next_turn).cond
    def _there_is_a_next_player_to_go_to(self) -> bool:
        return self.current_player != self._last_player

    @cast(TransitionList, _next_turn).on
    def _increment_current_player_index(self) -> None:
        self._current_index_in_turn_order += 1

    _next_round: DynamicallySetEvent = (
        s.CARD_PLAY.to(s.COMPLETE) | s.PRELUDE.to(s.COMPLETE) | s.PIPS.to(s.COMPLETE)
    )
    _end_turn: DynamicallySetEvent = cast(TransitionList, _next_turn) | cast(
        TransitionList, _next_round
    )

    _end_prelude: DynamicallySetEvent = s.PRELUDE.to(s.PIPS)

    _end_pips: DynamicallySetEvent = s.PIPS.to(
        s.CARD_PLAY,
        after="_end_turn",
    )

    _current_index_in_turn_order: int
    _lead_play: InitiativePlay | None
    _non_initiative_plays: Final[MutableSequence[NonInitiativePlay]]
    _pips_remaining: int
    _seized: bool
    _event_bus: Final[EventBus]

    @property
    def _first_player(self) -> Color:
        return self.turn_order[0]

    @property
    def _last_player(self) -> Color:
        return self.turn_order[-1]

    @property
    def _non_lead_card_plays(self) -> list[ActionCardPlay]:
        return [p for p in self._non_initiative_plays if isinstance(p, ActionCardPlay)]

    @property
    def _highest_surpass(self) -> ActionCardPlay | None:
        highest_surpass: ActionCardPlay | None = None
        for p in self._non_lead_card_plays:
            if not isinstance(p, Surpass):
                continue
            # TODO(base): Not happy with these asserts needing to exist. See the comments in `Lead`
            # for more details.
            assert p.rank is not None
            # Assumption: it is never possible to surpass with a card of the same rank.
            if highest_surpass is None or (
                highest_surpass.rank is not None and highest_surpass.rank < p.rank
            ):
                highest_surpass = p
        return highest_surpass

    @property
    def complete(self) -> bool:
        return self.get_current_state_value() == Step.COMPLETE

    @property
    def step(self) -> Step:
        return self.get_current_state_value()

    @property
    def current_player(self) -> Color:
        if self.current_state_value == Step.COMPLETE:
            raise ValueError("There is no current player when the round is complete.")
        return self.turn_order[self._current_index_in_turn_order]

    @property
    def next_player(self) -> Color:
        return self.turn_order[(self._current_index_in_turn_order + 1) % len(self.turn_order)]

    @property
    def all_card_plays(self) -> list[ActionCardPlay]:
        return [self.lead_card_play] + self._non_lead_card_plays

    @property
    def lead_card_play(self) -> ActionCardPlay:
        if self._lead_play is None:
            raise ValueError("No lead card play exists before anything is played.")
        if not isinstance(self._lead_play, ActionCardPlay):
            raise ValueError(f"Lead play ({self._lead_play}) isn't a card play.")
        return self._lead_play

    @property
    def current_play(self) -> Play:
        if self.current_state_value == Step.COMPLETE:
            raise ValueError("There is no current play when the round is complete.")
        if self._lead_play is None:
            raise ValueError("There cannot be a current play if there isn't even a lead play.")
        if self.current_player != self._first_player and len(self._non_initiative_plays) == 0:
            raise ValueError(
                "There cannot be a current play if there are no following plays and the current"
                f" player ({self.current_player}) did not start with initaitive."
            )
        if self.current_player == self._first_player:
            return self._lead_play
        else:
            return self._non_initiative_plays[-1]

    @property
    def current_card_play(self) -> ActionCardPlay:
        if not isinstance(self.current_play, ActionCardPlay):
            raise ValueError(f"Current play ({self.current_play}) is not a card play.")
        return self.current_play

    @property
    def pips_remaining(self) -> int:
        if self.step != Step.PIPS:
            raise ValueError("pips_remaining only has meaning during the pips step.")
        return self._pips_remaining

    def __init__(
        self,
        turn_order: Sequence[Color],
        event_bus: EventBus | None = None,
    ) -> None:
        super().__init__()

        self.turn_order = turn_order
        self._seized = False
        self._current_index_in_turn_order = 0
        self._lead_play = None
        self._non_initiative_plays = []

        # For convenience, if you are unit testing one component and don't need an event bus, you
        # can skip it. One will be created, but it won't be very useful because it won't be linked
        # to anything else.
        if event_bus is None:
            event_bus = EventBus()
        self._event_bus = event_bus

    def _seize(self, player: Color) -> None:
        self._event_bus.publish(InitiativeGainedEvent(player))
        self._seized = True

    def begin_turn(self, play: Play) -> None:
        # TODO(cleanup): This has to exist so callers don't need to use `cast`. StateMachine does
        # some really hard to handle stuff during initialization...
        typing.cast(Callable[..., Any], self._begin_turn)(play)

    def end_prelude(self) -> None:
        typing.cast(Callable[..., Any], self._end_prelude)()

    def end_pips(self) -> None:
        typing.cast(Callable[..., Any], self._end_pips)()


if __name__ == "__main__":
    pass
