from datetime import date, datetime
from uuid import UUID

import pytest
from mongoengine.fields import ObjectId

from mixer import mixer
from mixer.main import Mixer

from . import fixtures as fx

# TODO:
# mixer.register
# mix?


def test_mixer():
    assert mixer
    assert mixer.RANDOM
    assert mixer.SKIP
    assert mixer.blend
    assert mixer.cycle
    assert mixer.middleware
    assert mixer.reload


FIXTURES = [
    (fx.Post, fx.User),
    (fx.DCPost, fx.DCUser),
    (fx.PDPost, fx.PDUser),
    (fx.PWPost, fx.PWUser),
    (fx.DJPost, fx.DJUser),
    (fx.SAPost, fx.SAUser),
    (fx.MEPost, fx.MEUser),
]


@pytest.mark.parametrize(("post_type", "user_type"), FIXTURES)
def test_generation(post_type, user_type):
    res = mixer.blend(post_type)
    assert res
    assert isinstance(res, post_type)
    if post_type is fx.SAPost:
        assert isinstance(res.id, int)
    elif post_type is fx.MEPost:
        assert isinstance(res.id, ObjectId)
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


def test_params_fake(mixer: Mixer):
    res = mixer.blend(fx.Post)
    assert res
    assert res.title
    with mixer.ctx(fake=False):
        res = mixer.blend(fx.Post)
    assert res
    assert res.title


@pytest.mark.parametrize("post_type", [p for p, _ in FIXTURES])
def test_cycle(post_type):
    res = mixer.cycle(3).blend(post_type)
    assert res
    assert len(res) == 3
    assert all(isinstance(rp, post_type) for rp in res)


@pytest.mark.parametrize("post_type", [p for p, _ in FIXTURES])
def test_cycle_gen(post_type):
    res = mixer.cycle(3).blend(post_type, title=(t for t in ["p0", "p1", "p2"]))
    assert res
    assert len(res) == 3
    posts = list(res)
    assert posts[0].title == "p0"
    assert posts[1].title == "p1"
    assert posts[2].title == "p2"


@pytest.mark.parametrize("post_type", [p for p, _ in FIXTURES])
def test_cycle_mixer_gen_str(post_type):
    res = mixer.cycle(3).blend(post_type, title=mixer.gen("p{}"))
    assert res
    assert len(res) == 3
    posts = list(res)
    assert posts[0].title == "p0"
    assert posts[1].title == "p1"
    assert posts[2].title == "p2"


@pytest.mark.parametrize("post_type", [p for p, _ in FIXTURES])
def test_cycle_mixer_gen_seq(post_type):
    res = mixer.cycle(3).blend(post_type, title=mixer.gen("p0", "p1", "p2"))
    assert res
    assert len(res) == 3
    posts = list(res)
    assert posts[0].title == "p0"
    assert posts[1].title == "p1"
    assert posts[2].title == "p2"


@pytest.mark.parametrize("post_type", [p for p, _ in FIXTURES])
def test_cycle_mixer_gen_rand(post_type):
    res = mixer.cycle(3).blend(post_type, title=mixer.gen("p0", "p1", "p2", rand=True))
    assert res
    assert len(res) == 3
    posts = list(res)
    assert posts[0].title in ["p0", "p1", "p2"]
    assert posts[1].title in ["p0", "p1", "p2"]
    assert posts[2].title in ["p0", "p1", "p2"]


@pytest.mark.parametrize("post_type", [p for p, _ in FIXTURES])
def test_values(post_type):
    res = mixer.blend(post_type, title="title", user__email="name@test.com")
    assert res
    assert res.title == "title"
    assert res.user.email == "name@test.com"


@pytest.mark.parametrize("post_type", [p for p, _ in FIXTURES if p not in [fx.DCPost, fx.PDPost]])
def test_skip(post_type):
    res = mixer.blend(post_type, title=mixer.SKIP)
    assert res
    assert not getattr(res, "title", None)


@pytest.mark.parametrize("post_type", [p for p, _ in FIXTURES])
def test_random(post_type):
    res = mixer.blend(
        post_type, order=mixer.RANDOM, user__logged_at=mixer.RANDOM, is_published=mixer.RANDOM
    )
    assert res
    assert res.order != 0
    assert res.user.logged_at
    assert isinstance(res.user.logged_at, datetime)


@pytest.mark.parametrize("post_type", [p for p, _ in FIXTURES])
def test_middleware(post_type, mixer):
    @mixer.middleware(post_type)
    def middleware(post):
        post.title = "middleware"
        return post

    res = mixer.blend(post_type)
    assert res
    assert res.title == "middleware"


def test_mixer_values_base(mixer):
    assert mixer.values
    assert mixer.values.ticket.barcode
    assert mixer.values.ticket.barcode.path == ["ticket", "barcode"]


@pytest.mark.parametrize(("post_type", "user_type"), FIXTURES)
def test_mixer_values(post_type, user_type, mixer):
    post = mixer.blend(post_type, title=mixer.values.user.email)
    assert post
    assert post.title == post.user.email

    users = mixer.cycle(3).blend(user_type)
    posts = mixer.cycle(3).blend(post_type, title=mixer.values.user.email, user=mixer.gen(*users))
    for post in posts:
        assert post.title == post.user.email


def test_map_type(mixer):
    class CustomType(float):
        pass

    mixer.map_type(CustomType, int)
    res = mixer.blend(CustomType)
    assert isinstance(res, int)


def test_register_gen(mixer):
    mixer.register(int, lambda: 1)
    assert mixer.blend(int) == 1


def test_register_factory(mixer):
    @mixer.register(int)
    def factory(**params):
        return lambda: 1

    assert mixer.blend(int) == 1


def test_mixer_faker(mixer):
    assert mixer.faker.pyint()
    assert mixer.faker.pystr()


# ruff: noqa: PD011
