from datetime import date, datetime
from uuid import UUID

import pytest

from mixer import mixer

from . import fixtures as fx

# TODO:
# mixer.reload
# mixer.register
# mixer.middleware


def test_mixer():
    assert mixer
    assert mixer.RANDOM
    assert mixer.SKIP
    assert mixer.blend
    assert mixer.cycle
    assert mixer.middleware
    assert mixer.reload


@pytest.mark.parametrize(
    ("post_type", "user_type"),
    [
        (fx.Post, fx.User),
        (fx.DCPost, fx.DCUser),
        (fx.PWPost, fx.PWUser),
        (fx.PDPost, fx.PDUser),
        (fx.DJPost, fx.DJUser),
        (fx.MEPost, fx.MEUser),
        (fx.SAPost, fx.SAUser),
    ],
)
def test_generation(post_type, user_type):
    res = mixer.blend(post_type)
    assert res
    assert isinstance(res, post_type)
    if post_type is fx.SAPost:
        assert isinstance(res.id, int)
    elif post_type is fx.MEPost:
        assert isinstance(res.id, fx.me.ObjectIdField)
    else:
        assert isinstance(res.id, UUID)

    assert isinstance(res.title, str)
    assert isinstance(res.body, str)
    assert isinstance(res.image, bytes)
    assert isinstance(res.dtpublish, date)
    assert res.order == 0
    assert isinstance(res.user, user_type)
    assert isinstance(res.user.email, str)
    assert "@" in res.user.email
    assert res.user.logged_at is None
    role = res.user.role
    if not isinstance(role, str):
        role = role.value
    assert role in ["user", "admin"]


@pytest.mark.parametrize(
    "post_type", [fx.Post, fx.DCPost, fx.PWPost, fx.PDPost, fx.DJPost, fx.MEPost, fx.SAPost]
)
def test_cycle(post_type):
    res = mixer.cycle(3).blend(post_type)
    assert res
    assert len(res) == 3
    assert all(isinstance(rp, post_type) for rp in res)


@pytest.mark.parametrize(
    "post_type", [fx.Post, fx.DCPost, fx.PWPost, fx.PDPost, fx.DJPost, fx.MEPost, fx.SAPost]
)
def test_values(post_type):
    res = mixer.blend(post_type, title="title", user__email="name@test.com")
    assert res
    assert res.title == "title"
    assert res.user.email == "name@test.com"


@pytest.mark.parametrize("post_type", [fx.Post, fx.PWPost, fx.DJPost, fx.MEPost, fx.SAPost])
def test_skip(post_type):
    res = mixer.blend(post_type, title=mixer.SKIP)
    assert res
    assert not getattr(res, "title", None)


@pytest.mark.parametrize(
    "post_type", [fx.Post, fx.DCPost, fx.PWPost, fx.PDPost, fx.DJPost, fx.MEPost, fx.SAPost]
)
def test_random(post_type):
    res = mixer.blend(post_type, order=mixer.RANDOM, user__logged_at=mixer.RANDOM)
    assert res
    assert res.order != 0
    assert res.user.logged_at
    assert isinstance(res.user.logged_at, datetime)


@pytest.mark.parametrize(
    "post_type", [fx.Post, fx.DCPost, fx.PWPost, fx.PDPost, fx.DJPost, fx.MEPost, fx.SAPost]
)
def test_middleware(post_type, mixer):
    @mixer.middleware(post_type)
    def middleware(post):
        post.title = "middleware"
        return post

    res = mixer.blend(post_type)
    assert res
    assert res.title == "middleware"
