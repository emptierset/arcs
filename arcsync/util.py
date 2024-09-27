"""For various utilities useful throughout ``arcsync``."""

from __future__ import annotations

import pprint
from collections.abc import Sequence
from typing import Any, NoReturn


# TODO(base): Update to Python 3.11 so we can just import this from typing.
def assert_never(value: NoReturn) -> NoReturn:
    assert False, f"Unhandled value: {value} ({type(value).__name__})"


class DunderDictEqMixin(object):
    """A mixin that implements ``__eq__`` via ``__dict__().__eq__``.

    An object with this mixed in will equate to other objects that share this mixin and have equal
    ``__dict__``\\s.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def __eq__(self, other: object) -> bool:
        if not issubclass(other.__class__, DunderDictEqMixin):
            return NotImplemented
        return self.__dict__ == other.__dict__


class DunderDictReprMixin(object):
    """A mixin implementing ``__repr__`` by dumping ``__dict__()``.

    Additionally, this ignores class attributes, since they (typically) do not change and are
    therefore uninteresting.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    # TODO(cleanup): Conditionally print newlines when pprint.pformat emits multiline output.
    # e.g., if pformat's output is simple, we can just emit it as we have here. If pformat's output
    # is multiline, then this code produces ugly output because the parens are on the same line as
    # the first and last values.
    def __repr__(self) -> str:
        instance_attrs = {k: v for k, v in self.__dict__.items() if not hasattr(self.__class__, k)}
        return f"{type(self).__name__}({pprint.pformat(instance_attrs)[1:-1]})"


class DunderDictReprTruncatedSequencesMixin(object):
    """A mixin implementing ``__repr__`` by dumping ``__dict__()`` with truncated sequences.

    Specifically, any instance attribute of type `Sequence
    <https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence>`_ with
    more than 1 element will be represented as such::

        ["foo", ... 4 more elements]

    Additionally, this ignores class attributes, since they (typically) do not change and are
    therefore uninteresting.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def __repr__(self) -> str:
        # This doesn't work if dataclasses were created in the "bare" manner, since it thinks all
        # of the dataclass' fields should be set, and crashes when they aren't.
        instance_attrs = {k: v for k, v in self.__dict__.items() if not hasattr(self.__class__, k)}

        items = []
        for k, v in instance_attrs.items():
            item = f"'{k}': "
            if isinstance(v, Sequence) and len(v) > 1:
                item += f"[{v[0]}, ... {len(v)-1} more elements]"
            else:
                item += f"{v}"
            items.append(item)

        item_string = ", ".join(items)
        return f"{type(self).__name__}({item_string})"


if __name__ == "__main__":
    pass
