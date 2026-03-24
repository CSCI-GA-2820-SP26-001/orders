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
TestOrder API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Order, Item

from .factories import OrderFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/orders"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class OrderService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Item).delete()  # clean up items first (FK constraint)
        db.session.query(Order).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def _create_orders(self, count: int = 1) -> list:
        """Factory method to create orders in bulk"""
        orders = []
        for _ in range(count):
            test_order = OrderFactory()
            response = self.client.post(BASE_URL, json=test_order.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test order",
            )
            new_order = response.get_json()
            test_order.id = new_order["id"]
            orders.append(test_order)
        return orders


    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertIsNotNone(data)
        self.assertIn("name", data)
        self.assertIn("version", data)
        self.assertIn("paths", data)
        self.assertEqual(data["paths"]["list_orders"], "/orders")

    def test_list_orders(self):
        """It should return a list of all Orders"""
        for _ in range(3):
            OrderFactory().create()
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 3)

    def test_create_order(self):
        """It should Create a new Order"""
        test_order = OrderFactory.build()
        response = self.client.post(
            BASE_URL,
            json={
                "name": test_order.name,
                "address": test_order.address,
                "email": test_order.email,
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.get_json()
        self.assertEqual(data["name"], test_order.name)
        self.assertIn("Location", response.headers)

    def test_create_order_missing_data(self):
        """It should return 400 when creating an Order with missing fields"""
        response = self.client.post(
            BASE_URL,
            json={"name": "Incomplete"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        
    def test_create_order_no_content_type(self):
        """It should return 415 when creating an Order without Content-Type"""
        response = self.client.post(BASE_URL, data="not json")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_get_order(self):
        """It should Get a single order"""
        # create one order in the database
        test_order = OrderFactory()
        test_order.create()

        response = self.client.get(f"{BASE_URL}/{test_order.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        self.assertEqual(data["name"], test_order.name)
        self.assertEqual(data["id"], test_order.id)
        self.assertEqual(data["address"], test_order.address)
        self.assertEqual(data["email"], test_order.email)

    def test_get_order_not_found(self):
        """It should not Get an order thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])


    def test_delete_order(self):
        """It should Delete a order"""
        # create one order in the database
        test_order = OrderFactory()
        test_order.create()

        response = self.client.delete(f"{BASE_URL}/{test_order.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # make sure the order is deleted
        response = self.client.get(f"{BASE_URL}/{test_order.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_update_order(self):
        """It should Update an existing Order"""
        # create an order to update
        test_order = OrderFactory()
        response = self.client.post(BASE_URL, json=test_order.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the order
        new_order = response.get_json()
        logging.debug(new_order)
        new_order["name"] = "Updated Order"
        response = self.client.put(
            f"{BASE_URL}/{new_order['id']}", json=new_order
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_order = response.get_json()
        self.assertEqual(
            updated_order["name"],
            "Updated Order",
        )

    def test_update_order_not_found(self):
        """It should return 404 when updating an Order that doesn't exist"""
        response = self.client.put(
            f"{BASE_URL}/0",
            json={"name": "X", "address": "X", "email": "x@x.com"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    #  I T E M   T E S T   C A S E S
    ######################################################################

    def test_get_item(self):
        """It should Read an Item from an Order"""
        order = OrderFactory()
        order.create()
        item = ItemFactory(order_id=order.id)
        order.items.append(item)
        order.update()
        item_id = order.items[0].id

        response = self.client.get(f"{BASE_URL}/{order.id}/items/{item_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], item.name)

    def test_get_item_order_not_found(self):
        """It should return 404 when reading an Item from a non-existent Order"""
        response = self.client.get(f"{BASE_URL}/0/items/1")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_item_not_found(self):
        """It should return 404 when Item is not in the Order"""
        order = OrderFactory()
        order.create()
        response = self.client.get(f"{BASE_URL}/{order.id}/items/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_item(self):
        """It should Update an Item in an Order"""
        order = OrderFactory()
        order.create()
        item = ItemFactory(order_id=order.id)
        order.items.append(item)
        order.update()
        item_id = order.items[0].id

        new_data = {"name": "Updated Item", "quantity": 5, "price": 19.99}
        response = self.client.put(
            f"{BASE_URL}/{order.id}/items/{item_id}",
            json=new_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], "Updated Item")

    def test_update_item_order_not_found(self):
        """It should return 404 when updating an Item in a non-existent Order"""
        response = self.client.put(
            f"{BASE_URL}/0/items/1",
            json={"name": "X", "quantity": 1, "price": 1.0},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_item_not_found(self):
        """It should return 404 when the Item doesn't exist in the Order"""
        order = OrderFactory()
        order.create()
        response = self.client.put(
            f"{BASE_URL}/{order.id}/items/0",
            json={"name": "X", "quantity": 1, "price": 1.0},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_wrong_content_type(self):
        """It should return 415 when sending wrong Content-Type"""
        response = self.client.post(
            BASE_URL,
            data="not json",
            content_type="text/plain",
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_method_not_allowed(self):
        """It should return 405 when using an unsupported HTTP method"""
        response = self.client.patch(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
