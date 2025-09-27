---
title: Exceptions
---

# Exceptions

The library raises a small, focused set of exceptions for invalid defaults and converter errors.

- [`InvalidDefaultError`](pdoc:confkit.InvalidDefaultError)
- [`InvalidConverterError`](pdoc:confkit.InvalidConverterError)

These both subclass `ValueError` to keep failure modes familiar while allowing precise catching.
