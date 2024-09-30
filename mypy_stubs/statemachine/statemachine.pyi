from .callbacks import (
    CallbacksExecutor as CallbacksExecutor,
    CallbacksRegistry as CallbacksRegistry,
    SPECS_ALL as SPECS_ALL,
    SPECS_SAFE as SPECS_SAFE,
    SpecReference as SpecReference,
)
from .dispatcher import Listener as Listener, Listeners as Listeners
from .engines.async_ import AsyncEngine as AsyncEngine
from .engines.sync import SyncEngine as SyncEngine
from .event import Event as Event
from .event_data import TriggerData as TriggerData
from .exceptions import (
    InvalidDefinition as InvalidDefinition,
    InvalidStateValue as InvalidStateValue,
    TransitionNotAllowed as TransitionNotAllowed,
)
from .factory import StateMachineMetaclass as StateMachineMetaclass
from .graph import iterate_states_and_transitions as iterate_states_and_transitions
from .i18n import _ as _
from .model import Model as Model
from .state import State as State
from .utils import run_async_from_sync as run_async_from_sync
from _typeshed import Incomplete
from typing import Any, TypeVar, Generic
from enum import Enum

# from typing import Any
# def __getattr__(name: str) -> Any: ...

class StateMachine(metaclass=StateMachineMetaclass):
    pass
    # TransitionNotAllowed = TransitionNotAllowed
    # model: Model
    # state_field: str
    # start_value: Any
    # allow_event_without_transition: bool
    # def __init__(
    #    self,
    #    model: Model | None = None,
    #    state_field: str = "state",
    #    start_value: Any | None = None,
    #    rtc: bool = True,
    #    allow_event_without_transition: bool = False,
    #    listeners: list[object] | None = None,
    # ) -> None: ...
    # def activate_initial_state(self): ...
    # def __init_subclass__(cls, strict_states: bool = False): ...
    # def __getattr__(self, attribute: str) -> Any: ...
    # def __deepcopy__(self, memo): ...
    # def bind_events_to(self, *targets) -> None: ...
    # def add_observer(self, *observers): ...
    # def add_listener(self, *listeners): ...
    @property
    def current_state_value(self) -> Any: ...
    @current_state_value.setter
    def current_state_value(self, value: Any) -> None: ...
    @property
    def current_state(self) -> State: ...
    @current_state.setter
    def current_state(self, value: State) -> None: ...
    # def send(self, event: str, *args: Any, **kwargs: Any) -> None: ...
