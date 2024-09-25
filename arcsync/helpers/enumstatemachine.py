import typing
from collections.abc import Collection
from enum import Enum
from typing import Any, Generic, TypeVar

from statemachine import StateMachine
from statemachine.states import States

EnumT = TypeVar("EnumT", bound=Enum)


# TODO(cleanup): Stop overusing typing.final. It should only be used if there is a specific reason
# not to subclass a class, not just by default. For example, this class should not be subclassed
# because __new__ is annotated as returned its own type, rather than Self, so subclasses might not
# return the right type from __new__. I'm not sure how to annotate Self[EnumT], since Self type
# "cannot have type arguments".
@typing.final
class EnumStates(States, Generic[EnumT]):
    def __new__(
        cls,
        enum_: type[EnumT],
        initial: EnumT,
        *args: Any,
        final: Collection[EnumT] | None = None,
        **kwargs: Any
    ) -> "EnumStates[EnumT]":
        return typing.cast(
            EnumStates[EnumT],
            States.from_enum(enum_, initial, final=final, use_enum_instance=True),
        )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class EnumStateMachine(StateMachine, Generic[EnumT]):
    s: EnumStates[EnumT]

    def get_current_state_value(self) -> EnumT:
        return typing.cast(EnumT, super().current_state_value)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
