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