"""Test cases from the original article by Stefan Gössner.

See https://goessner.net/articles/JsonPath/
"""

import dataclasses
import operator
from typing import Any
from typing import Dict
from typing import List
from typing import Union

import pytest
from jsonpath_ext import JSONPathEnvironment


@dataclasses.dataclass
class Case:
    description: str
    query: str
    data: Union[List[Any], Dict[str, Any]]
    want: Union[List[Any], Dict[str, Any]]


REFERENCE_DATA = {
    "store": {
        "book": [
            {
                "category": "reference",
                "author": "Nigel Rees",
                "title": "Sayings of the Century",
                "price": 8.95,
            },
            {
                "category": "fiction",
                "author": "Evelyn Waugh",
                "title": "Sword of Honour",
                "price": 12.99,
            },
            {
                "category": "fiction",
                "author": "Herman Melville",
                "title": "Moby Dick",
                "isbn": "0-553-21311-3",
                "price": 8.99,
            },
            {
                "category": "fiction",
                "author": "J. R. R. Tolkien",
                "title": "The Lord of the Rings",
                "isbn": "0-395-19395-8",
                "price": 22.99,
            },
        ],
        "bicycle": {"color": "red", "price": 19.95},
    }
}

TEST_CASES = [
    Case(
        description="(reference) authors of all books in store",
        query="$.store.book[*].author",
        data=REFERENCE_DATA,
        want=["Nigel Rees", "Evelyn Waugh", "Herman Melville", "J. R. R. Tolkien"],
    ),
    Case(
        description="(reference) all authors",
        query="$..author",
        data=REFERENCE_DATA,
        want=["Nigel Rees", "Evelyn Waugh", "Herman Melville", "J. R. R. Tolkien"],
    ),
    Case(
        description="(reference) all store items",
        query="$.store.*",
        data=REFERENCE_DATA,
        want=[
            [
                {
                    "category": "reference",
                    "author": "Nigel Rees",
                    "title": "Sayings of the Century",
                    "price": 8.95,
                },
                {
                    "category": "fiction",
                    "author": "Evelyn Waugh",
                    "title": "Sword of Honour",
                    "price": 12.99,
                },
                {
                    "category": "fiction",
                    "author": "Herman Melville",
                    "title": "Moby Dick",
                    "isbn": "0-553-21311-3",
                    "price": 8.99,
                },
                {
                    "category": "fiction",
                    "author": "J. R. R. Tolkien",
                    "title": "The Lord of the Rings",
                    "isbn": "0-395-19395-8",
                    "price": 22.99,
                },
            ],
            {"color": "red", "price": 19.95},
        ],
    ),
    Case(
        description="(reference) prices of all store items",
        query="$.store..price",
        data=REFERENCE_DATA,
        want=[8.95, 12.99, 8.99, 22.99, 19.95],
    ),
    Case(
        description="(reference) the third book",
        query="$..book[2]",
        data=REFERENCE_DATA,
        want=[
            {
                "category": "fiction",
                "author": "Herman Melville",
                "title": "Moby Dick",
                "isbn": "0-553-21311-3",
                "price": 8.99,
            }
        ],
    ),
    Case(
        description="(reference) the last book",
        query="$..book[-1:]",
        data=REFERENCE_DATA,
        want=[
            {
                "category": "fiction",
                "author": "J. R. R. Tolkien",
                "title": "The Lord of the Rings",
                "isbn": "0-395-19395-8",
                "price": 22.99,
            }
        ],
    ),
    Case(
        description="(reference) the first two books",
        query="$..book[0,1]",
        data=REFERENCE_DATA,
        want=[
            {
                "category": "reference",
                "author": "Nigel Rees",
                "title": "Sayings of the Century",
                "price": 8.95,
            },
            {
                "category": "fiction",
                "author": "Evelyn Waugh",
                "title": "Sword of Honour",
                "price": 12.99,
            },
        ],
    ),
    Case(
        description="(reference) the first two books slice notation",
        query="$..book[:2]",
        data=REFERENCE_DATA,
        want=[
            {
                "category": "reference",
                "author": "Nigel Rees",
                "title": "Sayings of the Century",
                "price": 8.95,
            },
            {
                "category": "fiction",
                "author": "Evelyn Waugh",
                "title": "Sword of Honour",
                "price": 12.99,
            },
        ],
    ),
    Case(
        description="(reference) filter books with ISBN number",
        query="$..book[?(@.isbn)]",
        data=REFERENCE_DATA,
        want=[
            {
                "category": "fiction",
                "author": "Herman Melville",
                "title": "Moby Dick",
                "isbn": "0-553-21311-3",
                "price": 8.99,
            },
            {
                "category": "fiction",
                "author": "J. R. R. Tolkien",
                "title": "The Lord of the Rings",
                "isbn": "0-395-19395-8",
                "price": 22.99,
            },
        ],
    ),
    Case(
        description="(reference) filter books cheaper than 10",
        query="$..book[?(@.price<10)]",
        data=REFERENCE_DATA,
        want=[
            {
                "category": "reference",
                "author": "Nigel Rees",
                "title": "Sayings of the Century",
                "price": 8.95,
            },
            {
                "category": "fiction",
                "author": "Herman Melville",
                "title": "Moby Dick",
                "isbn": "0-553-21311-3",
                "price": 8.99,
            },
        ],
    ),
    # Case(
    #     description="root descent",
    #     query="$..",
    #     data=REFERENCE_DATA,
    #     want=[
    #         {
    #             "store": {
    #                 "book": [
    #                     {
    #                         "category": "reference",
    #                         "author": "Nigel Rees",
    #                         "title": "Sayings of the Century",
    #                         "price": 8.95,
    #                     },
    #                     {
    #                         "category": "fiction",
    #                         "author": "Evelyn Waugh",
    #                         "title": "Sword of Honour",
    #                         "price": 12.99,
    #                     },
    #                     {
    #                         "category": "fiction",
    #                         "author": "Herman Melville",
    #                         "title": "Moby Dick",
    #                         "isbn": "0-553-21311-3",
    #                         "price": 8.99,
    #                     },
    #                     {
    #                         "category": "fiction",
    #                         "author": "J. R. R. Tolkien",
    #                         "title": "The Lord of the Rings",
    #                         "isbn": "0-395-19395-8",
    #                         "price": 22.99,
    #                     },
    #                 ],
    #                 "bicycle": {"color": "red", "price": 19.95},
    #             }
    #         },
    #         {
    #             "book": [
    #                 {
    #                     "category": "reference",
    #                     "author": "Nigel Rees",
    #                     "title": "Sayings of the Century",
    #                     "price": 8.95,
    #                 },
    #                 {
    #                     "category": "fiction",
    #                     "author": "Evelyn Waugh",
    #                     "title": "Sword of Honour",
    #                     "price": 12.99,
    #                 },
    #                 {
    #                     "category": "fiction",
    #                     "author": "Herman Melville",
    #                     "title": "Moby Dick",
    #                     "isbn": "0-553-21311-3",
    #                     "price": 8.99,
    #                 },
    #                 {
    #                     "category": "fiction",
    #                     "author": "J. R. R. Tolkien",
    #                     "title": "The Lord of the Rings",
    #                     "isbn": "0-395-19395-8",
    #                     "price": 22.99,
    #                 },
    #             ],
    #             "bicycle": {"color": "red", "price": 19.95},
    #         },
    #         [
    #             {
    #                 "category": "reference",
    #                 "author": "Nigel Rees",
    #                 "title": "Sayings of the Century",
    #                 "price": 8.95,
    #             },
    #             {
    #                 "category": "fiction",
    #                 "author": "Evelyn Waugh",
    #                 "title": "Sword of Honour",
    #                 "price": 12.99,
    #             },
    #             {
    #                 "category": "fiction",
    #                 "author": "Herman Melville",
    #                 "title": "Moby Dick",
    #                 "isbn": "0-553-21311-3",
    #                 "price": 8.99,
    #             },
    #             {
    #                 "category": "fiction",
    #                 "author": "J. R. R. Tolkien",
    #                 "title": "The Lord of the Rings",
    #                 "isbn": "0-395-19395-8",
    #                 "price": 22.99,
    #             },
    #         ],
    #         {
    #             "category": "reference",
    #             "author": "Nigel Rees",
    #             "title": "Sayings of the Century",
    #             "price": 8.95,
    #         },
    #         {
    #             "category": "fiction",
    #             "author": "Evelyn Waugh",
    #             "title": "Sword of Honour",
    #             "price": 12.99,
    #         },
    #         {
    #             "category": "fiction",
    #             "author": "Herman Melville",
    #             "title": "Moby Dick",
    #             "isbn": "0-553-21311-3",
    #             "price": 8.99,
    #         },
    #         {
    #             "category": "fiction",
    #             "author": "J. R. R. Tolkien",
    #             "title": "The Lord of the Rings",
    #             "isbn": "0-395-19395-8",
    #             "price": 22.99,
    #         },
    #         {"color": "red", "price": 19.95},
    #     ],
    # ),
    Case(
        description="(reference) all elements",
        query="$..*",
        data=REFERENCE_DATA,
        want=[
            {
                "book": [
                    {
                        "category": "reference",
                        "author": "Nigel Rees",
                        "title": "Sayings of the Century",
                        "price": 8.95,
                    },
                    {
                        "category": "fiction",
                        "author": "Evelyn Waugh",
                        "title": "Sword of Honour",
                        "price": 12.99,
                    },
                    {
                        "category": "fiction",
                        "author": "Herman Melville",
                        "title": "Moby Dick",
                        "isbn": "0-553-21311-3",
                        "price": 8.99,
                    },
                    {
                        "category": "fiction",
                        "author": "J. R. R. Tolkien",
                        "title": "The Lord of the Rings",
                        "isbn": "0-395-19395-8",
                        "price": 22.99,
                    },
                ],
                "bicycle": {"color": "red", "price": 19.95},
            },
            [
                {
                    "category": "reference",
                    "author": "Nigel Rees",
                    "title": "Sayings of the Century",
                    "price": 8.95,
                },
                {
                    "category": "fiction",
                    "author": "Evelyn Waugh",
                    "title": "Sword of Honour",
                    "price": 12.99,
                },
                {
                    "category": "fiction",
                    "author": "Herman Melville",
                    "title": "Moby Dick",
                    "isbn": "0-553-21311-3",
                    "price": 8.99,
                },
                {
                    "category": "fiction",
                    "author": "J. R. R. Tolkien",
                    "title": "The Lord of the Rings",
                    "isbn": "0-395-19395-8",
                    "price": 22.99,
                },
            ],
            {"color": "red", "price": 19.95},
            {
                "category": "reference",
                "author": "Nigel Rees",
                "title": "Sayings of the Century",
                "price": 8.95,
            },
            {
                "category": "fiction",
                "author": "Evelyn Waugh",
                "title": "Sword of Honour",
                "price": 12.99,
            },
            {
                "category": "fiction",
                "author": "Herman Melville",
                "title": "Moby Dick",
                "isbn": "0-553-21311-3",
                "price": 8.99,
            },
            {
                "category": "fiction",
                "author": "J. R. R. Tolkien",
                "title": "The Lord of the Rings",
                "isbn": "0-395-19395-8",
                "price": 22.99,
            },
            "reference",
            "Nigel Rees",
            "Sayings of the Century",
            8.95,
            "fiction",
            "Evelyn Waugh",
            "Sword of Honour",
            12.99,
            "fiction",
            "Herman Melville",
            "Moby Dick",
            "0-553-21311-3",
            8.99,
            "fiction",
            "J. R. R. Tolkien",
            "The Lord of the Rings",
            "0-395-19395-8",
            22.99,
            "red",
            19.95,
        ],
    ),
]


@pytest.fixture()
def env() -> JSONPathEnvironment:
    return JSONPathEnvironment()


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_goessner(env: JSONPathEnvironment, case: Case) -> None:
    path = env.compile(case.query)
    assert path.find(case.data).values() == case.want
