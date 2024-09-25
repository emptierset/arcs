# from .i18n import _ as _
# from .state import State as State
# from _typeshed import Incomplete

from typing import Any

def __getattr__(name: str) -> Any: ...

# class StateMachineError(Exception): ...
# class InvalidDefinition(StateMachineError): ...
#
# class InvalidStateValue(InvalidDefinition):
#    value: str
#    def __init__(self, value: str, msg: str | None = None) -> None: ...
#
# class AttrNotFound(InvalidDefinition): ...
#
# class TransitionNotAllowed(StateMachineError):
#    event: str
#    state: State
#    def __init__(self, event: str, state: State) -> None: ...
