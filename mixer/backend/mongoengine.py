""" Support for Mongoengine ODM.

.. note:: Support for Mongoengine_ is in early development.

::

    from mixer.backend.mongoengine import mixer

    class User(Document):
        created_at = DateTimeField(default=datetime.datetime.now)
        email = EmailField(required=True)
        first_name = StringField(max_length=50)
        last_name = StringField(max_length=50)

    class Post(Document):
        title = StringField(max_length=120, required=True)
        author = ReferenceField(User)
        tags = ListField(StringField(max_length=30))

    post = mixer.blend(Post, author__username='foo')

"""
from __future__ import absolute_import

import datetime
import decimal

from bson import ObjectId
from mongoengine import (
    BooleanField,
    DateTimeField,
    DecimalField,
    Document,
    EmailField,
    EmbeddedDocumentField,
    FloatField,
    GenericReferenceField,
    GeoPointField,
    IntField,
    LineStringField,
    ListField,
    ObjectIdField,
    PointField,
    PolygonField,
    ReferenceField,
    StringField,
    URLField,
    UUIDField,
)

from .. import mix_types as t, generators as g, fakers as f
from ..main import (
    Field, Relation, NO_VALUE,
    TypeMixer as BaseTypeMixer,
    GenFactory as BaseFactory,
    Mixer as BaseMixer,
)


def get_objectid(**kwargs):
    """ Create a new ObjectId instance.

    :return ObjectId:

    """
    return ObjectId()


def get_pointfield(**kwargs):
    """ Get a Point structure.

    :return dict:

    """
    return dict(type='Point', coordinates=f.get_coordinates())


def get_linestring(length=5, **kwargs):
    """ Get a LineString structure.

    :return dict:

    """
    return dict(
        type='LineString',
        coordinates=[f.get_coordinates() for _ in range(length)])


def get_polygon(length=5, **kwargs):
    """ Get a Poligon structure.

    :return dict:

    """
    lines = []
    for _ in range(length):
        line = get_linestring()['coordinates']
        if lines:
            line.insert(0, lines[-1][-1])

        lines.append(line)

    if lines:
        lines[0].insert(0, lines[-1][-1])

    return dict(type='Poligon', coordinates=lines)


class GenFactory(BaseFactory):

    """ Map a mongoengine classes to simple types. """

    types = {
        BooleanField: bool,
        DateTimeField: datetime.datetime,
        DecimalField: decimal.Decimal,
        EmailField: t.EmailString,
        FloatField: float,
        IntField: int,
        StringField: str,
        URLField: t.URL,
        UUIDField: t.UUID,
    }

    generators = {
        ObjectIdField: g.loop(get_objectid),
        LineStringField: g.loop(get_linestring),
        GeoPointField: g.loop(f.get_coordinates),
        PointField: g.loop(get_pointfield),
        PolygonField: g.loop(get_polygon),
    }


class TypeMixer(BaseTypeMixer):

    """ TypeMixer for Mongoengine. """

    factory = GenFactory

    def make_generator(self, field, field_name=None, fake=None):
        """ Make values generator for field.

        :param field: Mongoengine field's instance
        :param field_name: Field name
        :param fake: Force fake data

        :return generator:

        """
        ftype = type(field)
        stype = self.factory.cls_to_simple(ftype)
        kwargs = dict()

        if field.choices:
            choices, _ = list(zip(*field.choices))
            return g.gen_choice(choices)

        if stype is str:
            kwargs['length'] = field.max_length

        elif ftype is ListField:
            gen = self.make_generator(field.field)
            return g.loop(lambda: [next(gen) for _ in range(3)])()

        elif ftype is EmbeddedDocumentField:
            return g.loop(TypeMixer(field.document_type).blend)()

        elif ftype is DecimalField:
            sign, (ii,), dd = field.precision.as_tuple()
            kwargs['d'] = abs(dd)
            kwargs['positive'] = not sign
            kwargs['i'] = ii + 1

        return self.factory.gen_maker(stype, field_name, fake)(**kwargs)

    @staticmethod
    def get_default(field, target):
        """ Get default value from field.

        :return value: A default value or NO_VALUE

        """
        if not field.scheme.default:
            return NO_VALUE

        if callable(field.scheme.default):
            return field.scheme.default()

        return field.scheme.default

    @staticmethod
    def is_unique(field):
        """ Return True is field's value should be a unique.

        :return bool:

        """
        return field.scheme.unique

    @staticmethod
    def is_required(field):
        """ Return True is field's value should be defined.

        :return bool:

        """
        return field.scheme.required or isinstance(field.scheme, ObjectIdField)

    def gen_relation(self, target, field_name, relation, force=False):
        """ Generate a related relation by `relation`.

        :param target: Target for generate value.
        :param field_name: Name of relation for generation.
        :param relation: Instance of :class:`Relation`

        :return None:

        """
        if isinstance(relation.scheme, GenericReferenceField):
            meta = type(self.__class__)
            new_scheme = g.get_choice([
                m for (_, m, _, _) in meta.mixers.keys()
                if issubclass(m, Document) and not m is self.__scheme
            ])
        else:
            new_scheme = relation.scheme.document_type

        if new_scheme != self.__scheme:
            value = self.__mixer and self.__mixer.blend(
                new_scheme, **relation.params
            ) or TypeMixer(
                new_scheme, factory=self.__factory, fake=self.fake
            ).blend(**relation.params)

        return self.set_value(target, field_name, value)

    def __load_fields(self):
        for fname, field in self.__scheme._fields.items():

            if isinstance(field, (ReferenceField, GenericReferenceField)):
                yield fname, Relation(field, fname)
                continue

            yield fname, Field(field, fname)


class Mixer(BaseMixer):

    """ Mixer class for mongoengine.

    Default mixer (desnt save a generated instances to db)
    ::

        from mixer.backend.mongoengine import mixer

        user = mixer.blend(User)

    You can initialize the Mixer by manual:
    ::
        from mixer.backend.mongoengine import Mixer

        mixer = Mixer(commit=True)
        user = mixer.blend(User)

    """

    type_mixer_cls = TypeMixer

    def __init__(self, commit=False, **params):
        """ Initialize the Mongoengine Mixer.

        :param fake: (True) Generate fake data instead of random data.
        :param commit: (False) Save object to Mongo DB.

        """
        super(Mixer, self).__init__(**params)
        self.commit = commit

    def post_generate(self, result):
        """ Save instance to DB.

        :return instance:

        """

        if self.commit and isinstance(result, Document):
            result.save()

        return result


mixer = Mixer()


# lint_ignore=W0212
