"""JSONPath query expression lexical scanner."""

from __future__ import annotations

import re
from functools import partial
from typing import TYPE_CHECKING
from typing import Iterator
from typing import List
from typing import Pattern
from typing import Tuple

from .exceptions import JSONPathSyntaxError
from .tokens import Token
from .tokens import TokenType

if TYPE_CHECKING:
    from .environment import JSONPathEnvironment


class Lexer:
    """Lexical scanner for JSONPath query expressions."""

    def __init__(self, *, env: JSONPathEnvironment) -> None:
        self.env = env
        self.rules = self.compile_rules()

    def compile_rules(self) -> Pattern[str]:
        """Prepare regular expression rules."""
        rules: List[Tuple[TokenType, str]] = [
            (TokenType.DOUBLE_QUOTE_STRING, r'"(?P<G_DQUOTE>(?:(?!(?<!\\)").)*)"'),
            (TokenType.SINGLE_QUOTE_STRING, r"'(?P<G_SQUOTE>(?:(?!(?<!\\)').)*)'"),
            (
                TokenType.SLICE,
                (
                    r"(?P<G_SLICE_START>\-?\d*)\s*"
                    r":\s*(?P<G_SLICE_STOP>\-?\d*)\s*"
                    r"(?::\s*(?P<G_SLICE_STEP>\-?\d*))?"
                ),
            ),
            (TokenType.FUNCTION, r"(?P<G_FUNC>[a-z][a-z_0-9]+)\(\s*"),
            (
                TokenType.DOT_PROPERTY,
                r"\.(?P<G_PROP>[\u0080-\uFFFFa-zA-Z_][\u0080-\uFFFFa-zA-Z0-9_-]*)",
            ),
            (TokenType.FLOAT, r"-?\d+\.\d*(?:e[+-]?\d+)?"),
            (TokenType.INT, r"-?\d+(?P<G_EXP>e[+\-]?\d+)?\b"),
            (TokenType.DOUBLE_DOT, r"\.\."),
            (TokenType.AND, r"&&"),
            (TokenType.OR, r"\|\|"),
            (TokenType.ROOT, r"\$"),
            (TokenType.CURRENT, r"@"),
            (TokenType.WILD, r"\*"),
            (TokenType.FILTER, r"\?"),
            (TokenType.TRUE, r"true"),
            (TokenType.FALSE, r"false"),
            (TokenType.NULL, r"null"),
            (TokenType.LBRACKET, r"\["),
            (TokenType.RBRACKET, r"]"),
            (TokenType.COMMA, r","),
            (TokenType.EQ, r"=="),
            (TokenType.NE, r"!="),
            (TokenType.LG, r"<>"),
            (TokenType.LE, r"<="),
            (TokenType.GE, r">="),
            (TokenType.LT, r"<"),
            (TokenType.GT, r">"),
            (TokenType.NOT, r"!"),
            (
                TokenType.SHORTHAND_PROPERTY,
                r"[\u0080-\uFFFFa-zA-Z_][\u0080-\uFFFFa-zA-Z0-9_-]*",
            ),
            (TokenType.LPAREN, r"\("),
            (TokenType.RPAREN, r"\)"),
            (TokenType.SKIP, r"[ \n\t\r\.]+"),  # TODO: dots
            (TokenType.ILLEGAL, r"."),
        ]

        return re.compile(
            "|".join([f"(?P<{token.name}>{pattern})" for token, pattern in rules]),
            re.DOTALL,
        )

    def tokenize(self, path: str) -> Iterator[Token]:  # noqa PLR0912
        """Generate a sequence of tokens from a JSONPath string."""
        _token = partial(Token, path=path)

        for match in self.rules.finditer(path):
            kind = match.lastgroup
            assert kind is not None

            if kind == TokenType.DOT_PROPERTY.name:
                yield _token(
                    kind=TokenType.PROPERTY,
                    value=match.group("G_PROP"),
                    index=match.start("G_PROP"),
                )
            elif kind == TokenType.SHORTHAND_PROPERTY.name:
                yield _token(
                    kind=TokenType.PROPERTY,
                    value=match.group(),
                    index=match.start(),
                )
            elif kind == TokenType.SLICE.name:
                yield _token(
                    kind=TokenType.SLICE_START,
                    value=match.group("G_SLICE_START"),
                    index=match.start("G_SLICE_START"),
                )
                yield _token(
                    kind=TokenType.SLICE_STOP,
                    value=match.group("G_SLICE_STOP"),
                    index=match.start("G_SLICE_STOP"),
                )
                yield _token(
                    kind=TokenType.SLICE_STEP,
                    value=match.group("G_SLICE_STEP") or "",
                    index=match.start("G_SLICE_STEP"),
                )
            elif kind == TokenType.DOUBLE_QUOTE_STRING.name:
                yield _token(
                    kind=TokenType.DOUBLE_QUOTE_STRING,
                    value=match.group("G_DQUOTE"),
                    index=match.start("G_DQUOTE"),
                )
            elif kind == TokenType.SINGLE_QUOTE_STRING.name:
                yield _token(
                    kind=TokenType.SINGLE_QUOTE_STRING,
                    value=match.group("G_SQUOTE"),
                    index=match.start("G_SQUOTE"),
                )
            elif kind == TokenType.INT.name:
                if match.group("G_EXP") and match.group("G_EXP")[1] == "-":
                    yield _token(
                        kind=TokenType.FLOAT,
                        value=match.group(),
                        index=match.start(),
                    )
                else:
                    yield _token(
                        kind=TokenType.INT,
                        value=match.group(),
                        index=match.start(),
                    )
            elif kind == TokenType.FUNCTION.name:
                yield _token(
                    kind=TokenType.FUNCTION,
                    value=match.group("G_FUNC"),
                    index=match.start("G_FUNC"),
                )
            elif kind == TokenType.SKIP.name:
                continue
            elif kind == TokenType.ILLEGAL.name:
                raise JSONPathSyntaxError(
                    f"unexpected token {match.group()!r}",
                    token=_token(
                        TokenType.ILLEGAL,
                        value=match.group(),
                        index=match.start(),
                    ),
                )
            else:
                yield _token(
                    kind=TokenType[kind],
                    value=match.group(),
                    index=match.start(),
                )
