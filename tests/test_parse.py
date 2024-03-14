import dataclasses
import operator

import pytest

from jsonpath import JSONPathEnvironment


@dataclasses.dataclass
class Case:
    description: str
    path: str
    want: str


TEST_CASES = [
    Case(description="just root", path="$", want="$"),
    Case(description="root dot property", path="$.thing", want="$['thing']"),
    Case(description="root bracket property", path="$['thing']", want="$['thing']"),
    Case(
        description="root double quoted property", path='$["thing"]', want="$['thing']"
    ),
    Case(
        description="root single quoted property", path="$['thing']", want="$['thing']"
    ),
    Case(
        description="root quoted property with non-ident chars",
        path="$['anything{!%']",
        want="$['anything{!%']",
    ),
    Case(description="root bracket index", path="$[1]", want="$[1]"),
    Case(description="root slice", path="$[1:-1]", want="$[1:-1:1]"),
    Case(description="root slice with step", path="$[1:-1:2]", want="$[1:-1:2]"),
    Case(description="root slice with empty start", path="$[:-1]", want="$[:-1:1]"),
    Case(description="root slice with empty stop", path="$[1:]", want="$[1::1]"),
    Case(description="root dot wild", path="$.*", want="$[*]"),
    Case(description="root bracket wild", path="$[*]", want="$[*]"),
    Case(description="root selector list", path="$[1,2]", want="$[1, 2]"),
    Case(
        description="root selector list with slice",
        path="$[1,5:-1:1]",
        want="$[1, 5:-1:1]",
    ),
    Case(
        description="root selector list with quoted properties",
        path="$[\"some\",'thing']",
        want="$['some', 'thing']",
    ),
    Case(
        description="implicit root selector list with mixed selectors",
        path='$["some","thing", 1, 2:-2:2]',
        want="$['some', 'thing', 1, 2:-2:2]",
    ),
    Case(
        description="filter self dot property",
        path="$[?(@.thing)]",
        want="$[?@['thing']]",
    ),
    Case(
        description="filter root dot property",
        path="$.some[?($.thing)]",
        want="$['some'][?$['thing']]",
    ),
    Case(
        description="filter with equality test",
        path="$.some[?(@.thing == 7)]",
        want="$['some'][?@['thing'] == 7]",
    ),
    Case(
        description="filter with >=",
        path="$.some[?(@.thing >= 7)]",
        want="$['some'][?@['thing'] >= 7]",
    ),
    Case(
        description="filter with >=",
        path="$.some[?(@.thing >= 7)]",
        want="$['some'][?@['thing'] >= 7]",
    ),
    Case(
        description="filter with !=",
        path="$.some[?(@.thing != 7)]",
        want="$['some'][?@['thing'] != 7]",
    ),
    Case(
        description="filter with boolean literals",
        path="$.some[?(true == false)]",
        want="$['some'][?true == false]",
    ),
    Case(
        description="filter with null literal",
        path="$.some[?(@.thing == null)]",
        want="$['some'][?@['thing'] == null]",
    ),
    Case(
        description="filter with string literal",
        path="$.some[?(@.thing == 'foo')]",
        want="$['some'][?@['thing'] == \"foo\"]",
    ),
    Case(
        description="filter with integer literal",
        path="$.some[?(@.thing == 1)]",
        want="$['some'][?@['thing'] == 1]",
    ),
    Case(
        description="filter with float literal",
        path="$.some[?(@.thing == 1.1)]",
        want="$['some'][?@['thing'] == 1.1]",
    ),
    Case(
        description="filter with logical not",
        path="$.some[?(@.thing > 1 && !$.other)]",
        want="$['some'][?(@['thing'] > 1 && !$['other'])]",
    ),
    Case(
        description="filter with grouped expression",
        path="$.some[?(@.thing > 1 && ($.foo || $.bar))]",
        want="$['some'][?(@['thing'] > 1 && ($['foo'] || $['bar']))]",
    ),
    Case(
        description="comparison to single quoted string literal with escape",
        path="$[?@.foo == 'ba\\'r']",
        want="$[?@['foo'] == \"ba'r\"]",
    ),
    Case(
        description="comparison to double quoted string literal with escape",
        path='$[?@.foo == "ba\\"r"]',
        want='$[?@[\'foo\'] == "ba\\"r"]',
    ),
    Case(
        description="not binds more tightly than or",
        path="$[?!@.a || !@.b]",
        want="$[?(!@['a'] || !@['b'])]",
    ),
    Case(
        description="not binds more tightly than and",
        path="$[?!@.a && !@.b]",
        want="$[?(!@['a'] && !@['b'])]",
    ),
    Case(
        description="control precedence with parens",
        path="$[?!(@.a && !@.b)]",
        want="$[?!(@['a'] && !@['b'])]",
    ),
]


@pytest.fixture()
def env() -> JSONPathEnvironment:
    return JSONPathEnvironment()


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_parser(env: JSONPathEnvironment, case: Case) -> None:
    path = env.compile(case.path)
    assert str(path) == case.want
