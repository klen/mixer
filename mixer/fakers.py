""" Generate fake data.

Functions for generation some kind of fake datas. You can use ``mixer.fakers``
by manual, like this:

::

    from mixer import fakers as f

    name = f.get_name()
    country = f.get_country()

    url_gen = f.gen_url()(hostname=True)
    urls = [next(url_gen) for _ in range(10)]


Or you can using shortcut from :class:`mixer.main.Mixer` like this:

::

    mixer.f.get_city()  # -> Moscow

"""

from . import generators as g
import random
import uuid
import decimal

DEFAULT_NAME_MASK = "{firstname} {lastname}"
DEFAULT_USERNAME_MASK_CHOICES = (
    '{one}{num}', '{one}_{two}', '{one}.{two}', '{two}{one}{num}')

FIRSTNAMES = (
    "Alice", "Adams", "Allen", "Anderson", "Baker", "Barbara", "Betty",
    "Brown", "Bob", "Campbell", "Carol", "Carter", "Clark", "Collins", "Davis",
    "Deborah", "Donna", "Dorothy", "Edwards", "Elizabeth", "Evans", "Garcia",
    "Gonzalez", "Green", "Hall", "Harris", "Helen", "Hernandez", "Hill",
    "Jackson", "Jennifer", "Johnson", "Jones", "Karen", "Kimberly", "King",
    "Laura", "Lee", "Lewis", "Linda", "Lisa", "Lopez", "Margaret", "Maria",
    "Martin", "Martinez", "Mary", "Michelle", "Miller", "Mitchell", "Moore",
    "Nancy", "Nelson", "Parker", "Patricia", "Perez", "Phillips", "Roberts",
    "Robinson", "Rodriguez", "Ruth", "Sandra", "Sarah", "Scott", "Sharon",
    "Smith", "Susan", "Taylor", "Thomas", "Thompson", "Turner", "Walker",
    "White", "Williams", "Wilson", "Wright", "Young",
)

LASTNAMES = (
    "Allen", "Anderson", "Angelo", "Baker", "Bell", "Boulstridge", "Bungard",
    "Bursnell", "Cabrera", "Carlisle", "Carlisle", "Cart", "Chaisty", "Clark",
    "Clayworth", "Colchester", "Cooper", "Darlington", "Davis", "Denial",
    "Derby", "Dissanayake", "Domville", "Dorchester", "Dua", "Dudley",
    "Dundee", "Dundee", "Durham", "Edeson", "Galashiels", "Galashiels",
    "Galashiels", "Garrott", "Gaspar", "Gauge", "Gelson", "Gloucester",
    "Happer", "Harris", "Harrison", "Harrow", "Hawa", "Helling",
    "Hollingberry", "Howsham", "Huddersfield", "Husher", "Ipswich", "James",
    "Khambaita", "Kilmarnok", "King", "Kinlan", "Le", "Leatherby", "Lee",
    "Leicester", "Lerwick", "Lerwick", "Lerwick", "Lincoln", "Llandrindod",
    "Llandrindod", "Llandudno", "Llandudno", "Llandudno", "Llandudno",
    "Llandudno", "London", "Lowsley", "Mardling", "Martin", "McCalman",
    "McKiddie", "McQuillen", "Meath", "Mitchell", "Moore", "Morgan", "Morris",
    "Mustow", "Nana", "Newcastle", "Newport", "Norwich", "Norwich", "Oldham",
    "Parker", "Patel", "Pepall", "Perdue", "Phillips", "Ravensdale", "Rukin",
    "Selvaratnam", "Shelsher", "Shrewsbury", "Silsbury", "Smih", "Southway",
    "Sunderland", "Swansea", "Swansea", "Swansea", "Swansea", "Swansea",
    "Taunton", "Upadhyad", "Valji", "Virji", "Wadd", "Wakefield", "Walsall",
    "Ward", "Watson", "Weild", "Wigan", "Witte", "Wolverhampton", "York",
)

COUNTRIES = (
    "Afghanistan", "Algeria", "Argentina", "Canada", "Colombia", "Ghana",
    "Iraq", "Kenya", "Malaysia", "Morocco", "Mozambique", "Nepal", "Peru",
    "Poland", "Sudan", "Uganda", "Ukraine", "Uzbekistan", "Venezuela", "Yemen",
    'Bangladesh', 'Brazil', 'Burma', 'China', 'Egypt', 'Ethiopia', 'France',
    'Germany', 'India', 'Indonesia', 'Iran', 'Italy', 'Japan', 'Mexico',
    'Nigeria', 'Pakistan', 'Philippines', 'Russia', 'South Africa', 'Spain',
    'Tanzania', 'Thailand', 'Turkey', 'United Kingdom', 'United States',
    'Vietnam',
)

COUNTRY_CODES = (
    'cn', 'in', 'id', 'de', 'el', 'en', 'es', 'fr', 'it', 'pt', 'ru', 'ua'
)

CITY_PREFIXIES = ("North", "East", "West", "South", "New", "Lake", "Port")

CITY_SUFFIXIES = (
    "town", "ton", "land", "ville", "berg", "burgh", "borough", "bury", "view",
    "port", "mouth", "stad", "furt", "chester", "mouth", "fort", "haven",
    "side", "shire"
)

CITIES = (
    "Los Angeles", "Bangkok", "Beijing", "Bogota", "Buenos Aires", "Cairo",
    "Delhi", "Dhaka", "Guangzhou", "Istanbul", "Jakarta", "Karachi", "Kolkata",
    "Lagos", "London", "Manila", "Mexico City", "Moscow", "Mumbai",
    "New York City", "Osaka", "Rio de Janeiro", "Sao Paulo", "Seoul",
    "Shanghai", "Tianjin", "Tokyo"
)

LOREM_CHOICES = (
    "alias", "consequatur", "aut", "perferendis", "sit", "voluptatem",
    "accusantium", "doloremque", "aperiam", "eaque", "ipsa", "quae", "ab",
    "illo", "inventore", "veritatis", "et", "quasi", "architecto", "beatae",
    "vitae", "dicta", "sunt", "explicabo", "aspernatur", "aut", "odit", "aut",
    "fugit", "sed", "quia", "consequuntur", "magni", "dolores", "eos", "qui",
    "ratione", "voluptatem", "sequi", "nesciunt", "neque", "dolorem", "ipsum",
    "quia", "dolor", "sit", "amet", "consectetur", "adipisci", "velit", "sed",
    "quia", "non", "numquam", "eius", "modi", "tempora", "incidunt", "ut",
    "labore", "et", "dolore", "magnam", "aliquam", "quaerat", "voluptatem",
    "ut", "enim", "ad", "minima", "veniam", "quis", "nostrum",
    "exercitationem", "ullam", "corporis", "nemo", "enim", "ipsam",
    "voluptatem", "quia", "voluptas", "sit", "suscipit", "laboriosam", "nisi",
    "ut", "aliquid", "ex", "ea", "commodi", "consequatur", "quis", "autem",
    "vel", "eum", "iure", "reprehenderit", "qui", "in", "ea", "voluptate",
    "velit", "esse", "quam", "nihil", "molestiae", "et", "iusto", "odio",
    "dignissimos", "ducimus", "qui", "blanditiis", "praesentium", "laudantium",
    "totam", "rem", "voluptatum", "deleniti", "atque", "corrupti", "quos",
    "dolores", "et", "quas", "molestias", "excepturi", "sint", "occaecati",
    "cupiditate", "non", "provident", "sed", "ut", "perspiciatis", "unde",
    "omnis", "iste", "natus", "error", "similique", "sunt", "in", "culpa",
    "qui", "officia", "deserunt", "mollitia", "animi", "id", "est", "laborum",
    "et", "dolorum", "fuga", "et", "harum", "quidem", "rerum", "facilis",
    "est", "et", "expedita", "distinctio", "nam", "libero", "tempore", "cum",
    "soluta", "nobis", "est", "eligendi", "optio", "cumque", "nihil",
    "impedit", "quo", "porro", "quisquam", "est", "qui", "minus", "id", "quod",
    "placeat", "facere", "possimus", "omnis", "voluptas", "assumenda", "est",
    "omnis", "dolor", "repellendus", "temporibus", "autem", "quibusdam", "et",
    "aut", "consequatur", "vel", "illum", "qui", "dolorem", "eum", "fugiat",
    "quo", "voluptas", "nulla", "pariatur", "at", "vero", "eos", "et",
    "accusamus", "officiis", "debitis", "aut", "rerum", "necessitatibus",
    "saepe", "eveniet", "ut", "et", "voluptates", "repudiandae", "sint", "et",
    "molestiae", "non", "recusandae", "itaque", "earum", "rerum", "hic",
    "tenetur", "a", "sapiente", "delectus", "ut", "aut", "reiciendis",
    "voluptatibus", "maiores", "doloribus", "asperiores", "repellat", "maxime",
)


HOSTNAMES = (
    "facebook", "google", "youtube", "yahoo", "baidu", "wikipedia", "amazon",
    "qq", "live", "taobao", "blogspot", "linkedin", "twitter", "bing",
    "yandex", "vk", "msn", "ebay", "163", "wordpress", "ask", "weibo", "mail",
    "microsoft", "hao123", "tumblr", "xvideos", "googleusercontent", "fc2"
)

HOSTZONES = (
    "aero", "asia", "biz", "cat", "com", "coop", "info", "int", "jobs", "mobi",
    "museum", "name", "net", "org", "post", "pro", "tel", "travel", "xxx",
    "edu", "gov", "mil", "eu", "ee", "dk", "ch", "bg", "vn", "tw", "tr", "tm",
    "su", "si", "sh", "se", "pt", "ar", "pl", "pe", "nz", "my", "gr", "pm",
    "re", "tf", "wf", "yt", "fi", "br", "ac") + COUNTRY_CODES

USERNAMES = (
    "admin", "akholic", "ass", "bear", "bee", "beep", "blood", "bone", "boots",
    "boss", "boy", "boyscouts", "briefs", "candy", "cat", "cave", "climb",
    "cookie", "cop", "crunching", "daddy", "diller", "dog", "fancy", "gamer",
    "garlic", "gnu", "hot", "jack", "job", "kicker", "kitty", "lemin", "lol",
    "lover", "low", "mix", "mom", "monkey", "nasty", "new", "nut", "nutjob",
    "owner", "park", "peppermint", "pitch", "poor", "potato", "prune",
    "raider", "raiser", "ride", "root", "scull", "shattered", "show", "sleep",
    "sneak", "spamalot", "star", "table", "test", "tips", "user", "ustink",
    "weak"
) + tuple([n.lower() for n in FIRSTNAMES])

GENRES = (
    'general', 'pop', 'dance', 'traditional', 'rock', 'alternative', 'rap',
    'country', 'jazz', 'gospel', 'latin', 'reggae', 'comedy', 'historical',
    'action', 'animation', 'documentary', 'family', 'adventure', 'fantasy',
    'drama', 'crime', 'horror', 'music', 'mystery', 'romance', 'sport',
    'thriller', 'war', 'western', 'fiction', 'epic', 'tragedy', 'parody',
    'pastoral', 'culture', 'art', 'dance', 'drugs', 'social'
)

COMPANY_SYFFIXES = ('LLC', 'Group', 'LTD', 'PLC', 'LLP', 'Corp', 'Inc', 'DBA')

GEOCOORD_MASK = decimal.Decimal('.000001')

STREET_SUFFIXES = (
    'Alley', 'Avenue', 'Branch', 'Bridge', 'Brook', 'Brooks', 'Burg', 'Burgs',
    'Bypass', 'Camp', 'Canyon', 'Cape', 'Causeway', 'Center', 'Centers',
    'Circle', 'Circles', 'Cliff', 'Cliffs', 'Club', 'Common', 'Corner',
    'Corners', 'Course', 'Court', 'Courts', 'Cove', 'Coves', 'Creek',
    'Crescent', 'Crest', 'Crossing', 'Crossroad', 'Curve', 'Dale', 'Dam',
    'Divide', 'Drive', 'Drive', 'Drives', 'Estate', 'Estates', 'Expressway',
    'Extension', 'Extensions', 'Fall', 'Falls', 'Ferry', 'Field', 'Fields',
    'Flat', 'Flats', 'Ford', 'Fords', 'Forest', 'Forge', 'Forges', 'Fork',
    'Forks', 'Fort', 'Freeway', 'Garden', 'Gardens', 'Gateway', 'Glen',
    'Glens', 'Green', 'Greens', 'Grove', 'Groves', 'Harbor', 'Harbors',
    'Haven', 'Heights', 'Highway', 'Hill', 'Hills', 'Hollow', 'Inlet', 'Inlet',
    'Island', 'Island', 'Islands', 'Islands', 'Isle', 'Isle', 'Junction',
    'Junctions', 'Key', 'Keys', 'Knoll', 'Knolls', 'Lake', 'Lakes', 'Land',
    'Landing', 'Lane', 'Light', 'Lights', 'Loaf', 'Lock', 'Locks', 'Locks',
    'Lodge', 'Lodge', 'Loop', 'Mall', 'Manor', 'Manors', 'Meadow', 'Meadows',
    'Mews', 'Mill', 'Mills', 'Mission', 'Mission', 'Motorway', 'Mount',
    'Mountain', 'Mountain', 'Mountains', 'Mountains', 'Neck', 'Orchard',
    'Oval', 'Overpass', 'Park', 'Parks', 'Parkway', 'Parkways', 'Pass',
    'Passage', 'Path', 'Pike', 'Pine', 'Pines', 'Place', 'Plain', 'Plains',
    'Plains', 'Plaza', 'Plaza', 'Point', 'Points', 'Port', 'Ports', 'Ports',
    'Prairie', 'Prairie', 'Radial', 'Ramp', 'Ranch', 'Rapid', 'Rapids', 'Rest',
    'Ridge', 'Ridges', 'River', 'Road', 'Roads', 'Route', 'Row', 'Rue', 'Run',
    'Shoal', 'Shoals', 'Shore', 'Shores', 'Skyway', 'Spring', 'Springs',
    'Springs', 'Spur', 'Spurs', 'Square', 'Squares', 'Station', 'Stravenue',
    'Stream', 'Street', 'Streets', 'Summit', 'Terrace', 'Throughway', 'Trace',
    'Track', 'Trafficway', 'Trail', 'Trail', 'Tunnel', 'Turnpike', 'Underpass',
    'Union', 'Unions', 'Valley', 'Valleys', 'Via', 'Viaduct', 'View', 'Views',
    'Village', 'Villages', 'Ville', 'Vista', 'Walk', 'Walks', 'Wall', 'Way',
    'Ways', 'Well', 'Wells')


def get_firstname(**kwargs):
    """ Get a first name.

    :return str:

    ::

        print get_firstname()  # -> Johnson

    """
    return g.get_choice(FIRSTNAMES)

#: Generator's fabric for :meth:`mixer.fakers.get_firstname`
gen_firstname = g.loop(get_firstname)


def get_lastname(**kwargs):
    """ Get a last name.

    :return str:

    ::

        print get_lastname()  # -> Gaspar

    """
    return g.get_choice(LASTNAMES)

#: Generator's fabric for :meth:`mixer.fakers.get_lastname`
gen_lastname = g.loop(get_lastname)


def get_name(mask=DEFAULT_NAME_MASK, length=100, **kwargs):
    """ Get a full name.

    :return str:

    ::

        print get_name()  # -> Barbara Clayworth

    """
    name = mask.format(firstname=get_firstname(), lastname=get_lastname())
    return name[:length]

#: Generator's fabric for :meth:`mixer.fakers.get_lastname`
gen_name = g.loop(get_name)


def get_country(**kwargs):
    """ Get a country.

    :return str:

    ::

        print get_country()  # -> Italy

    """
    return g.get_choice(COUNTRIES)

#: Generator's fabric for :meth:`mixer.fakers.get_country`
gen_country = g.loop(get_country)


def get_country_code():
    """ Get a country code.

    :return str:

    ::

        print get_country_code()  # -> ru

    """
    return g.get_choice(COUNTRY_CODES)

gen_country_code = g.loop(get_country_code)


def get_city(**kwargs):
    """ Get a city.

    :return str:

    ::

        print get_city()  # -> North Carter

    """
    prf, sfx, city = g.get_choice(CITY_PREFIXIES), g.get_choice(CITY_SUFFIXIES), g.get_choice(CITIES) #noqa

    return g.get_choice((
        city,
        "{0} {1}".format(prf, city),
        "{0} {1}".format(prf, get_firstname()),
        "{0} {1}".format(get_lastname(), sfx),
    ))

#: Generator's fabric for :meth:`mixer.fakers.get_city`
gen_city = g.loop(get_city)


def get_lorem(length=None, **kwargs):
    """ Get a text (based on lorem ipsum.

    :return str:

    ::

        print get_lorem()  # -> atque rerum et aut reiciendis...

    """
    lorem = ' '.join(g.get_choices(LOREM_CHOICES))
    if length:
        lorem = lorem[:length]
        lorem, _ = lorem.rsplit(' ', 1)
    return lorem

#: Generator's fabric for :meth:`mixer.fakers.get_lorem`
gen_lorem = g.loop(get_lorem)


def get_short_lorem(length=64, **kwargs):
    """ Get a small text (based on lorem ipsum.

    :return str:

    ::

        print get_short_lorem()  # -> atque rerum et aut reiciendis

    """
    lorem = g.get_choice(LOREM_CHOICES)
    while True:
        choice = g.get_choice(LOREM_CHOICES)
        if len(lorem + choice) > length - 1:
            return lorem
        lorem += ' ' + choice

#: Generator's fabric for :meth:`mixer.fakers.get_short_lorem`
gen_short_lorem = g.loop(get_short_lorem)


def get_slug(length=64, **kwargs):
    """ Get a part of URL using human-readable words.

    :returns: Generated string

    ::

        print get_slug()  # -> atque-rerum-et-aut-reiciendis

    """
    return get_short_lorem(length, **kwargs).replace(' ', '-')

#: Generator's fabric for :meth:`mixer.fakers.get_slug`
gen_slug = g.loop(get_slug)


def get_numerify(template='', symbol='#', **kwargs):
    """ Generate number string from templates.

    :return str:

    ::

        print get_numerify('####-##')  # -> 2345-23

    """
    return ''.join(
        (str(random.randint(0, 10)) if c == '#' else c)
        for c in template
    )

#: Generator's fabric for :meth:`mixer.fakers.get_numerify`
gen_numerify = g.loop(get_numerify)


def get_username(length=100, choices=DEFAULT_USERNAME_MASK_CHOICES, **kwargs):
    """ Get a username.

    :return str:

    ::

        print get_username()  # -> boss1985

    """
    gen = g.gen_choice(USERNAMES)
    params = dict(
        one=next(gen),
        two=next(gen),
        num=g.get_integer(low=1900, high=2020),
    )
    mask = g.get_choice(choices)
    username = mask.format(**params)
    return username[:length]

#: Generator's fabric for :meth:`mixer.fakers.get_username`
gen_username = g.loop(get_username)


def get_simple_username(**kwargs):
    """ Get a simplest username.

    :return str:

    ::

        print get_username()  # -> boss1985

    """
    return get_username(choices=(
        '{one}', '{one}{num}'
    ))

#: Generator's fabric for :meth:`mixer.fakers.get_simple_username`
gen_simple_username = g.loop(get_simple_username)


def get_hostname(host=None, zone=None, **kwargs):
    """ Get a hostname.

    :return str:

    ::

        print get_hostname()  # -> twitter.az

    """
    params = dict(
        host=host or g.get_choice(HOSTNAMES),
        zone=zone or g.get_choice(HOSTZONES)
    )
    return g.get_choice((
        '{host}.{zone}'.format(**params),
        'www.{host}.{zone}'.format(**params)
    ))

#: Generator's fabric for :meth:`mixer.fakers.get_hostname`
gen_hostname = g.loop(get_hostname)


def get_email(username=None, host=None, zone=None, **kwargs):
    """ Get a email.

    :param username: set the username or get it by random if none
    :param host: set the host or get it by random if none
    :param zone: set the zone or get it by random if none

    :return str:

    ::

        print get_email()  # -> team.cool@microsoft.de

    """
    hostname = get_hostname(host, zone)
    if hostname.startswith('www.'):
        hostname = hostname[4:]
    return '{0}@{1}'.format(username or get_username(), hostname)

#: Generator's fabric for :meth:`mixer.fakers.get_email`
gen_email = g.loop(get_email)


def get_ip4(**kwargs):
    """ Get IPv4 address.

    :return str:

    ::

        print get_ip4()  # 192.168.1.1

    """
    gen = g.gen_positive_integer(255)
    return '{0}.{1}.{2}.{3}'.format(next(gen), next(gen), next(gen), next(gen))

#: Generator's fabric for :meth:`mixer.fakers.get_ip4`
gen_ip4 = g.loop(get_ip4)


def get_ip6(**kwargs):
    """ Get IPv6 addvess.

    :return str:

    ::

        print get_ip6()  # 0:0:0:0:0:0:0:1

    """
    gen = g.gen_positive_integer(2 ** 16)
    return '{0:x}:{1:x}:{2:x}:{3:x}:{4:x}:{5:x}:{6:x}:{7:x}'.format(
        next(gen), next(gen), next(gen), next(gen),
        next(gen), next(gen), next(gen), next(gen),
    )

#: Generator's fabric for :meth:`mixer.fakers.get_ip6`
gen_ip6 = g.loop(get_ip6)


def get_ip_generic(protocol=None, **kwargs):
    """ Get IP (v4 or v6) address.

    :param protocol:
        Set protocol to 'ipv4' or 'ipv6'. Generate either IPv4 or
        IPv6 address if none.

    :return str:

    ::

        print get_ip_generic()  # 192.168.1.1

    """
    if protocol == 'ipv4':
        choices = get_ip4(**kwargs),
    elif protocol == 'ipv6':
        choices = get_ip6(**kwargs),
    else:
        choices = get_ip4(**kwargs), get_ip6(**kwargs)

    return g.get_choice(choices)

#: Generator's fabric for :meth:`mixer.fakers.get_ip_generic`
gen_ip_generic = g.loop(get_ip_generic)


def get_url(hostname=None, **kwargs):
    """ Get a URL.

    :return str:

    """
    if hostname is None:
        hostname = get_hostname()

    parts = [hostname]

    parts += g.get_choices(LOREM_CHOICES, g.get_integer(1, 3))

    return '/'.join(parts)

#: Generator's fabric for :meth:`mixer.fakers.get_url`
gen_url = g.loop(get_url)


def get_uuid(**kwargs):
    """ Get a UUID.

    :return str:

    """
    return str(uuid.uuid1())

#: Generator's fabric for :meth:`mixer.fakers.get_uuid`
gen_uuid = g.loop(get_uuid)


def get_phone(template='###-###-###', **kwargs):
    """ Get a phone number.

    :param template: A template for number.
    :return str:

    """
    return get_numerify(template)

#: Generator's fabric for :meth:`mixer.fakers.get_phone`
gen_phone = g.loop(get_phone)


def get_company():
    """ Get a company name.

    :return str:

    """
    return '%s %s' % (get_lastname(), g.get_choice(COMPANY_SYFFIXES))

#: Generator's fabric for :meth:`mixer.fakers.get_company`
gen_company = g.loop(get_company)


def get_latlon():
    """ Get a value simular to latitude (longitude).

    :return float:

    ::

        print get_latlon()  # -> 137.60858

    """
    return float(
        decimal.Decimal(str(g.get_float(-180, 180))).quantize(GEOCOORD_MASK))

#: Generator's fabric for :meth:`mixer.fakers.get_latlon`
gen_latlon = g.loop(get_latlon)


def get_coordinates():
    """ Get a geographic coordinates.

    :return [float, float]:

    ::

        print get_coordinates()  # -> [116.256223, 43.790918]

    """
    return [get_latlon(), get_latlon()]

#: Generator's fabric for :meth:`mixer.fakers.get_coordinates`
gen_coordinates = g.loop(get_coordinates)


def get_genre():
    """ Return random genre.

    :returns: A choosen genre
    ::

        print get_genre()  # -> 'pop'

    """
    return g.get_choice(GENRES)


#: Generator's fabric for :meth:`mixer.fakers.get_genre`
gen_genre = g.loop(get_genre)


def get_street():
    """ Generate street name. """
    params = dict(
        first_name=get_firstname(),
        last_name=get_lastname(),
        suffix=g.get_choice(STREET_SUFFIXES),
    )

    return g.get_choice((
        '{first_name} {suffix}'.format(**params),
        '{last_name} {suffix}'.format(**params)
    ))

#: Generator's fabric for :meth:`mixer.fakers.get_street`
gen_street = g.loop(get_street)


def get_address():
    """ Generate address. """
    params = dict(
        street=get_street(),
        number1=g.get_small_positive_integer(high=99),
        number2=g.get_integer(high=999, low=100),
    )

    return g.get_choice((
        '{number1} {street}'.format(**params),
        '{number1} {street} Apt. {number2}'.format(**params),
        '{number1} {street} Suite. {number2}'.format(**params)
    ))

#: Generator's fabric for :meth:`mixer.fakers.get_address`
gen_address = g.loop(get_address)
