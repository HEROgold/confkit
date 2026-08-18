---
title: Exceptions
---

# Exceptions

The library raises a small, focused set of exceptions for invalid defaults and converter errors.

- [InvalidDefaultError](/confkit/api/confkit.html#InvalidDefaultError)
- [InvalidConverterError](/confkit/api/confkit.html#InvalidConverterError)

These both subclass `ValueError` to keep failure modes familiar while allowing precise catching.
