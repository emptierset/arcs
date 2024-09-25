import abc
import dataclasses
import typing
from collections.abc import Mapping
from typing import Final, Protocol

from arcsync.actioncard import ActionCard, Rank, Suit
from arcsync.ambition import Ambition
from arcsync.color import Color

_rank_from_ambition: Final[Mapping[Ambition, Rank]] = {
    Ambition.TYCOON: 2,
    Ambition.EDENGUARD: 2,
    Ambition.TYRANT: 3,
    Ambition.WARLORD: 4,
    Ambition.KEEPER: 5,
    Ambition.EMPATH: 6,
    Ambition.BLIGHTKIN: 6,
}


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
        # This is a hack to set attributes even though the dataclass is frozen. This is OK because
        # it's in __post_init__, so it's basically still construction.
        object.__setattr__(self, "zero_token_placed", self.ambition is not None)

        self._validate_ambition()

    def _validate_ambition(self) -> None:
        if self.ambition is None:
            return

        if self._card.rank == 1:
            raise ValueError("Cannot declare any ambition by leading a 1.")

        expected_rank = _rank_from_ambition[self.ambition]
        if self._card.rank != expected_rank and self._card.rank != 7:
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
class NonInitiativePlay(Play, metaclass=abc.ABCMeta):
    pass


@typing.final
@dataclasses.dataclass(frozen=True)
class CouldNotFollow(NonInitiativePlay):
    pass


@dataclasses.dataclass(frozen=True)
class Follow(NonInitiativePlay, metaclass=abc.ABCMeta):
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
