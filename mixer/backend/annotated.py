from ..main import Mixer as BaseMixer, TypeMixer as BaseTypeMixer, GenFactory as BaseGenFactory
import typing
import mixer.mix_types as t
import sys
import random


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
        if issubclass(self.__scheme, dict):
            return self.__scheme(**{k: v for k,v in values})
        
        return super().populate_target(values)

    def __load_fields(self):
        annotations = getattr(self.__scheme, "__annotations__", None)
        if annotations is None:
            raise ValueError(f"Class {self.__scheme} has no type annotations")

        # https://docs.python.org/3/howto/annotations.html#manually-un-stringizing-stringized-annotations
        for fname, prop in annotations.items():
            if fname.startswith("_"):
                continue
            

            try:
                obj_globals = sys.modules[self.__scheme.__module__].__dict__
            except (AttributeError, KeyError):
                obj_globals = None
            
            if isinstance(prop, typing.ForwardRef):
                prop = prop.__forward_arg__
            
            prop_type = eval(prop, obj_globals, dict(vars(self.__scheme)))

            yield fname, t.Field(
                prop_type,
                fname,
            )


class Mixer(BaseMixer):
    type_mixer_cls = TypeMixer


mixer = Mixer()
