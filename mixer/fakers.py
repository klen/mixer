from . import generators as g
import random

DEFAULT_NAME_MASK = "{firstname} {lastname}"

FIRSTNAME_CHOICES = (
    "Adams", "Allen", "Anderson", "Baker", "Barbara", "Betty", "Brown",
    "Campbell", "Carol", "Carter", "Clark", "Collins", "Davis", "Deborah",
    "Donna", "Dorothy", "Edwards", "Elizabeth", "Evans", "Garcia", "Gonzalez",
    "Green", "Hall", "Harris", "Helen", "Hernandez", "Hill", "Jackson",
    "Jennifer", "Johnson", "Jones", "Karen", "Kimberly", "King", "Laura",
    "Lee", "Lewis", "Linda", "Lisa", "Lopez", "Margaret", "Maria", "Martin",
    "Martinez", "Mary", "Michelle", "Miller", "Mitchell", "Moore", "Nancy",
    "Nelson", "Parker", "Patricia", "Perez", "Phillips", "Roberts", "Robinson",
    "Rodriguez", "Ruth", "Sandra", "Sarah", "Scott", "Sharon", "Smith",
    "Susan", "Taylor", "Thomas", "Thompson", "Turner", "Walker", "White",
    "Williams", "Wilson", "Wright", "Young",
)

LASTNAME_CHOICES = (
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

COUNTRY_CHOICES = (
    "Afghanistan", "Algeria", "Argentina", "Canada", "Colombia", "Ghana",
    "Iraq", "Kenya", "Malaysia", "Morocco", "Mozambique", "Nepal", "Peru",
    "Poland", "Sudan", "Uganda", "Ukraine", "Uzbekistan", "Venezuela", "Yemen",
    'Bangladesh', 'Brazil', 'Burma', 'China', 'Egypt', 'Ethiopia', 'France',
    'Germany', 'India', 'Indonesia', 'Iran', 'Italy', 'Japan', 'Mexico',
    'Nigeria', 'Pakistan', 'Philippines', 'Russia', 'South Africa', 'Spain',
    'Tanzania', 'Thailand', 'Turkey', 'United Kingdom', 'United States',
    'Vietnam',
)

CITY_PREFIX_CHOICES = ("North", "East", "West", "South", "New", "Lake", "Port")

CITY_SUFFIX_CHOICES = (
    "town", "ton", "land", "ville", "berg", "burgh", "borough", "bury", "view",
    "port", "mouth", "stad", "furt", "chester", "mouth", "fort", "haven",
    "side", "shire"
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
    "edu", "gov", "mil", "eu", "ee", "dk", "de", "ch", "bg", "vn", "tw", "tr",
    "tm", "su", "si", "sh", "se", "pt", "ar", "pl", "pe", "nz", "my", "it",
    "gr", "fr", "pm", "re", "tf", "wf", "yt", "fi", "br", "ac", "ru", "cn"
)

USERNAMES = (
    "root", "admin", "user", "owner", "monkey", "ass", "nut", "job", "mom",
    "akholic", "spamalot", "daddy", "ustink", "nutjob", "cookie", "jack",
    "raider", "raiser", "kitty", "lover", "potato", "cave", "diller", "kicker"
)


def get_firstname():
    return g.get_choice(*FIRSTNAME_CHOICES)

gen_firstname = g.loop(get_firstname)


def get_lastname():
    return g.get_choice(*LASTNAME_CHOICES)

gen_lastname = g.loop(get_lastname)


def get_name(max_length=100, mask=DEFAULT_NAME_MASK):
    name = mask.format(firstname=get_firstname(), lastname=get_lastname())
    return name[:max_length]

gen_name = g.loop(get_name)


def get_country():
    return g.get_choice(*COUNTRY_CHOICES)

gen_country = g.loop(get_country)


def get_city():
    return g.get_choice(
        "{0} {1}".format(g.get_choice(*CITY_PREFIX_CHOICES), get_firstname()),
        "{0} {1}".format(get_lastname(), g.get_choice(*CITY_SUFFIX_CHOICES)),
    )

gen_city = g.loop(get_city)


def get_lorem(length=None):
    lorem = ' '.join(g.get_choices(LOREM_CHOICES))
    if length:
        lorem = lorem[:length]
    return lorem

gen_lorem = g.loop(get_lorem)


def get_numerify(template, symbol='#'):
    return ''.join(
        (str(random.randint(0, 10)) if c == '#' else c)
        for c in template
    )

gen_numerify = g.loop(get_numerify)


def get_username(max_length=100):
    params = dict(
        one=g.get_choice(*USERNAMES),
        two=g.get_choice(*USERNAMES),
        num=g.get_positive_integer(high=2020),
    )
    username = g.get_choice(
        '{one}_{two}'.format(**params),
        '{one}.{two}'.format(**params),
        '{one}{num}'.format(**params),
        '{num}{one}'.format(**params),
    )
    return username[:max_length]

gen_username = g.loop(get_username)


def get_hostname(host=None, zone=None):
    params = dict(
        host=host or g.get_choice(*HOSTNAMES),
        zone=zone or g.get_choice(*HOSTZONES)
    )
    return g.get_choice(
        '{host}.{zone}'.format(**params),
        'www.{host}.{zone}'.format(**params)
    )

gen_hostname = g.loop(get_hostname)


def get_email(username=None, host=None, zone=None):
    hostname = get_hostname(host, zone)
    if hostname.startswith('www.'):
        hostname = hostname[4:]
    return '{0}@{1}'.format(
        username or get_username(),
        get_hostname(host, zone),
    )

gen_email = g.loop(get_email)
