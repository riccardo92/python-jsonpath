"""Test Python JSONPath against the JSONPath Compliance Test Suite.

The CTS is a submodule located in /tests/cts. After a git clone, run
`git submodule update --init` from the root of the repository.
"""

import json
import operator
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import List
from typing import Mapping
from typing import Optional
from typing import Sequence
from typing import Union

import pytest

import jsonpath


@dataclass
class Case:
    name: str
    selector: str
    document: Union[Mapping[str, Any], Sequence[Any], None] = None
    result: Any = None
    results: Optional[List[Any]] = None
    invalid_selector: Optional[bool] = None


SKIP: Dict[str, str] = {}


def cases() -> List[Case]:
    with open("tests/cts/cts.json", encoding="utf8") as fd:
        data = json.load(fd)
    return [Case(**case) for case in data["tests"]]


def valid_cases() -> List[Case]:
    return [case for case in cases() if not case.invalid_selector]


def invalid_cases() -> List[Case]:
    return [case for case in cases() if case.invalid_selector]


@pytest.mark.parametrize("case", valid_cases(), ids=operator.attrgetter("name"))
def test_compliance(case: Case) -> None:
    if case.name in SKIP:
        pytest.skip(reason=SKIP[case.name])

    assert case.document is not None
    rv = jsonpath.JSONPathNodeList(
        jsonpath.query(case.selector, case.document)
    ).values()

    if case.results is not None:
        assert rv in case.results
    else:
        assert rv == case.result


@pytest.mark.parametrize("case", invalid_cases(), ids=operator.attrgetter("name"))
def test_invalid_selectors(case: Case) -> None:
    if case.name in SKIP:
        pytest.skip(reason=SKIP[case.name])

    with pytest.raises(jsonpath.JSONPathError):
        jsonpath.compile(case.selector)
