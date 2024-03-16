# RFC 9535 JSONPath: Query Expressions for JSON in Python

We follow [RFC 9535](https://datatracker.ietf.org/doc/html/rfc9535) strictly and test against the [JSONPath Compliance Test Suite](https://github.com/jsonpath-standard/jsonpath-compliance-test-suite).

See also [Python JSONPath](https://github.com/jg-rp/python-jsonpath), which also follows RFC 9535, but with additional features and customization options.

---

**Table of Contents**

- [Install](#install)
- [Links](#links)
- [Usage](#usage)
- [License](#license)

## Install

TODO:

## Links

- Change log: https://github.com/jg-rp/python-jsonpath-rfc9535/blob/main/CHANGELOG.md
- PyPi: TODO
- Source code: https://github.com/jg-rp/python-jsonpath-rfc9535
- Issue tracker: https://github.com/jg-rp/python-jsonpath-rfc9535/issues

## Usage

NOTE: If you're coming from [Python JSONPath](https://github.com/jg-rp/python-jsonpath), this API is similar but different. Neither implementation is guaranteed to be a drop-in replacement for the other.

### `query(path, data)`

Apply JSONPath expression _path_ to _data_. _data_ should arbitrary, possible nested, Python dictionaries, lists, strings, integers, floats, booleans or `None`, as you would get from [`json.load()`](https://docs.python.org/3/library/json.html#json.load).

A list of `JSONPathNode` instances is returned, one node for each value in _data_ matched by _path_. The returned list will be empty if there were no matches.

Each `JSONPathNode` has:

- a `value` property, which is the JSON-like value associated with the node.
- a `parts` property, which is a tuple of property names and array/list indices that were required to reach the node's value in the target JSON document.
- a `path()` method, which returns the normalized path to the node in the target JSON document.

The returned list is a subclass of `list` with some helper methods.

- `values()` returns a list of values, one for each node.
- `values_or_singular()` returns a scalar value if the list has exactly one node, or a list of values otherwise.

**Example:**

```python
from jsonpath_rfc9535 import query

data = {
    "users": [
        {"name": "Sue", "score": 100},
        {"name": "John", "score": 86, "admin": True},
        {"name": "Sally", "score": 84, "admin": False},
        {"name": "Jane", "score": 55},
    ],
    "moderator": "John",
}

for node in query("$.users[?@.score > 85]", data):
    print(f"{node.value} at '{node.path()}'")

# {'name': 'Sue', 'score': 100} at '$['users'][0]'
# {'name': 'John', 'score': 86, 'admin': True} at '$['users'][1]'
```

### findall(path, data)

`findall()` accepts the same arguments as [`query()`](#querypath-data), but returns a list of value rather than a list of nodes.

`findall()` is equivalent to `query("$.some.thing", data).values()`.

### finditer(path, data)

`finditer()` accepts the same arguments as [`query()`](#querypath-data), but returns an iterator over `JSONPathNode` instances rather than a list. This could be useful if you're expecting a large number of results that you don't want to load into memory all at once.

## License

`python-jsonpath-rfc9535` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
