import inspect
from types import FunctionType
from typing import Any, Callable


def nonstaticmethod(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to make a method nonstatic."""
    f._should_make_static = False  # type: ignore[attr-defined]
    return f


class Autostatic(type):
    """Decorate all instance methods (unless excluded) with @staticmethod."""

    def __new__(cls, clsname: str, bases: tuple[type, ...], dct: dict[str, Any]) -> type:
        for key, value in dct.items():
            if cls._should_make_static(key, value):
                dct[key] = staticmethod(value)
        return super().__new__(cls, clsname, bases, dct)

    def __setattr__(self, attr: str, value: Any) -> None:
        if self._should_make_static(attr, value):
            value = staticmethod(value)
        super().__setattr__(attr, value)

    @classmethod
    def _should_make_static(cls, key: str, value: Any) -> bool:
        return (
            not inspect.isclass(value)
            and isinstance(value, FunctionType)
            and getattr(value, "_should_make_static", True)
        )
