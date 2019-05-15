Feature: Workflows 
  As a user, I want to run various local workflows with GeneFlow

  Scenario: Parameter strings with spaces are correctly passed to workflow step shell commands when running local workflows.
    Given The "local" "param-space" workflow has been installed
    When I run the "local" "param-space" workflow with a "string" parameter of "hello world"
    Then The "local" "param-space" workflow "print" step produces an output file called "output.txt" with contents "hello world"
  
  Scenario: Apps with multi exec blocks are correctly executed locally.
    Given The "local" "multi-exec" workflow has been installed
    When I run the "local" "multi-exec" workflow with a "string" parameter of "hello world"
    Then The "local" "multi-exec" workflow "print" step produces an output file called "output.txt" with multi-line contents
        | line        |
        | hello world |
        | hello world |

  Scenario: Apps with if-else exec blocks are correctly executed locally.
    Given The "local" "if-else-exec" workflow has been installed
    When I run the "local" "if-else-exec" workflow with a "string" parameter of "hello world"
    Then The "local" "if-else-exec" workflow "print" step produces an output file called "output.txt" with contents "hello world else condition"

  Scenario: Apps with str-contain if blocks are correctly executed locally.
    Given The "local" "str-contain" workflow has been installed
    When I run the "local" "str-contain" workflow with a "super_string" parameter of "super string"
    Then The "local" "str-contain" workflow "contain" step produces an output file called "output.txt" with contents "string contains"

    When I run the "local" "str-contain" workflow with a "super_string" parameter of "super"
    Then The "local" "str-contain" workflow "contain" step produces an output file called "output.txt" with contents "string does not contain"

  Scenario: Apps with Any input or parameter types are correctly handled locally.
    Given The "local" "any-type" workflow has been installed
    When I run the "local" "any-type" workflow with a "param" parameter of "file.txt"
    Then The "local" "any-type" workflow "print" step produces an output file called "output.txt" with multi-line contents
        | line     |
        | test.txt |
        | file.txt |
