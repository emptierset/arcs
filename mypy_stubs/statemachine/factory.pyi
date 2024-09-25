from . import registry as registry
from .event import Event as Event, trigger_event_factory as trigger_event_factory
from .exceptions import InvalidDefinition as InvalidDefinition
from .graph import (
    iterate_states_and_transitions as iterate_states_and_transitions,
    visit_connected_states as visit_connected_states,
)
from .i18n import _ as _
from .state import State as State
from .states import States as States
from .transition import Transition as Transition
from .transition_list import TransitionList as TransitionList
from _typeshed import Incomplete
from typing import Any

# from typing import Any
# def __getattr__(name: str) -> Any: ...

class StateMachineMetaclass(type):
    pass
    # def __init__(
    #    cls, name: str, bases: tuple[type], attrs: dict[str, Any], strict_states: bool = False
    # ) -> None: ...
    # def __getattr__(self, attribute: str) -> Any: ...
    # def add_inherited(cls, bases) -> None: ...
    # def add_from_attributes(cls, attrs): ...
    # def add_state(cls, id, state: State): ...
    # def add_event(cls, event, transitions: Incomplete | None = None): ...
    # @property
    # def events(self): ...
