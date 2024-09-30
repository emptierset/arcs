from .callbacks import (
    CallbackGroup as CallbackGroup,
    CallbackPriority as CallbackPriority,
    CallbackSpecList as CallbackSpecList,
    SpecListGrouper as SpecListGrouper,
)
from .exceptions import StateMachineError as StateMachineError
from .i18n import _ as _
from .statemachine import StateMachine as StateMachine
from .transition import Transition as Transition
from .transition_list import TransitionList as TransitionList
from enum import Enum
from typing import Any
from typing import TypeVar, Generic, Callable
from typing_extensions import ParamSpec
from collections.abc import Sequence, Iterable

P = ParamSpec("P")
T = TypeVar("T")

# from typing import Any
# def __getattr__(name: str) -> Any: ...

class State:
    pass
    # name: str
    value: Any
    # transitions: TransitionList
    # NOTE: `enter` and `exit` are of type SpecListGrouper during state initialization, but they
    # are decorating functions by the time our subclass is initialized.
    enter: Callable[[Callable[P, T]], Callable[P, T]]
    exit: Callable[[Callable[P, T]], Callable[P, T]]
    # def __init__(
    #    self,
    #    name: str = "",
    #    value: Any = None,
    #    initial: bool = False,
    #    final: bool = False,
    #    enter: Any = None,
    #    exit: Any = None,
    # ) -> None: ...
    # def __eq__(self, other): ...
    # def __hash__(self): ...
    # def __get__(self, machine, owner): ...
    # def __set__(self, instance, value) -> None: ...
    # def for_instance(self, machine: StateMachine, cache: dict["State", "State"]) -> State: ...
    # @property
    # def id(self) -> str: ...
    @property
    def to(self) -> Callable[..., Any]: ...
    # @property
    # def from_(self): ...
    # @property
    # def initial(self): ...
    # @property
    # def final(self): ...

class InstanceState(State):
    pass
    # def __eq__(self, other): ...
    # def __hash__(self): ...
    # def __init__(self, state: State, machine: StateMachine) -> None: ...
    # @property
    # def name(self): ...
    # @property
    # def value(self): ...
    # @property
    # def transitions(self): ...
    # @property
    # def enter(self): ...
    # @property
    # def exit(self): ...
    # @property
    # def initial(self): ...
    # @property
    # def final(self): ...
    # @property
    # def id(self) -> str: ...
    # @property
    # def is_active(self): ...
