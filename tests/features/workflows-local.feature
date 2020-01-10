Feature: Workflows 
  As a user, I want to run various local workflows with GeneFlow

  Scenario: Parameter strings with spaces are correctly passed to workflow step shell commands when running local workflows.
    Given The "local" "param-space" workflow has been installed
    When I run the "local" "param-space" workflow with the following inputs and parameters
        | type      | name   | value         |
        | input     | input  | data/test.txt |
        | parameter | string | hello world   |
    Then The "local" "param-space" workflow "print" step produces an output file called "output.txt" with the following contents
        | line        |
        | hello world |
  
  Scenario: Apps with multi exec blocks are correctly executed locally.
    Given The "local" "multi-exec" workflow has been installed
    When I run the "local" "multi-exec" workflow with the following inputs and parameters
        | type      | name   | value         |
        | input     | input  | data/test.txt |
        | parameter | string | hello world   |
    Then The "local" "multi-exec" workflow "print" step produces an output file called "output.txt" with the following contents
        | line        |
        | hello world |
        | hello world |

  Scenario: Apps with if-else exec blocks are correctly executed locally.
    Given The "local" "if-else-exec" workflow has been installed
    When I run the "local" "if-else-exec" workflow with the following inputs and parameters
        | type      | name   | value         |
        | input     | input  | data/test.txt |
        | parameter | string | hello world   |
    Then The "local" "if-else-exec" workflow "print" step produces an output file called "output.txt" with the following contents
        | line                       |
        | hello world else condition |

  Scenario: Apps with str-contain if blocks are correctly executed locally.
    Given The "local" "str-contain" workflow has been installed
    When I run the "local" "str-contain" workflow with the following inputs and parameters
        | type      | name         | value         |
        | input     | input        | data/test.txt |
        | parameter | super_string | super string  |
    Then The "local" "str-contain" workflow "contain" step produces an output file called "output.txt" with the following contents
        | line            |
        | string contains |

    When I run the "local" "str-contain" workflow with the following inputs and parameters
        | type      | name         | value         |
        | input     | input        | data/test.txt |
        | parameter | super_string | super         |
    Then The "local" "str-contain" workflow "contain" step produces an output file called "output.txt" with the following contents
        | line                    |
        | string does not contain |

  Scenario: Apps with Any input or parameter types are correctly handled locally.
    Given The "local" "any-type" workflow has been installed
    When I run the "local" "any-type" workflow with the following inputs and parameters
        | type      | name  | value         |
        | input     | input | data/test.txt |
        | parameter | param | file.txt      |
    Then The "local" "any-type" workflow "print" step produces an output file called "output.txt" with the following contents
        | line     |
        | test.txt |
        | file.txt |

  Scenario: Workflows run locally place logs in a consistent and structured location.
    Given The "local" "rotate" workflow has been installed
    When I run the "local" "rotate" workflow with the following inputs and parameters
        | type  | name         | value |
        | input | input_folder | data  |
    Then The "local" "rotate" workflow "rotate_3" step produces an output file called "_log/test1_rot1_rot2b_rot3.txt.log" with the following contents
        | line      |
        | log stuff |
    
  Scenario: Apps with singularity commands are correctly executed locally.
    Given The "local" "singularity-exec" workflow has been installed
    When I run the "local" "singularity-exec" workflow with the following inputs and parameters
        | type      | name   | value         |
        | input     | input  | data/test.txt |
        | parameter | string | hello world   |
    Then The "local" "singularity-exec" workflow "print" step produces an output file called "output.txt" with the following contents
        | line        |
        | hello world |

  Scenario: Workflows with inputs that have spaces in the path run successfully locally.
    Given The "local" "rotate" workflow has been installed
    When I run the "local" "rotate" workflow with the following inputs and parameters
        | type  | name         | value                  |
        | input | input_folder | data/data with spaces  |
    Then The "local" "rotate" workflow "rotate_3" step produces an output file called "test 1_rot1_rot2b_rot3.txt" with the following contents
        | line   |
        | Nkrru  |
        | Cuxrj! |

  Scenario: Apps with invalid description lengths cannot be installed locally.
    Then The "local" "test-app-def-01" workflow cannot be installed
