import sys

import pytest
from decimal import Decimal
from datetime import datetime

pytestmark = pytest.mark.skipif(
    sys.version_info > (2, 8), reason='Pony doesnt support python3')

try:

    from pony.orm import * # noqa

    db = Database("sqlite", ":memory:", create_db=True)

    class Customer(db.Entity):
        address = Required(unicode)
        country = Required(unicode)
        email = Required(unicode, unique=True)
        name = Required(unicode)
        password = Required(unicode)

        cart_items = Set("CartItem")
        orders = Set("Order")

    class Product(db.Entity):
        id = PrimaryKey(int, auto=True)
        name = Required(unicode)
        categories = Set("Category")
        description = Optional(unicode)
        picture = Optional(buffer)
        price = Required(Decimal)
        quantity = Required(int)
        cart_items = Set("CartItem")
        order_items = Set("OrderItem")

    class CartItem(db.Entity):
        quantity = Required(int)
        customer = Required(Customer)
        product = Required(Product)

    class OrderItem(db.Entity):
        quantity = Required(int, default=1)
        price = Required(Decimal)
        order = Required("Order")
        product = Required(Product)
        PrimaryKey(order, product)

    class Order(db.Entity):
        id = PrimaryKey(int, auto=True)
        state = Required(unicode)
        date_created = Required(datetime)
        date_shipped = Optional(datetime)
        date_delivered = Optional(datetime)
        total_price = Required(Decimal)
        customer = Required(Customer)
        items = Set(OrderItem)

    class Category(db.Entity):
        name = Required(unicode, unique=True)
        products = Set(Product)

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

except ImportError:
    pass
