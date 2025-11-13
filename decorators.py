from __future__ import annotations
from functools import wraps
from typing import TypeVar
from typing import Callable

T = TypeVar("T")
U = TypeVar("U")


def optional(transform: Callable[[T], U]) -> Callable[[T | None], U | None]:
    """
    Wrap a transformation function to handle None values gracefully.
    """

    @wraps(transform)
    def wrapper(value: T | None) -> U | None:
        if value is None:
            return None
        return transform(value)

    return wrapper
