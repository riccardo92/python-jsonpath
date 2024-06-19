<h1 align="center">RFC 9535 JSONPath: Query Expressions for JSON in Python</h1>

<p align="center">
We follow <a href="https://datatracker.ietf.org/doc/html/rfc9535">RFC 9535</a> strictly and test against the <a href="https://github.com/jsonpath-standard/jsonpath-compliance-test-suite">JSONPath Compliance Test Suite</a>.
</p>

<p align="center">
  <a href="https://github.com/riccardo92/python-jsonpath-ext/blob/main/LICENSE.txt">
    <img src="https://img.shields.io/pypi/l/jsonpath-ext.svg?style=flat-square" alt="License">
  </a>
  <a href="https://github.com/riccardo92/python-jsonpath-ext/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/jg-rp/python-jsonpath-ext/tests.yaml?branch=main&label=tests&style=flat-square" alt="Tests">
  </a>
  <br>
  <a href="https://pypi.org/project/jsonpath-ext">
    <img src="https://img.shields.io/pypi/v/jsonpath-ext.svg?style=flat-square" alt="PyPi - Version">
  </a>
  <a href="https://pypi.org/project/jsonpath-ext">
    <img src="https://img.shields.io/pypi/pyversions/jsonpath-ext.svg?style=flat-square" alt="Python versions">
  </a>
</p>

---

**Table of Contents**

- [Install](#install)
- [Example](#example)
- [Links](#links)
- [Related projects](#related-projects)
- [API](#api)
- [License](#license)

## Install

Install Python JSONPath RFC 9535 using [pip](https://pip.pypa.io/en/stable/getting-started/):

```
pip install jsonpath-ext
```

Or [Pipenv](https://pipenv.pypa.io/en/latest/):

```
pipenv install -u jsonpath-ext
```

## Example

```python
import jsonpath_ext as jsonpath

data = {
    "users": [
        {"name": "Sue", "score": 100},
        {"name": "Sally", "score": 84, "admin": False},
        {"name": "John", "score": 86, "admin": True},
        {"name": "Jane", "score": 55},
    ],
    "moderator": "John",
}

for node in jsonpath.find("$.users[?@.score > 85]", data):
    print(node.value)

# {'name': 'Sue', 'score': 100}
# {'name': 'John', 'score': 86, 'admin': True}
```

Or, reading JSON data from a file:

```python
import json
import jsonpath_ext as jsonpath

with open("/path/to/some.json", encoding="utf-8") as fd:
    data = json.load(fd)

nodes = jsonpath.find("$.some.query", data)
values = nodes.values()
# ...
```

You could read data from a YAML formatted file too. If you have [PyYaml](https://pyyaml.org/wiki/PyYAML) installed:

```python
import jsonpath_ext as jsonpath
import yaml

with open("some.yaml") as fd:
    data = yaml.safe_load(fd)

products = jsonpath.find("$..products.*", data).values()
# ...
```

## Links

- Change log: https://github.com/riccardo92/python-jsonpath-ext/blob/main/CHANGELOG.md
- PyPi: https://pypi.org/project/jsonpath-ext
- Source code: https://github.com/riccardo92/python-jsonpath-ext
- Issue tracker: https://github.com/riccardo92/python-jsonpath-ext/issues

## Related projects

- [Python JSONPath](https://github.com/riccardo92/python-jsonpath) - Another Python package implementing JSONPath, but with additional features and customization options.
- [JSON P3](https://github.com/jg-rp/json-p3) - RFC 9535 implemented in TypeScript.

## API

### find

`find(query: str, value: JSONValue) -> JSONPathNodeList`

Apply JSONPath expression _query_ to _value_. _value_ should arbitrary, possible nested, Python dictionaries, lists, strings, integers, floats, Booleans or `None`, as you would get from [`json.load()`](https://docs.python.org/3/library/json.html#json.load).

A list of `JSONPathNode` instances is returned, one node for each value matched by _path_. The returned list will be empty if there were no matches.

Each `JSONPathNode` has:

- a `value` property, which is the JSON-like value associated with the node.
- a `location` property, which is a tuple of property names and array/list indexes that were required to reach the node's value in the target JSON document.
- a `path()` method, which returns the normalized path to the node in the target JSON document.

```python
import jsonpath_ext as jsonpath

value = {
    "users": [
        {"name": "Sue", "score": 100},
        {"name": "John", "score": 86, "admin": True},
        {"name": "Sally", "score": 84, "admin": False},
        {"name": "Jane", "score": 55},
    ],
    "moderator": "John",
}

for node in jsonpath.find("$.users[?@.score > 85]", value):
    print(f"{node.value} at '{node.path()}'")

# {'name': 'Sue', 'score': 100} at '$['users'][0]'
# {'name': 'John', 'score': 86, 'admin': True} at '$['users'][1]'
```

`JSONPathNodeList` is a subclass of `list` with some helper methods.

- `values()` returns a list of values, one for each node.
- `items()` returns a list of `(normalized path, value)` tuples.

### find_one

`find_one(query: str, value: JSONValue) -> Optional[JSONPathNode]`

`find_one()` accepts the same arguments as [`find()`](#findquery-value), but returns the first available `JSONPathNode`, or `None` if there were no matches.

`find_one()` is equivalent to:

```python
def find_one(query, value):
    try:
        return next(iter(jsonpath.finditer(query, value)))
    except StopIteration:
        return None
```

### finditer

`finditer(query: str, value: JSONValue) -> Iterable[JSONPathNode]`

`finditer()` accepts the same arguments as [`find()`](#findquery-value), but returns an iterator over `JSONPathNode` instances rather than a list. This could be useful if you're expecting a large number of results that you don't want to load into memory all at once.

### compile

`compile(query: str) -> JSONPathQuery`

`find(query, value)` is a convenience function for `JSONPathEnvironment().compile(query).apply(value)`. Use `compile(query)` to obtain a `JSONPathQuery` instance which can be applied to difference JSON-like values repeatedly.

```python
import jsonpath_ext as jsonpath

value = {
    "users": [
        {"name": "Sue", "score": 100},
        {"name": "John", "score": 86, "admin": True},
        {"name": "Sally", "score": 84, "admin": False},
        {"name": "Jane", "score": 55},
    ],
    "moderator": "John",
}

query = jsonpath.compile("$.users[?@.score > 85]")

for node in query.apply(value):
    print(f"{node.value} at '{node.path()}'")

# {'name': 'Sue', 'score': 100} at '$['users'][0]'
# {'name': 'John', 'score': 86, 'admin': True} at '$['users'][1]'
```

A `JSONPathQuery` has a `finditer(value)` method too, and `find(value)` is an alias for `apply(value)`.

## License

`python-jsonpath-ext` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
