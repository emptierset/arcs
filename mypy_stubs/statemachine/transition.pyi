# from .callbacks import (
#    CallbackGroup as CallbackGroup,
#    CallbackPriority as CallbackPriority,
#    CallbackSpecList as CallbackSpecList,
# )
# from .event import same_event_cond_builder as same_event_cond_builder
# from .events import Events as Events
# from .exceptions import InvalidDefinition as InvalidDefinition
# from _typeshed import Incomplete

from typing import Any

def __getattr__(name: str) -> Any: ...

class Transition:
    pass
    # source: Incomplete
    # target: Incomplete
    # internal: Incomplete
    # validators: Incomplete
    # before: Incomplete
    # on: Incomplete
    # after: Incomplete
    # cond: Incomplete
    # def __init__(
    #    self,
    #    source,
    #    target,
    #    event: Incomplete | None = None,
    #    internal: bool = False,
    #    validators: Incomplete | None = None,
    #    cond: Incomplete | None = None,
    #    unless: Incomplete | None = None,
    #    on: Incomplete | None = None,
    #    before: Incomplete | None = None,
    #    after: Incomplete | None = None,
    # ) -> None: ...
    # def match(self, event: str): ...
    # @property
    # def event(self): ...
    # @property
    # def events(self): ...
    # def add_event(self, value) -> None: ...
