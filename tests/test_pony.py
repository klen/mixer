from decimal import Decimal
from datetime import datetime

from pony import orm

db = orm.Database("sqlite", ":memory:", create_db=True)


class Customer(db.Entity):
    address = orm.Required(str)
    country = orm.Required(str)
    email = orm.Required(str, unique=True)
    name = orm.Required(str)
    password = orm.Required(str)

    cart_items = orm.Set("CartItem")
    orders = orm.Set("Order")


class Product(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    name = orm.Required(str)
    categories = orm.Set("Category")
    description = orm.Optional(str)
    picture = orm.Optional(bytes)
    price = orm.Required(Decimal)
    quantity = orm.Required(int)
    cart_items = orm.Set("CartItem")
    order_items = orm.Set("OrderItem")


class CartItem(db.Entity):
    quantity = orm.Required(int)
    customer = orm.Required(Customer)
    product = orm.Required(Product)


class OrderItem(db.Entity):
    quantity = orm.Required(int, default=1)
    price = orm.Required(Decimal)
    order = orm.Required("Order")
    product = orm.Required(Product)
    orm.PrimaryKey(order, product)


class Order(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    state = orm.Required(str)
    date_created = orm.Required(datetime)
    date_shipped = orm.Optional(datetime)
    date_delivered = orm.Optional(datetime)
    total_price = orm.Required(Decimal)
    customer = orm.Required(Customer)
    items = orm.Set(OrderItem)


class Category(db.Entity):
    name = orm.Required(str, unique=True)
    products = orm.Set(Product)


db.generate_mapping(create_tables=True)


def test_backend():
    from mixer.backend.pony import mixer
    assert mixer


@orm.db_session
def test_mixer():
    from mixer.backend.pony import mixer

    customer = mixer.blend(Customer)
    assert customer.name
    assert customer.email

    product = mixer.blend(Product)
    assert product.price

    order = mixer.blend(Order)
    assert order.customer

    orderitem = mixer.blend(OrderItem, product=product)
    assert orderitem.quantity == 1
    assert orderitem.order

    order = mixer.blend(Order, customer__name='John Snow')
    assert order.customer.name == 'John Snow'

    with mixer.ctx(commit=True):
        order = mixer.blend(Order)
        assert order.id
