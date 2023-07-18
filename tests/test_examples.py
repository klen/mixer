import pytest

from mixer import Mixer


def test_basic_example(mixer: Mixer):
    class User:
        id: int
        email: str

    class Post:
        id: int
        title: str
        body: str
        user: User

    post = mixer.blend(Post)
    assert post
    assert post.id
    assert post.title
    assert post.body
    assert post.user
    assert post.user.id
    assert post.user.email

    post = mixer.blend(Post, title="My title")
    assert post.title == "My title"

    post = mixer.blend(Post, user__email="jane.doe@test")
    assert post.user.email == "jane.doe@test"

    posts = mixer.cycle(3).blend(Post)
    assert len(posts) == 3

    # You may use generators to define values
    posts = mixer.cycle(3).blend(Post, title=(name for name in ["foo", "bar", "baz"]))
    assert len(posts) == 3

    p1, p2, p3 = posts
    assert p1.title == "foo"
    assert p2.title == "bar"
    assert p3.title == "baz"

    # optionaly use mixer.gen(...) to define generators
    posts = mixer.cycle(3).blend(Post, title=mixer.gen("foo", "bar", "baz"))
    assert len(posts) == 3

    # or simplier
    posts = mixer.cycle(3).blend(Post, title=mixer.gen("foo-{}"))
    assert len(posts) == 3
    p1, p2, p3 = posts
    assert p1.title == "foo-0"
    assert p2.title == "foo-1"
    assert p3.title == "foo-2"

    post = mixer.blend(Post, title=mixer.SKIP)
    assert not hasattr(post, "title")


@pytest.mark.parametrize("mixer_commit", [True])
def test_django_example(mixer: Mixer):
    from .fixtures import DJPost, DJUser

    # Generate a random user
    user = mixer.blend(DJUser)
    assert user

    post = mixer.blend(DJPost)
    assert post

    post = mixer.blend(DJPost, user__email="test@test.com")
    assert post.user.email == "test@test.com"
