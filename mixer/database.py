from typing import Callable, Dict, Literal, Type

COMMIT_HANDLERS: Dict[Type, Callable] = {}
RELOAD_HANDLERS: Dict[Type, Callable] = {}


def register(ftype: Type, htype="commit"):
    """Commit instance to DB."""

    def wrapper(func):
        handlers = COMMIT_HANDLERS if htype == "commit" else RELOAD_HANDLERS
        handlers[ftype] = func
        return func

    return wrapper


def handle(instance, htype: Literal["commit", "reload"], **params):
    """Commit instance to DB."""
    ftype = type(instance)
    handlers = COMMIT_HANDLERS if htype == "commit" else RELOAD_HANDLERS
    for stype in ftype.__mro__:
        if stype in handlers:
            break
    else:
        msg = f"Cannot {htype} {ftype}"
        raise TypeError(msg)

    return handlers[stype](instance, **params)


def commit(instance, **params):
    """Commit instance to DB."""
    return handle(instance, "commit", **params)


def reload(instance, **params):
    """Reload instance."""
    return handle(instance, "reload", **params)
