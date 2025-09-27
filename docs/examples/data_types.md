# Data Types Example ([`data_types.py`](https://github.com/HEROgold/confkit/blob/master/examples/data_types.py))

## Purpose

Showcases the breadth of built-in and helper data types:

- Explicit vs implicit (auto-detected) types
- Numeric formatting ([Hex](pdoc:confkit.Hex), [Octal](pdoc:confkit.Octal), [Binary](pdoc:confkit.Binary))
- Custom base integers (encoded as `<base>c<value>` in the file)
- Bytes → integer conversion via [`Binary`](pdoc:confkit.Binary)

## Running

```bash
uv run python examples/data_types.py
```

## Generated `config.ini` (Excerpt)

Values may accumulate across runs; representative first-run section:

```ini
[DataTypeConfig]
string_value = default string
int_value = 42
float_value = 3.14159
bool_value = True
auto_string = auto-detected string
auto_int = 100
auto_float = 2.71828
auto_bool = False
hex_value = 0xff
octal_value = 0o755
binary_value = 0b10101010
binary_from_bytes = 0b0110100001100101011011000110110001101111
base7_value = 7c42
base5_value = 5c13
```

After updates inside the script, the file reflects the new values (hex, octal, binary adjustments).

## Notes

- Changing `base` persists a prefixed representation so it can be reliably parsed later.
- `Binary` will store integers; when constructed from `bytes`, those bytes are interpreted as a big-endian integer.

## Try Variations

- Manually edit `hex_value` to `0x1a2b` and re-run.
- Remove `binary_from_bytes` line; script re-creates it.

## Custom Type Extension

See the separate custom data type example [`examples/custom_data_type.py`](https://github.com/HEROgold/confkit/blob/master/examples/custom_data_type.py) for how to implement and register your own converter (e.g. an `UpperString` normalizer) by subclassing `BaseDataType`.
