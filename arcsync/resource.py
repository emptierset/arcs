import enum
import typing


@typing.final
class Resource(enum.Enum):
    MATERIAL = 1
    FUEL = 2
    WEAPON = 3
    RELIC = 4
    PSIONIC = 5


if __name__ == "__main__":
    pass
