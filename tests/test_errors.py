from typing import Any
from typing import List

import pytest

from jsonpath_rfc9535 import JSONPathEnvironment
from jsonpath_rfc9535.exceptions import JSONPathRecursionError
from jsonpath_rfc9535.exceptions import JSONPathSyntaxError
from jsonpath_rfc9535.exceptions import JSONPathTypeError


@pytest.fixture()
def env() -> JSONPathEnvironment:
    return JSONPathEnvironment()


def test_unclosed_selection_list(env: JSONPathEnvironment) -> None:
    with pytest.raises(
        JSONPathSyntaxError, match=r"unclosed bracketed selection, line 1, column 5"
    ):
        env.compile("$[1,2")


def test_function_missing_param(env: JSONPathEnvironment) -> None:
    with pytest.raises(JSONPathTypeError):
        env.compile("$[?(length()==1)]")


def test_function_too_many_params(env: JSONPathEnvironment) -> None:
    with pytest.raises(JSONPathTypeError):
        env.compile("$[?(length(@.a, @.b)==1)]")


def test_non_singular_query_is_not_comparable(env: JSONPathEnvironment) -> None:
    with pytest.raises(JSONPathTypeError):
        env.compile("$[?@.* > 2]")


def test_recursive_data() -> None:
    class MockEnv(JSONPathEnvironment):
        nondeterministic = False

    env = MockEnv()
    query = "$..a"
    arr: List[Any] = []
    data: Any = {"foo": arr}
    arr.append(data)

    with pytest.raises(JSONPathRecursionError):
        env.find(query, data)


def test_low_recursion_limit() -> None:
    class MockEnv(JSONPathEnvironment):
        max_recursion_depth = 3

    env = MockEnv()
    query = "$..a"
    data = {"foo": [{"bar": [1, 2, 3]}]}

    with pytest.raises(JSONPathRecursionError):
        env.find(query, data)
