######################################################################
# Orders Steps
#
# Steps file for orders.feature
######################################################################

import requests
from compare3 import expect
from behave import given  # pylint: disable=no-name-in-module

HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

WAIT_TIMEOUT = 60


def get_service_url(context):
    """Returns the service root URL"""
    return context.base_url.removesuffix("/static/index.html")


@given('the following orders')
def step_impl(context):
    """Delete all Orders and load new ones"""
    service_url = get_service_url(context)
    rest_endpoint = f"{service_url}/orders"

    # Get all existing orders
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    expect(context.resp.status_code).equal_to(HTTP_200_OK)

    # Delete them one by one
    for order in context.resp.json():
        context.resp = requests.delete(
            f"{rest_endpoint}/{order['id']}",
            timeout=WAIT_TIMEOUT,
        )
        expect(context.resp.status_code).equal_to(HTTP_204_NO_CONTENT)

    # Load fresh test data
    for row in context.table:
        payload = {
            "customer_id": int(row["customer_id"]),
            "name": row["name"],
            "address": row["address"],
            "email": row["email"],
            "status": row["status"],
        }
        context.resp = requests.post(
            rest_endpoint,
            json=payload,
            timeout=WAIT_TIMEOUT,
        )
        expect(context.resp.status_code).equal_to(HTTP_201_CREATED)