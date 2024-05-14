# Python JSONPath RFC 9535 Change Log

## Version 0.1.2

**Fixes**

- Handle end of query when lexing inside a filter expression.
- Check patterns passed to `search` and `match` are valid I-Regexp patterns. Both of these functions now return _LogicalFalse_ if the pattern is not valid according to RFC 9485.

## Version 0.1.1

Fix PyPi classifiers and README.

## Version 0.1.0

Initial release.
