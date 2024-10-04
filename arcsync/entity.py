import enum
import typing

from arcsync.color import Color


@typing.final
class NonPlayerEntity(enum.Enum):
    EMPIRE = 1
    BLIGHT = 2


Entity = Color | NonPlayerEntity


if __name__ == "__main__":  # pragma: no cover
    pass
