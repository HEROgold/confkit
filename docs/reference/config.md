---
title: Config Descriptor
---

# Config Descriptor

This section provides curated guidance around the core `Config` descriptor and its decorators. For full auto-generated API documentation see the pdoc pages linked via the `pdoc:` references below.

## Core Class

- [`Config`](pdoc:confkit.Config) – Descriptor managing reading/writing typed values.

## Lifecycle / Initialization Helpers

- [`Config.set_parser`](pdoc:confkit.Config.set_parser)
- [`Config.set_file`](pdoc:confkit.Config.set_file)
- [`Config.write`](pdoc:confkit.Config.write)

## Runtime Flags

- [`Config.validate_types`](pdoc:confkit.Config.validate_types)
- [`Config.write_on_edit`](pdoc:confkit.Config.write_on_edit)

## Decorators

- [`Config.set`](pdoc:confkit.Config.set) – Always set a value before calling a function.
- [`Config.default`](pdoc:confkit.Config.default) – Set only when unset.
- [`Config.with_setting`](pdoc:confkit.Config.with_setting) – Inject an existing descriptor value as a kwarg.
- [`Config.with_kwarg`](pdoc:confkit.Config.with_kwarg) – (Named `with_kwarg` in code; often described as `with_kwarg`) inject by section/setting with optional rename & default.

## Internal Validation (Selected)

- [`Config.validate_file`](pdoc:confkit.Config.validate_file)
- [`Config.validate_parser`](pdoc:confkit.Config.validate_parser)
- [`Config.validate_strict_type`](pdoc:confkit.Config.validate_strict_type)

> Tip: Use the decorators for imperative flows and prefer descriptor attributes for normal configuration access.
>
## Class vs Instance Access

Reading configuration values works the same whether you access a `Config` descriptor from the class or from an instance, but setting behaves differently and is important to understand:

- Reading: You may read values using either the class or an instance.
  - Example: `AppConfig.debug` and `AppConfig().debug` will both return the current value.
- Setting: To write a value back through the `Config` descriptor you must assign on an *instance*.
  - Example: `cfg = AppConfig(); cfg.debug = True` will persist the descriptor.
  - Assigning to `AppConfig.debug = True` (class-level assignment) does not go through the instance write-path and therefore will not behave like an instance write, overriding the entire descriptor.

If you need class-level assignment semantics (so that `AppConfig.debug = True` updates configuration), use the provided metaclass `ConfigContainerMeta`. This metaclass adjusts container behavior so class access can be used for setting values. See `tests/test_metaclass.py` for a concrete example of using `ConfigContainerMeta` in the test-suite.
