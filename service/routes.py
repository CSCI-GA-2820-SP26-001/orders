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
Order Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Order"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Order, DataValidationError
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        "This is the main page of the order part :)",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# Todo: Place your REST API code here ...

def create_order():
    """
    Create a Order
    This endpoint will create a Order based the data in the body that is posted
    """
    app.logger.info("Request to Create a Order...")
    check_content_type("application/json")

    order = Order()
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    order.deserialize(data)

    order.create()
    app.logger.info("Order with new id [%s] saved!", order.id)

    location_url = url_for(
        "get_orders", order_id=order.id, _external=True
    )
    return (
        jsonify(order.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )

@app.route("/orders/<int:order_id>", methods=["GET"])
def get_orders(order_id):
    """
    Retrieve a single order

    This endpoint will return a order based on it's id
    """
    app.logger.info("Request to Retrieve a order with id [%s]", order_id)

    # Attempt to find the order and abort if not found
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"order with id '{order_id}' was not found.")

    app.logger.info("Returning order: %s", order.id)
    return jsonify(order.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE AN EXISTING ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods=["PUT"])
def update_orders(order_id):
    """
    Update an Order

    This endpoint will update an Order based on its id
    """
    app.logger.info("Request to Update an order with id [%s]", order_id)

    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"order with id '{order_id}' was not found.")

    data = request.get_json()
    if not data:
        abort(status.HTTP_400_BAD_REQUEST, "No data provided")

    order.deserialize(data)
    order.update()
    app.logger.info("Order with id [%s] updated.", order_id)
    return jsonify(order.serialize()), status.HTTP_200_OK
# Delete a order with API
@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    """
    Delete a Order

    This endpoint will delete a Order based the id specified in the path
    """
    app.logger.info(
        "Request to Delete a order with id [%s]", order_id
    )

    order = Order.find(order_id)
    if order:
        app.logger.info("Order with ID: %d found.", order.id)
        order.delete()

    app.logger.info("Order with ID: %d delete complete.", order_id)
    return {}, status.HTTP_204_NO_CONTENT
