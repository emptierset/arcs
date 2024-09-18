import enum
import typing
from typing import ClassVar, Final, Protocol

from arcsync.color import Color
from arcsync.entity import Entity
from arcsync.util import DunderDictReprMixin


@typing.final
class DamageState(enum.Enum):
    FRESH = enum.auto()
    DAMAGED = enum.auto()
    DESTROYED = enum.auto()


@typing.runtime_checkable
class DamageablePiece(Protocol):
    damage_state: DamageState

    @property
    def hits_to_damage(self) -> int: ...


class Piece(DunderDictReprMixin):
    pass


class MapPiece(Piece):
    pass


class PlayerPiece(Protocol):
    @property
    def loyalty(self) -> Color: ...


@typing.final
class Agent(Piece):
    loyalty: Final[Color]

    def __init__(self, loyalty: Color):
        self.loyalty = loyalty


@typing.final
class Ship(MapPiece):
    hits_to_damage: ClassVar[int] = 1

    loyalty: Final[Color]
    damage_state: DamageState

    def __init__(
        self,
        loyalty: Color,
        damage_state: DamageState = DamageState.FRESH,
    ):
        self.loyalty = loyalty
        self.damage_state = damage_state


class Building(MapPiece):
    hits_to_damage: ClassVar[int] = 1


class City(Building):
    loyalty: Final[Color]
    damage_state: DamageState

    def __init__(
        self,
        loyalty: Color,
        damage_state: DamageState = DamageState.FRESH,
    ):
        self.loyalty = loyalty
        self.damage_state = damage_state


class CloudCity(City):
    pass


@typing.final
class Starport(Building):
    loyalty: Final[Color]
    damage_state: DamageState

    def __init__(
        self,
        loyalty: Color,
        damage_state: DamageState = DamageState.FRESH,
    ):
        self.loyalty = loyalty
        self.damage_state = damage_state


def hit(culprit: Entity, p: DamageablePiece, *, num_hits: int = 1) -> None:
    if num_hits < p.hits_to_damage:
        return

    for _ in range(num_hits):
        match p:
            case DamageablePiece(damage_state=DamageState.FRESH):
                p.damage_state = DamageState.DAMAGED
            case DamageablePiece(damage_state=DamageState.DAMAGED):
                # TODO(base): Announce that entity hit a piece.
                p.damage_state = DamageState.DESTROYED
            case DamageablePiece(damage_state=DamageState.DESTROYED):
                # TODO(base): Announce that entity hit a piece.
                # TODO(base): Announce that entity destroyed a piece.
                break


if __name__ == "__main__":
    s1 = Ship(Color.BLUE)
    s2 = Ship(Color.BLUE, DamageState.DAMAGED)

    x: list[Ship] = [s1]
    y: list[MapPiece] = [s1]
    z: list[Piece] = [s1]

    a1 = Agent(Color.BLUE)

    d: DamageablePiece = s2
    ds: list[DamageablePiece] = [s2]

    bc = City(Color.BLUE)

    print(s1)
    hit(Color.BLUE, s1, num_hits=4)
    print(s1)
