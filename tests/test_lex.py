import dataclasses
import operator
from typing import List

import pytest

from jsonpath import JSONPathEnvironment
from jsonpath.exceptions import JSONPathSyntaxError
from jsonpath.tokens import Token
from jsonpath.tokens import TokenType


@dataclasses.dataclass
class Case:
    description: str
    path: str
    want: List[Token]


TEST_CASES = [
    Case(
        description="just root",
        path="$",
        want=[
            Token(kind=TokenType.ROOT, value="$", index=0, path="$"),
        ],
    ),
    Case(
        description="root dot property",
        path="$.some.thing",
        want=[
            Token(kind=TokenType.ROOT, value="$", index=0, path="$.some.thing"),
            Token(kind=TokenType.PROPERTY, value="some", index=2, path="$.some.thing"),
            Token(kind=TokenType.PROPERTY, value="thing", index=7, path="$.some.thing"),
        ],
    ),
    Case(
        description="root double quoted property",
        path='$["some"]',
        want=[
            Token(kind=TokenType.ROOT, value="$", index=0, path='$["some"]'),
            Token(kind=TokenType.LBRACKET, value="[", index=1, path='$["some"]'),
            Token(
                kind=TokenType.DOUBLE_QUOTE_STRING,
                value="some",
                index=3,
                path='$["some"]',
            ),
            Token(kind=TokenType.RBRACKET, value="]", index=8, path='$["some"]'),
        ],
    ),
    Case(
        description="root single quoted property",
        path="$['some']",
        want=[
            Token(kind=TokenType.ROOT, value="$", index=0, path="$['some']"),
            Token(kind=TokenType.LBRACKET, value="[", index=1, path="$['some']"),
            Token(
                kind=TokenType.SINGLE_QUOTE_STRING,
                value="some",
                index=3,
                path="$['some']",
            ),
            Token(kind=TokenType.RBRACKET, value="]", index=8, path="$['some']"),
        ],
    ),
    Case(
        description="root bracket index",
        path="$[1]",
        want=[
            Token(kind=TokenType.ROOT, value="$", index=0, path="$[1]"),
            Token(kind=TokenType.LBRACKET, value="[", index=1, path="$[1]"),
            Token(kind=TokenType.INT, value="1", index=2, path="$[1]"),
            Token(kind=TokenType.RBRACKET, value="]", index=3, path="$[1]"),
        ],
    ),
    Case(
        description="root dot bracket index",  # XXX
        path="$.[1]",
        want=[
            Token(kind=TokenType.ROOT, value="$", index=0, path="$.[1]"),
            Token(kind=TokenType.LBRACKET, value="[", index=2, path="$.[1]"),
            Token(kind=TokenType.INT, value="1", index=3, path="$.[1]"),
            Token(kind=TokenType.RBRACKET, value="]", index=4, path="$.[1]"),
        ],
    ),
    Case(
        description="empty slice",
        path="[:]",
        want=[
            Token(kind=TokenType.LBRACKET, value="[", index=0, path="[:]"),
            Token(kind=TokenType.SLICE_START, value="", index=1, path="[:]"),
            Token(kind=TokenType.SLICE_STOP, value="", index=2, path="[:]"),
            Token(kind=TokenType.SLICE_STEP, value="", index=-1, path="[:]"),
            Token(kind=TokenType.RBRACKET, value="]", index=2, path="[:]"),
        ],
    ),
    Case(
        description="empty slice empty step",
        path="[::]",
        want=[
            Token(kind=TokenType.LBRACKET, value="[", index=0, path="[::]"),
            Token(kind=TokenType.SLICE_START, value="", index=1, path="[::]"),
            Token(kind=TokenType.SLICE_STOP, value="", index=2, path="[::]"),
            Token(kind=TokenType.SLICE_STEP, value="", index=3, path="[::]"),
            Token(kind=TokenType.RBRACKET, value="]", index=3, path="[::]"),
        ],
    ),
    Case(
        description="slice empty stop",
        path="[1:]",
        want=[
            Token(kind=TokenType.LBRACKET, value="[", index=0, path="[1:]"),
            Token(kind=TokenType.SLICE_START, value="1", index=1, path="[1:]"),
            Token(kind=TokenType.SLICE_STOP, value="", index=3, path="[1:]"),
            Token(kind=TokenType.SLICE_STEP, value="", index=-1, path="[1:]"),
            Token(kind=TokenType.RBRACKET, value="]", index=3, path="[1:]"),
        ],
    ),
    Case(
        description="slice empty start",
        path="[:-1]",
        want=[
            Token(kind=TokenType.LBRACKET, value="[", index=0, path="[:-1]"),
            Token(kind=TokenType.SLICE_START, value="", index=1, path="[:-1]"),
            Token(kind=TokenType.SLICE_STOP, value="-1", index=2, path="[:-1]"),
            Token(kind=TokenType.SLICE_STEP, value="", index=-1, path="[:-1]"),
            Token(kind=TokenType.RBRACKET, value="]", index=4, path="[:-1]"),
        ],
    ),
    Case(
        description="slice start and stop",
        path="[1:7]",
        want=[
            Token(kind=TokenType.LBRACKET, value="[", index=0, path="[1:7]"),
            Token(kind=TokenType.SLICE_START, value="1", index=1, path="[1:7]"),
            Token(kind=TokenType.SLICE_STOP, value="7", index=3, path="[1:7]"),
            Token(kind=TokenType.SLICE_STEP, value="", index=-1, path="[1:7]"),
            Token(kind=TokenType.RBRACKET, value="]", index=4, path="[1:7]"),
        ],
    ),
    Case(
        description="slice start, stop and step",
        path="[1:7:2]",
        want=[
            Token(kind=TokenType.LBRACKET, value="[", index=0, path="[1:7:2]"),
            Token(kind=TokenType.SLICE_START, value="1", index=1, path="[1:7:2]"),
            Token(kind=TokenType.SLICE_STOP, value="7", index=3, path="[1:7:2]"),
            Token(kind=TokenType.SLICE_STEP, value="2", index=5, path="[1:7:2]"),
            Token(kind=TokenType.RBRACKET, value="]", index=6, path="[1:7:2]"),
        ],
    ),
    Case(
        description="root dot wild",
        path="$.*",
        want=[
            Token(kind=TokenType.ROOT, value="$", index=0, path="$.*"),
            Token(kind=TokenType.WILD, value="*", index=2, path="$.*"),
        ],
    ),
    Case(
        description="root bracket wild",
        path="$[*]",
        want=[
            Token(kind=TokenType.ROOT, value="$", index=0, path="$[*]"),
            Token(kind=TokenType.LBRACKET, value="[", index=1, path="$[*]"),
            Token(kind=TokenType.WILD, value="*", index=2, path="$[*]"),
            Token(kind=TokenType.RBRACKET, value="]", index=3, path="$[*]"),
        ],
    ),
    Case(
        description="root dot bracket wild",
        path="$.[*]",
        want=[
            Token(kind=TokenType.ROOT, value="$", index=0, path="$.[*]"),
            Token(kind=TokenType.LBRACKET, value="[", index=2, path="$.[*]"),
            Token(kind=TokenType.WILD, value="*", index=3, path="$.[*]"),
            Token(kind=TokenType.RBRACKET, value="]", index=4, path="$.[*]"),
        ],
    ),
    Case(
        description="root descend property",
        path="$..thing",
        want=[
            Token(kind=TokenType.ROOT, value="$", index=0, path="$..thing"),
            Token(kind=TokenType.DOUBLE_DOT, value="..", index=1, path="$..thing"),
            Token(kind=TokenType.PROPERTY, value="thing", index=3, path="$..thing"),
        ],
    ),
    Case(
        description="root selector list of indices",
        path="$[1,4,5]",
        want=[
            Token(kind=TokenType.ROOT, value="$", index=0, path="$[1,4,5]"),
            Token(kind=TokenType.LBRACKET, value="[", index=1, path="$[1,4,5]"),
            Token(kind=TokenType.INT, value="1", index=2, path="$[1,4,5]"),
            Token(kind=TokenType.COMMA, value=",", index=3, path="$[1,4,5]"),
            Token(kind=TokenType.INT, value="4", index=4, path="$[1,4,5]"),
            Token(kind=TokenType.COMMA, value=",", index=5, path="$[1,4,5]"),
            Token(kind=TokenType.INT, value="5", index=6, path="$[1,4,5]"),
            Token(kind=TokenType.RBRACKET, value="]", index=7, path="$[1,4,5]"),
        ],
    ),
    Case(
        description="root selector list with a slice",
        path="$[1,4:9]",
        want=[
            Token(kind=TokenType.ROOT, value="$", index=0, path="$[1,4:9]"),
            Token(kind=TokenType.LBRACKET, value="[", index=1, path="$[1,4:9]"),
            Token(kind=TokenType.INT, value="1", index=2, path="$[1,4:9]"),
            Token(kind=TokenType.COMMA, value=",", index=3, path="$[1,4:9]"),
            Token(kind=TokenType.SLICE_START, value="4", index=4, path="$[1,4:9]"),
            Token(kind=TokenType.SLICE_STOP, value="9", index=6, path="$[1,4:9]"),
            Token(kind=TokenType.SLICE_STEP, value="", index=-1, path="$[1,4:9]"),
            Token(kind=TokenType.RBRACKET, value="]", index=7, path="$[1,4:9]"),
        ],
    ),
    Case(
        description="root dot filter on self dot property",
        path="$.[?(@.some)]",
        want=[
            Token(kind=TokenType.ROOT, value="$", index=0, path="$.[?(@.some)]"),
            Token(kind=TokenType.LBRACKET, value="[", index=2, path="$.[?(@.some)]"),
            Token(kind=TokenType.FILTER, value="?", index=3, path="$.[?(@.some)]"),
            Token(kind=TokenType.LPAREN, value="(", index=4, path="$.[?(@.some)]"),
            Token(kind=TokenType.CURRENT, value="@", index=5, path="$.[?(@.some)]"),
            Token(kind=TokenType.PROPERTY, value="some", index=7, path="$.[?(@.some)]"),
            Token(kind=TokenType.RPAREN, value=")", index=11, path="$.[?(@.some)]"),
            Token(kind=TokenType.RBRACKET, value="]", index=12, path="$.[?(@.some)]"),
        ],
    ),
    Case(
        description="root dot filter on root dot property",
        path="$.[?($.some)]",
        want=[
            Token(kind=TokenType.ROOT, value="$", index=0, path="$.[?($.some)]"),
            Token(kind=TokenType.LBRACKET, value="[", index=2, path="$.[?($.some)]"),
            Token(kind=TokenType.FILTER, value="?", index=3, path="$.[?($.some)]"),
            Token(kind=TokenType.LPAREN, value="(", index=4, path="$.[?($.some)]"),
            Token(kind=TokenType.ROOT, value="$", index=5, path="$.[?($.some)]"),
            Token(kind=TokenType.PROPERTY, value="some", index=7, path="$.[?($.some)]"),
            Token(kind=TokenType.RPAREN, value=")", index=11, path="$.[?($.some)]"),
            Token(kind=TokenType.RBRACKET, value="]", index=12, path="$.[?($.some)]"),
        ],
    ),
    Case(
        description="root dot filter on self index",
        path="$.[?(@[1])]",
        want=[
            Token(kind=TokenType.ROOT, value="$", index=0, path="$.[?(@[1])]"),
            Token(kind=TokenType.LBRACKET, value="[", index=2, path="$.[?(@[1])]"),
            Token(kind=TokenType.FILTER, value="?", index=3, path="$.[?(@[1])]"),
            Token(kind=TokenType.LPAREN, value="(", index=4, path="$.[?(@[1])]"),
            Token(kind=TokenType.CURRENT, value="@", index=5, path="$.[?(@[1])]"),
            Token(kind=TokenType.LBRACKET, value="[", index=6, path="$.[?(@[1])]"),
            Token(kind=TokenType.INT, value="1", index=7, path="$.[?(@[1])]"),
            Token(kind=TokenType.RBRACKET, value="]", index=8, path="$.[?(@[1])]"),
            Token(kind=TokenType.RPAREN, value=")", index=9, path="$.[?(@[1])]"),
            Token(kind=TokenType.RBRACKET, value="]", index=10, path="$.[?(@[1])]"),
        ],
    ),
    Case(
        description="filter self dot property equality with float",
        path="[?(@.some == 1.1)]",
        want=[
            Token(
                kind=TokenType.LBRACKET, value="[", index=0, path="[?(@.some == 1.1)]"
            ),
            Token(kind=TokenType.FILTER, value="?", index=1, path="[?(@.some == 1.1)]"),
            Token(kind=TokenType.LPAREN, value="(", index=2, path="[?(@.some == 1.1)]"),
            Token(
                kind=TokenType.CURRENT, value="@", index=3, path="[?(@.some == 1.1)]"
            ),
            Token(
                kind=TokenType.PROPERTY,
                value="some",
                index=5,
                path="[?(@.some == 1.1)]",
            ),
            Token(kind=TokenType.EQ, value="==", index=10, path="[?(@.some == 1.1)]"),
            Token(
                kind=TokenType.FLOAT, value="1.1", index=13, path="[?(@.some == 1.1)]"
            ),
            Token(
                kind=TokenType.RPAREN, value=")", index=16, path="[?(@.some == 1.1)]"
            ),
            Token(
                kind=TokenType.RBRACKET, value="]", index=17, path="[?(@.some == 1.1)]"
            ),
        ],
    ),
    Case(
        description=(
            "filter self dot property equality with float in scientific notation"
        ),
        path="[?(@.some == 1.1e10)]",
        want=[
            Token(
                kind=TokenType.LBRACKET,
                value="[",
                index=0,
                path="[?(@.some == 1.1e10)]",
            ),
            Token(
                kind=TokenType.FILTER, value="?", index=1, path="[?(@.some == 1.1e10)]"
            ),
            Token(
                kind=TokenType.LPAREN,
                value="(",
                index=2,
                path="[?(@.some == 1.1e10)]",
            ),
            Token(
                kind=TokenType.CURRENT, value="@", index=3, path="[?(@.some == 1.1e10)]"
            ),
            Token(
                kind=TokenType.PROPERTY,
                value="some",
                index=5,
                path="[?(@.some == 1.1e10)]",
            ),
            Token(
                kind=TokenType.EQ, value="==", index=10, path="[?(@.some == 1.1e10)]"
            ),
            Token(
                kind=TokenType.FLOAT,
                value="1.1e10",
                index=13,
                path="[?(@.some == 1.1e10)]",
            ),
            Token(
                kind=TokenType.RPAREN, value=")", index=19, path="[?(@.some == 1.1e10)]"
            ),
            Token(
                kind=TokenType.RBRACKET,
                value="]",
                index=20,
                path="[?(@.some == 1.1e10)]",
            ),
        ],
    ),
    Case(
        description="filter self index equality with float",
        path="[?(@[1] == 1.1)]",
        want=[
            Token(kind=TokenType.LBRACKET, value="[", index=0, path="[?(@[1] == 1.1)]"),
            Token(kind=TokenType.FILTER, value="?", index=1, path="[?(@[1] == 1.1)]"),
            Token(kind=TokenType.LPAREN, value="(", index=2, path="[?(@[1] == 1.1)]"),
            Token(kind=TokenType.CURRENT, value="@", index=3, path="[?(@[1] == 1.1)]"),
            Token(kind=TokenType.LBRACKET, value="[", index=4, path="[?(@[1] == 1.1)]"),
            Token(kind=TokenType.INT, value="1", index=5, path="[?(@[1] == 1.1)]"),
            Token(kind=TokenType.RBRACKET, value="]", index=6, path="[?(@[1] == 1.1)]"),
            Token(kind=TokenType.EQ, value="==", index=8, path="[?(@[1] == 1.1)]"),
            Token(kind=TokenType.FLOAT, value="1.1", index=11, path="[?(@[1] == 1.1)]"),
            Token(kind=TokenType.RPAREN, value=")", index=14, path="[?(@[1] == 1.1)]"),
            Token(
                kind=TokenType.RBRACKET, value="]", index=15, path="[?(@[1] == 1.1)]"
            ),
        ],
    ),
    Case(
        description="filter self dot property equality with int",
        path="[?(@.some == 1)]",
        want=[
            Token(kind=TokenType.LBRACKET, value="[", index=0, path="[?(@.some == 1)]"),
            Token(kind=TokenType.FILTER, value="?", index=1, path="[?(@.some == 1)]"),
            Token(kind=TokenType.LPAREN, value="(", index=2, path="[?(@.some == 1)]"),
            Token(kind=TokenType.CURRENT, value="@", index=3, path="[?(@.some == 1)]"),
            Token(
                kind=TokenType.PROPERTY, value="some", index=5, path="[?(@.some == 1)]"
            ),
            Token(kind=TokenType.EQ, value="==", index=10, path="[?(@.some == 1)]"),
            Token(kind=TokenType.INT, value="1", index=13, path="[?(@.some == 1)]"),
            Token(kind=TokenType.RPAREN, value=")", index=14, path="[?(@.some == 1)]"),
            Token(
                kind=TokenType.RBRACKET, value="]", index=15, path="[?(@.some == 1)]"
            ),
        ],
    ),
    Case(
        description="filter self dot property equality with int in scientific notation",
        path="[?(@.some == 1e10)]",
        want=[
            Token(
                kind=TokenType.LBRACKET,
                value="[",
                index=0,
                path="[?(@.some == 1e10)]",
            ),
            Token(
                kind=TokenType.FILTER,
                value="?",
                index=1,
                path="[?(@.some == 1e10)]",
            ),
            Token(
                kind=TokenType.LPAREN,
                value="(",
                index=2,
                path="[?(@.some == 1e10)]",
            ),
            Token(
                kind=TokenType.CURRENT, value="@", index=3, path="[?(@.some == 1e10)]"
            ),
            Token(
                kind=TokenType.PROPERTY,
                value="some",
                index=5,
                path="[?(@.some == 1e10)]",
            ),
            Token(kind=TokenType.EQ, value="==", index=10, path="[?(@.some == 1e10)]"),
            Token(
                kind=TokenType.INT, value="1e10", index=13, path="[?(@.some == 1e10)]"
            ),
            Token(
                kind=TokenType.RPAREN, value=")", index=17, path="[?(@.some == 1e10)]"
            ),
            Token(
                kind=TokenType.RBRACKET, value="]", index=18, path="[?(@.some == 1e10)]"
            ),
        ],
    ),
    Case(
        description="filter expression with logical and",
        path="[?(@.some > 1 && @.some < 5)]",
        want=[
            Token(
                kind=TokenType.LBRACKET,
                value="[",
                index=0,
                path="[?(@.some > 1 && @.some < 5)]",
            ),
            Token(
                kind=TokenType.FILTER,
                value="?",
                index=1,
                path="[?(@.some > 1 && @.some < 5)]",
            ),
            Token(
                kind=TokenType.LPAREN,
                value="(",
                index=2,
                path="[?(@.some > 1 && @.some < 5)]",
            ),
            Token(
                kind=TokenType.CURRENT,
                value="@",
                index=3,
                path="[?(@.some > 1 && @.some < 5)]",
            ),
            Token(
                kind=TokenType.PROPERTY,
                value="some",
                index=5,
                path="[?(@.some > 1 && @.some < 5)]",
            ),
            Token(
                kind=TokenType.GT,
                value=">",
                index=10,
                path="[?(@.some > 1 && @.some < 5)]",
            ),
            Token(
                kind=TokenType.INT,
                value="1",
                index=12,
                path="[?(@.some > 1 && @.some < 5)]",
            ),
            Token(
                kind=TokenType.AND,
                value="&&",
                index=14,
                path="[?(@.some > 1 && @.some < 5)]",
            ),
            Token(
                kind=TokenType.CURRENT,
                value="@",
                index=17,
                path="[?(@.some > 1 && @.some < 5)]",
            ),
            Token(
                kind=TokenType.PROPERTY,
                value="some",
                index=19,
                path="[?(@.some > 1 && @.some < 5)]",
            ),
            Token(
                kind=TokenType.LT,
                value="<",
                index=24,
                path="[?(@.some > 1 && @.some < 5)]",
            ),
            Token(
                kind=TokenType.INT,
                value="5",
                index=26,
                path="[?(@.some > 1 && @.some < 5)]",
            ),
            Token(
                kind=TokenType.RPAREN,
                value=")",
                index=27,
                path="[?(@.some > 1 && @.some < 5)]",
            ),
            Token(
                kind=TokenType.RBRACKET,
                value="]",
                index=28,
                path="[?(@.some > 1 && @.some < 5)]",
            ),
        ],
    ),
    Case(
        description="filter expression with logical ||",
        path="[?(@.some == 1 || @.some == 5)]",
        want=[
            Token(
                kind=TokenType.LBRACKET,
                value="[",
                index=0,
                path="[?(@.some == 1 || @.some == 5)]",
            ),
            Token(
                kind=TokenType.FILTER,
                value="?",
                index=1,
                path="[?(@.some == 1 || @.some == 5)]",
            ),
            Token(
                kind=TokenType.LPAREN,
                value="(",
                index=2,
                path="[?(@.some == 1 || @.some == 5)]",
            ),
            Token(
                kind=TokenType.CURRENT,
                value="@",
                index=3,
                path="[?(@.some == 1 || @.some == 5)]",
            ),
            Token(
                kind=TokenType.PROPERTY,
                value="some",
                index=5,
                path="[?(@.some == 1 || @.some == 5)]",
            ),
            Token(
                kind=TokenType.EQ,
                value="==",
                index=10,
                path="[?(@.some == 1 || @.some == 5)]",
            ),
            Token(
                kind=TokenType.INT,
                value="1",
                index=13,
                path="[?(@.some == 1 || @.some == 5)]",
            ),
            Token(
                kind=TokenType.OR,
                value="||",
                index=15,
                path="[?(@.some == 1 || @.some == 5)]",
            ),
            Token(
                kind=TokenType.CURRENT,
                value="@",
                index=18,
                path="[?(@.some == 1 || @.some == 5)]",
            ),
            Token(
                kind=TokenType.PROPERTY,
                value="some",
                index=20,
                path="[?(@.some == 1 || @.some == 5)]",
            ),
            Token(
                kind=TokenType.EQ,
                value="==",
                index=25,
                path="[?(@.some == 1 || @.some == 5)]",
            ),
            Token(
                kind=TokenType.INT,
                value="5",
                index=28,
                path="[?(@.some == 1 || @.some == 5)]",
            ),
            Token(
                kind=TokenType.RPAREN,
                value=")",
                index=29,
                path="[?(@.some == 1 || @.some == 5)]",
            ),
            Token(
                kind=TokenType.RBRACKET,
                value="]",
                index=30,
                path="[?(@.some == 1 || @.some == 5)]",
            ),
        ],
    ),
    Case(
        description="filter expression with logical not",
        path="[?(@.some == 1 || !@.some < 5)]",
        want=[
            Token(
                kind=TokenType.LBRACKET,
                value="[",
                index=0,
                path="[?(@.some == 1 || !@.some < 5)]",
            ),
            Token(
                kind=TokenType.FILTER,
                value="?",
                index=1,
                path="[?(@.some == 1 || !@.some < 5)]",
            ),
            Token(
                kind=TokenType.LPAREN,
                value="(",
                index=2,
                path="[?(@.some == 1 || !@.some < 5)]",
            ),
            Token(
                kind=TokenType.CURRENT,
                value="@",
                index=3,
                path="[?(@.some == 1 || !@.some < 5)]",
            ),
            Token(
                kind=TokenType.PROPERTY,
                value="some",
                index=5,
                path="[?(@.some == 1 || !@.some < 5)]",
            ),
            Token(
                kind=TokenType.EQ,
                value="==",
                index=10,
                path="[?(@.some == 1 || !@.some < 5)]",
            ),
            Token(
                kind=TokenType.INT,
                value="1",
                index=13,
                path="[?(@.some == 1 || !@.some < 5)]",
            ),
            Token(
                kind=TokenType.OR,
                value="||",
                index=15,
                path="[?(@.some == 1 || !@.some < 5)]",
            ),
            Token(
                kind=TokenType.NOT,
                value="!",
                index=18,
                path="[?(@.some == 1 || !@.some < 5)]",
            ),
            Token(
                kind=TokenType.CURRENT,
                value="@",
                index=19,
                path="[?(@.some == 1 || !@.some < 5)]",
            ),
            Token(
                kind=TokenType.PROPERTY,
                value="some",
                index=21,
                path="[?(@.some == 1 || !@.some < 5)]",
            ),
            Token(
                kind=TokenType.LT,
                value="<",
                index=26,
                path="[?(@.some == 1 || !@.some < 5)]",
            ),
            Token(
                kind=TokenType.INT,
                value="5",
                index=28,
                path="[?(@.some == 1 || !@.some < 5)]",
            ),
            Token(
                kind=TokenType.RPAREN,
                value=")",
                index=29,
                path="[?(@.some == 1 || !@.some < 5)]",
            ),
            Token(
                kind=TokenType.RBRACKET,
                value="]",
                index=30,
                path="[?(@.some == 1 || !@.some < 5)]",
            ),
        ],
    ),
    Case(
        description="filter true and false",
        path="[?(true == false)]",
        want=[
            Token(
                kind=TokenType.LBRACKET,
                value="[",
                index=0,
                path="[?(true == false)]",
            ),
            Token(
                kind=TokenType.FILTER,
                value="?",
                index=1,
                path="[?(true == false)]",
            ),
            Token(
                kind=TokenType.LPAREN,
                value="(",
                index=2,
                path="[?(true == false)]",
            ),
            Token(
                kind=TokenType.TRUE, value="true", index=3, path="[?(true == false)]"
            ),
            Token(kind=TokenType.EQ, value="==", index=8, path="[?(true == false)]"),
            Token(
                kind=TokenType.FALSE, value="false", index=11, path="[?(true == false)]"
            ),
            Token(
                kind=TokenType.RPAREN, value=")", index=16, path="[?(true == false)]"
            ),
            Token(
                kind=TokenType.RBRACKET, value="]", index=17, path="[?(true == false)]"
            ),
        ],
    ),
    Case(
        description="list of quoted properties",
        path="$['some', 'thing']",
        want=[
            Token(kind=TokenType.ROOT, value="$", index=0, path="$['some', 'thing']"),
            Token(
                kind=TokenType.LBRACKET, value="[", index=1, path="$['some', 'thing']"
            ),
            Token(
                kind=TokenType.SINGLE_QUOTE_STRING,
                value="some",
                index=3,
                path="$['some', 'thing']",
            ),
            Token(kind=TokenType.COMMA, value=",", index=8, path="$['some', 'thing']"),
            Token(
                kind=TokenType.SINGLE_QUOTE_STRING,
                value="thing",
                index=11,
                path="$['some', 'thing']",
            ),
            Token(
                kind=TokenType.RBRACKET, value="]", index=17, path="$['some', 'thing']"
            ),
        ],
    ),
    Case(
        description="call a function",
        path="$.some[?(length(@.thing) < 2)]",
        want=[
            Token(
                kind=TokenType.ROOT,
                value="$",
                index=0,
                path="$.some[?(length(@.thing) < 2)]",
            ),
            Token(
                kind=TokenType.PROPERTY,
                value="some",
                index=2,
                path="$.some[?(length(@.thing) < 2)]",
            ),
            Token(
                kind=TokenType.LBRACKET,
                value="[",
                index=6,
                path="$.some[?(length(@.thing) < 2)]",
            ),
            Token(
                kind=TokenType.FILTER,
                value="?",
                index=7,
                path="$.some[?(length(@.thing) < 2)]",
            ),
            Token(
                kind=TokenType.LPAREN,
                value="(",
                index=8,
                path="$.some[?(length(@.thing) < 2)]",
            ),
            Token(
                kind=TokenType.FUNCTION,
                value="length",
                index=9,
                path="$.some[?(length(@.thing) < 2)]",
            ),
            Token(
                kind=TokenType.CURRENT,
                value="@",
                index=16,
                path="$.some[?(length(@.thing) < 2)]",
            ),
            Token(
                kind=TokenType.PROPERTY,
                value="thing",
                index=18,
                path="$.some[?(length(@.thing) < 2)]",
            ),
            Token(
                kind=TokenType.RPAREN,
                value=")",
                index=23,
                path="$.some[?(length(@.thing) < 2)]",
            ),
            Token(
                kind=TokenType.LT,
                value="<",
                index=25,
                path="$.some[?(length(@.thing) < 2)]",
            ),
            Token(
                kind=TokenType.INT,
                value="2",
                index=27,
                path="$.some[?(length(@.thing) < 2)]",
            ),
            Token(
                kind=TokenType.RPAREN,
                value=")",
                index=28,
                path="$.some[?(length(@.thing) < 2)]",
            ),
            Token(
                kind=TokenType.RBRACKET,
                value="]",
                index=29,
                path="$.some[?(length(@.thing) < 2)]",
            ),
        ],
    ),
]


@pytest.fixture()
def env() -> JSONPathEnvironment:
    return JSONPathEnvironment()


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_lexer(env: JSONPathEnvironment, case: Case) -> None:
    tokens = list(env.lexer.tokenize(case.path))
    assert tokens == case.want


def test_illegal_token(env: JSONPathEnvironment) -> None:
    with pytest.raises(JSONPathSyntaxError):
        list(env.lexer.tokenize("%"))
