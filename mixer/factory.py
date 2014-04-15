""" Mixer factories. """

import datetime
import decimal

from . import _compat as _, generators as g, mix_types as t, fakers as f


class GenFactoryMeta(type):

    """ Precache generators. """

    def __new__(mcs, name, bases, params):
        generators = dict()
        fakers = dict()
        types = dict()

        for cls in bases:
            if isinstance(cls, GenFactoryMeta):
                generators.update(cls.generators)
                fakers.update(cls.fakers)
                types.update(cls.types)

        fakers.update(params.get('fakers', dict()))
        types.update(params.get('types', dict()))

        types = dict(mcs.__flat_keys(types))

        if types:
            for atype, btype in types.items():
                factory = generators.get(btype)
                if factory:
                    generators[atype] = factory

        generators.update(params.get('generators', dict()))
        generators = dict(mcs.__flat_keys(generators))

        params['generators'] = generators
        params['fakers'] = fakers
        params['types'] = types

        return super(GenFactoryMeta, mcs).__new__(mcs, name, bases, params)

    @staticmethod
    def __flat_keys(d):
        for key, value in d.items():
            if isinstance(key, (tuple, list)):
                for k in key:
                    yield k, value
                continue
            yield key, value


class GenFactory(_.with_metaclass(GenFactoryMeta)):

    """ Make generators for types. """

    generators = {
        bool: g.get_boolean,
        float: g.get_float,
        int: g.get_integer,
        str: g.get_string,
        list: g.get_list,
        set: lambda **kwargs: set(g.get_list()),
        tuple: lambda **kwargs: tuple(g.get_list()),
        dict: lambda **kwargs: dict(zip(g.get_list(), g.get_list())),
        datetime.date: g.get_date,
        datetime.datetime: g.get_datetime,
        datetime.time: g.get_time,
        decimal.Decimal: g.get_decimal,
        t.BigInteger: g.get_big_integer,
        t.EmailString: f.get_email,
        t.HostnameString: f.get_hostname,
        t.IP4String: f.get_ip4,
        t.NullOrBoolean: g.get_null_or_boolean,
        t.PositiveDecimal: g.get_positive_decimal,
        t.PositiveInteger: g.get_positive_integer,
        t.SmallInteger: g.get_small_integer,
        t.Text: f.get_lorem,
        t.URL: f.get_url,
        t.UUID: f.get_uuid,
        type(None): '',
    }

    fakers = {
        ('name', str): f.get_name,
        ('first_name', str): f.get_firstname,
        ('firstname', str): f.get_firstname,
        ('last_name', str): f.get_lastname,
        ('lastname', str): f.get_lastname,
        ('title', str): f.get_lorem,
        ('description', str): f.get_lorem,
        ('content', str): f.get_lorem,
        ('body', str): f.get_lorem,
        ('city', str): f.get_city,
        ('country', str): f.get_country,
        ('email', str): f.get_email,
        ('username', str): f.get_username,
        ('login', str): f.get_username,
        ('domain', str): f.get_hostname,
        ('phone', str): f.get_phone,
        ('company', str): f.get_company,
        ('lat', float): f.get_latlon,
        ('latitude', float): f.get_latlon,
        ('lon', float): f.get_latlon,
        ('longitude', float): f.get_latlon,
        ('url', t.URL): f.get_url,
    }

    types = {}

    @classmethod
    def cls_to_simple(cls, fcls):
        """ Translate class to one of simple base types.

        :return type: A simple type for generation

        """
        return cls.types.get(fcls) or (
            fcls if fcls in cls.generators
            else None
        )

    @staticmethod
    def name_to_simple(fname):
        """ Translate name to one of simple base names.

        :return str:

        """
        fname = fname or ''
        return fname.lower().strip()

    @classmethod
    def gen_maker(cls, fcls, fname=None, fake=False):
        """ Make a generator based on class and name.

        :return generator:

        """
        simple = cls.cls_to_simple(fcls)
        func = cls.generators.get(fcls)

        if fname and fake and (fname, simple) in cls.fakers:
            fname = cls.name_to_simple(fname)
            func = cls.fakers.get((fname, simple)) or func

        return g.loop(func) if func is not None else False
