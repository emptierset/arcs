import enum
import typing

from arcsync.color import Color


@typing.final
class NonPlayerEntity(enum.Enum):
    EMPIRE = enum.auto()
    BLIGHT = enum.auto()


Entity = Color | NonPlayerEntity


if __name__ == "__main__":
    pass
