from signalbus import create_signal


@create_signal
def commit(ftype: type, *, instance, **params):
    """Commit instance to DB."""
    emit = yield
    return emit(ftype, instance=instance, **params)


@create_signal
def reload(ftype: type, *, instance, **params):
    """Reload instance."""
    emit = yield
    return emit(ftype, instance=instance, **params)


@create_signal
async def async_commmit(ftype: type, *, instance, **params):
    """Commit instance to DB."""
    emit = yield
    yield emit(ftype, instance=instance, **params)


@create_signal
async def async_reload(ftype: type, *, instance, **params):
    """Reload instance."""
    emit = yield
    yield emit(ftype, instance=instance, **params)
