"""Test against the JSONPath Compliance Test Suite with nondeterminism enabled.

The CTS is a submodule located in /tests/cts. After a git clone, run
`git submodule update --init` from the root of the repository.
"""

import json
import operator
from dataclasses import dataclass
from typing import Any
from typing import List
from typing import Optional

import pytest

from jsonpath_rfc9535 import JSONPathEnvironment
from jsonpath_rfc9535 import JSONValue


@dataclass
class Case:
    name: str
    selector: str
    document: JSONValue = None
    result: Any = None
    results: Optional[List[Any]] = None
    invalid_selector: Optional[bool] = None


def cases() -> List[Case]:
    with open("tests/cts/cts.json", encoding="utf8") as fd:
        data = json.load(fd)
    return [Case(**case) for case in data["tests"]]


def valid_cases() -> List[Case]:
    return [case for case in cases() if not case.invalid_selector]


class MockEnv(JSONPathEnvironment):
    nondeterministic = True


@pytest.mark.parametrize("case", valid_cases(), ids=operator.attrgetter("name"))
def test_nondeterminism(case: Case) -> None:
    assert case.document is not None
    env = MockEnv()
    rv = env.find(case.selector, case.document).values()

    if case.results is not None:
        assert rv in case.results
    else:
        assert rv == case.result
