from __future__ import annotations

import dataclasses as dc
from typing import Any, Callable, Dict, TypeVar

from mixer.factories.utils import get

TV = TypeVar("TV")
TGen = Callable[..., TV]
TFactory = Callable[..., TGen[TV]]
TNone = type(None)
TValues = Dict[str, Any]


@dc.dataclass(eq=False, slots=True)
class MixerValues:
    """Mixer values class."""

    path: list[str] = dc.field(default_factory=list)

    def __getattr__(self, name):
        self.path.append(name)
        return self

    def __call__(self, value):
        """Get a value from the given values."""
        for part in self.path:
            value = get(value, part)

        return value
