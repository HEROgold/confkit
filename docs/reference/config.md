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
