import enum
import random
import typing
from collections import Counter
from typing import Final, NewType


@typing.final
class Symbol(enum.Enum):
    HIT = 1
    BUILDING_HIT = 2
    SELF_HIT = 3
    KEY = 4
    INTERCEPT = 5


Face = NewType("Face", Counter[Symbol])

Die = list[Face]


AssaultDie: Final[Die] = [
    Face(Counter({Symbol.HIT: 2})),
    Face(Counter({Symbol.HIT: 2, Symbol.SELF_HIT: 1})),
    Face(Counter({Symbol.HIT: 1, Symbol.SELF_HIT: 1})),
    Face(Counter({Symbol.HIT: 1, Symbol.SELF_HIT: 1})),
    Face(Counter({Symbol.HIT: 1, Symbol.INTERCEPT: 1})),
    Face(Counter()),
]


SkirmishDie: Final[Die] = [
    Face(Counter({Symbol.HIT: 1})),
    Face(Counter({Symbol.HIT: 1})),
    Face(Counter({Symbol.HIT: 1})),
    Face(Counter()),
    Face(Counter()),
    Face(Counter()),
]


RaidDie: Final[Die] = [
    Face(Counter({Symbol.KEY: 2, Symbol.INTERCEPT: 1})),
    Face(Counter({Symbol.KEY: 1, Symbol.SELF_HIT: 1})),
    Face(Counter({Symbol.KEY: 1, Symbol.BUILDING_HIT: 1})),
    Face(Counter({Symbol.SELF_HIT: 1, Symbol.BUILDING_HIT: 1})),
    Face(Counter({Symbol.SELF_HIT: 1, Symbol.BUILDING_HIT: 1})),
    Face(Counter({Symbol.INTERCEPT: 1})),
]


# TODO(campaign): Event dice


DicePool = Counter[Die]


RollResult = NewType("RollResult", Counter[Symbol])


@typing.overload
def roll(d: DicePool, /) -> RollResult: ...


@typing.overload
def roll(d: Die, /) -> RollResult: ...


def roll(d: DicePool | Die) -> RollResult:
    def roll_die(d: Die) -> RollResult:
        return RollResult(random.choice(d))

    def roll_dice_pool(dp: DicePool) -> RollResult:
        r = RollResult(Counter())
        for die, count in dp.items():
            for _ in range(count):
                r += roll(die)
        return r

    if isinstance(d, list):
        return roll_die(d)
    elif isinstance(d, Counter):
        return roll_dice_pool(d)
    else:
        raise TypeError


if __name__ == "__main__":
    pass
