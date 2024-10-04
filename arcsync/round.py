import enum
import typing
from collections.abc import MutableSequence, Sequence
from typing import Any, Callable, Final

from statemachine.transition_list import TransitionList

from arcsync.color import Color
from arcsync.event import AmbitionDeclaredEvent, InitiativeGainedEvent, RoundCompleteEvent
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

AnyFunc = Callable[..., Any]


# TODO(base): Should there be some sort of pre-CARD_PLAY step? I think PRESETUP works well in Game,
# even if the name is a little wonky, because it means we aren't barreling straight into a
# meaningful step during class initialization.
@typing.final
class Step(enum.Enum):
    CARD_PLAY = 1
    PRELUDE = 2
    PIPS = 3
    TURN_END = 4
    COMPLETE = 5


# TODO(base): Make some prettier print representation of this.
@typing.final
class Round(EnumStateMachine[Step]):
    turn_order: Final[Sequence[Color]]

    s = EnumStates[Step](Step, Step.CARD_PLAY, final=Step.COMPLETE)

    @s.PIPS.enter
    def initialize_pips_for_current_turn(self) -> None:
        self._pips_remaining = self.current_card_play.pips

    _next_turn: TransitionList = s.TURN_END.to(s.CARD_PLAY)

    @_next_turn.cond
    def _there_is_a_next_player_to_go_to(self) -> bool:
        return self.current_player != self._last_player

    @_next_turn.on
    def _increment_current_player_index(self) -> None:
        self._current_index_in_turn_order += 1

    _end_round: TransitionList = s.TURN_END.to(s.COMPLETE)

    _next_turn_or_end_round: AnyFunc = _next_turn | _end_round

    @s.TURN_END.enter
    def _consider_ending_the_round(self) -> None:
        self._next_turn_or_end_round()

    @s.COMPLETE.enter
    def _cleanup_round(self) -> None:
        if not self._seized:
            self._assign_initative_to_highest_surpass()
        self._event_bus.publish(RoundCompleteEvent())

    def _assign_initative_to_highest_surpass(self) -> None:
        highest_surpass = self._highest_surpass
        if highest_surpass is not None:
            self._event_bus.publish(InitiativeGainedEvent(highest_surpass.player))

    _lead: TransitionList = s.CARD_PLAY.to(
        s.PRELUDE,
        cond=lambda play: isinstance(play, Lead),
    )

    @_lead.on
    def _handle_lead(self, play: Lead) -> None:
        if play.ambition is not None:
            self._event_bus.publish(AmbitionDeclaredEvent(play.player, play.ambition))

    _pass_initiative: TransitionList = s.CARD_PLAY.to(
        s.COMPLETE,
        cond=lambda play: isinstance(play, PassInitiative),
    )

    @_pass_initiative.on
    def _publish_initiative_gained_for_next_player(self, play: PassInitiative) -> None:
        # TODO(base): This is technically wrong, because you pass initiative to the next player
        # _with cards_. It often doesn't really make a difference, but it can in certain
        # situations.
        self._event_bus.publish(InitiativeGainedEvent(self.next_player))

    _could_not_follow: TransitionList = s.CARD_PLAY.to(
        s.TURN_END,
        cond=lambda play: isinstance(play, CouldNotFollow),
    )

    _follow: TransitionList = s.CARD_PLAY.to(
        s.PRELUDE,
        cond=lambda play: isinstance(play, Follow),
    )

    @_follow.on
    def _seize_by_following(self, play: Follow) -> None:
        if not self._seized:
            if play.seize_card is not None or (isinstance(play, Surpass) and play.rank == 7):
                self._seize(play.player)

    _do_initiative_play: TransitionList = _lead | _pass_initiative

    @_do_initiative_play.on
    def _set_initiative_play(self, play: InitiativePlay) -> None:
        self._lead_play = play

    _do_non_initiative_play: TransitionList = _follow | _could_not_follow

    @_do_non_initiative_play.on
    def _append_non_initiative_play(self, play: NonInitiativePlay) -> None:
        self._non_initiative_plays.append(play)

    begin_turn: AnyFunc = _do_initiative_play | _do_non_initiative_play
    end_prelude: AnyFunc = s.PRELUDE.to(s.PIPS)
    end_pips: AnyFunc = s.PIPS.to(s.TURN_END)

    _current_index_in_turn_order: int
    # TODO(base): Make this public, because we are using it in Game now.
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
    def card_plays(self) -> list[ActionCardPlay]:
        if not isinstance(self._lead_play, ActionCardPlay):
            return []
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

    def __repr__(self) -> str:
        return (
            "Round("
            f"turn_order={self.turn_order},"
            f" _lead_play={self._lead_play},"
            f" _non_initiative_plays={self._non_initiative_plays})"
        )

    def _seize(self, player: Color) -> None:
        self._event_bus.publish(InitiativeGainedEvent(player))
        self._seized = True

    # Validation

    @_lead.validators
    @_pass_initiative.validators
    @_could_not_follow.validators
    @_follow.validators
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


if __name__ == "__main__":  # pragma: no cover
    pass
