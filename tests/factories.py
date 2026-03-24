"""
Test Factory to make fake objects for testing
"""

import factory
from service.models import Order, Item


class OrderFactory(factory.Factory):
    """Creates fake Orders for testing"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Order

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    address = factory.Faker("street_address")
    email = factory.Faker("email")
    status = "Unprocessed"


class ItemFactory(factory.Factory):
    """Creates fake Items for testing"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Item

    id = factory.Sequence(lambda n: n)
    order_id = factory.Sequence(lambda n: n)
    name = factory.Faker("word")
    quantity = factory.Faker("random_int", min=1, max=100)
    price = factory.Faker("pyfloat", min_value=0.01, max_value=999.99, right_digits=2)
