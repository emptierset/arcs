import enum
import typing


@typing.final
class Resource(enum.Enum):
    MATERIAL = enum.auto()
    FUEL = enum.auto()
    WEAPON = enum.auto()
    RELIC = enum.auto()
    PSIONIC = enum.auto()


if __name__ == "__main__":
    pass
