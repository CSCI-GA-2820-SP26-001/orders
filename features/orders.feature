Feature: Orders UI test environment
    As a Developer
    I need the Orders UI BDD environment
    So that I can run automated UI tests with Selenium and Behave

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Orders UI" in the title
    And I should not see "404 Not Found"