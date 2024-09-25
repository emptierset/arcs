# from .exceptions import AttrNotFound as AttrNotFound
# from .i18n import _ as _
# from .utils import ensure_iterable as ensure_iterable
# from _typeshed import Incomplete
# from enum import IntEnum, IntFlag
# from typing import Callable, Generator, Iterable, Any, Literal

from typing import Any

def __getattr__(name: str) -> Any: ...

# class CallbackPriority(IntEnum):
#    GENERIC = 0
#    INLINE = 10
#    DECORATOR = 20
#    NAMING = 30
#    AFTER = 40
#
# class SpecReference(IntFlag):
#    NAME = ...
#    CALLABLE = ...
#    PROPERTY = ...
#
# SPECS_ALL: Incomplete
# SPECS_SAFE: Incomplete
#
# class CallbackGroup(IntEnum):
#    ENTER = ...
#    EXIT = ...
#    VALIDATOR = ...
#    BEFORE = ...
#    ON = ...
#    AFTER = ...
#    COND = ...
#    def build_key(self, specs: CallbackSpecList) -> str: ...
#
# def allways_true(*args: Any, **kwargs: Any) -> Literal[True]: ...
#
# class CallbackSpec:
#    func: Incomplete
#    group: Incomplete
#    is_convention: Incomplete
#    cond: Incomplete
#    expected_value: Incomplete
#    priority: Incomplete
#    reference: Incomplete
#    attr_name: Incomplete
#    is_bounded: Incomplete
#    def __init__(
#        self,
#        func,
#        group: CallbackGroup,
#        is_convention: bool = False,
#        cond: Incomplete | None = None,
#        priority: CallbackPriority = ...,
#        expected_value: Incomplete | None = None,
#    ) -> None: ...
#    def __eq__(self, other): ...
#    def __hash__(self): ...
#    def build(self, resolver) -> Generator["CallbackWrapper", None, None]: ...
#
# class SpecListGrouper:
#    list: Incomplete
#    group: Incomplete
#    factory: Incomplete
#    key: Incomplete
#    def __init__(self, list: CallbackSpecList, group: CallbackGroup, factory=...) -> None: ...
#    def add(self, callbacks, **kwargs): ...
#    def __call__(self, callback): ...
#    def __iter__(self): ...
#
# class CallbackSpecList:
#    items: Incomplete
#    conventional_specs: Incomplete
#    factory: Incomplete
#    def __init__(self, factory=...) -> None: ...
#    def __iter__(self): ...
#    def clear(self) -> None: ...
#    def grouper(
#        self, group: CallbackGroup, factory: type[CallbackSpec] = ...
#    ) -> SpecListGrouper: ...
#    def add(self, callbacks, group: CallbackGroup, **kwargs): ...
#
# class CallbackWrapper:
#    condition: Incomplete
#    meta: Incomplete
#    unique_key: Incomplete
#    expected_value: Incomplete
#    def __init__(
#        self, callback: Callable, condition: Callable, meta: CallbackSpec, unique_key: str
#    ) -> None: ...
#    def __lt__(self, other): ...
#    async def __call__(self, *args, **kwargs): ...
#    def call(self, *args, **kwargs): ...
#
# class CallbacksExecutor:
#    items: Incomplete
#    items_already_seen: Incomplete
#    def __init__(self) -> None: ...
#    def __iter__(self): ...
#    def add(self, items: Iterable[CallbackSpec], resolver: Callable): ...
#    async def async_call(self, *args, **kwargs): ...
#    async def async_all(self, *args, **kwargs): ...
#    def call(self, *args, **kwargs): ...
#    def all(self, *args, **kwargs): ...
#
# class CallbacksRegistry:
#    has_async_callbacks: bool
#    def __init__(self) -> None: ...
#    def clear(self) -> None: ...
#    def __getitem__(self, key: str) -> CallbacksExecutor: ...
#    def check(self, specs: CallbackSpecList): ...
#    def async_or_sync(self) -> None: ...
