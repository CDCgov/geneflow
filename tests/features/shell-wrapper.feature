Feature: Shell Wrapper
  As a user, I want to run shell commands and manage processes

  Scenario: Shell invokes a valid command
    Given I create a "test-shell" Shell instance
    When I run the invoke method for the "test-shell" Shell instance with a valid argument
    Then I see a valid response for invoke method of the "test-shell" Shell instance

  Scenario: Shell invokes an invalid command
    Given I create a "test-shell" Shell instance
    When I run the invoke method for the "test-shell" Shell instance with an invalid argument
    Then I see a False return value for the invoke method of the "test-shell" Shell instance

  Scenario: Shell spawns a valid command
    Given I create a "test-shell" Shell instance
    When I run the spawn method for the "test-shell" Shell instance with a valid argument
    Then I see a valid response for the spawn method of the "test-shell" Shell instance

  Scenario: Shell spawns an invalid command
    Given I create a "test-shell" Shell instance
    When I run the spawn method for the "test-shell" Shell instance with an invalid argument
    Then I see a negative result for the spawn method of the "test-shell" Shell instance

  Scenario: Shell checks if a valid process is running
    Given I create a "test-shell" Shell instance
    When I run the spawn method for the "test-shell" Shell instance with a valid argument
    And I call the is_running method for the "test-shell" Shell instance
    Then I see a value of True returned for is_running method of the "test-shell" Shell instance


