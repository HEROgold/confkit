---
title: Data Types
---

# Data Types

confkit uses a family of small converter classes to provide type safety and round‑trip serialization.

## Base Type

- [BaseDataType](/confkit/api/confkit.html#BaseDataType)
  - [BaseDataType.convert](/confkit/api/confkit.html#BaseDataType.convert)
  - [BaseDataType.validate](/confkit/api/confkit.html#BaseDataType.validate)
  - [BaseDataType.cast](/confkit/api/confkit.html#BaseDataType.cast)
  - [BaseDataType.cast_optional](/confkit/api/confkit.html#BaseDataType.cast_optional)

## Primitive Converters

- [String](/confkit/api/confkit.html#String)
- [Integer](/confkit/api/confkit.html#Integer)
- [Float](/confkit/api/confkit.html#Float)
- [Boolean](/confkit/api/confkit.html#Boolean)
- [NoneType](/confkit/api/confkit.html#NoneType)

## Enum Converters

- [Enum](/confkit/api/confkit.html#Enum)
- [StrEnum](/confkit/api/confkit.html#StrEnum)
- [IntEnum](/confkit/api/confkit.html#IntEnum)
- [IntFlag](/confkit/api/confkit.html#IntFlag)

All enum types automatically display allowed values as inline comments in the config file, making them self-documenting for end-users. For example:

```ini
log_level = info  # allowed: debug, info, warning, error
```

The format varies by enum type:
- **StrEnum**: Shows member values (e.g., `debug, info, warning, error`)
- **IntEnum/IntFlag**: Shows member names with integer values (e.g., `LOW(0), MEDIUM(5), HIGH(10)`)
- **Enum**: Shows member names (e.g., `DEBUG, INFO, WARNING, ERROR`)

Comments are automatically stripped when reading values, ensuring they don't interfere with parsing.

## Number Representation Helpers

- [Hex](/confkit/api/confkit.html#Hex)
- [Octal](/confkit/api/confkit.html#Octal)
- [Binary](/confkit/api/confkit.html#Binary)

## Optional & Composite

- [Optional](/confkit/api/confkit.html#Optional)
- [List](/confkit/api/confkit.html#List)

> Design note: `Optional` wraps another `BaseDataType` and returns `None` when a null sentinel is parsed.

## Collections

- [Tuple](/confkit/api/confkit.html#Tuple)
- [Set](/confkit/api/confkit.html#Set)
- [Dict](/confkit/api/confkit.html#Dict)

`Tuple`, `Set`, and `Dict` mirror their built‑in counterparts. Allowing for collections to be stored in INI files.

## Date & Time

- [DateTime](/confkit/api/confkit.html#DateTime)
- [Date](/confkit/api/confkit.html#Date)
- [Time](/confkit/api/confkit.html#Time)
- [TimeDelta](/confkit/api/confkit.html#TimeDelta)

`DateTime`, `Date`, `Time` and `TimeDelta` mirror their built-in counterparts. Allowing to store date information in INI files.

## Custom Type Example

- [BaseDataType](/confkit/api/confkit.html#BaseDataType)
