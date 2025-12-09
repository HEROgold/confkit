---
title: Data Types
---

# Data Types

confkit uses a family of small converter classes to provide type safety and round‑trip serialization.

## Base Type

- [`BaseDataType`](pdoc:confkit.BaseDataType)
  - [`BaseDataType.convert`](pdoc:confkit.BaseDataType.convert)
  - [`BaseDataType.validate`](pdoc:confkit.BaseDataType.validate)
  - [`BaseDataType.cast`](pdoc:confkit.BaseDataType.cast)
  - [`BaseDataType.cast_optional`](pdoc:confkit.BaseDataType.cast_optional)

## Primitive Converters

- [`String`](pdoc:confkit.String)
- [`Integer`](pdoc:confkit.Integer)
- [`Float`](pdoc:confkit.Float)
- [`Boolean`](pdoc:confkit.Boolean)
- [`NoneType`](pdoc:confkit.NoneType)

## Enum Converters

- [`Enum`](pdoc:confkit.Enum)
- [`StrEnum`](pdoc:confkit.StrEnum)
- [`IntEnum`](pdoc:confkit.IntEnum)
- [`IntFlag`](pdoc:confkit.IntFlag)

## Number Representation Helpers

- [`Hex`](pdoc:confkit.Hex)
- [`Octal`](pdoc:confkit.Octal)
- [`Binary`](pdoc:confkit.Binary)

## Optional & Composite

- [`Optional`](pdoc:confkit.Optional)
- [`List`](pdoc:confkit.List)

> Design note: `Optional` wraps another `BaseDataType` and returns `None` when a null sentinel is parsed.

## Collections

- [`Tuple`](pdoc:confkit.Tuple)
- [`Set`](pdoc:confkit.Set)
- [`Dict`](pdoc:confkit.Dict)

`Tuple`, `Set`, and `Dict` mirror their built‑in counterparts. Allowing for collections to be stored in INI files.

## Date & Time

- [`DateTime`](pdoc:confkit.DateTime)
- [`Date`](pdoc:confkit.Date)
- [`Time`](pdoc:confkit.Time)
- [`TimeDelta`](pdoc:confkit.TimeDelta)

`DateTime`, `Date`, `Time` and `TimeDelta` mirror their built-in counterparts. Allowing to store date information in INI files.

## Custom Type Example

- [`BaseDataType`](pdoc:confkit.BaseDataType)
