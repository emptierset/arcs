import enum
import typing


# TODO(base): This should probably be PlayerColor, and maybe it can go back to player.py with
# typing.TYPE_CHECKING guards. If we do that, rename all `color` and `player` fields to
# `player_color`.
@typing.final
class Color(enum.Enum):
    RED = enum.auto()
    BLUE = enum.auto()
    YELLOW = enum.auto()
    WHITE = enum.auto()


if __name__ == "__main__":
    pass
