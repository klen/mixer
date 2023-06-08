from __future__ import annotations

from typing import Callable, TypeVar

TV = TypeVar("TV")
TGen = Callable[..., TV]
TFactory = Callable[..., TGen[TV]]
TNone = type(None)
