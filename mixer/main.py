from importlib import import_module
import datetime
import decimal

from . import generators as g, fakers as f


RANDOM = object()
FAKE = object()


class GeneratorRegistry(object):

    generators = {
        bool: g.gen_boolean(),
        float: g.gen_float(),
        int: g.gen_integer(),
        long: g.gen_big_integer(),
        str: g.gen_string(),
        datetime.date: g.gen_date(),
        datetime.datetime: g.gen_datetime(),
        datetime.time: g.gen_time(),
        decimal.Decimal: g.gen_decimal(),
        None: g.loop(lambda: '')(),
    }

    fakers = {
        ('name', str): f.gen_name(),
        ('description', str): f.gen_lorem(),
        ('city', str): f.gen_city(),
    }

    def add_generator(self, types, gen):
        for cls in types:
            self.generators[cls] = gen

    def random(self, cls):
        gen = self.generators.get(cls, self.generators.get(None))
        return next(gen)

    def fake(self, cls, name):
        gen = self.fakers.get((name, cls), self.generators.get(None))
        return next(gen)


class TypeMixer(object):

    random = RANDOM
    fake = FAKE

    def __init__(self, cls, generator=None):
        self.cls = self.__load_cls(cls)
        self.fields = list(self.__load_default_fields())
        self.generator = generator or GeneratorRegistry()

    def blend(self, **values):
        target = self.cls()
        for fname, ftype in self.fields:
            value = values.get(fname, self.random)

            if value is self.random:
                value = self.generator.random(ftype)

            if value is self.fake:
                value = self.generator.fake(ftype, fname)

            setattr(target, fname, value)

        return target

    @staticmethod
    def __load_cls(cls_type):
        if isinstance(cls_type, basestring):
            mod, cls_type = cls_type.rsplit('.', 1)
            mod = import_module(mod)
            cls_type = getattr(mod, cls_type)
        return cls_type

    def __load_default_fields(self):
        for fname in dir(self.cls):
            if fname.startswith('_'):
                continue
            yield fname, getattr(self.cls, fname)

    def __get_field_generator(self, field):
        pass
