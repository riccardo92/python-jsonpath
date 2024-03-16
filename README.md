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

### `find(query, value)`

Apply JSONPath expression _query_ to _value_. _value_ should arbitrary, possible nested, Python dictionaries, lists, strings, integers, floats, Booleans or `None`, as you would get from [`json.load()`](https://docs.python.org/3/library/json.html#json.load).

A list of `JSONPathNode` instances is returned, one node for each value matched by _path_. The returned list will be empty if there were no matches.

Each `JSONPathNode` has:

- a `value` property, which is the JSON-like value associated with the node.
- a `location` property, which is a tuple of property names and array/list indexes that were required to reach the node's value in the target JSON document.
- a `path()` method, which returns the normalized path to the node in the target JSON document.

The returned list is a subclass of `list` with some helper methods.

- `values()` returns a list of values, one for each node.
- `values_or_singular()` returns a scalar value if the list has exactly one node, or a list of values otherwise.

**Example:**

```python
import jsonpath_rfc9535 as jsonpath

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

### finditer(query, value)

`finditer()` accepts the same arguments as [`find()`](#findquery-value), but returns an iterator over `JSONPathNode` instances rather than a list. This could be useful if you're expecting a large number of results that you don't want to load into memory all at once.

## License

`python-jsonpath-rfc9535` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
