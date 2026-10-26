# Types Ideas

| Type               | Description                                   | Example 1                                | Example 2                                | Example 3                                |
| ------------------ | --------------------------------------------- | ---------------------------------------- | ---------------------------------------- | ---------------------------------------- |
| `str`              | String                                        | `"hello"`                                | `"EveryBase"`                            | `"Alice"`                                |
| `int`              | Integer number                                | `0`                                      | `42`                                     | `-7`                                     |
| `float`            | Number with a decimal point                   | `3.14`                                   | `0.5`                                    | `-12.75`                                 |
| `bool`             | `True` or `False`                             | `true`                                   | `false`                                  | `true`                                   |
|                    |                                               |                                          |                                          |                                          |
| `positive`         | Integer from 1 to infinity                    | `1`                                      | `42`                                     | `1000`                                   |
| `positive0`        | Integer from 0 to infinity                    | `0`                                      | `12`                                     | `999`                                    |
| `negative`         | Integer from negative infinity to -1          | `-1`                                     | `-12`                                    | `-999`                                   |
| `negative0`        | Integer from negative infinity to 0           | `0`                                      | `-8`                                     | `-500`                                   |
| `positivle`        | Float from 1 to infinity                      | `1.0`                                    | `2.5`                                    | `100.01`                                 |
| `positivle0`       | Float from 0 to infinity                      | `0.0`                                    | `0.75`                                   | `42.5`                                   |
| `negativle`        | Float from negative infinity to -1            | `-1.0`                                   | `-2.5`                                   | `-100.01`                                |
| `negativle0`       | Float from negative infinity to 0             | `0.0`                                    | `-0.75`                                  | `-42.5`                                  |
| `zero`             | Number equal to 0                             | `0`                                      | `0.0`                                    | `-0`                                     |
| `nonzero`          | Number not equal to 0                         | `1`                                      | `-1`                                     | `0.5`                                    |
| `uint`             | Non-negative integer                          | `0`                                      | `10`                                     | `255`                                    |
| `uint8`            | Integer from 0 to 255                         | `0`                                      | `128`                                    | `255`                                    |
| `int8`             | Integer from -128 to 127                      | `-128`                                   | `0`                                      | `127`                                    |
| `int16`            | Integer from -32,768 to 32,767                | `-32768`                                 | `0`                                      | `32767`                                  |
| `int32`            | Integer from -2,147,483,648 to 2,147,483,647  | `-2147483648`                            | `0`                                      | `2147483647`                             |
| `percent`          | Number from 0 to 100                          | `0`                                      | `50`                                     | `100`                                    |
| `percent0`         | Number from 0 to 1                            | `0`                                      | `0.5`                                    | `1`                                      |
| `ratio`            | Number from 0 to 1                            | `0`                                      | `0.25`                                   | `1`                                      |
|                    |                                               |                                          |                                          |                                          |
| `char`             | One character                                 | `"A"`                                    | `"?"`                                    | `"é"`                                    |
| `text`             | Long-form text                                | `"Hello world."`                         | `"A longer note."`                       | `"Description"`                          |
| `word`             | One word                                      | `"hello"`                                | `"EveryBase"`                            | `"admin"`                                |
| `username`         | User name containing only allowed characters  | `"alice"`                                | `"user_42"`                              | `"dev-user"`                             |
| `password`         | Secret text value                             | `"p@ssword1"`                            | `"correct-horse"`                        | `"A7!secure"`                            |
| `str_alpha`        | String containing only letters                | `"abc"`                                  | `"EveryBase"`                            | `"Bonjour"`                              |
| `str_alphanumeric` | String containing only letters and numbers    | `"abc123"`                               | `"User42"`                               | `"A1B2"`                                 |
| `str_numeric`      | String containing only numbers                | `"123"`                                  | `"007"`                                  | `"2026"`                                 |
| `str_lower`        | Lowercase string                              | `"hello"`                                | `"everybase"`                            | `"user42"`                               |
| `str_upper`        | Uppercase string                              | `"HELLO"`                                | `"EVERYBASE"`                            | `"USER42"`                               |
| `str_trimmed`      | String without leading or trailing whitespace | `"hello"`                                | `"EveryBase"`                            | `"user name"`                            |
| `str_slug`         | URL-friendly string                           | `"hello-world"`                          | `"everybase-v1"`                         | `"types-ideas"`                          |
|                    |                                               |                                          |                                          |                                          |
| `date`             | Calendar date                                 | `"2026-10-26"`                           | `"2000-01-01"`                           | `"2030-12-31"`                           |
| `time`             | Time of day                                   | `"07:30:00"`                             | `"12:00:00"`                             | `"23:59:59"`                             |
| `datetime`         | Date and time                                 | `"2026-10-26T07:30:00"`                  | `"2000-01-01T00:00:00"`                  | `"2030-12-31T23:59:59"`                  |
| `timestamp`        | Numeric date and time value                   | `0`                                      | `1761463800`                             | `1893455999`                             |
| `duration`         | Amount of time                                | `"30s"`                                  | `"15m"`                                  | `"2h"`                                   |
| `timezone`         | Time zone identifier                          | `"UTC"`                                  | `"Europe/London"`                        | `"America/New_York"`                     |
|                    |                                               |                                          |                                          |                                          |
| `email`            | Valid email address                           | `"alice@example.com"`                    | `"admin@everybase.dev"`                  | `"user42@mail.org"`                      |
| `url`              | Valid web address                             | `"https://example.com"`                  | `"https://everybase.dev"`                | `"http://localhost:8000"`                |
| `uuid`             | Universally unique identifier                 | `"550e8400-e29b-41d4-a716-446655440000"` | `"123e4567-e89b-12d3-a456-426614174000"` | `"6ba7b810-9dad-11d1-80b4-00c04fd430c8"` |
| `phone`            | Telephone number                              | `"+44 20 1234 5678"`                     | `"+1 555 123 4567"`                      | `"020 7946 0958"`                        |
| `ipv4`             | IPv4 address                                  | `"127.0.0.1"`                            | `"192.168.1.1"`                          | `"8.8.8.8"`                              |
| `ipv6`             | IPv6 address                                  | `"::1"`                                  | `"2001:db8::1"`                          | `"fe80::1"`                              |
| `mac`              | MAC address                                   | `"00:1A:2B:3C:4D:5E"`                    | `"AA-BB-CC-DD-EE-FF"`                    | `"12:34:56:78:9A:BC"`                    |
| `hex`              | Hexadecimal value                             | `"0xFF"`                                 | `"#00FF00"`                              | `"deadbeef"`                             |
| `color`            | Color value                                   | `"#FF0000"`                              | `"rgb(0, 128, 255)"`                     | `"blue"`                                 |
| `currency`         | Monetary value                                | `"£19.99"`                               | `"$100.00"`                              | `"€5.50"`                                |
|                    |                                               |                                          |                                          |                                          |
| `list`             | List of values                                | `[1, 2, 3]`                              | `["red", "green"]`                       | `[]`                                     |
| `set`              | Collection of unique values                   | `{1, 2, 3}`                              | `{"admin", "user"}`                      | `{"a", "b"}`                             |
| `tuple`            | Fixed-length collection of values             | `(1, 2)`                                 | `("Alice", 30)`                          | `( true, false )`                        |
| `dict`             | Key-value collection                          | `{"name": "Alice"}`                      | `{"id": 42}`                             | `{"active": true}`                       |
| `json`             | Valid JSON value                              | `{"key": "value"}`                       | `[1, 2, 3]`                              | `"hello"`                                |
| `enum`             | One value from a defined list                 | `"small"`                                | `"medium"`                               | `"large"`                                |
|                    |                                               |                                          |                                          |                                          |
| `latitude`         | Geographic latitude                           | `0.0`                                    | `51.5074`                                | `-33.8688`                               |
| `longitude`        | Geographic longitude                          | `0.0`                                    | `-0.1278`                                | `151.2093`                               |
| `locale`           | Language and region identifier                | `"en-GB"`                                | `"en-US"`                                | `"de-DE"`                                |
| `country`          | Country code                                  | `"GB"`                                   | `"US"`                                   | `"DE"`                                   |
| `language`         | Language code                                 | `"en"`                                   | `"de"`                                   | `"fr"`                                   |
|                    |                                               |                                          |                                          |                                          |
| `path`             | File or directory path                        | `"/home/user/file.txt"`                  | `"./configs"`                            | `"C:\\Users\\Alice"`                     |
| `file`             | File reference                                | `"notes.txt"`                            | `"data.json"`                            | `"image.png"`                            |
| `directory`        | Directory reference                           | `"/tmp"`                                 | `"./configs"`                            | `"C:\\Projects"`                         |
|                    |                                               |                                          |                                          |                                          |
| `nullable`         | Value that may also be `null`                 | `null`                                   | `"value"`                                | `42`                                     |
| `optional`         | Value that may be omitted                     | `{}`                                     | `{"name": "Alice"}`                      | `{"enabled": true}`                      |
| `constant`         | Value that cannot be changed                  | `"VERSION_1"`                            | `42`                                     | `true`                                   |
