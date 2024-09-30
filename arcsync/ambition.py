import dataclasses
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


@dataclasses.dataclass(kw_only=True, frozen=True)
class AmbitionMarkerFace(object):
    first_place: Power
    second_place: Power


# TODO(base): We may need to keep track of whether there was an ambition declared this round, for
# things like Galactic Bards. That may get tracked here, or somewhere else.
@typing.final
class AmbitionMarker(DunderDictReprMixin):
    first_place: Power
    second_place: Power

    _front: Final[AmbitionMarkerFace]
    _back: Final[AmbitionMarkerFace]

    def __init__(
        self, *, front: AmbitionMarkerFace, back: AmbitionMarkerFace, starts_on_back: bool = False
    ):
        self.first_place = back.first_place if starts_on_back else front.first_place
        self.second_place = back.second_place if starts_on_back else front.second_place
        self._front = front
        self._back = back

    def flip(self) -> None:
        if self.first_place == self._front.first_place:
            self.first_place = self._back.first_place
        else:
            self.first_place = self._front.first_place
        if self.second_place == self._front.second_place:
            self.second_place = self._back.second_place
        else:
            self.second_place = self._front.second_place


@typing.final
class AmbitionManager(DunderDictReprMixin):
    available_markers: MutableSet[AmbitionMarker]
    boxes: Final[Mapping[Ambition, MutableSet[AmbitionMarker]]]

    _event_bus: Final[EventBus]

    def __init__(self, event_bus: EventBus | None = None) -> None:
        super().__init__()
        self.available_markers = set(
            [
                # TODO(base): Double check all of these numbers.
                AmbitionMarker(
                    front=AmbitionMarkerFace(first_place=Power(5), second_place=Power(100)),
                    back=AmbitionMarkerFace(first_place=Power(9), second_place=Power(100)),
                ),
                AmbitionMarker(
                    front=AmbitionMarkerFace(first_place=Power(3), second_place=Power(100)),
                    back=AmbitionMarkerFace(first_place=Power(100), second_place=Power(100)),
                ),
                AmbitionMarker(
                    front=AmbitionMarkerFace(first_place=Power(2), second_place=Power(0)),
                    back=AmbitionMarkerFace(first_place=Power(100), second_place=Power(100)),
                ),
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

        def handle_ambition_declared_event(event: AmbitionDeclaredEvent) -> None:
            self.declare(event.player, event.ambition)

        self._event_bus.subscribe(AmbitionDeclaredEvent, handle_ambition_declared_event)

    def declare(self, player: Color, ambition: Ambition) -> None:
        if not self.available_markers:
            raise ValueError("Cannot declare ambition without available ambition marker.")
        am: AmbitionMarker = self._pop_most_valuable_available_marker()
        self.boxes[ambition].add(am)
        # TODO(base): We need to use a different type of event for declaring an ambition, and
        # publishing that an ambition was declared. Using the same event causes recursion.
        # self._event_bus.publish(AmbitionDeclaredEvent(player, ambition))

    def first_place_value(self, ambition: Ambition) -> Power:
        return Power(sum(marker.first_place for marker in self.boxes[ambition]))

    def second_place_value(self, ambition: Ambition) -> Power:
        return Power(sum(marker.second_place for marker in self.boxes[ambition]))

    def clear(self) -> None:
        for markers in self.boxes.values():
            self.available_markers |= markers
            markers.clear()

    @property
    def most_valuable_available_marker(self) -> AmbitionMarker:
        if not self.available_markers:
            raise ValueError("There is no most valuable ambition marker when none is available.")
        return max(self.available_markers, key=lambda m: m.first_place)

    def _pop_most_valuable_available_marker(self) -> AmbitionMarker:
        am: AmbitionMarker | None = self.most_valuable_available_marker
        if am is None:
            raise ValueError("Cannot pop empty set of ambition markers.")
        self.available_markers.remove(am)
        return am


if __name__ == "__main__":
    pass
