Feature: Workflows 
  As a user, I want to run various workflows with GeneFlow

  Scenario: Parameter strings with spaces are correctly passed to workflow step shell commands when running local workflows.
    Given The "local" "stringprinter" workflow has been installed
    When I run the "local" "stringprinter" workflow with a "string" parameter of "hello world"
    Then The "local" "stringprinter" workflow "print" step produces an output file called "output.txt" with contents "hello world"
  
  Scenario: Parameter strings with spaces are correctly passed to workflow step shell commands when running Agave workflows.
    Given The "agave" "stringprinter" workflow has been installed
    When I run the "agave" "stringprinter" workflow with a "string" parameter of "hello world"
    Then The "agave" "stringprinter" workflow "print" step produces an output file called "output.txt" with contents "hello world"

  Scenario: Apps with multi exec blocks are correctly executed locally.
    Given The "local" "multiexec" workflow has been installed
    When I run the "local" "multiexec" workflow with a "string" parameter of "hello world"
    Then The "local" "multiexec" workflow "print" step produces an output file called "output.txt" with contents "hello world\nhello world"
 
