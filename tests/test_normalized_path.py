import dataclasses
import operator
from typing import Any
from typing import List
from typing import Mapping
from typing import Sequence
from typing import Union

import pytest

from jsonpath_rfc9535 import JSONPathEnvironment


@dataclasses.dataclass
class Case:
    description: str
    path: str
    data: Union[Sequence[Any], Mapping[str, Any]]
    want: List[str]


TEST_CASES = [
    Case(
        description="normalized negative index",
        path="$.a[-2]",
        data={"a": [1, 2, 3, 4, 5]},
        want=["$['a'][3]"],
    ),
    Case(
        description="normalized reverse slice",
        path="$.a[3:0:-1]",
        data={"a": [1, 2, 3, 4, 5]},
        want=["$['a'][3]", "$['a'][2]", "$['a'][1]"],
    ),
]


@pytest.fixture()
def env() -> JSONPathEnvironment:
    return JSONPathEnvironment()


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_find(env: JSONPathEnvironment, case: Case) -> None:
    path = env.compile(case.path)
    nodes = list(path.query(case.data))
    assert len(nodes) == len(case.want)
    for node, want in zip(nodes, case.want):  # noqa: B905
        assert node.path() == want
