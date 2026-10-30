# RESP (Redis Serialization Protocol)

Redis clients and servers communicate using **RESP** (**RE**dis **S**erialization **P**rotocol). Its format is simple to implement, fast to parse, human-readable, and binary-safe. RESP serializes values such as integers, strings, and arrays. The [RESP specification](https://redis.io/docs/latest/develop/reference/protocol-spec/) describes the complete protocol.

## Type prefixes and lengths

The first byte identifies a value's type. Common prefixes include:

| Prefix | Type |
| --- | --- |
| `*` | Array |
| `$` | Bulk string |
| `+` | Simple string |
| `-` | Error |
| `:` | Integer |

RESP terminates each element with `\r\n`. A Redis command is encoded as an array of bulk strings, with an explicit byte length for each argument.

## Encoding a `SET` command

The command `SET country:LB Lebanon` has three arguments: the command name, key, and value. Its readable RESP representation is:

```text
*3
$3
SET
$10
country:LB
$7
Lebanon
```

`*3` denotes an array of three elements. Each `$` prefix introduces a bulk string followed by its length in bytes: `SET` is 3 bytes, `country:LB` is 10 bytes, and `Lebanon` is 7 bytes. Those bulk strings represent the command name, key, and value, respectively.

On the wire, the line endings are `\r\n`:

```text
*3\r\n$3\r\nSET\r\n$10\r\ncountry:LB\r\n$7\r\nLebanon\r\n
```
