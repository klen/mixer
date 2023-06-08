from mixer import types as t
from mixer.factories.constants import FAKER

from . import register
from ._builtin import int_factory

register(t.SQLSmallSerial, int_factory(int, unique=True, min=1, max=32767))
register(t.SQLSerial, int_factory(int, unique=True, min=1, max=2147483647))
register(t.SQLBigSerial, int_factory(int, unique=True, min=1, max=9223372036854775807))

register(t.Int8, int_factory(int, min=-128, max=127))
register(t.Int16, int_factory(int, min=-32768, max=32767))
register(t.Int32, int_factory(int, min=-2147483648, max=2147483647))
register(t.Int64, int_factory(int, min=-9223372036854775808, max=9223372036854775807))
register(t.UInt16, int_factory(int, min=0, max=65535))
register(t.UInt32, int_factory(int, min=0, max=4294967295))
register(t.UInt64, int_factory(int, min=0, max=18446744073709551615))
register(t.Timestamp, FAKER.unix_time)
register(t.IP4, FAKER.ipv4)
register(t.IP6, FAKER.ipv6)
register(t.Email, FAKER.email)
register(t.FilePath, FAKER.file_path)
register(t.URL, FAKER.url)
register(t.JSON, FAKER.json)
