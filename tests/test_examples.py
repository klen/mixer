def test_basic_example(mixer):
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
    assert post.id  # e.g. 772654888
    assert post.title  # e.g. 'Race Company Within Event Recent'
    assert (
        post.body
    )  # e.g. 'Meeting also family cause just decade peace. Such rise rule well Democrat seat.'
    assert post.user
    assert post.user.id  # e.g. 772654888
    assert post.user.email  # e.g. 'jane.doe@example'

    post = mixer.blend(Post, title="My title")
    assert post.title == "My title"

    post = mixer.blend(Post, user__email="jane.doe@test")
    assert post.user.email == "jane.doe@test"

    # posts = mixer.cycle(3).blend(Post)
    # assert len(posts) == 3
    #
    # # You may use generators to define values
    # posts = mixer.cycle(3).blend(Post, title=(name for name in ["foo", "bar", "baz"]))
    # assert len(posts) == 3
    # assert posts[0].title == "foo"
    # assert posts[1].title == "bar"
    # assert posts[2].title == "baz"
    #
    # # optionaly use mixer.gen(...) to define generators
    # posts = mixer.cycle(3).blend(Post, title=mixer.gen("foo", "bar", "baz"))
    # assert len(posts) == 3
    #
    # # or simplier
    # posts = mixer.cycle(3).blend(Post, title=mixer.gen("foo-{}"))
    # assert len(posts) == 3
    # assert posts[0].title == "foo-0"
    # assert posts[1].title == "foo-1"
