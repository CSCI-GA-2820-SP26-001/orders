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
from service.models import Order, Item, DataValidationError
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Orders REST API Service",
            version="1.0.0",
            paths={
                "list_orders": "GET /orders",
                "create_order": "POST /orders",
                "get_order": "GET /orders/{id}",
                "update_order": "PUT /orders/{id}",
                "delete_order": "DELETE /orders/{id}",
                "get_item": "GET /orders/{id}/items/{item_id}",
                "update_item": "PUT /orders/{id}/items/{item_id}",
                "delete_item": "DELETE /orders/{id}/items/{item_id}",
            },
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# LIST ALL ORDERS
######################################################################
@app.route("/orders", methods=["GET"])
def list_orders():
    """Returns all of the Orders"""
    app.logger.info("Request for order list")

    orders = Order.all()
    results = [order.serialize() for order in orders]
    app.logger.info("Returning %d orders", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# CREATE A NEW ORDER
######################################################################
@app.route("/orders", methods=["POST"])
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
    check_content_type("application/json")

    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

    data = request.get_json()
    app.logger.info("Processing: %s", data)
    order.deserialize(data)
    order.update()
    app.logger.info("Order with id [%s] updated.", order_id)
    return jsonify(order.serialize()), status.HTTP_200_OK


######################################################################
# READ AN ITEM IN AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["GET"])
def get_order_item(order_id, item_id):
    """
    Read an Item in an Order

    This endpoint will return an Item from an Order based on their ids
    """
    app.logger.info(
        "Request to Read item %s in order %s", item_id, order_id
    )

    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' was not found.",
        )

    item = Item.find(item_id)
    if not item or item.order_id != order_id:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' was not found in order '{order_id}'.",
        )

    app.logger.info("Returning item %s from order %s", item_id, order_id)
    return jsonify(item.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE AN ITEM IN AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["PUT"])
def update_order_item(order_id, item_id):
    """
    Update an Item in an Order

    This endpoint will update an Item in an Order based on their ids
    """
    app.logger.info(
        "Request to Update item %s in order %s", item_id, order_id
    )
    check_content_type("application/json")

    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' was not found.",
        )

    item = Item.find(item_id)
    if not item or item.order_id != order_id:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' was not found in order '{order_id}'.",
        )

    data = request.get_json()
    app.logger.info("Processing: %s", data)
    item.deserialize(data)
    item.id = item_id
    item.order_id = order_id
    order.update()

    app.logger.info("Item %s in order %s updated.", item_id, order_id)
    return jsonify(item.serialize()), status.HTTP_200_OK


######################################################################
# UTILITY FUNCTIONS
######################################################################
def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error(
        "Invalid Content-Type: %s", request.headers["Content-Type"]
    )
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )
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


######################################################################
# DELETE AN ITEM FROM AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["DELETE"])
def delete_item(order_id, item_id):
    """
    Delete an Item from an Order

    This endpoint will delete an Item from an Order based on the order id and item id
    """
    app.logger.info(
        "Request to Delete Item %d from Order %d", item_id, order_id
    )

    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

    if order.status not in ("Pending", "Unprocessed"):
        abort(
            status.HTTP_409_CONFLICT,
            f"Order with id '{order_id}' has status '{order.status}' and cannot have items deleted.",
        )

    item = None
    for i in order.items:
        if i.id == item_id:
            item = i
            break

    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' was not found in Order '{order_id}'.",
        )

    item.delete()
    app.logger.info("Item with ID: %d deleted from Order %d.", item_id, order_id)
    return jsonify(message=f"Item with id '{item_id}' has been deleted from order '{order_id}'."), status.HTTP_200_OK
