import abc
import dataclasses
import enum
import typing
from collections.abc import Mapping, MutableSequence, Sequence
from typing import Final, Protocol

from arcsync.actioncard import ActionCard, Rank, Suit
from arcsync.ambition import Ambition
from arcsync.color import Color
from arcsync.event import AmbitionDeclaredEvent, InitiativeGainedEvent
from arcsync.eventbus import EventBus
from arcsync.util import DunderDictReprMixin

rank_from_ambition: Final[Mapping[Ambition, Rank]] = {
    Ambition.TYCOON: 2,
    Ambition.EDENGUARD: 2,
    Ambition.TYRANT: 3,
    Ambition.WARLORD: 4,
    Ambition.KEEPER: 5,
    Ambition.EMPATH: 6,
    Ambition.BLIGHTKIN: 6,
}


@typing.final
class Phase(enum.Enum):
    CARD_PLAY = enum.auto()
    PRELUDE = enum.auto()
    PIPS = enum.auto()


@typing.runtime_checkable
class ActionCardPlay(Protocol):
    @property
    def player(self) -> Color: ...

    @property
    def suit(self) -> Suit | None: ...

    @property
    def rank(self) -> Rank | None: ...

    @property
    def pips(self) -> int: ...


@dataclasses.dataclass(frozen=True)
class Play(object, metaclass=abc.ABCMeta):
    player: Color


@dataclasses.dataclass(frozen=True)
class InitiativePlay(Play, metaclass=abc.ABCMeta):
    pass


@typing.final
@dataclasses.dataclass(frozen=True)
class Lead(InitiativePlay):
    _card: ActionCard
    ambition: Ambition | None = None
    zero_token_placed: bool = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        # This is sort of a hack to set attributes even though the dataclass is frozen. This is OK
        # because it's in __post_init__, so it's basically still construction.
        object.__setattr__(self, "zero_token_placed", self.ambition is not None)

        if self.ambition is not None:
            if self._card.rank == 1:
                raise ValueError("Cannot declare any ambition by leading a 1.")
            if self._card.rank != 7:
                expected_rank = rank_from_ambition[self.ambition]
                if self._card.rank != expected_rank:
                    raise ValueError(
                        f"Cannot declare {self.ambition} because you did not lead a 7 or a"
                        f" {expected_rank}; you led a {self._card.rank}"
                    )

    # TODO(base): This returns | None to structurally agree with Follow, but is that
    # evil? This will never actually return None for any InitiativePlay.
    @property
    def suit(self) -> Suit | None:
        return self._card.suit

    # TODO(base): This returns | None to structurally agree with Follow, but is that
    # evil? This will never actually return None for any InitiativePlay.
    @property
    def rank(self) -> Rank | None:
        return 0 if self.zero_token_placed else self._card.rank

    @property
    def pips(self) -> int:
        return self._card.pips


@typing.final
@dataclasses.dataclass(frozen=True)
class PassInitiative(InitiativePlay):
    pass


@dataclasses.dataclass(frozen=True)
class NoInitiativePlay(Play, metaclass=abc.ABCMeta):
    pass


@typing.final
@dataclasses.dataclass(frozen=True)
class CouldNotFollow(NoInitiativePlay):
    pass


@dataclasses.dataclass(frozen=True)
class Follow(NoInitiativePlay, metaclass=abc.ABCMeta):
    _card: ActionCard
    _: dataclasses.KW_ONLY
    seize_card: ActionCard | None = None

    @property
    @abc.abstractmethod
    def suit(self) -> Suit | None: ...

    @property
    @abc.abstractmethod
    def rank(self) -> Rank | None: ...

    @property
    @abc.abstractmethod
    def pips(self) -> int: ...

    @property
    @abc.abstractmethod
    def is_face_up(self) -> bool: ...


@typing.final
@dataclasses.dataclass(frozen=True)
class Surpass(Follow):
    @property
    def suit(self) -> Suit | None:
        return self._card.suit

    @property
    def rank(self) -> Rank | None:
        return self._card.rank

    @property
    def pips(self) -> int:
        return self._card.pips

    @property
    def is_face_up(self) -> bool:
        return True


@typing.final
@dataclasses.dataclass(frozen=True)
class Copy(Follow):
    @property
    def suit(self) -> Suit | None:
        return None

    @property
    def rank(self) -> Rank | None:
        return None

    @property
    def pips(self) -> int:
        return 1

    @property
    def is_face_up(self) -> bool:
        return False


@typing.final
@dataclasses.dataclass(frozen=True)
class Pivot(Follow):
    @property
    def suit(self) -> Suit | None:
        return self._card.suit

    @property
    def rank(self) -> Rank | None:
        return self._card.rank

    @property
    def pips(self) -> int:
        return 1

    @property
    def is_face_up(self) -> bool:
        return True


# TODO(campaign): "Mirror" (?), for event cards.


# TODO(base): Make some prettier print representation of this.
# TODO(base): It's possible that a round or a player turn (or both?) should be a StateMachine,
# using python-statemachine. If so, certain methods or properties can just only work in certain
# states.
@typing.final
class Round(DunderDictReprMixin):
    turn_order: Final[Sequence[Color]]

    _phase: Phase | None
    _current_index_in_turn_order: int | None
    _lead_play: InitiativePlay | None
    _following_plays: Final[MutableSequence[NoInitiativePlay]]
    _pips_remaining: int | None
    _seized: bool
    _complete: bool
    _event_bus: Final[EventBus]

    @property
    def complete(self) -> bool:
        return self._complete

    @property
    def phase(self) -> Phase:
        if self._phase is None:
            raise ValueError("Not currently in any phase; maybe the round is complete?")
        return self._phase

    @property
    def current_player(self) -> Color:
        if self._current_index_in_turn_order is None:
            raise ValueError("There is no current player; maybe the round is complete?")
        return self.turn_order[self._current_index_in_turn_order]

    @property
    def next_player(self) -> Color:
        if self._current_index_in_turn_order is None:
            raise ValueError("There is no next player; maybe the round is complete?")
        return self.turn_order[(self._current_index_in_turn_order + 1) % len(self.turn_order)]

    @property
    def lead_card_play(self) -> ActionCardPlay:
        if self._lead_play is None:
            raise ValueError("No lead card play exists before anything is played.")
        if not isinstance(self._lead_play, Lead):
            raise ValueError(f"Lead play ({self._lead_play}) isn't a card play.")
        return self._lead_play

    @property
    def current_card_play(self) -> ActionCardPlay:
        if not isinstance(self.current_play, ActionCardPlay):
            raise ValueError(f"Current play ({self.current_play}) is not a card play.")
        return self.current_play

    @property
    def current_play(self) -> Play:
        if self._lead_play is None:
            raise ValueError("There cannot be a current play if there isn't even a lead play.")
        if self.current_player != self._first_player and len(self._following_plays) == 0:
            raise ValueError(
                "There cannot be a current play if there are no following plays and the current"
                f" player ({self.current_player}) did not start with initaitive."
            )
        if self.current_player == self._first_player:
            return self._lead_play
        else:
            return self._following_plays[-1]

    @property
    def pips_remaining(self) -> int:
        if self._pips_remaining is None:
            raise ValueError(
                f"Pips are not currently being tracked; maybe the phase ({self.phase}) isn't"
                " Phase.PIPS?"
            )
        return self._pips_remaining

    @property
    def _first_player(self) -> Color:
        return self.turn_order[0]

    @property
    def _last_player(self) -> Color:
        return self.turn_order[-1]

    def __init__(
        self,
        turn_order: Sequence[Color],
        event_bus: EventBus | None = None,
    ) -> None:
        self.turn_order = turn_order

        self._seized = False
        self._complete = False
        self._phase = Phase.CARD_PLAY
        self._current_index_in_turn_order = 0
        self._lead_play = None
        self._following_plays = []
        self._pips_remaining = None

        # For convenience, if you are unit testing one component and don't need an event bus, you
        # can skip it. One will be created, but it won't be very useful because it won't be linked
        # to anything else.
        if event_bus is None:
            event_bus = EventBus()
        self._event_bus = event_bus

    def begin_turn(self, play: Play) -> None:
        if self._complete:
            raise ValueError("Cannot begin a turn because the round is over.")
        if play.player != self.current_player:
            raise ValueError(
                f"Cannot begin a turn because it is not {play.player}'s turn; current player is"
                f" {self.current_player}."
            )
        if self.phase != Phase.CARD_PLAY:
            raise ValueError(
                "Cannot begin a turn because it is not the card play phase; current phase is"
                f" {self.phase}."
            )
        match play:
            case Lead():
                self._handle_lead(play)
            case PassInitiative():
                self._handle_pass_initiative(play)
            case CouldNotFollow():
                self._handle_could_not_follow(play)
            case Follow():
                self._handle_follow(play)
            case _:  # pragma: no cover
                raise ValueError(f"Unhandled subclass of `Play`: {type(play)}.")
        ###################################
        # Mutative logic below this line. #
        ###################################
        self._phase = Phase.PRELUDE

    def _handle_lead(self, play: Lead) -> None:
        if play.player != self._first_player:
            raise ValueError(
                f"Cannot lead because {play.player} did not start with initiative this round;"
                f" {self._first_player} started with initiative."
            )
        ###################################
        # Mutative logic below this line. #
        ###################################
        if play.ambition is not None:
            self._event_bus.publish(AmbitionDeclaredEvent(play.player, play.ambition))
        self._lead_play = play

    def _handle_pass_initiative(self, play: PassInitiative) -> None:
        if play.player != self._first_player:
            raise ValueError(
                f"Cannot pass initiative because {play.player} did not start with initiative this"
                f" round; {self._first_player} started with initiative."
            )
        ###################################
        # Mutative logic below this line. #
        ###################################
        self._event_bus.publish(InitiativeGainedEvent(self.next_player))
        self._lead_play = play
        self._end_round()

    def _handle_could_not_follow(self, play: CouldNotFollow) -> None:
        # We can't actually validate this from here, because we don't have a reference to the
        # player's hand, only their color. Is that a problem? Probably not, because there won't
        # ever be a "I can't follow" button -- it is always mandatory when a player can do it, and
        # never possible when they cannot.
        ###################################
        # Mutative logic below this line. #
        ###################################
        self._following_plays.append(play)
        # TODO(base): Is it a problem if players who have no cards technically begin a turn and
        # then end it? As opposed to being skipped entirely?
        self._end_turn()

    def _handle_follow(self, play: Follow) -> None:
        self._validate_follow(play)
        ###################################
        # Mutative logic below this line. #
        ###################################
        if play.seize_card is not None:
            self._event_bus.publish(InitiativeGainedEvent(play.player))
            self._seized = True
        # TODO(base): Handle autoseize by 7.
        # TODO(base): Is there a way to share the append logic to CouldNotFollow? If so, delete the
        # duplicate unit tests and centralize.
        self._following_plays.append(play)

    def _validate_follow(self, play: Follow) -> None:
        if play.player == self._first_player:
            raise ValueError(
                f"{play.player} cannot follow because {play.player} started with initiative this"
                " round."
            )
        # TODO(campaign): Validate that event cards are not played face down or discarded.
        if play.seize_card is not None and self._seized:
            raise ValueError(
                f"{play.player} cannot seize initiative because it was already seized by"
                f" {play.player} this round."
            )
        match play:
            case Surpass():
                self._validate_surpass(play)
            case Copy():
                # TODO(campaign): Validate that event cards are not played face down or discarded.
                pass
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

    def _validate_pivot(self, play: Pivot) -> None:
        if play.suit == self.lead_card_play.suit:
            raise ValueError(
                f"Cannot pivot because played card's suit ({play.suit}) matches lead card's suit"
                f" ({self.lead_card_play.suit})."
            )

    def end_prelude(self) -> None:
        if self._complete:
            raise ValueError("Cannot end prelude because the round is over.")
        if self.phase != Phase.PRELUDE:
            raise ValueError(f"Can only end prelude while in prelude, not {self.phase}.")
        ###################################
        # Mutative logic below this line. #
        ###################################
        self._pips_remaining = self.current_card_play.pips
        self._phase = Phase.PIPS

    def end_pips_phase(self) -> None:
        if self._complete:
            raise ValueError("Cannot end pips phase because the round is over.")
        if self.phase != Phase.PIPS:
            raise ValueError(f"Can only end pips phase while in pips phase, not {self.phase}.")
        if self.current_player == self._last_player:
            self._end_round()
        else:
            self._end_turn()
        ###################################
        # Mutative logic below this line. #
        ###################################

    def _end_turn(self) -> None:
        is_pips_phase = self.phase == Phase.PIPS
        if not is_pips_phase:
            try:
                current_play = self.current_play
            except ValueError:
                current_play = None
            current_player_had_empty_hand = self.phase == Phase.CARD_PLAY and isinstance(
                current_play, CouldNotFollow
            )
            if not current_player_had_empty_hand:
                raise ValueError(
                    f"Can only end turn from the pips phase (not {self.phase}), or by having no"
                    " action cards when expected to follow."
                )
        if self.current_player == self._last_player:
            self._end_round()
            return
        ###################################
        # Mutative logic below this line. #
        ###################################
        # Assert is safe because _current_index_in_turn_order is only None when the round is
        # complete.
        assert self._current_index_in_turn_order is not None
        self._current_index_in_turn_order += 1
        self._pips_remaining = None
        self._phase = Phase.CARD_PLAY

    def _end_round(self) -> None:
        is_pips_phase_of_last_player = (
            self.phase == Phase.PIPS and self.current_player == self._last_player
        )
        first_played_just_passed = (
            self.phase == Phase.CARD_PLAY and self.current_player == self._first_player
        )
        if not is_pips_phase_of_last_player and not first_played_just_passed:
            raise ValueError(
                "Can only end round if the first player passes, or from the pips phase of the"
                f" last player in turn order ({self._last_player}), not {self.current_player}."
            )
        ###################################
        # Mutative logic below this line. #
        ###################################
        self._pips_remaining = None
        self._phase = None
        self._current_index_in_turn_order = None
        self._complete = True


if __name__ == "__main__":
    pass
