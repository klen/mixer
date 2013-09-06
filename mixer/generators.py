""" Generate random data.

Functions for generation some kind of random datas. You can use
``mixer.generators`` by manual, like this:

::

    from mixer import generators as g

    price = g.get_positive_integer()
    date = g.get_date()

Or you can using shortcut from :class:`mixer.main.Mixer` like this:

::

    mixer.g.get_integer()  # -> 143

"""
import datetime
import random
import decimal
from functools import wraps

DEFAULT_STRING_LENGTH = 8
DEFAULT_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'  # noqa
DEFAULT_DATE = datetime.date.today()


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
    if not hasattr(get_func, '__call__'):
        r = get_func
        get_func = lambda: r

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


def get_date(min_date=(1900, 1, 1), max_date=(2020, 12, 31), **kwargs):
    """ Get a random date.

    :param mix_date: date or date's tuple from
    :param max_date: date or date's tuple to

    :return date:

    ::

        print get_date()  # -> date(1989, 06, 06)

        print get_date((1979, 01, 01), (1981, 01, 01))  # -> date(1980, 04, 03)

    """
    if isinstance(min_date, datetime.date):
        min_date = datetime.datetime(*min_date.timetuple()[:-4])

    if isinstance(max_date, datetime.date):
        max_date = datetime.datetime(*max_date.timetuple()[:-4])

    random_datetime = get_datetime(min_date, max_date)
    return random_datetime.date()

#: Generator's fabric for :meth:`mixer.generators.get_date`
gen_date = loop(get_date)


def get_time(min_time=(0, 0, 0), max_time=(23, 59, 59), **kwargs):
    """ Get a random time.

    :param min_time: `datetime.time` or time's tuple from
    :param max_time: `datetime.time` or time's tuple to

    :return time:

    ::

        print get_time()  # -> time(15, 00)

    """
    if not isinstance(min_time, datetime.time):
        min_time = datetime.time(*min_time)

    if not isinstance(max_time, datetime.time):
        max_time = datetime.time(*max_time)

    random_datetime = get_datetime(
        datetime.datetime.combine(DEFAULT_DATE, min_time),
        datetime.datetime.combine(DEFAULT_DATE, max_time)
    )
    return random_datetime.time()

#: Generator's fabric for :meth:`mixer.generators.get_time`
gen_time = loop(get_time)


def get_datetime(min_datetime=(1900, 1, 1, 0, 0, 0),
                 max_datetime=(2020, 12, 31, 23, 59, 59), **kwargs):
    """ Get a random datetime.

    :param low: datetime or datetime's tuple from
    :param hight: datetime or datetime's tuple to

    :return datetime:

    ::

        print get_datetime()  # -> datetime(1989, 06, 06, 15, 00)

    """
    if not isinstance(min_datetime, datetime.datetime):
        min_datetime = datetime.datetime(*min_datetime)

    if not isinstance(max_datetime, datetime.datetime):
        max_datetime = datetime.datetime(*max_datetime)

    delta = max_datetime - min_datetime
    delta = (delta.days * 24 * 60 * 60 + delta.seconds)
    delta = get_integer(0, delta)

    return min_datetime + datetime.timedelta(seconds=delta)

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


def get_float(low=-1e10, high=1e10, **kwargs):
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

# lint_ignore=E1103
