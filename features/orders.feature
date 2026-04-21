Feature: Orders UI test environment
    As an eCommerce manager
    I need a web interface to manage orders
    So that I can view the orders in the system

Background:
    Given the following orders
        | customer_id | name          | address             | email                 | status    |
        | 1001        | Alice Johnson | 1 Main Street       | alice@example.com     | Pending   |
        | 1002        | Bob Smith     | 22 Park Avenue      | bob@example.com       | Paid      |
        | 1003        | Carol Davis   | 305 Broadway        | carol@example.com     | Shipped   |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Orders UI" in the title
    And I should not see "404 Not Found"

Scenario: List all orders
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Alice Johnson" in the results
    And I should see "Bob Smith" in the results
    And I should see "Carol Davis" in the results

Scenario: Retrieve an order by ID
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "Name" field
    And I copy the "ID" field
    And I press the "Clear" button
    Then the "Order ID" field should be empty
    And the "Name" field should be empty
    When I paste the "Order ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And the "Name" field should not be empty
    And the "Customer ID" field should not be empty
    And the "Address" field should not be empty
    And the "Email" field should not be empty

Scenario: Retrieve an order with a non-existent ID
    When I visit the "Home Page"
    And I set the "Order ID" to "0"
    And I press the "Retrieve" button
    Then I should see the message "was not found"
    And the "Name" field should be empty

Scenario: Search orders by status
    When I visit the "Home Page"
    And I select "Paid" in the "Status" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Bob Smith" in the results
    And I should not see "Alice Johnson" in the results
    And I should not see "Carol Davis" in the results

Scenario: Search orders by customer ID
    When I visit the "Home Page"
    And I set the "Customer ID" to "1003"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Carol Davis" in the results
    And I should not see "Alice Johnson" in the results
    And I should not see "Bob Smith" in the results

Scenario: Search orders by name
    When I visit the "Home Page"
    And I set the "Name" to "Alice Johnson"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Alice Johnson" in the results
    And I should not see "Bob Smith" in the results
    And I should not see "Carol Davis" in the results

Scenario: Update an order
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "ID" field
    And I press the "Clear" button
    And I paste the "Order ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    When I change "Name" to "Updated Name"
    And I change "Address" to "999 New Street"
    And I press the "Update" button
    Then I should see the message "Order has been Updated!"
    And I should see "Updated Name" in the "Name" field
    And I should see "999 New Street" in the "Address" field
    When I press the "Clear" button
    And I paste the "Order ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Updated Name" in the "Name" field
    And I should see "999 New Street" in the "Address" field

Scenario: Cancel an order
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "ID" field
    And I press the "Clear" button
    And I paste the "Order ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    When I press the "Cancel" button
    Then I should see the message "Order has been Cancelled!"
    And I should see "Cancelled" in the "Status" field

Scenario: Delete an order
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "ID" field
    And I press the "Clear" button
    And I paste the "Order ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    When I press the "Delete" button
    Then I should see the message "Order has been Deleted!"
    And the "Order ID" field should be empty
    And the "Name" field should be empty
    When I paste the "Order ID" field
    And I press the "Retrieve" button
    Then I should see the message "was not found"
