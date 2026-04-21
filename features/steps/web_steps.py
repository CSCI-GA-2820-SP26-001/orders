######################################################################
# Web Steps for Orders UI
######################################################################

# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa

import re
from typing import Any
from behave import when, then  # pylint: disable=no-name-in-module
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions

ID_PREFIX = "order_"


def save_screenshot(context: Any, filename: str) -> None:
    """Takes a snapshot of the web page for debugging"""
    filename = re.sub(r"[^\w\s]", "", filename)
    filename = re.sub(r"\s+", "-", filename)
    context.driver.save_screenshot(f"./captures/{filename}.png")


@when('I visit the "Home Page"')
def step_impl(context: Any) -> None:
    """Visit the Orders UI home page"""
    context.driver.get(context.base_url)


@then('I should see "{message}" in the title')
def step_impl(context: Any, message: str) -> None:
    """Check the browser title"""
    assert message in context.driver.title


@then('I should not see "{text_string}"')
def step_impl(context: Any, text_string: str) -> None:
    """Ensure the body does not contain text"""
    element = context.driver.find_element(By.TAG_NAME, "body")
    assert text_string not in element.text


@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context: Any, element_name: str, text_string: str) -> None:
    """Set a text input field"""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(text_string)


@when('I select "{text}" in the "{element_name}" dropdown')
def step_impl(context: Any, text: str, element_name: str) -> None:
    """Select a dropdown option"""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = Select(context.driver.find_element(By.ID, element_id))
    element.select_by_visible_text(text)


@then('I should see "{text}" in the "{element_name}" dropdown')
def step_impl(context: Any, text: str, element_name: str) -> None:
    """Verify selected dropdown option"""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = Select(context.driver.find_element(By.ID, element_id))
    assert element.first_selected_option.text == text


@then('the "{element_name}" field should be empty')
def step_impl(context: Any, element_name: str) -> None:
    """Verify a field is empty"""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    assert element.get_attribute("value") == ""


@then('the "{element_name}" field should not be empty')
def step_impl(context: Any, element_name: str) -> None:
    """Verify a field has a value"""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        lambda d: d.find_element(By.ID, element_id).get_attribute("value") != ""
    )
    assert element


@when('I copy the "{element_name}" field')
def step_impl(context: Any, element_name: str) -> None:
    """Copy a field value"""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute("value")


@when('I paste the "{element_name}" field')
def step_impl(context: Any, element_name: str) -> None:
    """Paste a field value"""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)


@when('I press the "{button}" button')
def step_impl(context: Any, button: str) -> None:
    """Click a button"""
    button_id = button.lower().replace(" ", "_") + "-btn"
    context.driver.find_element(By.ID, button_id).click()


@then('I should see "{name}" in the results')
def step_impl(context: Any, name: str) -> None:
    """Verify text appears in search results"""
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "search_results"), name
        )
    )
    assert found


@then('I should not see "{name}" in the results')
def step_impl(context: Any, name: str) -> None:
    """Verify text does not appear in search results"""
    element = context.driver.find_element(By.ID, "search_results")
    assert name not in element.text


@then('I should see the message "{message}"')
def step_impl(context: Any, message: str) -> None:
    """Verify flash message text"""
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "flash_message"), message
        )
    )
    assert found


@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context: Any, text_string: str, element_name: str) -> None:
    """Verify a field contains a value"""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id), text_string
        )
    )
    assert found


@when('I change "{element_name}" to "{text_string}"')
def step_impl(context: Any, element_name: str, text_string: str) -> None:
    """Change an existing field value"""
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)