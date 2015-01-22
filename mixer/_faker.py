""" Work with faker. """
import decimal as dc

from faker import Factory
from faker.providers import BaseProvider


GENRES = ('general', 'pop', 'dance', 'traditional', 'rock', 'alternative', 'rap', 'country',
          'jazz', 'gospel', 'latin', 'reggae', 'comedy', 'historical', 'action', 'animation',
          'documentary', 'family', 'adventure', 'fantasy', 'drama', 'crime', 'horror', 'music',
          'mystery', 'romance', 'sport', 'thriller', 'war', 'western', 'fiction', 'epic',
          'tragedy', 'parody', 'pastoral', 'culture', 'art', 'dance', 'drugs', 'social')


class MixerProvider(BaseProvider):

    """ Implement some mixer methods. """

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

    def positive_integer(self, max=2147483647): # noqa
        """ Get a positive integer. """
        return self.random_int(0, max=max) # noqa

    def small_integer(self, min=-32768, max=32768): # noqa
        """ Get a positive integer. """
        return self.random_int(min=min, max=max) # noqa

    def small_positive_integer(self, max=65536): # noqa
        """ Get a positive integer. """
        return self.random_int(0, max=max) # noqa

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


faker = Factory.create()
faker.add_provider(MixerProvider)
