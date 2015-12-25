""" Integrate Faker to the Mixer. """
import decimal as dc
import datetime as dt
import locale as pylocale
from collections import defaultdict

from faker import Factory, Generator
from faker.config import DEFAULT_LOCALE, AVAILABLE_LOCALES
try:
    from faker.config import PROVIDERS
except ImportError:
    from faker.config import DEFAULT_PROVIDERS as PROVIDERS

from faker.providers import BaseProvider


GENRES = ('general', 'pop', 'dance', 'traditional', 'rock', 'alternative', 'rap', 'country',
          'jazz', 'gospel', 'latin', 'reggae', 'comedy', 'historical', 'action', 'animation',
          'documentary', 'family', 'adventure', 'fantasy', 'drama', 'crime', 'horror', 'music',
          'mystery', 'romance', 'sport', 'thriller', 'war', 'western', 'fiction', 'epic',
          'tragedy', 'parody', 'pastoral', 'culture', 'art', 'dance', 'drugs', 'social')

HOSTNAMES = ('facebook', 'google', 'youtube', 'yahoo', 'baidu', 'wikipedia', 'amazon', 'qq',
             'live', 'taobao', 'blogspot', 'linkedin', 'twitter', 'bing', 'yandex', 'vk', 'msn',
             'ebay', '163', 'wordpress', 'ask', 'weibo', 'mail', 'microsoft', 'hao123', 'tumblr',
             'googleusercontent', 'fc2')

COUNTRY_CODES = 'cn', 'in', 'id', 'de', 'el', 'en', 'es', 'fr', 'it', 'pt', 'ru', 'ua'

HOSTZONES = ("aero", "asia", "biz", "cat", "com", "coop", "info", "int", "jobs", "mobi", "museum",
             "name", "net", "org", "post", "pro", "tel", "travel", "xxx", "edu", "gov", "mil",
             "eu", "ee", "dk", "ch", "bg", "vn", "tw", "tr", "tm", "su", "si", "sh", "se", "pt",
             "ar", "pl", "pe", "nz", "my", "gr", "pm", "re", "tf", "wf", "yt", "fi", "br", "ac") \
    + COUNTRY_CODES

USERNAMES = ('admin', 'akholic', 'ass', 'bear', 'bee', 'beep', 'blood', 'bone', 'boots', 'boss',
             'boy', 'boyscouts', 'briefs', 'candy', 'cat', 'cave', 'climb', 'cookie', 'cop',
             'crunching', 'daddy', 'diller', 'dog', 'fancy', 'gamer', 'garlic', 'gnu', 'hot',
             'jack', 'job', 'kicker', 'kitty', 'lemin', 'lol', 'lover', 'low', 'mix', 'mom',
             'monkey', 'nasty', 'new', 'nut', 'nutjob', 'owner', 'park', 'peppermint', 'pitch',
             'poor', 'potato', 'prune', 'raider', 'raiser', 'ride', 'root', 'scull', 'shattered',
             'show', 'sleep', 'sneak', 'spamalot', 'star', 'table', 'test', 'tips', 'user',
             'ustink', 'weak')


class UTCZone(dt.tzinfo):

    """ Implement UTC timezone. """

    utcoffset = dst = lambda s, d: dt.timedelta(0)
    tzname = lambda s, d: "UTC"

UTC = UTCZone()


class MixerProvider(BaseProvider):

    """ Implement some mixer methods. """

    def __init__(self, generator):
        self.providers = []
        self.generator = generator

    def load(self, providers=PROVIDERS, locale=None):
        if locale is None:
            locale = self.generator.locale

        for pname in providers:
            pcls, lang_found = Factory._get_provider_class(pname, locale)
            provider = pcls(self.generator)
            provider.__provider__ = pname
            provider.__lang__ = lang_found
            self.generator.add_provider(provider)

    @classmethod
    def choices(cls, elements=('a', 'b', 'c'), length=None):
        """ Get a pack of random elements from collection.

        :param elements: A collection
        :param length: Number of elements. By default len(collection).

        :return tuple:

        ::

            print get_choices([1, 2, 3], 2)  # -> [1, 1] or [2, 1] and etc...

        """
        if length is None:
            length = len(elements)
        return tuple(cls.random_element(elements) for _ in range(length))

    def big_integer(self):
        """ Get a big integer.

        Get integer from -9223372036854775808 to 9223372036854775807.

        """
        return self.generator.random_int(-9223372036854775808, 9223372036854775807)

    def ip_generic(self, protocol=None):
        """ Get IP (v4 or v6) address.

        :param protocol:
            Set protocol to 'ipv4' or 'ipv6'. Generate either IPv4 or
            IPv6 address if none.

        """
        if protocol == 'ipv4':
            return self.generator.ipv4()

        if protocol == 'ipv6':
            return self.generator.ipv6()

        return self.generator.ipv4() if self.generator.boolean() else self.generator.ipv6()

    def positive_decimal(self, **kwargs):
        """ Get a positive decimal. """
        return self.generator.pydecimal(positive=True, **kwargs)

    def positive_integer(self, max=2147483647):  # noqa
        """ Get a positive integer. """
        return self.random_int(0, max=max)  # noqa

    def small_integer(self, min=-32768, max=32768):  # noqa
        """ Get a positive integer. """
        return self.random_int(min=min, max=max)  # noqa

    def small_positive_integer(self, max=65536):  # noqa
        """ Get a positive integer. """
        return self.random_int(0, max=max)  # noqa

    @staticmethod
    def uuid():
        import uuid
        return str(uuid.uuid1())

    @classmethod
    def genre(cls):
        return cls.random_element(GENRES)

    @classmethod
    def percent(cls):
        return cls.random_int(0, 100)

    @classmethod
    def percent_decimal(cls):
        return dc.Decimal("0.%d" % cls.random_int(0, 99)) + dc.Decimal('0.01')

    def title(self):
        words = self.generator.words(6)
        return " ".join(words).title()

    def datetime(self, start_date='-30y', end_date='now', tzinfo=False):
        dt = self.generator.date_time_between(start_date, end_date)
        if tzinfo:
            dt = dt.replace(tzinfo=UTC)
        return dt

    def coordinates(self):
        return (self.generator.latitude(), self.generator.longitude())

    def hostzone(self):
        return self.generator.random_element(HOSTZONES)

    def hostname(self):
        return "%s.%s" % (self.generator.random_element(HOSTNAMES), self.hostzone())

    def email_address(self):
        return self.generator.parse("{{nickname}}@{{hostname}}")

    def alias(self):
        return self.random_element(USERNAMES)

    def nickname(self):
        template = self.random_element((
            '{{alias}}.{{alias}}',
            '{{alias}}_{{alias}}',
            '{{alias}}{{alias}}#',
            '{{alias}}##',
            '?{{alias}}',
        ))
        return self.bothify(self.generator.parse(template))

    def pybytes(self, size=20):
        return self.pystr(size).encode('utf-8')

    # FIXME: Fix Faker datetime provider
    def date_time_this_month(self, before_now=True, after_now=False):
        """Get a DateTime object for the current month.

        :param before_now: include days in current month before today
        :param after_now: include days in current month after today
        :example DateTime('2012-04-04 11:02:02')
        :return DateTime
        """
        now = dt.datetime.now()
        this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month_start = dt.datetime(now.year, (now.month + 1) % 12, 1)

        if before_now and after_now:
            return self.generator.date_time_between_dates(this_month_start, next_month_start)
        if not before_now and after_now:
            return self.generator.date_time_between_dates(now, next_month_start)
        if not after_now and before_now:
            return self.generator.date_time_between_dates(this_month_start, now)
        return now


class MixerGenerator(Generator):

    """ Support dynamic locales switch. """

    def __init__(self, locale=DEFAULT_LOCALE, providers=PROVIDERS, **config):
        self._locale = None
        self._envs = defaultdict(self.__create_env)
        self.locale = locale
        super(MixerGenerator, self).__init__(**config)
        self.env.load(providers)

    def __create_env(self):
        return MixerProvider(self)

    def __getattr__(self, name):
        return getattr(self.env, name)

    @property
    def providers(self):
        return self.env.providers

    @providers.setter
    def providers(self, value):
        self.env.providers = value

    @property
    def locale(self):
        return self._locale

    @locale.setter
    def locale(self, value):
        value = pylocale.normalize(value.replace('-', '_')).split('.')[0]
        if value not in AVAILABLE_LOCALES:
            value = DEFAULT_LOCALE

        if value == self._locale:
            return None

        nenv = self._envs[value]
        senv = self.env
        self._locale = value

        if senv.providers and not nenv.providers:
            nenv.load([p.__provider__ for p in senv.providers], value)

    @property
    def env(self):
        return self._envs[self._locale]

    def set_formatter(self, name, method):
        if not hasattr(self.env, name):
            setattr(self.env, name, method)


faker = MixerGenerator()
