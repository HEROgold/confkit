# Custom Data Type ([`custom_data_type.py`](https://github.com/HEROgold/confkit/blob/master/examples/custom_data_type.py))

## Purpose

Shows how to create and use a custom [`BaseDataType`](pdoc:confkit.BaseDataType) implementation.

- Normalize and persist a value in a consistent representation
- Demonstrate the required `convert` method
- (Optionally) override `__str__` for serialization formatting

## Implementation

```python
from configparser import ConfigParser
from pathlib import Path
from confkit import Config
from confkit.data_types import BaseDataType

# Configure parser + file
parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(Path("config.ini"))

class UpperString(BaseDataType[str]):
    """String that is always stored / returned in UPPER CASE."""
    def convert(self, value: str) -> str:  # raw INI -> normalized
        return str(value).upper()

    def __str__(self, value: str):  # normalized -> persisted string
        return value.upper()

class CustomCfg:
    shout_name = Config(UpperString("confkit"))

print(CustomCfg.shout_name)  # CONFKIT
CustomCfg.shout_name = "MixedCase"
print(CustomCfg.shout_name)  # MIXEDCASE
```

## Generated File Snippet

After the first run (values normalized):

```ini
[CustomCfg]
shout_name = CONFKIT
```

After reassignment:

```ini
[CustomCfg]
shout_name = MIXEDCASE
```

## Design Notes

- `convert` should raise an appropriate exception (let `BaseDataType.validate` help if you call it) when input cannot be parsed.
- Override `validate` if you need domain rules (e.g. length limits). Call `super().validate()` if stacking behavior.
- `__str__` mainly matters when you want the persisted form to differ from `str(value)`.

## Integration Checklist

1. Create subclass `class X(BaseDataType[T]):`
2. Implement `convert(self, value: str) -> T`
3. (Optional) override `__str__(self, value: T) -> str`
4. (Optional) override `validate(self, value: T)` for domain constraints.
5. Use with `Config(X(default_value))`

## Related Docs

- Usage Guide: [Adding a New Data Type](../usage.md#adding-a-new-data-type)
- Reference: [Data Types](../reference/data_types.md)
- Source example: [`examples/custom_data_type.py`](https://github.com/HEROgold/confkit/blob/master/examples/custom_data_type.py)
