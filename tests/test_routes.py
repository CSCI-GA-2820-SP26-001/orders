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

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

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

    def test_update_order(self):
        """It should Update an existing Order and return 200"""
        test_order = OrderFactory()
        test_order.create()

        updated_data = {
            "name": "Updated Name",
            "address": test_order.address,
            "email": test_order.email,
        }
        response = self.client.put(
            f"{BASE_URL}/{test_order.id}",
            json=updated_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], "Updated Name")
        self.assertEqual(data["id"], test_order.id)

    def test_update_order_with_items(self):
        """It should Update an Order with items and return 200"""
        test_order = OrderFactory()
        test_order.create()

        item = ItemFactory.build()
        updated_data = {
            "name": test_order.name,
            "address": test_order.address,
            "email": test_order.email,
            "items": [
                {"name": item.name, "quantity": item.quantity, "price": item.price}
            ],
        }
        response = self.client.put(
            f"{BASE_URL}/{test_order.id}",
            json=updated_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data["items"]), 1)
        self.assertEqual(data["items"][0]["name"], item.name)
        self.assertEqual(data["items"][0]["quantity"], item.quantity)

    def test_update_order_not_found(self):
        """It should return 404 when updating an Order that does not exist"""
        response = self.client.put(
            f"{BASE_URL}/0",
            json={"name": "X", "address": "Y", "email": "z@z.com"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])

    def test_update_order_bad_data(self):
        """It should return 400 when updating an Order with missing required fields"""
        test_order = OrderFactory()
        test_order.create()

        response = self.client.put(
            f"{BASE_URL}/{test_order.id}",
            json={"name": "Missing fields"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_no_body(self):
        """It should return 400 when updating with no JSON body"""
        test_order = OrderFactory()
        test_order.create()

        response = self.client.put(
            f"{BASE_URL}/{test_order.id}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should return 415 when Content-Type is not application/json"""
        test_order = OrderFactory()
        test_order.create()

        response = self.client.put(
            f"{BASE_URL}/{test_order.id}",
            data="not json",
            content_type="text/plain",
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_method_not_allowed(self):
        """It should return 405 for unsupported HTTP methods"""
        response = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    ######################################################################
    #  I T E M   T E S T   C A S E S
    ######################################################################

    def _create_order_with_item(self):
        """Helper: creates an Order with one Item and returns both"""
        order = OrderFactory()
        order.create()
        item = ItemFactory.build()
        item.order_id = order.id
        order.items.append(item)
        order.update()
        return order, order.items[0]

    def test_get_item_in_order(self):
        """It should Read an Item from an Order"""
        order, item = self._create_order_with_item()

        response = self.client.get(
            f"{BASE_URL}/{order.id}/items/{item.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["id"], item.id)
        self.assertEqual(data["order_id"], order.id)
        self.assertEqual(data["name"], item.name)
        self.assertEqual(data["quantity"], item.quantity)
        self.assertEqual(data["price"], item.price)

    def test_get_item_order_not_found(self):
        """It should return 404 when the Order does not exist"""
        response = self.client.get(f"{BASE_URL}/0/items/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("not found", data["message"])

    def test_get_item_not_found(self):
        """It should return 404 when the Item does not exist"""
        order = OrderFactory()
        order.create()

        response = self.client.get(f"{BASE_URL}/{order.id}/items/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("not found", data["message"])

    def test_get_item_wrong_order(self):
        """It should return 404 when the Item belongs to a different Order"""
        order1, item = self._create_order_with_item()
        order2 = OrderFactory()
        order2.create()

        response = self.client.get(
            f"{BASE_URL}/{order2.id}/items/{item.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_order_then_get(self):
        """It should return the updated Order data on subsequent GET"""
        test_order = OrderFactory()
        test_order.create()

        updated_data = {
            "name": "Confirmed Update",
            "address": "123 New St",
            "email": "new@example.com",
        }
        put_response = self.client.put(
            f"{BASE_URL}/{test_order.id}",
            json=updated_data,
            content_type="application/json",
        )
        self.assertEqual(put_response.status_code, status.HTTP_200_OK)

        get_response = self.client.get(f"{BASE_URL}/{test_order.id}")
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        data = get_response.get_json()
        self.assertEqual(data["name"], "Confirmed Update")
        self.assertEqual(data["address"], "123 New St")
        self.assertEqual(data["email"], "new@example.com")