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

    def test_health(self):
        """It should return OK from the health endpoint"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertIsNotNone(data)
        self.assertEqual(data["name"], "Orders REST API Service")
        self.assertIn("version", data)
        self.assertIn("paths", data)
        self.assertEqual(data["paths"]["list_orders"], "GET /orders")
        self.assertEqual(data["paths"]["create_order"], "POST /orders")
        self.assertEqual(data["paths"]["get_order"], "GET /orders/{id}")
        self.assertEqual(data["paths"]["update_order"], "PUT /orders/{id}")
        self.assertEqual(data["paths"]["delete_order"], "DELETE /orders/{id}")
        self.assertEqual(data["paths"]["get_item"], "GET /orders/{id}/items/{item_id}")
        self.assertEqual(data["paths"]["update_item"], "PUT /orders/{id}/items/{item_id}")
        self.assertEqual(data["paths"]["delete_item"], "DELETE /orders/{id}/items/{item_id}")

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
                "customer_id": test_order.customer_id,
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
            "customer_id": test_order.customer_id,
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
            "customer_id": test_order.customer_id,
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
            json={"customer_id": 1, "name": "X", "address": "Y", "email": "z@z.com"},
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
            json={"customer_id": 1, "name": "Missing fields"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_no_content_type(self):
        """It should return 415 when updating without Content-Type"""
        test_order = OrderFactory()
        test_order.create()

        response = self.client.put(
            f"{BASE_URL}/{test_order.id}",
            data="not json",
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_order_wrong_content_type(self):
        """It should return 415 when Content-Type is not application/json"""
        test_order = OrderFactory()
        test_order.create()

        response = self.client.put(
            f"{BASE_URL}/{test_order.id}",
            data="not json",
            content_type="text/plain",
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

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

    def test_update_order_then_get(self):
        """It should return the updated Order data on subsequent GET"""
        test_order = OrderFactory()
        test_order.create()

        updated_data = {
            "customer_id": test_order.customer_id,
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

    ######################################################################
    #  F I L T E R I N G   &   P A G I N A T I O N   T E S T S
    ######################################################################

    def test_list_orders_paginated(self):
        """It should return paginated results with metadata"""
        for _ in range(5):
            OrderFactory().create()

        response = self.client.get(f"{BASE_URL}?page=1&limit=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["page"], 1)
        self.assertEqual(data["limit"], 2)
        self.assertEqual(data["totalCount"], 5)
        self.assertEqual(data["totalPages"], 3)
        self.assertEqual(len(data["results"]), 2)

    def test_list_orders_paginated_last_page(self):
        """It should return remaining orders on the last page"""
        for _ in range(5):
            OrderFactory().create()

        response = self.client.get(f"{BASE_URL}?page=3&limit=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["totalPages"], 3)

    def test_list_orders_filter_by_status(self):
        """It should filter orders by status"""
        OrderFactory(status="Pending").create()
        OrderFactory(status="Pending").create()
        OrderFactory(status="Shipped").create()

        response = self.client.get(f"{BASE_URL}?status=Pending")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 2)
        for order in data:
            self.assertEqual(order["status"], "Pending")

    def test_list_orders_filter_by_customer_id(self):
        """It should filter orders by customer_id"""
        OrderFactory(customer_id=42).create()
        OrderFactory(customer_id=42).create()
        OrderFactory(customer_id=99).create()

        response = self.client.get(f"{BASE_URL}?customer_id=42")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 2)
        for order in data:
            self.assertEqual(order["customer_id"], 42)

    def test_list_orders_filter_combined_with_pagination(self):
        """It should filter and paginate at the same time"""
        for _ in range(4):
            OrderFactory(status="Pending", customer_id=10).create()
        OrderFactory(status="Shipped", customer_id=10).create()

        response = self.client.get(f"{BASE_URL}?status=Pending&customer_id=10&page=1&limit=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["totalCount"], 4)
        self.assertEqual(data["totalPages"], 2)
        self.assertEqual(len(data["results"]), 2)

    def test_list_orders_invalid_page(self):
        """It should return 400 for invalid page parameter"""
        response = self.client.get(f"{BASE_URL}?page=abc&limit=10")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_orders_invalid_limit(self):
        """It should return 400 for invalid limit parameter"""
        response = self.client.get(f"{BASE_URL}?page=1&limit=xyz")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_orders_negative_page(self):
        """It should return 400 for page < 1"""
        response = self.client.get(f"{BASE_URL}?page=0&limit=10")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_orders_negative_limit(self):
        """It should return 400 for limit < 1"""
        response = self.client.get(f"{BASE_URL}?page=1&limit=0")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_orders_invalid_customer_id(self):
        """It should return 400 for non-integer customer_id"""
        response = self.client.get(f"{BASE_URL}?customer_id=abc")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_orders_filter_by_name(self):
        """It should filter orders by name"""
        order = OrderFactory(name="Alice Smith")
        order.create()
        OrderFactory(name="Bob Jones").create()

        response = self.client.get(f"{BASE_URL}?name=Alice Smith")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Alice Smith")

    def test_list_orders_filter_by_created_after(self):
        """It should filter orders created after a given date"""
        order = OrderFactory()
        order.create()
        response = self.client.get(f"{BASE_URL}?created_after=2000-01-01T00:00:00")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)

    def test_list_orders_filter_by_created_before(self):
        """It should filter orders created before a given date"""
        OrderFactory().create()
        response = self.client.get(f"{BASE_URL}?created_before=2000-01-01T00:00:00")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_list_orders_invalid_created_after(self):
        """It should return 400 for invalid created_after format"""
        response = self.client.get(f"{BASE_URL}?created_after=not-a-date")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_orders_invalid_created_before(self):
        """It should return 400 for invalid created_before format"""
        response = self.client.get(f"{BASE_URL}?created_before=not-a-date")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_orders_filter_by_total_min(self):
        """It should filter orders with total >= total_min"""
        order = OrderFactory()
        order.create()
        item = ItemFactory(order_id=order.id, quantity=2, price=50.0)
        item.create()

        response = self.client.get(f"{BASE_URL}?total_min=50")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)

        response = self.client.get(f"{BASE_URL}?total_min=200")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_list_orders_filter_by_total_max(self):
        """It should filter orders with total <= total_max"""
        order = OrderFactory()
        order.create()
        item = ItemFactory(order_id=order.id, quantity=2, price=50.0)
        item.create()

        response = self.client.get(f"{BASE_URL}?total_max=150")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)

        response = self.client.get(f"{BASE_URL}?total_max=50")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_list_orders_invalid_total_min(self):
        """It should return 400 for non-numeric total_min"""
        response = self.client.get(f"{BASE_URL}?total_min=abc")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_orders_invalid_total_max(self):
        """It should return 400 for non-numeric total_max"""
        response = self.client.get(f"{BASE_URL}?total_max=abc")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_orders_no_filters_returns_all(self):
        """It should return all orders when no filters are provided"""
        for _ in range(3):
            OrderFactory().create()
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 3)

    def test_list_orders_filters_no_match_returns_empty(self):
        """It should return 200 with empty list when filters match nothing"""
        OrderFactory(status="Pending").create()
        response = self.client.get(f"{BASE_URL}?status=DoesNotExist")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    ######################################################################
    #  C A N C E L   O R D E R   A C T I O N   T E S T S
    ######################################################################

    def test_cancel_order_success(self):
        """It should cancel a Pending order"""
        order = OrderFactory(status="Pending")
        order.create()

        response = self.client.put(f"{BASE_URL}/{order.id}/cancel")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["status"], "Cancelled")

    def test_cancel_order_pending(self):
        """It should cancel a Pending order"""
        order = OrderFactory(status="Pending")
        order.create()

        response = self.client.put(f"{BASE_URL}/{order.id}/cancel")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["status"], "Cancelled")

    def test_cancel_order_already_shipped(self):
        """It should return 409 when cancelling a Shipped order"""
        order = OrderFactory(status="Shipped")
        order.create()

        response = self.client.put(f"{BASE_URL}/{order.id}/cancel")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_cancel_order_already_cancelled(self):
        """It should return 409 when cancelling an already Cancelled order"""
        order = OrderFactory(status="Cancelled")
        order.create()

        response = self.client.put(f"{BASE_URL}/{order.id}/cancel")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_cancel_order_not_found(self):
        """It should return 404 when cancelling a non-existent order"""
        response = self.client.put(f"{BASE_URL}/0/cancel")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    #  S T A T U S   W O R K F L O W   T E S T S
    ######################################################################

    def test_order_default_status_is_pending(self):
        """It should assign Pending as the default status on creation"""
        order = OrderFactory()
        data = order.serialize()
        data.pop("status", None)
        response = self.client.post(BASE_URL, json=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.get_json()["status"], "Pending")

    def test_update_order_valid_transition_pending_to_paid(self):
        """It should allow a valid Pending -> Paid transition"""
        orders = self._create_orders(1)
        order = orders[0]
        payload = order.serialize()
        payload["status"] = "Paid"
        response = self.client.put(f"{BASE_URL}/{order.id}", json=payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_json()["status"], "Paid")

    def test_update_order_valid_transition_paid_to_shipped(self):
        """It should allow a valid Paid -> Shipped transition"""
        order = OrderFactory(status="Paid")
        order.create()
        payload = order.serialize()
        payload["status"] = "Shipped"
        response = self.client.put(f"{BASE_URL}/{order.id}", json=payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_json()["status"], "Shipped")

    def test_update_order_invalid_transition_pending_to_shipped(self):
        """It should reject an invalid Pending -> Shipped transition"""
        orders = self._create_orders(1)
        order = orders[0]
        payload = order.serialize()
        payload["status"] = "Shipped"
        response = self.client.put(f"{BASE_URL}/{order.id}", json=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_invalid_transition_from_cancelled(self):
        """It should reject any transition out of Cancelled"""
        order = OrderFactory(status="Cancelled")
        order.create()
        payload = order.serialize()
        payload["status"] = "Pending"
        response = self.client.put(f"{BASE_URL}/{order.id}", json=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_invalid_transition_from_shipped(self):
        """It should reject any transition out of Shipped"""
        order = OrderFactory(status="Shipped")
        order.create()
        payload = order.serialize()
        payload["status"] = "Paid"
        response = self.client.put(f"{BASE_URL}/{order.id}", json=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_invalid_status_value(self):
        """It should return 400 when creating an order with an invalid status"""
        order = OrderFactory()
        payload = order.serialize()
        payload["status"] = "InvalidStatus"
        response = self.client.post(BASE_URL, json=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_invalid_status_value(self):
        """It should return 400 when updating an order with an invalid status value"""
        orders = self._create_orders(1)
        order = orders[0]
        payload = order.serialize()
        payload["status"] = "Bogus"
        response = self.client.put(f"{BASE_URL}/{order.id}", json=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_status_included_in_order_response(self):
        """It should include status in order API response"""
        orders = self._create_orders(1)
        order = orders[0]
        response = self.client.get(f"{BASE_URL}/{order.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "Pending")

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
        _, item = self._create_order_with_item()
        order2 = OrderFactory()
        order2.create()

        response = self.client.get(
            f"{BASE_URL}/{order2.id}/items/{item.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    #  U P D A T E   I T E M   T E S T   C A S E S
    ######################################################################

    def test_update_item_in_order(self):
        """It should Update an Item in an Order"""
        order, item = self._create_order_with_item()

        updated_data = {
            "name": "Updated Widget",
            "quantity": 5,
            "price": 19.99,
        }
        response = self.client.put(
            f"{BASE_URL}/{order.id}/items/{item.id}",
            json=updated_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], "Updated Widget")
        self.assertEqual(data["quantity"], 5)
        self.assertEqual(data["price"], 19.99)
        self.assertEqual(data["id"], item.id)
        self.assertEqual(data["order_id"], order.id)

    def test_update_item_order_not_found(self):
        """It should return 404 when updating an Item in a non-existent Order"""
        response = self.client.put(
            f"{BASE_URL}/0/items/0",
            json={"name": "X", "quantity": 1, "price": 1.0},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("not found", data["message"])

    def test_update_item_not_found(self):
        """It should return 404 when the Item does not exist"""
        order = OrderFactory()
        order.create()

        response = self.client.put(
            f"{BASE_URL}/{order.id}/items/0",
            json={"name": "X", "quantity": 1, "price": 1.0},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("not found", data["message"])

    def test_update_item_wrong_order(self):
        """It should return 404 when the Item belongs to a different Order"""
        _, item = self._create_order_with_item()
        order2 = OrderFactory()
        order2.create()

        response = self.client.put(
            f"{BASE_URL}/{order2.id}/items/{item.id}",
            json={"name": "X", "quantity": 1, "price": 1.0},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_item_bad_data(self):
        """It should return 400 when updating an Item with missing fields"""
        order, item = self._create_order_with_item()

        response = self.client.put(
            f"{BASE_URL}/{order.id}/items/{item.id}",
            json={"name": "Missing fields"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_item_no_content_type(self):
        """It should return 415 when updating an Item without Content-Type"""
        order, item = self._create_order_with_item()

        response = self.client.put(
            f"{BASE_URL}/{order.id}/items/{item.id}",
            data="not json",
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    ######################################################################
    #  D E L E T E   I T E M   T E S T   C A S E S
    ######################################################################

    def test_delete_item_success_pending(self):
        """It should Delete an item from a Pending order"""
        test_order = OrderFactory(status="Pending")
        test_order.create()
        test_item = ItemFactory(order_id=test_order.id)
        test_item.create()

        response = self.client.delete(f"{BASE_URL}/{test_order.id}/items/{test_item.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertIn("deleted", data["message"])

        self.assertIsNone(Item.find(test_item.id))

    def test_delete_item_success_unprocessed(self):
        """It should Delete an item from an Unprocessed order"""
        test_order = OrderFactory(status="Unprocessed")
        test_order.create()
        test_item = ItemFactory(order_id=test_order.id)
        test_item.create()

        response = self.client.delete(f"{BASE_URL}/{test_order.id}/items/{test_item.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertIn("deleted", data["message"])

        self.assertIsNone(Item.find(test_item.id))

    def test_delete_item_order_not_found(self):
        """It should return 404 when order does not exist"""
        response = self.client.delete(f"{BASE_URL}/0/items/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_item_not_found(self):
        """It should return 404 when item does not exist in order"""
        test_order = OrderFactory(status="Pending")
        test_order.create()

        response = self.client.delete(f"{BASE_URL}/{test_order.id}/items/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_item_wrong_order_status(self):
        """It should return 409 when order status does not allow deletion"""
        test_order = OrderFactory(status="Completed")
        test_order.create()
        test_item = ItemFactory(order_id=test_order.id)
        test_item.create()

        response = self.client.delete(f"{BASE_URL}/{test_order.id}/items/{test_item.id}")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    ######################################################################
    #  E R R O R   H A N D L E R   T E S T S
    ######################################################################

    def test_method_not_allowed(self):
        """It should return 405 when using an unsupported HTTP method"""
        response = self.client.patch(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
