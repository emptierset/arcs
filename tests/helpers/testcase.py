import typing
from collections.abc import Mapping, Sequence

import _pytest
import pytest

Testcase = typing.NewType("Testcase", tuple[str, dict[str, typing.Any]])
AnonymousTestcase = typing.NewType("AnonymousTestcase", tuple[dict[str, typing.Any]])


def new(testname: str, **kwargs: typing.Any) -> Testcase:
    return Testcase((testname, kwargs))


def new_anonymous(**kwargs: typing.Any) -> AnonymousTestcase:
    return AnonymousTestcase((kwargs,))


def parametrize(
    param_names: Sequence[str],
    testcases: Sequence[Testcase | AnonymousTestcase],
    default_values: Mapping[str, typing.Any] | None = None,
) -> _pytest.mark.structures.MarkDecorator:
    deduped_param_names = set(param_names)
    if len(param_names) != len(deduped_param_names):
        raise ValueError(f"input params '{param_names}' must contain only unique params")

    _default_values = dict() if default_values is None else default_values
    param_names_with_default_values = set(_default_values.keys())
    if not param_names_with_default_values.issubset(deduped_param_names):
        raise ValueError("default_values keys must be a subset of param names")

    def testcase_to_pytest_param(
        tc: Testcase | AnonymousTestcase,
    ) -> _pytest.mark.structures.ParameterSet:
        if len(tc) == 2:
            testname, testcase_params = typing.cast(Testcase, tc)
            debugging_testname = testname
        elif len(tc) == 1:
            testname = None
            (testcase_params,) = typing.cast(AnonymousTestcase, tc)
            debugging_testname = "-".join(map(str, testcase_params.values()))
        else:
            raise ValueError(f"testcase {tc} has unhandled length")

        present_input_param_names = testcase_params.keys() | _default_values.keys()
        if present_input_param_names != deduped_param_names:
            missing_param_names = deduped_param_names.difference(present_input_param_names)
            raise ValueError(
                "all params in input params must be present in either default_values or the"
                f" testcase itself;\nThe testcase named '{debugging_testname}' is missing values"
                f" for the following params:\n{missing_param_names}"
            )

        param_values_in_order = []
        for param_name in param_names:
            try:
                param_value = testcase_params[param_name]
            except KeyError:
                param_value = _default_values[param_name]
            param_values_in_order.append(param_value)

        if testname is None:
            return pytest.param(*param_values_in_order)
        else:
            return pytest.param(*param_values_in_order, id=testname)

    param_name_list_joined = ",".join(param_names)
    pytest_params = [testcase_to_pytest_param(tc) for tc in testcases]
    return pytest.mark.parametrize(param_name_list_joined, pytest_params)
