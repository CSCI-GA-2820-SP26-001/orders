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
from service.models import db, Order

from .factories import OrderFactory

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

    # Todo: Add your test cases here...

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


    @app.route("/orders/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    """
    Update a Order

    This endpoint will update a Order based the body that is posted
    """
    app.logger.info(
        "Request to Update a order with id [%s]", order_id
    )
    check_content_type("application/json")

    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' was not found.",
        )

    data = request.get_json()
    app.logger.info("Processing: %s", data)
    order.deserialize(data)

    order.update()

    app.logger.info("Order with ID: %d updated.", order.id)
    return jsonify(order.serialize()), status.HTTP_200_OK