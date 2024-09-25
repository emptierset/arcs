# from .callbacks import (
#     CallbackSpec as CallbackSpec,
#     CallbackSpecList as CallbackSpecList,
#     SPECS_ALL as SPECS_ALL,
#     SpecReference as SpecReference,
# )
# from .signature import SignatureAdapter as SignatureAdapter
# from _typeshed import Incomplete
# from dataclasses import dataclass
# from typing import Any, Callable, Generator, Iterable

from typing import Any

def __getattr__(name: str) -> Any: ...

# @dataclass
# class Listener:
#     obj: object
#     all_attrs: set[str]
#     resolver_id: str
#     @classmethod
#     def from_obj(cls, obj, skip_attrs: Incomplete | None = None) -> Listener: ...
#     def __init__(self, obj, all_attrs, resolver_id) -> None: ...
#
# @dataclass
# class Listeners:
#     items: tuple[Listener, ...]
#     all_attrs: set[str]
#     @classmethod
#     def from_listeners(cls, listeners: Iterable["Listener"]) -> Listeners: ...
#     def resolve(
#         self, specs: CallbackSpecList, registry, allowed_references: SpecReference = ...
#     ): ...
#     def search(self, spec: CallbackSpec) -> Generator["Callable", None, None]: ...
#     def __init__(self, items, all_attrs) -> None: ...
#
# def callable_method(attribute, a_callable, resolver_id) -> Callable: ...
# def attr_method(attribute, obj, resolver_id) -> Callable: ...
# def event_method(attribute, func, resolver_id) -> Callable: ...
# def resolver_factory_from_objects(*objects: tuple[Any, ...]): ...
