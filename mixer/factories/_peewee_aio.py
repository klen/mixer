from peewee_aio import AIOModel

from mixer import database as db


@db.register(AIOModel)
async def commit(instance: AIOModel, **params):
    """Commit instance to the database."""
    for name, rel in instance.__rel__.items():
        if rel._pk is None:
            res = await db.commit(rel)
            setattr(instance, name, res)

    await instance.save(force_insert=True)
    return instance


@db.register(AIOModel, "reload")
async def reload(instance: AIOModel, **params):
    return await instance.get_or_none(instance._pk_expr())  # type: ignore[]
