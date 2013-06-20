""" Generate random data.

Functions for generation some kind of random datas. You can use
``mixer.generators`` by manual, like this:

::

    from mixer import generators as g

    price = g.get_positive_integer()
    date = g.get_date()

"""
import datetime
import sys
import random
import decimal
from functools import wraps

DEFAULT_STRING_LENGTH = 8
DEFAULT_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'  # nolint


def loop(get_func):
    """ Make generator from function.

    :return function: Generator's fabric

    ::

        def get_more(start=1):
            return start + 1

        # Generator's fabric
        f = loop(get_one)

        # Get generator
        g = f(2)

        print [next(g), next(g)]  # -> [3, 3]

    """
    @wraps(get_func)
    def wrapper(*args, **kwargs):
        while True:
            yield get_func(*args, **kwargs)

    return wrapper


def get_choice(choices=None, **kwargs):
    """ Get a random element from collection.

    :param choices: A collection

    :return value: A random element

    ::

        print get_choice([1, 2, 3])  # -> 1 or 2 or 3

    """
    if not choices:
        return None

    return random.choice(choices)

#: Generator's fabric for :meth:`mixer.generators.get_choice`
gen_choice = loop(get_choice)


def get_choices(choices=None, length=None, **kwargs):
    """ Get a lot of random elements from collection.

    :param choices: A collection
    :param length: Number of elements. By default len(collection).

    :return tuple:

    ::

        print get_choices([1, 2, 3], 2)  # -> [1, 1] or [2, 1] and etc...

    """
    gen = gen_choice(choices)
    if length is None:
        length = len(choices)
    return tuple(next(gen) for _ in range(length))

#: Generator's fabric for :meth:`mixer.generators.get_choices`
gen_choices = loop(get_choices)


def get_date(low=(1900, 1, 1), high=(2020, 12, 31), **kwargs):
    """ Get a random date.

    :param low: date's tuple from
    :param hight: date's tuple to

    :return date:

    ::

        print get_date()  # -> date(1989, 06, 06)

    """
    low = datetime.date(*low)
    high = datetime.date(*high)
    delta = high - low
    delta = datetime.timedelta(
        seconds=random.randrange(delta.days * 24 * 60 * 60 + delta.seconds))
    return low + delta

#: Generator's fabric for :meth:`mixer.generators.get_date`
gen_date = loop(get_date)


def get_time(low=(0, 0, 0), high=(23, 59, 59), **kwargs):
    """ Get a random time.

    :param low: time's tuple from
    :param hight: time's tuple to

    :return time:

    ::

        print get_time()  # -> time(15, 00)

    """
    h = random.randint(low[0], high[0])
    m = random.randint(low[1], high[1])
    s = random.randint(low[2], high[2])

    return datetime.time(h, m, s)

#: Generator's fabric for :meth:`mixer.generators.get_time`
gen_time = loop(get_time)


def get_datetime(low=(1900, 1, 1, 0, 0, 0),
                 high=(2020, 12, 31, 23, 59, 59), **kwargs):
    """ Get a random datetime.

    :param low: datetime's tuple from
    :param hight: datetime's tuple to

    :return datetime:

    ::

        print get_datetime()  # -> datetime(1989, 06, 06, 15, 00)

    """
    date = get_date(low[:3], high[:3])
    h = random.randint(low[3], high[3])
    ms = random.randint(low[4], high[4])
    s = random.randint(low[5], high[5])

    return datetime.datetime(date.year, date.month, date.day, h, ms, s)

#: Generator's fabric for :meth:`mixer.generators.get_datetime`
gen_datetime = loop(get_datetime)


def get_integer(low=-2147483647, high=2147483647, **kwargs):
    """ Get a random integer.

    :param low: min value
    :param hight: max value

    :return int:

    ::

        print get_integer()  # -> 4242

    """
    return random.randint(low, high)

#: Generator's fabric for :meth:`mixer.generators.get_integer`
gen_integer = loop(get_integer)


def get_big_integer(**kwargs):
    """ Get a big integer.

    Get integer from -9223372036854775808 to 9223372036854775807.

    :return int:

    ::

        print get_big_integer()  # -> 42424242424242424242424242424242

    """
    return get_integer(low=-9223372036854775808, high=9223372036854775807)

#: Generator's fabric for :meth:`mixer.generators.get_big_integer`
gen_big_integer = loop(get_big_integer)


def get_small_integer(**kwargs):
    """ Get a small integer.

    Get integer from -32768 to 32768.

    :return int:

    ::

        print get_small_integer()  # -> 42

    """
    return get_integer(low=-32768, high=32768)

#: Generator's fabric for :meth:`mixer.generators.get_small_integer`
gen_small_integer = loop(get_small_integer)


def get_positive_integer(high=4294967294, **kwargs):
    """ Get a positive integer.

    :param hight: max value

    :return int:

    ::

        print get_positive_integer()  # -> 42

    """
    return get_integer(low=0, high=high)

#: Generator's fabric for :meth:`mixer.generators.get_positive_integer`
gen_positive_integer = loop(get_positive_integer)


def get_small_positive_integer(**kwargs):
    """ Get a small positive integer.

    :return int:

    ::

        print get_small_positive_integer()  # -> 42

    """
    return get_integer(low=0, high=65536)

#: Generator's fabric for :meth:`mixer.generators.get_small_positive_integer`
gen_small_positive_integer = loop(get_small_positive_integer)


def get_float(low=sys.float_info.min, high=sys.float_info.max, **kwargs):
    """ Get a random float.

    :return float:

    ::

        print get_float()  # -> 42.42

    """
    return random.uniform(low, high)

#: Generator's fabric for :meth:`mixer.generators.get_float`
gen_float = loop(get_float)


def get_boolean(**kwargs):
    """ Get True or False.

    :return bool:

    ::

        print get_boolean()  # -> True

    """
    return get_choice((True, False))

#: Generator's fabric for :meth:`mixer.generators.get_boolean`
gen_boolean = loop(get_boolean)


def get_null_or_boolean(**kwargs):
    """ Get True, False or None.

    :return bool:

    ::

        print get_null_or_boolean()  # -> None

    """
    return get_choice((True, False, None))

#: Generator's fabric for :meth:`mixer.generators.get_null_or_boolean`
gen_null_or_boolean = loop(get_null_or_boolean)


def get_string(length=DEFAULT_STRING_LENGTH, chars=DEFAULT_CHARS, **kwargs):
    """ Get a random string.

    :return str:

    ::

        print get_string(5)  # -> eK4Jg
        print get_string(5, '01')  # -> 00110

    """
    return ''.join(get_choices(chars, length))

#: Generator's fabric for :meth:`mixer.generators.get_string`
gen_string = loop(get_string)


def get_decimal(i=4, d=2, positive=False, **kwargs):
    """ Get a random decimal.

    :return str:

    ::

        print get_decimal()  # -> decimal.Decimal('42.42')

    """
    i = 10 ** i
    d = 10 ** d
    return decimal.Decimal(
        "{0}.{1}".format(
            get_integer(low=0 if positive else (-i + 1), high=i - 1),
            get_positive_integer(high=d - 1)
        )
    )

#: Generator's fabric for :meth:`mixer.generators.get_decimal`
gen_decimal = loop(get_decimal)


def get_positive_decimal(**kwargs):
    """ Get a positive decimal.

    :return str:

    ::

        print get_positive_decimal()  # -> decimal.Decimal('42.42')

    """
    return get_decimal(positive=True)

#: Generator's fabric for :meth:`mixer.generators.get_positive_decimal`
gen_positive_decimal = loop(get_positive_decimal)
