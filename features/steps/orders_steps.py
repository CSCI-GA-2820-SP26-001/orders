######################################################################
# Orders Steps
#
# Steps file for orders.feature
######################################################################

import requests
from compare3 import expect
from behave import given, when, then  # pylint: disable=no-name-in-module

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

# ****************************************
# When Steps
# ****************************************

@when('I visit the "Home Page"')
def step_impl(context):
    context.driver.get(context.base_url)

@when('I set the "{field}" to "{value}"')
def step_impl(context, field, value):
    field_map = {
        "customer_id": "order_customer_id",
        "name": "order_name",
        "address": "order_address",
        "email": "order_email",
        "status": "order_status"
    }
    element_id = field_map.get(field, field)
    context.driver.find_element("id", element_id).clear()
    context.driver.find_element("id", element_id).send_keys(value)

@when('I press the "{button}" button')
def step_impl(context, button):
    button_map = {
        "Create": "create-btn",
        "Search": "search-btn",
        "Clear": "clear-btn"
    }
    button_id = button_map.get(button, button.lower() + "-btn")
    context.driver.find_element("id", button_id).click()


# ****************************************
# Then Steps
# ****************************************

@then('I should see the message "{message}"')
def step_impl(context, message):
    flash = context.driver.find_element("id", "flash_message").text
    expect(flash).equal_to(message)

@then('I should see "{text}" in the results')
def step_impl(context, text):
    results = context.driver.find_element("id", "search_results").text
    expect(results).contains(text)

@then('I should see "{text}" in the title')
def step_impl(context, text):
    expect(context.driver.title).contains(text)

@then('I should not see "{text}"')
def step_impl(context, text):
    page_text = context.driver.find_element("tag name", "body").text
    expect(page_text).does_not_contain(text)