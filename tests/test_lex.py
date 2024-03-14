import dataclasses
import operator
from typing import List

import pytest

from jsonpath.lex import lex
from jsonpath.tokens import Token
from jsonpath.tokens import TokenType


@dataclasses.dataclass
class Case:
    description: str
    path: str
    want: List[Token]


TEST_CASES = [
    Case(
        description="basic shorthand name",
        path="$.foo.bar",
        want=[
            Token(TokenType.ROOT, "$", 0, "$.foo.bar"),
            Token(TokenType.PROPERTY, "foo", 2, "$.foo.bar"),
            Token(TokenType.PROPERTY, "bar", 6, "$.foo.bar"),
            Token(TokenType.EOF, "", 9, "$.foo.bar"),
        ],
    ),
    Case(
        description="bracketed name",
        path="$['foo']['bar']",
        want=[
            Token(TokenType.ROOT, "$", 0, "$['foo']['bar']"),
            Token(TokenType.LBRACKET, "[", 1, "$['foo']['bar']"),
            Token(TokenType.SINGLE_QUOTE_STRING, "foo", 3, "$['foo']['bar']"),
            Token(TokenType.RBRACKET, "]", 7, "$['foo']['bar']"),
            Token(TokenType.LBRACKET, "[", 8, "$['foo']['bar']"),
            Token(TokenType.SINGLE_QUOTE_STRING, "bar", 10, "$['foo']['bar']"),
            Token(TokenType.RBRACKET, "]", 14, "$['foo']['bar']"),
            Token(TokenType.EOF, "", 15, "$['foo']['bar']"),
        ],
    ),
    Case(
        description="basic index",
        path="$.foo[1]",
        want=[
            Token(TokenType.ROOT, "$", 0, "$.foo[1]"),
            Token(TokenType.PROPERTY, "foo", 2, "$.foo[1]"),
            Token(TokenType.LBRACKET, "[", 5, "$.foo[1]"),
            Token(TokenType.INDEX, "1", 6, "$.foo[1]"),
            Token(TokenType.RBRACKET, "]", 7, "$.foo[1]"),
            Token(TokenType.EOF, "", 8, "$.foo[1]"),
        ],
    ),
    Case(
        description="missing root selector",
        path="foo.bar",
        want=[
            Token(TokenType.ERROR, "expected '$', found 'f'", 0, "foo.bar"),
        ],
    ),
    Case(
        description="root property selector without dot",
        path="$foo",
        want=[
            Token(TokenType.ROOT, "$", 0, "$foo"),
            Token(
                TokenType.ERROR,
                "expected '.', '..' or a bracketed selection, found 'f'",
                1,
                "$foo",
            ),
        ],
    ),
    Case(
        description="whitespace after root",
        path="$ .foo.bar",
        want=[
            Token(TokenType.ROOT, "$", 0, "$ .foo.bar"),
            Token(TokenType.PROPERTY, "foo", 3, "$ .foo.bar"),
            Token(TokenType.PROPERTY, "bar", 7, "$ .foo.bar"),
            Token(TokenType.EOF, "", 10, "$ .foo.bar"),
        ],
    ),
    Case(
        description="whitespace before dot property",
        path="$. foo.bar",
        want=[
            Token(TokenType.ROOT, "$", 0, "$. foo.bar"),
            Token(TokenType.ERROR, "unexpected whitespace after dot", 3, "$. foo.bar"),
        ],
    ),
    Case(
        description="whitespace after dot property",
        path="$.foo .bar",
        want=[
            Token(TokenType.ROOT, "$", 0, "$.foo .bar"),
            Token(TokenType.PROPERTY, "foo", 2, "$.foo .bar"),
            Token(TokenType.PROPERTY, "bar", 7, "$.foo .bar"),
            Token(TokenType.EOF, "", 10, "$.foo .bar"),
        ],
    ),
    Case(
        description="basic dot wild",
        path="$.foo.*",
        want=[
            Token(TokenType.ROOT, "$", 0, "$.foo.*"),
            Token(TokenType.PROPERTY, "foo", 2, "$.foo.*"),
            Token(TokenType.WILD, "*", 6, "$.foo.*"),
            Token(TokenType.EOF, "", 7, "$.foo.*"),
        ],
    ),
    Case(
        description="basic recurse",
        path="$..foo",
        want=[
            Token(TokenType.ROOT, "$", 0, "$..foo"),
            Token(TokenType.DOUBLE_DOT, "..", 1, "$..foo"),
            Token(TokenType.PROPERTY, "foo", 3, "$..foo"),
            Token(TokenType.EOF, "", 6, "$..foo"),
        ],
    ),
    Case(
        description="basic recurse with trailing dot",
        path="$...foo",
        want=[
            Token(TokenType.ROOT, "$", 0, "$...foo"),
            Token(TokenType.DOUBLE_DOT, "..", 1, "$...foo"),
            Token(
                TokenType.ERROR,
                "unexpected descendant selection token '.'",
                3,
                "$...foo",
            ),
        ],
    ),
    Case(
        description="erroneous double recurse",
        path="$....foo",
        want=[
            Token(TokenType.ROOT, "$", 0, "$....foo"),
            Token(TokenType.DOUBLE_DOT, "..", 1, "$....foo"),
            Token(
                TokenType.ERROR,
                "unexpected descendant selection token '.'",
                3,
                "$....foo",
            ),
        ],
    ),
    Case(
        description="bracketed name selector, double quotes",
        path='$.foo["bar"]',
        want=[
            Token(TokenType.ROOT, "$", 0, '$.foo["bar"]'),
            Token(TokenType.PROPERTY, "foo", 2, '$.foo["bar"]'),
            Token(TokenType.LBRACKET, "[", 5, '$.foo["bar"]'),
            Token(TokenType.DOUBLE_QUOTE_STRING, "bar", 7, '$.foo["bar"]'),
            Token(TokenType.RBRACKET, "]", 11, '$.foo["bar"]'),
            Token(TokenType.EOF, "", 12, '$.foo["bar"]'),
        ],
    ),
    Case(
        description="bracketed name selector, single quotes",
        path="$.foo['bar']",
        want=[
            Token(TokenType.ROOT, "$", 0, "$.foo['bar']"),
            Token(TokenType.PROPERTY, "foo", 2, "$.foo['bar']"),
            Token(TokenType.LBRACKET, "[", 5, "$.foo['bar']"),
            Token(TokenType.SINGLE_QUOTE_STRING, "bar", 7, "$.foo['bar']"),
            Token(TokenType.RBRACKET, "]", 11, "$.foo['bar']"),
            Token(TokenType.EOF, "", 12, "$.foo['bar']"),
        ],
    ),
    Case(
        description="multiple selectors",
        path="$.foo['bar', 123, *]",
        want=[
            Token(TokenType.ROOT, "$", 0, "$.foo['bar', 123, *]"),
            Token(TokenType.PROPERTY, "foo", 2, "$.foo['bar', 123, *]"),
            Token(TokenType.LBRACKET, "[", 5, "$.foo['bar', 123, *]"),
            Token(TokenType.SINGLE_QUOTE_STRING, "bar", 7, "$.foo['bar', 123, *]"),
            Token(TokenType.COMMA, ",", 11, "$.foo['bar', 123, *]"),
            Token(TokenType.INDEX, "123", 13, "$.foo['bar', 123, *]"),
            Token(TokenType.COMMA, ",", 16, "$.foo['bar', 123, *]"),
            Token(TokenType.WILD, "*", 18, "$.foo['bar', 123, *]"),
            Token(TokenType.RBRACKET, "]", 19, "$.foo['bar', 123, *]"),
            Token(TokenType.EOF, "", 20, "$.foo['bar', 123, *]"),
        ],
    ),
    Case(
        description="slice",
        path="$.foo[1:3]",
        want=[
            Token(TokenType.ROOT, "$", 0, "$.foo[1:3]"),
            Token(TokenType.PROPERTY, "foo", 2, "$.foo[1:3]"),
            Token(TokenType.LBRACKET, "[", 5, "$.foo[1:3]"),
            Token(TokenType.INDEX, "1", 6, "$.foo[1:3]"),
            Token(TokenType.COLON, ":", 7, "$.foo[1:3]"),
            Token(TokenType.INDEX, "3", 8, "$.foo[1:3]"),
            Token(TokenType.RBRACKET, "]", 9, "$.foo[1:3]"),
            Token(TokenType.EOF, "", 10, "$.foo[1:3]"),
        ],
    ),
    Case(
        description="filter",
        path="$.foo[?@.bar]",
        want=[
            Token(TokenType.ROOT, "$", 0, "$.foo[?@.bar]"),
            Token(TokenType.PROPERTY, "foo", 2, "$.foo[?@.bar]"),
            Token(TokenType.LBRACKET, "[", 5, "$.foo[?@.bar]"),
            Token(TokenType.FILTER, "?", 6, "$.foo[?@.bar]"),
            Token(TokenType.CURRENT, "@", 7, "$.foo[?@.bar]"),
            Token(TokenType.PROPERTY, "bar", 9, "$.foo[?@.bar]"),
            Token(TokenType.RBRACKET, "]", 12, "$.foo[?@.bar]"),
            Token(TokenType.EOF, "", 13, "$.foo[?@.bar]"),
        ],
    ),
    Case(
        description="filter, parenthesized expression",
        path="$.foo[?(@.bar)]",
        want=[
            Token(TokenType.ROOT, "$", 0, "$.foo[?(@.bar)]"),
            Token(TokenType.PROPERTY, "foo", 2, "$.foo[?(@.bar)]"),
            Token(TokenType.LBRACKET, "[", 5, "$.foo[?(@.bar)]"),
            Token(TokenType.FILTER, "?", 6, "$.foo[?(@.bar)]"),
            Token(TokenType.LPAREN, "(", 7, "$.foo[?(@.bar)]"),
            Token(TokenType.CURRENT, "@", 8, "$.foo[?(@.bar)]"),
            Token(TokenType.PROPERTY, "bar", 10, "$.foo[?(@.bar)]"),
            Token(TokenType.RPAREN, ")", 13, "$.foo[?(@.bar)]"),
            Token(TokenType.RBRACKET, "]", 14, "$.foo[?(@.bar)]"),
            Token(TokenType.EOF, "", 15, "$.foo[?(@.bar)]"),
        ],
    ),
    Case(
        description="two filters",
        path="$.foo[?@.bar, ?@.baz]",
        want=[
            Token(TokenType.ROOT, "$", 0, "$.foo[?@.bar, ?@.baz]"),
            Token(TokenType.PROPERTY, "foo", 2, "$.foo[?@.bar, ?@.baz]"),
            Token(TokenType.LBRACKET, "[", 5, "$.foo[?@.bar, ?@.baz]"),
            Token(TokenType.FILTER, "?", 6, "$.foo[?@.bar, ?@.baz]"),
            Token(TokenType.CURRENT, "@", 7, "$.foo[?@.bar, ?@.baz]"),
            Token(TokenType.PROPERTY, "bar", 9, "$.foo[?@.bar, ?@.baz]"),
            Token(TokenType.COMMA, ",", 12, "$.foo[?@.bar, ?@.baz]"),
            Token(TokenType.FILTER, "?", 14, "$.foo[?@.bar, ?@.baz]"),
            Token(TokenType.CURRENT, "@", 15, "$.foo[?@.bar, ?@.baz]"),
            Token(TokenType.PROPERTY, "baz", 17, "$.foo[?@.bar, ?@.baz]"),
            Token(TokenType.RBRACKET, "]", 20, "$.foo[?@.bar, ?@.baz]"),
            Token(TokenType.EOF, "", 21, "$.foo[?@.bar, ?@.baz]"),
        ],
    ),
    Case(
        description="filter, function",
        path="$[?count(@.foo)>2]",
        want=[
            Token(TokenType.ROOT, "$", 0, "$[?count(@.foo)>2]"),
            Token(TokenType.LBRACKET, "[", 1, "$[?count(@.foo)>2]"),
            Token(TokenType.FILTER, "?", 2, "$[?count(@.foo)>2]"),
            Token(TokenType.FUNCTION, "count", 3, "$[?count(@.foo)>2]"),
            Token(TokenType.CURRENT, "@", 9, "$[?count(@.foo)>2]"),
            Token(TokenType.PROPERTY, "foo", 11, "$[?count(@.foo)>2]"),
            Token(TokenType.RPAREN, ")", 14, "$[?count(@.foo)>2]"),
            Token(TokenType.GT, ">", 15, "$[?count(@.foo)>2]"),
            Token(TokenType.INT, "2", 16, "$[?count(@.foo)>2]"),
            Token(TokenType.RBRACKET, "]", 17, "$[?count(@.foo)>2]"),
            Token(TokenType.EOF, "", 18, "$[?count(@.foo)>2]"),
        ],
    ),
    Case(
        description="filter, function with two args",
        path="$[?count(@.foo, 1)>2]",
        want=[
            Token(TokenType.ROOT, "$", 0, "$[?count(@.foo, 1)>2]"),
            Token(TokenType.LBRACKET, "[", 1, "$[?count(@.foo, 1)>2]"),
            Token(TokenType.FILTER, "?", 2, "$[?count(@.foo, 1)>2]"),
            Token(TokenType.FUNCTION, "count", 3, "$[?count(@.foo, 1)>2]"),
            Token(TokenType.CURRENT, "@", 9, "$[?count(@.foo, 1)>2]"),
            Token(TokenType.PROPERTY, "foo", 11, "$[?count(@.foo, 1)>2]"),
            Token(TokenType.COMMA, ",", 14, "$[?count(@.foo, 1)>2]"),
            Token(TokenType.INT, "1", 16, "$[?count(@.foo, 1)>2]"),
            Token(TokenType.RPAREN, ")", 17, "$[?count(@.foo, 1)>2]"),
            Token(TokenType.GT, ">", 18, "$[?count(@.foo, 1)>2]"),
            Token(TokenType.INT, "2", 19, "$[?count(@.foo, 1)>2]"),
            Token(TokenType.RBRACKET, "]", 20, "$[?count(@.foo, 1)>2]"),
            Token(TokenType.EOF, "", 21, "$[?count(@.foo, 1)>2]"),
        ],
    ),
    Case(
        description="filter, parenthesized function",
        path="$[?(count(@.foo)>2)]",
        want=[
            Token(TokenType.ROOT, "$", 0, "$[?(count(@.foo)>2)]"),
            Token(TokenType.LBRACKET, "[", 1, "$[?(count(@.foo)>2)]"),
            Token(TokenType.FILTER, "?", 2, "$[?(count(@.foo)>2)]"),
            Token(TokenType.LPAREN, "(", 3, "$[?(count(@.foo)>2)]"),
            Token(TokenType.FUNCTION, "count", 4, "$[?(count(@.foo)>2)]"),
            Token(TokenType.CURRENT, "@", 10, "$[?(count(@.foo)>2)]"),
            Token(TokenType.PROPERTY, "foo", 12, "$[?(count(@.foo)>2)]"),
            Token(TokenType.RPAREN, ")", 15, "$[?(count(@.foo)>2)]"),
            Token(TokenType.GT, ">", 16, "$[?(count(@.foo)>2)]"),
            Token(TokenType.INT, "2", 17, "$[?(count(@.foo)>2)]"),
            Token(TokenType.RPAREN, ")", 18, "$[?(count(@.foo)>2)]"),
            Token(TokenType.RBRACKET, "]", 19, "$[?(count(@.foo)>2)]"),
            Token(TokenType.EOF, "", 20, "$[?(count(@.foo)>2)]"),
        ],
    ),
    Case(
        description="filter, parenthesized function argument",
        path="$[?(count((@.foo),1)>2)]",
        want=[
            Token(TokenType.ROOT, "$", 0, "$[?(count((@.foo),1)>2)]"),
            Token(TokenType.LBRACKET, "[", 1, "$[?(count((@.foo),1)>2)]"),
            Token(TokenType.FILTER, "?", 2, "$[?(count((@.foo),1)>2)]"),
            Token(TokenType.LPAREN, "(", 3, "$[?(count((@.foo),1)>2)]"),
            Token(TokenType.FUNCTION, "count", 4, "$[?(count((@.foo),1)>2)]"),
            Token(TokenType.LPAREN, "(", 10, "$[?(count((@.foo),1)>2)]"),
            Token(TokenType.CURRENT, "@", 11, "$[?(count((@.foo),1)>2)]"),
            Token(TokenType.PROPERTY, "foo", 13, "$[?(count((@.foo),1)>2)]"),
            Token(TokenType.RPAREN, ")", 16, "$[?(count((@.foo),1)>2)]"),
            Token(TokenType.COMMA, ",", 17, "$[?(count((@.foo),1)>2)]"),
            Token(TokenType.INT, "1", 18, "$[?(count((@.foo),1)>2)]"),
            Token(TokenType.RPAREN, ")", 19, "$[?(count((@.foo),1)>2)]"),
            Token(TokenType.GT, ">", 20, "$[?(count((@.foo),1)>2)]"),
            Token(TokenType.INT, "2", 21, "$[?(count((@.foo),1)>2)]"),
            Token(TokenType.RPAREN, ")", 22, "$[?(count((@.foo),1)>2)]"),
            Token(TokenType.RBRACKET, "]", 23, "$[?(count((@.foo),1)>2)]"),
            Token(TokenType.EOF, "", 24, "$[?(count((@.foo),1)>2)]"),
        ],
    ),
    Case(
        description="filter, nested",
        path="$[?@[?@>1]]",
        want=[
            Token(TokenType.ROOT, "$", 0, "$[?@[?@>1]]"),
            Token(TokenType.LBRACKET, "[", 1, "$[?@[?@>1]]"),
            Token(TokenType.FILTER, "?", 2, "$[?@[?@>1]]"),
            Token(TokenType.CURRENT, "@", 3, "$[?@[?@>1]]"),
            Token(TokenType.LBRACKET, "[", 4, "$[?@[?@>1]]"),
            Token(TokenType.FILTER, "?", 5, "$[?@[?@>1]]"),
            Token(TokenType.CURRENT, "@", 6, "$[?@[?@>1]]"),
            Token(TokenType.GT, ">", 7, "$[?@[?@>1]]"),
            Token(TokenType.INT, "1", 8, "$[?@[?@>1]]"),
            Token(TokenType.RBRACKET, "]", 9, "$[?@[?@>1]]"),
            Token(TokenType.RBRACKET, "]", 10, "$[?@[?@>1]]"),
            Token(TokenType.EOF, "", 11, "$[?@[?@>1]]"),
        ],
    ),
    Case(
        description="filter, nested brackets",
        path="$[?@[?@[1]>1]]",
        want=[
            Token(TokenType.ROOT, "$", 0, "$[?@[?@[1]>1]]"),
            Token(TokenType.LBRACKET, "[", 1, "$[?@[?@[1]>1]]"),
            Token(TokenType.FILTER, "?", 2, "$[?@[?@[1]>1]]"),
            Token(TokenType.CURRENT, "@", 3, "$[?@[?@[1]>1]]"),
            Token(TokenType.LBRACKET, "[", 4, "$[?@[?@[1]>1]]"),
            Token(TokenType.FILTER, "?", 5, "$[?@[?@[1]>1]]"),
            Token(TokenType.CURRENT, "@", 6, "$[?@[?@[1]>1]]"),
            Token(TokenType.LBRACKET, "[", 7, "$[?@[?@[1]>1]]"),
            Token(TokenType.INDEX, "1", 8, "$[?@[?@[1]>1]]"),
            Token(TokenType.RBRACKET, "]", 9, "$[?@[?@[1]>1]]"),
            Token(TokenType.GT, ">", 10, "$[?@[?@[1]>1]]"),
            Token(TokenType.INT, "1", 11, "$[?@[?@[1]>1]]"),
            Token(TokenType.RBRACKET, "]", 12, "$[?@[?@[1]>1]]"),
            Token(TokenType.RBRACKET, "]", 13, "$[?@[?@[1]>1]]"),
            Token(TokenType.EOF, "", 14, "$[?@[?@[1]>1]]"),
        ],
    ),
    Case(
        description="function",
        path="$[?foo()]",
        want=[
            Token(TokenType.ROOT, "$", 0, "$[?foo()]"),
            Token(TokenType.LBRACKET, "[", 1, "$[?foo()]"),
            Token(TokenType.FILTER, "?", 2, "$[?foo()]"),
            Token(TokenType.FUNCTION, "foo", 3, "$[?foo()]"),
            Token(TokenType.RPAREN, ")", 7, "$[?foo()]"),
            Token(TokenType.RBRACKET, "]", 8, "$[?foo()]"),
            Token(TokenType.EOF, "", 9, "$[?foo()]"),
        ],
    ),
    Case(
        description="function",
        path="$[?foo()]",
        want=[
            Token(TokenType.ROOT, "$", 0, "$[?foo()]"),
            Token(TokenType.LBRACKET, "[", 1, "$[?foo()]"),
            Token(TokenType.FILTER, "?", 2, "$[?foo()]"),
            Token(TokenType.FUNCTION, "foo", 3, "$[?foo()]"),
            Token(TokenType.RPAREN, ")", 7, "$[?foo()]"),
            Token(TokenType.RBRACKET, "]", 8, "$[?foo()]"),
            Token(TokenType.EOF, "", 9, "$[?foo()]"),
        ],
    ),
    Case(
        description="function, int literal",
        path="$[?foo(42)]",
        want=[
            Token(TokenType.ROOT, "$", 0, "$[?foo(42)]"),
            Token(TokenType.LBRACKET, "[", 1, "$[?foo(42)]"),
            Token(TokenType.FILTER, "?", 2, "$[?foo(42)]"),
            Token(TokenType.FUNCTION, "foo", 3, "$[?foo(42)]"),
            Token(TokenType.INT, "42", 7, "$[?foo(42)]"),
            Token(TokenType.RPAREN, ")", 9, "$[?foo(42)]"),
            Token(TokenType.RBRACKET, "]", 10, "$[?foo(42)]"),
            Token(TokenType.EOF, "", 11, "$[?foo(42)]"),
        ],
    ),
    Case(
        description="function, two int args",
        path="$[?foo(42, -7)]",
        want=[
            Token(TokenType.ROOT, "$", 0, "$[?foo(42, -7)]"),
            Token(TokenType.LBRACKET, "[", 1, "$[?foo(42, -7)]"),
            Token(TokenType.FILTER, "?", 2, "$[?foo(42, -7)]"),
            Token(TokenType.FUNCTION, "foo", 3, "$[?foo(42, -7)]"),
            Token(TokenType.INT, "42", 7, "$[?foo(42, -7)]"),
            Token(TokenType.COMMA, ",", 9, "$[?foo(42, -7)]"),
            Token(TokenType.INT, "-7", 11, "$[?foo(42, -7)]"),
            Token(TokenType.RPAREN, ")", 13, "$[?foo(42, -7)]"),
            Token(TokenType.RBRACKET, "]", 14, "$[?foo(42, -7)]"),
            Token(TokenType.EOF, "", 15, "$[?foo(42, -7)]"),
        ],
    ),
    Case(
        description="boolean literals",
        path="$[?true==false]",
        want=[
            Token(TokenType.ROOT, "$", 0, "$[?true==false]"),
            Token(TokenType.LBRACKET, "[", 1, "$[?true==false]"),
            Token(TokenType.FILTER, "?", 2, "$[?true==false]"),
            Token(TokenType.TRUE, "true", 3, "$[?true==false]"),
            Token(TokenType.EQ, "==", 7, "$[?true==false]"),
            Token(TokenType.FALSE, "false", 9, "$[?true==false]"),
            Token(TokenType.RBRACKET, "]", 14, "$[?true==false]"),
            Token(TokenType.EOF, "", 15, "$[?true==false]"),
        ],
    ),
    Case(
        description="logical and",
        path="$[?true && false]",
        want=[
            Token(TokenType.ROOT, "$", 0, "$[?true && false]"),
            Token(TokenType.LBRACKET, "[", 1, "$[?true && false]"),
            Token(TokenType.FILTER, "?", 2, "$[?true && false]"),
            Token(TokenType.TRUE, "true", 3, "$[?true && false]"),
            Token(TokenType.AND, "&&", 8, "$[?true && false]"),
            Token(TokenType.FALSE, "false", 11, "$[?true && false]"),
            Token(TokenType.RBRACKET, "]", 16, "$[?true && false]"),
            Token(TokenType.EOF, "", 17, "$[?true && false]"),
        ],
    ),
    Case(
        description="float",
        path="$[?@.foo > 42.7]",
        want=[
            Token(TokenType.ROOT, "$", 0, "$[?@.foo > 42.7]"),
            Token(TokenType.LBRACKET, "[", 1, "$[?@.foo > 42.7]"),
            Token(TokenType.FILTER, "?", 2, "$[?@.foo > 42.7]"),
            Token(TokenType.CURRENT, "@", 3, "$[?@.foo > 42.7]"),
            Token(TokenType.PROPERTY, "foo", 5, "$[?@.foo > 42.7]"),
            Token(TokenType.GT, ">", 9, "$[?@.foo > 42.7]"),
            Token(TokenType.FLOAT, "42.7", 11, "$[?@.foo > 42.7]"),
            Token(TokenType.RBRACKET, "]", 15, "$[?@.foo > 42.7]"),
            Token(TokenType.EOF, "", 16, "$[?@.foo > 42.7]"),
        ],
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_lexer(case: Case) -> None:
    lexer, tokens = lex(case.path)
    lexer.run()
    assert lexer.tokens == case.want