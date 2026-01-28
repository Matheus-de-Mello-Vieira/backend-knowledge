

# RESP (Redis Serialization Protocol)

* Redis clients communicate with Redis server using a protocol called **RESP** (**RE**dis **S**erialization **P**rotocol).
* Simple to implement: https://redis.io/docs/latest/develop/reference/protocol-spec/
* Fast to parse
* Human readable
* RESP can serialize different data type like intergers, strings and arrays.
* RESP is binnary safe.

## RESP basics

The type is indicated by the first bytes. Some of them are:

| Prefix | Meaning       |
| ------ | ------------- |
| `*`    | Array         |
| `$`    | Bulk string   |
| `+`    | Simple string |
| `-`    | Error         |
| `:`    | Integer       |

Each element is terminated with `\r\n`.

A Redis command is encoded as an **array of bulk strings**, where each argument includes its explicit byte length.

## Example: RESP encoding of a `SET` command

Command:

```
SET country:LB Lebanon
```

RESP representation:

```
*3
$3
SET
$10
country:LB
$7
Lebanon
```

Where:

- `*3`
  - `*` indicates an **array** in RESP
  - `3` specifies that the array contains **three elements**

- `$3`
  - `$` indicates a **bulk string**
  - `3` specifies the string length is **3 bytes**
  - `SET`
    - The bulk string content
    - Represents the **Redis command**

- `$10`
  - `$` indicates a **bulk string**
  - `10` specifies the string length is **10 bytes**
  - `country:LB`
    - The bulk string content
    - Represents the **key**

- `$7`
  - `$` indicates a **bulk string**
  - `7` specifies the string length is **7 bytes**
  - `Lebanon`
    - The bulk string content
    - Represents the **value**

Wire format:

```
*3\r\n$3\r\nSET\r\n$10\r\ncountry:LB\r\n$7\r\nLebanon\r\n
```