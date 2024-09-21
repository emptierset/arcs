import enum
import typing
from collections.abc import Mapping, MutableSet
from typing import Final, NewType

from arcsync.color import Color
from arcsync.event import AmbitionDeclaredEvent
from arcsync.eventbus import EventBus
from arcsync.util import DunderDictReprMixin


@typing.final
class Ambition(enum.Enum):
    TYCOON = 2
    EDENGUARD = 2.5
    TYRANT = 3
    WARLORD = 4
    KEEPER = 5
    EMPATH = 6
    BLIGHTKIN = 6.5


Power = NewType("Power", int)


# TODO(base): We may need to keep track of whether there was an ambition declared this round, for
# things like Galactic Bards. That may get tracked here, or somewhere else.
@typing.final
class AmbitionMarker(DunderDictReprMixin):
    value: Power

    _front: Final[Power]
    _back: Final[Power]

    def __init__(self, *, front: Power, back: Power, starts_on_back: bool = False):
        self.value = back if starts_on_back else front
        self._front = front
        self._back = back

    def flip(self) -> None:
        if self.value == self._front:
            self.value = self._back
        else:
            self.value = self._front


@typing.final
class AmbitionManager(DunderDictReprMixin):
    available_markers: MutableSet[AmbitionMarker]
    boxes: Final[Mapping[Ambition, MutableSet[AmbitionMarker]]]

    _event_bus: Final[EventBus]

    def __init__(self, event_bus: EventBus | None = None) -> None:
        super().__init__()
        self.available_markers = set(
            [
                AmbitionMarker(front=Power(5), back=Power(9)),
                # TODO(base): How many points is the back? 2?
                AmbitionMarker(front=Power(3), back=Power(100)),
                AmbitionMarker(front=Power(2), back=Power(0)),
            ]
        )
        self.boxes = {
            Ambition.TYCOON: set(),
            Ambition.TYRANT: set(),
            Ambition.WARLORD: set(),
            Ambition.KEEPER: set(),
            Ambition.EMPATH: set(),
        }

        # For convenience, if you are unit testing one component and don't need an event bus, you
        # can skip it. One will be created, but it won't be very useful because it won't be linked
        # to anything else.
        if event_bus is None:
            event_bus = EventBus()
        self._event_bus = event_bus
        self.initialize_event_handlers()

    def initialize_event_handlers(self) -> None:
        pass

    def declare(self, player: Color, ambition: Ambition) -> None:
        if not self.available_markers:
            raise ValueError("Cannot declare ambition without available ambition marker.")
        am: AmbitionMarker = self._pop_most_valuable_available_marker()
        self.boxes[ambition].add(am)
        self._event_bus.publish(AmbitionDeclaredEvent(player, ambition))

    def value_of(self, ambition: Ambition) -> Power:
        return Power(sum(marker.value for marker in self.boxes[ambition]))

    def clear(self) -> None:
        for markers in self.boxes.values():
            self.available_markers |= markers
            markers.clear()

    @property
    def most_valuable_available_marker(self) -> AmbitionMarker | None:
        if not self.available_markers:
            return None
        return max(self.available_markers, key=lambda m: m.value)

    def _pop_most_valuable_available_marker(self) -> AmbitionMarker:
        am: AmbitionMarker | None = self.most_valuable_available_marker
        if am is None:
            raise ValueError("Cannot pop empty set of ambition markers.")
        self.available_markers.remove(am)
        return am


if __name__ == "__main__":
    pass
