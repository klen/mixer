from __future__ import annotations

from contextlib import contextmanager
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Coroutine,
    Dict,
    Generator,
    Generic,
    Optional,
    Tuple,
    Type,
    cast,
)

from . import database as db
from .factories.constants import RANDOM, SKIP
from .factories.helpers import make_gen
from .factories.types import TV

if TYPE_CHECKING:
    from .types import TMixerParams


class Mixer:
    """Mixer class."""

    SKIP = SKIP
    RANDOM = RANDOM

    params: TMixerParams = {"fake": True, "commit": False}

    def __init__(self, *, fake: bool = True, commit: bool = False):
        self.params: TMixerParams = {"fake": fake, "commit": commit}
        self.__middlewares__: Dict[Type, Callable] = {}

    @contextmanager
    def ctx(self, **params):
        """Context manager."""
        old_params = self.params.copy()
        self.params.update(params)  # type: ignore[]
        yield
        self.params.update(old_params)

    def blend(self, mtype: Type[TV], **values) -> TV:
        """Blend method."""
        gen: Optional[Callable[..., TV]] = make_gen(mtype, **self.params)
        if gen is None:
            error_msg = f"Cannot blend {mtype}"
            raise TypeError(error_msg)

        res = gen(**values)
        md = self.__middlewares__.get(mtype)
        if md is not None:
            res = md(res)

        if self.params["commit"]:
            return db.commit(res, **self.params)

        return res

    async def ablend(self, mtype: Type[TV], **values) -> TV:
        return await cast(Coroutine[Any, Any, TV], self.blend(mtype, **values))

    def middleware(self, mtype):
        """Middleware method."""

        def wrapper(func: Callable[[TV], TV]) -> Callable[[TV], TV]:
            self.__middlewares__[mtype] = func
            return func

        return wrapper

    def cycle(self, count: int = 5) -> MixerChain:
        """Generate multi objects. The syntastic sugar for cycles.

        :param count: Number of objects to generate

        ::

            users = mixer.cycle(5).blend('somemodule.User')

            profiles = mixer.cycle(5).blend(
                'somemodule.Profile', user=(user for user in users)

            apples = mixer.cycle(10).blend(
                Apple, title=mixer.sequence('apple_{0}')

        """
        return MixerChain(self, count)

    def reload(self, instance, **params):
        """Reload instances."""
        return db.reload(instance, **(params or self.params))

    def commit(self, instance, **params):
        """Commit instances."""
        return db.commit(instance, **(params or self.params))


class MixerChain(Generic[TV]):
    """Mixer chain class."""

    def __init__(self, mixer: Mixer, count: int = 1):
        self.__mixer__ = mixer
        self.__cycle__ = count
        self.__type__: Any = None
        self.__params__: Dict[str, Any] = {}

    def cycle(self, count: int = 5):
        return MixerChain(self.__mixer__, count)

    def blend(self, mtype: Type[TV], **params) -> MixerChain[TV]:
        self.__type__ = mtype
        self.__params__ = params
        return self

    def __get_params__(self) -> Tuple[Type[TV], Dict[str, Any]]:
        if self.__type__ is None:
            msg = "You should call blend() method first"
            raise RuntimeError(msg)
        return self.__type__, cast(Dict[str, Any], self.__params__)

    def __iter__(self) -> Generator[TV, None, None]:
        mtype, params = self.__get_params__()
        for _ in range(self.__cycle__):
            res = self.__mixer__.blend(mtype, **params)
            yield res

    async def __aiter__(self):
        mtype, params = self.__get_params__()
        for _ in range(self.__cycle__):
            yield await self.__mixer__.ablend(mtype, **params)

    async def __coro__(self) -> list[TV]:
        return [res async for res in self]

    def __await__(self):
        return self.__coro__().__await__()

    def __len__(self):
        return self.__cycle__
