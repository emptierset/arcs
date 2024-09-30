import typing

from arcsync.util import EnumerableEnum


# TODO(base): This should probably be PlayerColor, and maybe it can go back to player.py with
# typing.TYPE_CHECKING guards. If we do that, rename all `color` and `player` fields to
# `player_color`.
@typing.final
class Color(EnumerableEnum):
    RED = 1
    BLUE = 2
    YELLOW = 3
    WHITE = 4


if __name__ == "__main__":
    pass
