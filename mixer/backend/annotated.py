import dataclasses
import random
import typing

import typing_extensions

import mixer.mix_types as t

from ..main import GenFactory as BaseGenFactory
from ..main import Mixer as BaseMixer
from ..main import TypeMixer as BaseTypeMixer


class GenFactory(BaseGenFactory):
    @classmethod
    def cls_to_simple(cls, fcls):
        if hasattr(fcls, "__origin__"):
            if fcls.__origin__ == typing.Union:
                return random.choice(fcls.__args__)

        return super().cls_to_simple(fcls)


class TypeMixer(BaseTypeMixer):
    factory = GenFactory

    def populate_target(self, values):
        if issubclass(self.__scheme, dict) or dataclasses.is_dataclass(self.__scheme):
            return self.__scheme(**{k: v for k, v in values})

        return super().populate_target(values)

    def __load_fields(self):
        for fname, type_ in typing_extensions.get_type_hints(self.__scheme).items():
            if fname.startswith("_"):
                continue

            yield fname, t.Field(
                type_,
                fname,
            )


class Mixer(BaseMixer):
    type_mixer_cls = TypeMixer


mixer = Mixer()
