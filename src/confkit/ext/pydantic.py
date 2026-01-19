"""Helper utilities for working with Pydantic models and confkit."""

try:
    from pydantic import BaseModel
except ImportError as exc:
    msg = (
        "confkit.ext.pydantic requires the optional 'pydantic' extra. "
        "Install it via 'pip install "
        "confkit[pydantic]' or 'uv add confkit[pydantic]'."
    )
    raise ImportError(msg) from exc


def apply_model(config_instance: object, model: BaseModel) -> None:
    """Apply values from a Pydantic model to matching Config descriptors."""
    for field, value in model.model_dump().items():
        if hasattr(type(config_instance), field):
            setattr(config_instance, field, value)

__all__ = ["apply_model"]
