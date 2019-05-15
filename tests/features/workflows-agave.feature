Feature: Workflows 
  As a user, I want to run various Agave workflows with GeneFlow

  Scenario: Parameter strings with spaces are correctly passed to workflow step shell commands when running Agave workflows.
    Given The "agave" "param-space" workflow has been installed
    When I run the "agave" "param-space" workflow with a "string" parameter of "hello world"
    Then The "agave" "param-space" workflow "print" step produces an output file called "output.txt" with contents "hello world"

  Scenario: Apps with multi exec blocks are correctly executed in Agave.
    Given The "agave" "multi-exec" workflow has been installed
    When I run the "agave" "multi-exec" workflow with a "string" parameter of "hello world"
    Then The "agave" "multi-exec" workflow "print" step produces an output file called "output.txt" with multi-line contents
        | line        |
        | hello world |
        | hello world |

  Scenario: Apps with if-else exec blocks are correctly executed in Agave.
    Given The "agave" "if-else-exec" workflow has been installed
    When I run the "agave" "if-else-exec" workflow with a "string" parameter of "hello world"
    Then The "agave" "if-else-exec" workflow "print" step produces an output file called "output.txt" with contents "hello world else condition"

  Scenario: Apps with str-contain if blocks are correctly executed in Agave.
    Given The "agave" "str-contain" workflow has been installed
    When I run the "agave" "str-contain" workflow with a "super_string" parameter of "super string"
    Then The "agave" "str-contain" workflow "contain" step produces an output file called "output.txt" with contents "string contains"

    When I run the "agave" "str-contain" workflow with a "super_string" parameter of "super"
    Then The "agave" "str-contain" workflow "contain" step produces an output file called "output.txt" with contents "string does not contain"

  Scenario: Apps with Any input or parameter types are correctly handled in Agave.
    Given The "agave" "any-type" workflow has been installed
    When I run the "agave" "any-type" workflow with a "param" parameter of "file.txt"
    Then The "agave" "any-type" workflow "print" step produces an output file called "output.txt" with multi-line contents
        | line     |
        | test.txt |
        | file.txt |
