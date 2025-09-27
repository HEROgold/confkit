# List Types Example ([`list_types.py`](https://github.com/HEROgold/confkit/blob/master/examples/list_types.py))

## Purpose

Shows how to work with list-based configuration values:

- Storing homogeneous lists of primitives
- Escaping separators & special characters
- Empty elements and explicit typed empty lists

## Running

```bash
uv run python examples/list_types.py
```

## Generated `config.ini` (Excerpt)

```ini
[ListConfig]
string_list = red,green,blue
int_list = 1,2,3,4,5
float_list = 1.1,2.2,3.3,4.4
bool_list = True,False,True
paths_list = /path/to/file1,C:\\path\\to\\file2
complex_list = item1,item\,with\,commas,normal item
with_empty = ,middle,
empty_list = 
```

## Notes

- See [`List.separator`](pdoc:confkit.List.separator) and [`List.escape_char`](pdoc:confkit.List.escape_char) for their default values (explicitly set in the example for clarity).
- Items containing the separator are escaped when written, then unescaped on read.
- An explicit empty list with a declared data type stays as a blank line after the equals sign.

## Try Variations

- Append a value manually to `int_list` in the file and re-run.
- Add a value containing a backslash and observe escaping.
