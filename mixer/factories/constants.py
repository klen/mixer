from typing import Dict, Final

from faker import Faker

SKIP: Final = object()
RANDOM: Final = object()
MAX_INT: Final = 1_000_000_000
FAKER: Final = Faker(includes=["mixer.provider"])

STR_NAME_TO_FAKER: Final[Dict[str, str]] = {
    "address": "street_address",
    "body": "text",
    "category": "genre",
    "city": "city",
    "company": "company",
    "content": "text",
    "department": "team",
    "description": "text",
    "domain": "domain_name",
    "email": "email",
    "first_name": "first_name",
    "firstname": "first_name",
    "full_name": "name",
    "genre": "genre",
    "ip": "ipv4",
    "ipv4": "ipv4",
    "ipv6": "ipv6",
    "job": "job",
    "last_name": "last_name",
    "lastname": "last_name",
    "login": "user_name",
    "mail": "email",
    "name": "name",
    "password": "password",
    "phone": "phone_number",
    "position": "job",
    "slug": "slug",
    "street": "street_name",
    "team": "team",
    "telephone": "phone_number",
    "time_zone": "timezone",
    "timezone": "timezone",
    "title": "title",
    "uri": "uri",
    "url": "uri",
    "username": "user_name",
}


FLOAT_NAME_TO_FAKER: Final = {
    "latitude": "latitude",
    "lat": "latitude",
    "longitude": "longitude",
    "long": "longitude",
}

STR_TO_TYPE: Final = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "list": list,
    "dict": dict,
    "tuple": tuple,
    "set": set,
    "frozenset": frozenset,
    "complex": complex,
    "bytes": bytes,
    "List": list,
    "Dict": dict,
    "Tuple": tuple,
    "Set": set,
    "FrozenSet": frozenset,
}
