---
title: Multiple Instances Behavior
---

# Multiple Instances Behavior

- **Test reference:** `tests/test_two_instances.py` — verifies that two instances of the same `Config`-container class observe the same values and that the descriptor-level `on_file_change` handler is invoked when the backing file is updated.
- **Singleton-like behavior:** When multiple instances are created from the same config-container class, they share the underlying parser and descriptor state. Mutating a value through one instance (or via the descriptor) is observable from the other instance; this is effectively a shared/singleton configuration surface backed by a single parser.
- **Descriptor-level hooks:** `on_file_change` is attached to the descriptor (not per-instance) in the test. This means file-change callbacks are shared across instances of the same config class and will fire when the `FileWatcher` indicates the file has changed.
- **Practical implication:** Treat config-container classes as views over a shared configuration store. Writes performed on any instance or via the descriptor update the shared parser and (when enabled) persist to the configured file.
