import abc
import dataclasses
import enum
import typing
from collections.abc import Mapping, MutableSequence, Sequence
from typing import Final

from arcsync.actioncard import ActionCard, Rank
from arcsync.ambition import Ambition, AmbitionManager
from arcsync.color import Color
from arcsync.eventbus import EventBus
from arcsync.util import DunderDictReprMixin

ambition_to_rank: Final[Mapping[Ambition, Rank]] = {
    Ambition.TYCOON: 2,
    Ambition.EDENGUARD: 2,
    Ambition.TYRANT: 3,
    Ambition.WARLORD: 4,
    Ambition.KEEPER: 5,
    Ambition.EMPATH: 6,
    Ambition.BLIGHTKIN: 6,
}


class Turn(object, metaclass=abc.ABCMeta):
    pass


class HaveInitiativeTurn(Turn, metaclass=abc.ABCMeta):
    pass


@typing.final
@dataclasses.dataclass(frozen=True)
class Lead(HaveInitiativeTurn):
    card: ActionCard
    ambition: Ambition | None = None


@typing.final
@dataclasses.dataclass(frozen=True)
class PassInitiative(HaveInitiativeTurn):
    pass


@dataclasses.dataclass(frozen=True)
class Follow(Turn, metaclass=abc.ABCMeta):
    card: ActionCard
    _: dataclasses.KW_ONLY
    discarded_card_for_seize: ActionCard | None = None


@typing.final
@dataclasses.dataclass(frozen=True)
class Surpass(Follow):
    pass


@typing.final
@dataclasses.dataclass(frozen=True)
class Copy(Follow):
    pass


@typing.final
@dataclasses.dataclass(frozen=True)
class Pivot(Follow):
    pass


# TODO(campaign): Mirror, for event cards.


@typing.final
class Phase(enum.Enum):
    CARD_PLAY = enum.auto()
    PRELUDE = enum.auto()
    PIPS = enum.auto()
    END_OF_TURN = enum.auto()


@dataclasses.dataclass(frozen=True)
class Play(object, metaclass=abc.ABCMeta):
    player: Color


@typing.final
@dataclasses.dataclass(frozen=True)
class CouldNotFollow(Play):
    player: Color


@dataclasses.dataclass(frozen=True)
class ActionCardPlay(Play, metaclass=abc.ABCMeta):
    player: Color
    card: ActionCard


@typing.final
@dataclasses.dataclass(frozen=True)
class ActionCardLed(ActionCardPlay):
    player: Color
    card: ActionCard
    zero_token_placed: bool


@typing.final
@dataclasses.dataclass(frozen=True)
class ActionCardFollowed(ActionCardPlay):
    player: Color
    card: ActionCard
    _: dataclasses.KW_ONLY
    face_up: bool = True
    discarded_card_for_seize: ActionCard | None = None


@typing.final
class Round(DunderDictReprMixin):
    turn_order: Final[Sequence[Color]]

    current_phase: Phase
    lead_play: ActionCardLed | None
    following_plays: Final[MutableSequence[Play]]
    seized: Color | None

    pips_remaining: int | None

    round_complete: bool

    _current_player_turn_order_index: int

    _ambition_manager: Final[AmbitionManager]
    _event_bus: Final[EventBus]

    def __init__(
        self,
        turn_order: Sequence[Color],
        ambition_manager: AmbitionManager,
        event_bus: EventBus | None = None,
    ) -> None:
        self.turn_order = turn_order

        self.current_phase = Phase.CARD_PLAY
        self.lead_play = None
        self.following_plays = []
        self.seized = None

        self.pips_remaining = None

        self.round_complete = False

        self._current_player_turn_order_index = 0

        self._ambition_manager = ambition_manager

        # For convenience, if you are testing and don't need an event bus, you can skip it. One
        # will be created, but it won't be very useful because it won't be linked to anything else.
        if event_bus is None:
            event_bus = EventBus()
        self._event_bus = event_bus

    @property
    def starting_initiative(self) -> Color:
        return self.turn_order[0]

    @property
    def lead_card(self) -> ActionCard:
        if not self.lead_play:
            raise ValueError("No lead card exists before anything is played.")
        return self.lead_play.card

    @property
    def current_player(self) -> Color:
        return self.turn_order[self._current_player_turn_order_index]

    @property
    def current_play(self) -> ActionCardPlay:
        if self.current_phase == Phase.CARD_PLAY:
            raise ValueError(
                "There is no current play when the current player has not played yet."
            )
        if self.current_player == self.starting_initiative:
            # Cast is safe because we know we are past the first card play phase, which is the only
            # time self.lead_play is None.
            return typing.cast(ActionCardLed, self.lead_play)
        # Cast is safe because we know we are not in a turn
        # time self.lead_play is None.
        return typing.cast(ActionCardPlay, self.following_plays[-1])

    @property
    def number_of_plays_so_far(self) -> int:
        n = len(self.following_plays)
        if self.lead_play is not None:
            n += 1
        return n

    def advance_phase(self) -> None:
        match self.current_phase:
            case Phase.CARD_PLAY:
                self._advance_to_prelude()
            case Phase.PRELUDE:
                self._advance_to_pips()
            case Phase.PIPS:
                if self._current_player_turn_order_index + 1 == len(self.turn_order):
                    self.round_complete = True
                    return
                self._current_player_turn_order_index += 1
                self.current_phase = Phase.CARD_PLAY

    def _advance_to_prelude(self) -> None:
        if self._current_player_turn_order_index + 1 != self.number_of_plays_so_far:
            raise ValueError(
                f"Cannot advance phase without current player ({self.current_player}) " "playing."
            )
        self.current_phase = Phase.PRELUDE

    def _advance_to_pips(self) -> None:
        self.current_phase = Phase.PIPS
        self.pips_remaining = self.current_play.card.pips

    def lead(self, player: Color, turn_data: Lead) -> None:
        self._validate_turn(player)
        self._validate_lead(player, turn_data)

        # TODO(base): Secret Order fits in somehow.
        ambition_declared = turn_data.ambition is not None

        self.lead_play = ActionCardLed(player, turn_data.card, zero_token_placed=ambition_declared)

    def cannot_follow(self, player: Color) -> None:
        self._validate_turn(player)
        self.following_plays.append(CouldNotFollow(player))
        self.advance_phase()
        self.advance_phase()
        self.advance_phase()

    def follow(self, player: Color, turn_data: Follow) -> None:
        self._validate_turn(player)
        self._validate_follow(player, turn_data)

        match turn_data:
            case Surpass():
                self._validate_surpass(player, turn_data)
            case Copy():
                self._validate_copy(player, turn_data)
            case Pivot():
                self._validate_pivot(player, turn_data)
            case _:
                raise ValueError(f"Unhandled subclass of `Follow`: {type(turn_data)}.")

        if turn_data.discarded_card_for_seize is not None:
            # TODO(base): Announce seize.
            self.seized = player

        match turn_data:
            case Surpass():
                self._surpass(player, turn_data)
            case Copy():
                self._copy(player, turn_data)
            case Pivot():
                self._pivot(player, turn_data)
            case _:
                raise ValueError(f"Unhandled subclass of `Follow`: {type(turn_data)}.")

    def _surpass(self, player: Color, turn_data: Surpass) -> None:
        self._validate_surpass(player, turn_data)

        self.following_plays.append(
            ActionCardFollowed(
                player,
                turn_data.card,
                discarded_card_for_seize=turn_data.discarded_card_for_seize,
            )
        )
        # TODO(base): Autoseize with 7.

    def _copy(self, player: Color, turn_data: Copy) -> None:
        self._validate_copy(player, turn_data)

        self.following_plays.append(
            ActionCardFollowed(
                player,
                turn_data.card,
                face_up=False,
                discarded_card_for_seize=turn_data.discarded_card_for_seize,
            )
        )

    def _pivot(self, player: Color, turn_data: Pivot) -> None:
        self._validate_pivot(player, turn_data)

        self.following_plays.append(
            ActionCardFollowed(
                player,
                turn_data.card,
                discarded_card_for_seize=turn_data.discarded_card_for_seize,
            )
        )

    def _validate_turn(self, player: Color) -> None:
        if self.round_complete:
            raise ValueError("Cannot act because the round is over.")
        if player != self.current_player:
            raise ValueError(
                f"Cannot act because it is not {player}'s turn; "
                f"current player is {self.current_player}."
            )
        if self.current_phase != Phase.CARD_PLAY:
            raise ValueError(
                "Cannot act because it is not the card play phase; "
                f"current phase is {self.current_phase}."
            )

    def _validate_lead(self, player: Color, turn_data: Lead) -> None:
        if player != self.starting_initiative:
            raise ValueError(
                f"Cannot lead because {player} did not start with initative this round; "
                f"{self.starting_initiative} started with initiative."
            )
        if turn_data.ambition is not None:
            if turn_data.card.rank != 7:
                expected_rank: Final[Rank] = turn_data.card.rank
                if turn_data.card.rank != expected_rank:
                    raise ValueError(
                        f"Cannot declare {turn_data.ambition} because you did not lead a 7 or a "
                        f"{expected_rank}; you led a {turn_data.card.rank}"
                    )

    def _validate_follow(self, player: Color, turn_data: Follow) -> None:
        if player == self.starting_initiative:
            raise ValueError(
                f"{player} cannot follow because {player} started with initative this round."
            )
        # TODO(campaign): Validate that event cards are not played face down or discarded.
        if turn_data.discarded_card_for_seize is not None:
            if self.seized is not None:
                raise ValueError(
                    f"{player} cannot seize initiative because it was already seized by {player} "
                    "this round."
                )

    def _validate_surpass(self, player: Color, turn_data: Surpass) -> None:
        if turn_data.card.suit != self.lead_card.suit:
            raise ValueError(
                f"Cannot surpass because played card's suit ({turn_data.card.suit}) "
                f"does not match lead card's suit ({self.lead_card.suit})."
            )
        if turn_data.card.rank <= self.lead_card.rank:
            raise ValueError(
                f"Cannot surpass because played card's rank ({turn_data.card.rank}) "
                f"does not exceed lead card's rank ({self.lead_card.rank})."
            )

    def _validate_copy(self, player: Color, turn_data: Copy) -> None:
        pass

    def _validate_pivot(self, player: Color, turn_data: Pivot) -> None:
        if turn_data.card.suit == self.lead_card.suit:
            raise ValueError(
                f"Cannot pivot because played card's suit ({turn_data.card.suit}) "
                f"matches lead card's suit ({self.lead_card.suit})."
            )


if __name__ == "__main__":
    r = Round([Color.RED, Color.BLUE, Color.YELLOW], AmbitionManager())
