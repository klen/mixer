from pony.orm import * # noqa
from decimal import Decimal


db = Database("sqlite", ":memory:", create_db=True)


class Customer(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(unicode)
    email = Required(unicode, unique=True)
    orders = Set("Order")


class Order(db.Entity):
    id = PrimaryKey(int, auto=True)
    total_price = Required(Decimal)
    customer = Required(Customer)
    items = Set("OrderItem")


class Product(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(unicode)
    price = Required(Decimal)
    items = Set("OrderItem")


class OrderItem(db.Entity):
    quantity = Required(int, default=1)
    order = Required(Order)
    product = Required(Product)
    PrimaryKey(order, product)


db.generate_mapping(create_tables=True)


def test_backend():
    from mixer.backend.pony import mixer
    assert mixer


@db_session
def test_mixer():
    from mixer.backend.pony import mixer

    customer = mixer.blend(Customer)
    assert customer.name
    assert customer.email
