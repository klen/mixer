from __future__ import absolute_import

import datetime
import decimal

import pytest
from django.core.management import call_command

from .django_app.models import Rabbit, models, Hole, Door, Customer, Simple, Client
from mixer.backend.django import Mixer


@pytest.fixture(autouse=True)
def mixer(request):
    call_command('syncdb', interactive=False, verbosity=0)
    request.addfinalizer(lambda: call_command('flush', interactive=False, verbosity=0))
    return Mixer()


def test_base():
    from mixer.backend.django import mixer

    simple = mixer.blend('django_app.simple')
    assert isinstance(simple.value, int)


def test_fields(mixer):
    rabbit = mixer.blend('django_app.rabbit')

    assert isinstance(rabbit, Rabbit)
    assert rabbit.id
    assert rabbit.pk
    assert rabbit.pk == 1
    assert len(rabbit.title) <= 16
    assert isinstance(rabbit.active, bool)
    assert isinstance(rabbit.object_id, int)
    assert rabbit.object_id >= 0
    assert isinstance(rabbit.error_code, int)
    assert rabbit.error_code >= 0
    assert isinstance(rabbit.created_at, datetime.date)
    assert isinstance(rabbit.updated_at, datetime.datetime)
    assert isinstance(rabbit.opened_at, datetime.time)
    assert '@' in rabbit.email
    assert isinstance(rabbit.speed, decimal.Decimal)
    assert rabbit.custom
    assert rabbit.text
    assert len(rabbit.text) <= 512
    assert rabbit.picture.read() == b'pylama\n'

    assert rabbit.ip.count('.') == 3
    for ip_section in rabbit.ip.split('.'):
        assert 0 <= int(ip_section) <= 255

    assert rabbit.ip6.count(':') == 7
    for ip_section in rabbit.ip6.split(':'):
        assert 0 <= int(ip_section, 16) <= 65535

    assert isinstance(rabbit.file_path, str)

    rabbit = mixer.blend('rabbit')
    assert rabbit


def test_random_fields():
    mixer = Mixer(fake=False)

    hat = mixer.blend('django_app.hat', color=mixer.RANDOM)
    assert hat.color in ('RD', 'GRN', 'BL')


def test_custom(mixer):
    mixer.register(
        Rabbit,
        title=lambda: 'Mr. Rabbit',
        speed=lambda: mixer.faker.small_positive_integer(99))

    rabbit = mixer.blend(Rabbit, speed=mixer.RANDOM, percent=23)
    assert isinstance(rabbit.speed, decimal.Decimal)
    assert isinstance(rabbit.percent, float)
    assert rabbit.title == 'Mr. Rabbit'

    from mixer.backend.django import GenFactory

    def getter(*args, **kwargs):
        return "Always same"

    class MyFactory(GenFactory):
        generators = {models.CharField: getter}

    fabric = MyFactory.get_fabric(models.CharField)
    assert fabric() == "Always same"

    mixer = Mixer(factory=MyFactory, fake=False)
    assert mixer._Mixer__factory == MyFactory

    test = mixer.blend(Rabbit)
    assert test.title == "Always same"

    @mixer.middleware('auth.user')
    def encrypt_password(user): # noqa
        user.set_password(user.password)
        return user

    user = mixer.blend('auth.User', password='test')
    assert user.check_password('test')

    user = user.__class__.objects.get(pk=user.pk)
    assert user.check_password('test')


def test_select(mixer):
    mixer.cycle(3).blend(Rabbit)
    hole = mixer.blend(Hole, rabbit=mixer.SELECT)
    assert not hole.rabbit

    rabbits = Rabbit.objects.all()
    hole = mixer.blend(Hole, owner=mixer.SELECT)
    assert hole.owner in rabbits

    rabbit = rabbits[0]
    hole = mixer.blend(Hole, owner=mixer.SELECT(email=rabbit.email))
    assert hole.owner == rabbit


def test_relation(mixer):
    hat = mixer.blend('django_app.hat')
    assert not hat.owner

    silk = mixer.blend('django_app.silk')
    assert not silk.hat.owner

    silk = mixer.blend('django_app.silk', hat__owner__title='booble')
    assert silk.hat.owner
    assert silk.hat.owner.title == 'booble'

    door = mixer.blend('django_app.door', hole__title='flash', hole__size=244)
    assert door.hole.owner
    assert door.hole.title == 'flash'
    assert door.hole.size == 244

    door = mixer.blend('django_app.door')
    assert door.hole.title != 'flash'

    num = mixer.blend('django_app.number', doors=[door])
    assert num.doors.get() == door

    num = mixer.blend('django_app.number')
    assert num.doors.count() == 0

    num = mixer.blend('django_app.number', doors__size=42)
    assert num.doors.all()[0].size == 42

    tag = mixer.blend('django_app.tag', customer=mixer.RANDOM)
    assert tag.customer


def test_many_to_many_through(mixer):
    pointa = mixer.blend('django_app.pointa', other=mixer.RANDOM)
    assert pointa.other.all()

    pointb = mixer.blend('pointb')
    pointa = mixer.blend('pointa', other=pointb)
    assert list(pointa.other.all()) == [pointb]


def test_random(mixer):
    user = mixer.blend(
        'auth.User', username=mixer.RANDOM('mixer', 'its', 'fun'))
    assert user.username in ('mixer', 'its', 'fun')

    rabbit = mixer.blend(Rabbit, url=mixer.RANDOM)
    assert '/' in rabbit.url


def test_mix(mixer):
    test = mixer.blend(Rabbit, title=mixer.MIX.username)
    assert test.title == test.username

    test = Rabbit.objects.get(pk=test.pk)
    assert test.title == test.username

    test = mixer.blend(Hole, title=mixer.MIX.owner.title)
    assert test.title == test.owner.title

    test = mixer.blend(Door, hole__title=mixer.MIX.owner.title)
    assert test.hole.title == test.hole.owner.title

    test = mixer.blend(Door, hole__title=mixer.MIX.owner.username(
        lambda t: t + 's hole'
    ))
    assert test.hole.owner.username in test.hole.title
    assert 's hole' in test.hole.title

    test = mixer.blend(Door, owner=mixer.MIX.hole.owner)
    assert test.owner == test.hole.owner


def test_contrib(mixer):
    from django.db import connection
    _ = connection.connection.total_changes
    assert mixer.blend('auth.user')
    assert connection.connection.total_changes - _ == 1

    _ = connection.connection.total_changes
    assert mixer.blend(Customer)
    assert connection.connection.total_changes - _ == 2


def test_invalid_scheme(mixer):
    with pytest.raises(ValueError):
        mixer.blend('django_app.Unknown')


def test_ctx(mixer):

    with mixer.ctx(commit=False):
        hole = mixer.blend(Hole)
        assert hole
        assert not Hole.objects.count()

    with mixer.ctx(commit=True):
        hole = mixer.blend(Hole)
        assert hole
        assert Hole.objects.count()


def test_skip(mixer):
    rabbit = mixer.blend(Rabbit, created_at=mixer.SKIP, title=mixer.SKIP)
    assert rabbit.created_at
    assert not rabbit.title


def test_generic(mixer):
    rabbit = mixer.blend(Rabbit)
    assert rabbit.content_type
    assert rabbit.content_type.model_class()

    obj = mixer.blend(Simple)
    with mixer.ctx(loglevel='DEBUG'):
        rabbit = mixer.blend(Rabbit, content_object=obj)
    assert rabbit.content_object == obj
    assert rabbit.object_id == obj.pk
    assert rabbit.content_type.model_class() == Simple


def test_deffered(mixer):
    simples = mixer.cycle(3).blend(Simple)
    rabbits = mixer.cycle(3).blend(
        Rabbit, content_object=(s for s in simples)
    )
    assert rabbits

    rabbit = rabbits[0]
    rabbit = rabbit.__class__.objects.get(pk=rabbit.pk)
    assert rabbit.content_object


def test_unique(mixer):
    for _ in range(100):
        mixer.blend(Client)


def test_guard(mixer):
    r1 = mixer.guard(username='maxi').blend(Rabbit, username='maxi')
    r2 = mixer.guard(username='maxi').blend(Rabbit, username='maxi')
    assert r1
    assert r1 == r2


def test_reload(mixer):
    r1 = mixer.blend(Rabbit)
    r1.title = 'wrong title'
    r2 = mixer.reload(r1)
    assert r2 == r1
    assert r2.title != r1.title

    s1 = mixer.blend(Simple)
    r2, s2 = mixer.reload(r1, s1)
    assert s1 == s2
