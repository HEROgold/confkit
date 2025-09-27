# Argparse Integration Example ([`argparse_example.py`](https://github.com/HEROgold/confkit/blob/master/examples/argparse_example.py))

## Purpose

Shows how to combine CLI argument parsing with confkit-backed defaults while keeping runtime-provided values separate from persisted configuration.

## Key Concepts

- Use descriptors to define defaults (`AppConfig`)
- Reuse those defaults when defining CLI args
- Disable write-on-edit (`Config.write_on_edit = False`) to avoid persisting transient CLI overrides
- Maintain a clean separation between runtime arguments and persistent config

## Running

```bash
uv run python examples/argparse_example.py --host 0.0.0.0 --port 9090 --debug --tags alpha beta
```

## Generated Files

Only `config.ini` is used for the descriptors; CLI values are not written because `write_on_edit` is disabled.

Example baseline (first run):

```ini
[AppConfig]
debug = False
host = 127.0.0.1
port = 8000
tags = example,demo
```

After running with overrides, the file remains unchanged (transient values do not persist):

```ini
[AppConfig]
debug = False
host = 127.0.0.1
port = 8000
tags = example,demo
```

## Notes

- If you enable `Config.write_on_edit = True`, assignments to descriptors (not argparse inputs) will persist.
- You can sync back only selected CLI values by explicitly assigning them to descriptors after parsing.

## Try Variations

- Manually edit `config.ini` default port and re-run with a different CLI value.
- Set `write_on_edit = True` temporarily and manually assign `AppConfig.port = args.port` after parsing.
