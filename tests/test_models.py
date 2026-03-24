######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Test cases for Pet Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import Order, Item, DataValidationError, db
from .factories import OrderFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  Order   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestOrder(TestCase):
    """Test Cases for Orders Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Item).delete()
        db.session.query(Order).delete()
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_order(self):
        """It should create a Order"""
        order = OrderFactory()
        order.create()
        self.assertIsNotNone(order.id)
        found = Order.all()
        self.assertEqual(len(found), 1)
        data = Order.find(order.id)
        self.assertEqual(data.name, order.name)
        self.assertEqual(data.address, order.address)
        self.assertEqual(data.email, order.email)

    def test_update_order(self):
        """It should update an Order"""
        order = OrderFactory()
        order.create()
        original_id = order.id
        order.name = "Updated Name"
        order.update()
        self.assertEqual(order.id, original_id)
        found = Order.find(order.id)
        self.assertEqual(found.name, "Updated Name")

    def test_update_order_no_id(self):
        """It should raise DataValidationError when updating with no ID"""
        order = Order(name="Test", address="123 St", email="t@t.com")
        self.assertRaises(DataValidationError, order.update)

    def test_delete_order(self):
        """It should delete an Order"""
        order = OrderFactory()
        order.create()
        self.assertEqual(len(Order.all()), 1)
        order.delete()
        self.assertEqual(len(Order.all()), 0)

    def test_find_all_orders(self):
        """It should return all Orders"""
        for _ in range(3):
            OrderFactory().create()
        orders = Order.all()
        self.assertEqual(len(orders), 3)

    def test_find_by_name(self):
        """It should find Orders by name"""
        order = OrderFactory()
        order.create()
        found = Order.find_by_name(order.name).all()
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].name, order.name)

    def test_deserialize_type_error(self):
        """It should raise DataValidationError on bad data type"""
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, None)

    def test_order_with_items(self):
        """It should create an Order with Items"""
        order = OrderFactory()
        order.create()
        item = ItemFactory.build()
        item.order_id = order.id
        order.items.append(item)
        order.update()

        found = Order.find(order.id)
        self.assertEqual(len(found.items), 1)
        self.assertEqual(found.items[0].name, item.name)
        self.assertEqual(found.items[0].quantity, item.quantity)

    def test_item_repr(self):
        """It should return a string representation of Item"""
        order = OrderFactory()
        order.create()
        item = ItemFactory.build()
        item.order_id = order.id
        order.items.append(item)
        order.update()
        found_item = Item.find(order.items[0].id)
        self.assertIn("Item", repr(found_item))

    def test_item_deserialize_missing_field(self):
        """It should raise DataValidationError when Item is missing a field"""
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, {"name": "Widget"})

    def test_item_deserialize_type_error(self):
        """It should raise DataValidationError on bad Item data type"""
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, None)

    def test_update_order_error(self):
        """It should raise DataValidationError on update failure"""
        order = OrderFactory()
        order.create()
        order.name = "Updated"
        with patch("service.models.db.session.commit", side_effect=Exception("DB error")):
            self.assertRaises(DataValidationError, order.update)

    def test_delete_order_error(self):
        """It should raise DataValidationError on delete failure"""
        order = OrderFactory()
        order.create()
        with patch("service.models.db.session.commit", side_effect=Exception("DB error")):
            self.assertRaises(DataValidationError, order.delete)

    def test_create_item(self):
        """It should create an Item within an Order"""
        order = OrderFactory()
        order.create()
        self.assertIsNotNone(order.id)
        item = ItemFactory(order_id=order.id)
        item.create()
        self.assertIsNotNone(item.id)
        found = Item.find(item.id)
        self.assertEqual(found.name, item.name)
        self.assertEqual(found.quantity, item.quantity)
        self.assertEqual(found.price, item.price)
        self.assertEqual(found.order_id, order.id)

    def test_delete_item(self):
        """It should delete an Item"""
        order = OrderFactory()
        order.create()
        item = ItemFactory(order_id=order.id)
        item.create()
        self.assertEqual(len(Item.query.all()), 1)
        item.delete()
        self.assertEqual(len(Item.query.all()), 0)

    def test_order_cascade_delete(self):
        """It should cascade delete Items when an Order is deleted"""
        order = OrderFactory()
        order.create()
        item = ItemFactory(order_id=order.id)
        item.create()
        self.assertEqual(len(Item.query.all()), 1)
        order.delete()
        self.assertEqual(len(Item.query.all()), 0)

    def test_deserialize_item_invalid_quantity(self):
        """It should raise DataValidationError for invalid quantity"""
        data = {"name": "Widget", "quantity": 0, "price": 9.99}
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_item_invalid_price(self):
        """It should raise DataValidationError for invalid price"""
        data = {"name": "Widget", "quantity": 5, "price": -1.0}
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_order_serialize_with_status(self):
        """It should serialize an Order with its status"""
        order = OrderFactory()
        order.create()
        data = order.serialize()
        self.assertEqual(data["status"], order.status)
