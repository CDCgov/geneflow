Feature: URI Parser
  As a user, I want to parse URIs

  Scenario: Parse local URIs
    Given I have a URI
      | uri                          |
      | local://server/path/to/name  |
      | local://server/path/to/name/ |
      | local:/path/to/name          |
      | local:/path/to/name/         |
      | local:/path//to/name/        |
      | local:/name                  |
      | local://server               |
      | local://server/              |
      | local:///                    |
      | local:/                      |
      | local:relative/path          |
      | local:relative/path/         |
      | local:./path/                |
      | local:../path/               |
      | local:relative               |
      | local:.                      |
      | local:..                     |
      | local:relative/              |
      | local:./                     |
      | local:../                    |
      | /path/to/name                |
      | /path/to/name/               |
      | /                            |
    When I parse the URI
    Then I see the following parsed components
      | uri                          | chopped_uri                 | scheme | authority | path           | chopped_path  | folder        | name     |
      | local://server/path/to/name  | local://server/path/to/name | local  | server    | /path/to/name  | /path/to/name | /path/to      | name     |
      | local://server/path/to/name/ | local://server/path/to/name | local  | server    | /path/to/name/ | /path/to/name | /path/to/name |          |
      | local:/path/to/name          | local:/path/to/name         | local  |           | /path/to/name  | /path/to/name | /path/to      | name     |
      | local:/path/to/name/         | local:/path/to/name         | local  |           | /path/to/name/ | /path/to/name | /path/to/name |          |
      | local:/path//to/name/        | local:/path/to/name         | local  |           | /path/to/name/ | /path/to/name | /path/to/name |          |
      | local:/name                  | local:/name                 | local  |           | /name          | /name         | /             | name     |
      | local://server               | local://server/             | local  | server    | /              | /             | /             |          |
      | local://server/              | local://server/             | local  | server    | /              | /             | /             |          |
      | local:///                    | local:/                     | local  |           | /              | /             | /             |          |
      | local:/                      | local:/                     | local  |           | /              | /             | /             |          |
      | local:relative/path          | local:relative/path         | local  |           | relative/path  | relative/path | relative      | path     |
      | local:relative/path/         | local:relative/path         | local  |           | relative/path/ | relative/path | relative/path |          |
      | local:./path/                | local:./path                | local  |           | ./path/        | ./path        | ./path        |          |
      | local:../path/               | local:../path               | local  |           | ../path/       | ../path       | ../path       |          |
      | local:relative               | local:relative              | local  |           | relative       | relative      |               | relative |
      | local:.                      | local:.                     | local  |           | .              | .             |               | .        |
      | local:..                     | local:..                    | local  |           | ..             | ..            |               | ..       |
      | local:relative/              | local:relative              | local  |           | relative/      | relative      | relative      |          |
      | local:./                     | local:.                     | local  |           | ./             | .             | .             |          |
      | local:../                    | local:..                    | local  |           | ../            | ..            | ..            |          |
      | /path/to/name                | local:/path/to/name         | local  |           | /path/to/name  | /path/to/name | /path/to      | name     |
      | /path/to/name/               | local:/path/to/name         | local  |           | /path/to/name/ | /path/to/name | /path/to/name |          |
      | /                            | local:/                     | local  |           | /              | /             | /             |          |
 
  Scenario: Switch local URI contexts to Agave
    Given I have a URI
      | uri                          |
      | local://server/path/to/name  |
      | local://server/path/to/name/ |
      | local:/path/to/name          |
      | local:/path/to/name/         |
      | local:/path//to/name/        |
      | local:/name                  |
      | local://server               |
      | local://server/              |
      | local:///                    |
      | local:/                      |
      | /path/to/name                |
      | /path/to/name/               |
      | /                            |
    When I switch the URI context to "agave://storage/newpath"
    Then I see the following switched URIs
      | uri                          | switched_uri                 |
      | local://server/path/to/name  | agave://storage/newpath/name |
      | local://server/path/to/name/ | agave://storage/newpath/     |
      | local:/path/to/name          | agave://storage/newpath/name |
      | local:/path/to/name/         | agave://storage/newpath/     |
      | local:/path//to/name/        | agave://storage/newpath/     |
      | local:/name                  | agave://storage/newpath/name |
      | local://server               | agave://storage/newpath/     |
      | local://server/              | agave://storage/newpath/     |
      | local:///                    | agave://storage/newpath/     |
      | local:/                      | agave://storage/newpath/     |
      | /path/to/name                | agave://storage/newpath/name |
      | /path/to/name/               | agave://storage/newpath/     |
      | /                            | agave://storage/newpath/     |
 
  Scenario: Switch agave URI contexts to local
    Given I have a URI
      | uri                           |
      | agave://storage/path/to/name  |
      | agave://storage/path/to/name/ |
      | agave:/path/to/name           |
      | agave:/path/to/name/          |
      | agave:/path//to/name/         |
      | agave:/name                   |
      | agave://server                |
      | agave://server/               |
      | agave:///                     |
      | agave:/                       |
    When I switch the URI context to "local:///"
    Then I see the following switched URIs
      | uri                           | switched_uri |
      | agave://storage/path/to/name  | local:/name  |
      | agave://storage/path/to/name/ | local:/      |
      | agave:/path/to/name           | local:/name  |
      | agave:/path/to/name/          | local:/      |
      | agave:/path//to/name/         | local:/      |
      | agave:/name                   | local:/name  |
      | agave://server                | local:/      |
      | agave://server/               | local:/      |
      | agave:///                     | local:/      |
      | agave:/                       | local:/      |
 
