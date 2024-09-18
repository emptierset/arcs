import collections
import typing
from collections.abc import MutableSequence
from typing import Callable, Final, MutableMapping, TypeVar

from arcsync.event import Event

EventT = TypeVar("EventT", bound=Event)


class EventBus(object):
    # Please do not manipulate `_subscriptions` manually -- it is not typesafe to do so!
    _subscriptions: Final[MutableMapping[type[Event], MutableSequence[Callable[[Event], None]]]]

    def __init__(self) -> None:
        self._subscriptions = collections.defaultdict(list)

    # TODO(base): Is it necessary to be able to unsubscribe? If, so, how? Maybe some sort of
    # subscription ID?
    def subscribe(self, event_type: type[EventT], callback: Callable[[EventT], None]) -> None:
        # Callbacks that you pass to `subscribe` must not mutate the event they are called on.
        # Otherwise, the order that subscribers process the event matters, which is a nightmare
        # that we don't want to get into.

        # There doesn't appear to be any way to enforce a type variable relationship between
        # the keys and values of `_subscriptions`, so we need a cast to assert that the callback
        # has the right type to be contained in the list of callbacks for this event type.
        #
        # Note that, as long as `_subscriptions` is only manipulated using `subscribe`, this is
        # still typesafe because `subscribe` is typesafe.
        casted_callback = typing.cast(Callable[[Event], None], callback)
        self._subscriptions[event_type].append(casted_callback)

    def publish(self, event: Event) -> None:
        try:
            callbacks = self._subscriptions[type(event)]
        except KeyError:
            return
        for callback in callbacks:
            callback(event)


if __name__ == "__main__":
    pass
