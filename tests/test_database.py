from __future__ import annotations

import pytest

from mixer.main import Mixer

from . import fixtures as fx


@pytest.fixture()
def mixer_commit():
    return True


@pytest.fixture()
async def setup_pwa():
    async with fx.pwa_manager.connection():
        await fx.PWAUser.create_table()
        await fx.PWAPost.create_table()

        yield True

        await fx.PWAUser.drop_table()
        await fx.PWAPost.drop_table()


@pytest.mark.parametrize("post_type", [fx.PWPost, fx.DJPost, fx.MEPost, fx.SAPost])
def test_commit_reload(post_type, mixer: Mixer):
    # Support SQLAlchemy
    if post_type is fx.SAPost:
        mixer.params["session"] = fx.SA_SESSION  # type: ignore[]

    post = mixer.blend(post_type)
    assert post.id

    post = mixer.reload(post)
    assert post
    assert post.user
    assert post.user.id

    user = mixer.reload(post.user)
    assert user


async def test_commit_reload_pwa(mixer: Mixer, setup_pwa):
    user = await mixer.blend(fx.PWAUser)
    assert user.id == 1

    post = await mixer.blend(fx.PWAPost, user=user)
    assert post.id

    post = await mixer.reload(post)
    assert post
    user = await post.user
    assert user
    assert user.id

    user = await mixer.reload(user)
    assert user
    assert user.id


@pytest.mark.parametrize(
    "post_type",
    [fx.PWPost, fx.DJPost, fx.MEPost, fx.SAPost],
)
def test_cycle_commit(mixer: Mixer, post_type):
    # Support SQLAlchemy
    if post_type is fx.SAPost:
        mixer.params["session"] = fx.SA_SESSION  # type: ignore[]

    posts = mixer.cycle(3).blend(post_type)
    for post in posts:
        assert post.id

        post = mixer.reload(post)  # noqa: PLW2901
        assert post
        assert post.user
        assert post.user.id


async def test_cycle_commit_pwa(mixer: Mixer, setup_pwa):
    posts = await mixer.cycle(3).blend(fx.PWAPost)
    for post in posts:
        assert post.id
        assert await post.user

    async for post in mixer.cycle(3).blend(fx.PWAPost):
        assert post.id
        assert await post.user


@pytest.mark.parametrize(
    "post_type",
    [fx.PWPost, fx.DJPost, fx.MEPost, fx.SAPost],
)
def test_guard(mixer: Mixer, post_type):
    # Support SQLAlchemy
    if post_type is fx.SAPost:
        mixer.params["session"] = fx.SA_SESSION  # type: ignore[]

    post = mixer.blend(post_type)
    assert post.id
