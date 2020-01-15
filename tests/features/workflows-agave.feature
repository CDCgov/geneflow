Feature: Workflows 
  As a user, I want to run various Agave workflows with GeneFlow

  Scenario: Parameter strings with spaces are correctly passed to workflow step shell commands when running Agave workflows.
    Given The "agave" "param-space" workflow has been installed
    When I run the "agave" "param-space" workflow with the following inputs and parameters
        | type      | name   | value         |
        | input     | input  | data/test.txt |
        | parameter | string | hello world   |
    Then The "agave" "param-space" workflow "print" step produces an output file called "output.txt" with the following contents
        | line        |
        | hello world |

  Scenario: Apps with multi exec blocks are correctly executed in Agave.
    Given The "agave" "multi-exec" workflow has been installed
    When I run the "agave" "multi-exec" workflow with the following inputs and parameters
        | type      | name   | value         |
        | input     | input  | data/test.txt |
        | parameter | string | hello world   |
    Then The "agave" "multi-exec" workflow "print" step produces an output file called "output.txt" with the following contents
        | line        |
        | hello world |
        | hello world |

  Scenario: Apps with if-else exec blocks are correctly executed in Agave.
    Given The "agave" "if-else-exec" workflow has been installed
    When I run the "agave" "if-else-exec" workflow with the following inputs and parameters
        | type      | name   | value         |
        | input     | input  | data/test.txt |
        | parameter | string | hello world   |
    Then The "agave" "if-else-exec" workflow "print" step produces an output file called "output.txt" with the following contents
        | line                       |
        | hello world else condition |

  Scenario: Apps with str-contain if blocks are correctly executed in Agave.
    Given The "agave" "str-contain" workflow has been installed
    When I run the "agave" "str-contain" workflow with the following inputs and parameters
        | type      | name         | value         |
        | input     | input        | data/test.txt |
        | parameter | super_string | super string  |
    Then The "agave" "str-contain" workflow "contain" step produces an output file called "output.txt" with the following contents
        | line            |
        | string contains |

    When I run the "agave" "str-contain" workflow with the following inputs and parameters
        | type      | name         | value         |
        | input     | input        | data/test.txt |
        | parameter | super_string | super         |
    Then The "agave" "str-contain" workflow "contain" step produces an output file called "output.txt" with the following contents
        | line                    |
        | string does not contain |

  Scenario: Apps with Any input or parameter types are correctly handled in Agave.
    Given The "agave" "any-type" workflow has been installed
    When I run the "agave" "any-type" workflow with the following inputs and parameters
        | type      | name  | value         |
        | input     | input | data/test.txt |
        | parameter | param | file.txt      |
    Then The "agave" "any-type" workflow "print" step produces an output file called "output.txt" with the following contents
        | line     |
        | test.txt |
        | file.txt |

  Scenario: Workflows run in Agave place logs in a consistent and structured location.
    Given The "agave" "rotate" workflow has been installed
    When I run the "agave" "rotate" workflow with the following inputs and parameters
        | type  | name         | value |
        | input | input_folder | data  |
    Then The "agave" "rotate" workflow "rotate_3" step produces an output file called "_log/test1_rot1_rot2b_rot3.txt.log" with the following contents
        | line      |
        | log stuff |

  Scenario: Apps with singularity commands are correctly executed in Agave.
    Given The "agave" "singularity-exec" workflow has been installed
    When I run the "agave" "singularity-exec" workflow with the following inputs and parameters
        | type      | name   | value         |
        | input     | input  | data/test.txt |
        | parameter | string | hello world   |
    Then The "agave" "singularity-exec" workflow "print" step produces an output file called "output.txt" with the following contents
        | line        |
        | hello world |

  Scenario: Workflows with inputs that have spaces in the path run successfully in Agave.
    Given The "agave" "rotate" workflow has been installed
    When I run the "agave" "rotate" workflow with the following inputs and parameters
        | type  | name         | value                  |
        | input | input_folder | data/data with spaces  |
    Then The "agave" "rotate" workflow "rotate_3" step produces an output file called "test 1_rot1_rot2b_rot3.txt" with the following contents
        | line   |
        | Nkrru  |
        | Cuxrj! |
 
  Scenario: Apps with invalid description lengths cannot be installed locally.
    Then The "agave" "test-app-def-01" workflow cannot be installed
