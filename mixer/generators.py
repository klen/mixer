import datetime
import sys
import random
import decimal
from functools import wraps

DEFAULT_STRING_LENGTH = 8
DEFAULT_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789' # nolint


def loop(gen_func):
    @wraps(gen_func)
    def wrapper(*args, **kwargs):
        while True:
            yield gen_func(*args, **kwargs)

    return wrapper


def get_choice(*choices):
    return random.choice(choices)

gen_choice = loop(get_choice)


def get_choices(choices, length=None):
    gen = gen_choice(*choices)
    if length is None:
        length = len(choices)
    return [next(gen) for _ in xrange(length)]

gen_choices = loop(get_choices)


def get_date(low=(1900, 1, 1), high=(2020, 12, 31)):
    low = datetime.date(*low)
    high = datetime.date(*high)
    delta = high - low
    delta = datetime.timedelta(
        seconds=random.randrange(delta.days * 24 * 60 * 60 + delta.seconds))
    return low + delta

gen_date = loop(get_date)


def get_time(low=(0, 0, 0), high=(23, 59, 59)):
    h = random.randint(low[0], high[0])
    m = random.randint(low[1], high[1])
    s = random.randint(low[2], high[2])

    return datetime.time(h, m, s)

gen_time = loop(get_time)


def get_datetime(low=(1900, 1, 1, 0, 0, 0),
                 high=(2020, 12, 31, 23, 59, 59)):
    date = get_date(low[:3], high[:3])
    h = random.randint(low[3], high[3])
    ms = random.randint(low[4], high[4])
    s = random.randint(low[5], high[5])

    return datetime.datetime(date.year, date.month, date.day, h, ms, s)

gen_datetime = loop(get_datetime)


def get_integer(low=-2147483647, high=2147483647):
    return random.randint(low, high)

gen_integer = loop(get_integer)


def get_big_integer():
    return get_integer(low=-9223372036854775808, high=9223372036854775807)

gen_big_integer = loop(get_big_integer)


def get_small_integer():
    return get_integer(low=-32768, high=32768)

gen_small_integer = loop(get_small_integer)


def get_positive_integer(high=4294967294):
    return get_integer(low=0, high=high)

gen_positive_integer = loop(get_positive_integer)


def get_small_positive_integer():
    return get_integer(low=0, high=65536)

gen_small_positive_integer = loop(get_small_positive_integer)


def get_float():
    return random.uniform(sys.float_info.min, sys.float_info.max)

gen_float = loop(get_float)


def get_boolean():
    return get_choice(True, False)

gen_boolean = loop(get_boolean)


def get_null_or_boolean():
    return get_choice(True, False, None)

gen_null_or_boolean = loop(get_null_or_boolean)


def get_string(length=DEFAULT_STRING_LENGTH, chars=DEFAULT_CHARS):
    return ''.join(get_choices(chars, length))

gen_string = loop(get_string)


def get_decimal(i=4, d=2, positive=False):
    i = 10 ** i
    d = 10 ** d
    return decimal.Decimal(
        "{0}.{1}".format(
            get_integer(low=0 if positive else -i, high=i),
            get_positive_integer(high=d)
        )
    )

gen_decimal = loop(get_decimal)


def get_positive_decimal():
    return get_decimal(positive=True)

gen_positive_decimal = loop(get_positive_decimal)
