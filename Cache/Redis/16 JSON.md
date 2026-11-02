# Redis JSON

Redis JSON stores JSON documents as a native Redis data type. Unlike a [JSON string](05%20Hashes.md#Hashes%2C%20Redis%20JSON%2C%20one%20JSON%20string%2C%20or%20separate%20string%20keys), which Redis treats as opaque bytes, a JSON value exposes its nested structure to server-side commands. Applications read or modify selected elements without retrieving and replacing the entire document. [Redis JSON](https://redis.io/docs/latest/develop/data-types/json/)

## Document representation and operations

Redis JSON preserves the document's structure and value types rather than flattening everything into string-valued fields:

- **JSON-standard support:** Documents support objects, arrays, strings, numbers, booleans, and `null`, including nested combinations.
- **Binary tree storage:** Parsed documents are stored in a binary tree structure, enabling fast access to sub-elements rather than treating the document as serialized text.
- **Typed operations:** Commands provide atomic operations for all JSON value types; the operation must match the selected value's type, such as incrementing a number or appending to an array.

These properties make nested document updates different from both whole-string replacement and flat hash-field updates. They do not imply that every path query has the same cost or that JSON is universally faster or smaller than another representation. [Redis JSON features](https://redis.io/docs/latest/develop/data-types/json/)

## Selecting elements with JSONPath

A **path** identifies elements inside a document. Redis JSON supports JSONPath syntax: `$` denotes the document root, `.name` selects an object member, and `[0]` selects the first array element. Paths also support expressions such as wildcards that match multiple elements. The selected path determines which part of the document a command reads or changes. [JSONPath syntax](https://redis.io/docs/latest/develop/data-types/json/path/)

The following commands assume a Redis deployment with JSON support and a fresh `product:5001` key. They use Redis CLI's RESP2-style replies and illustrate command behavior rather than a recorded server session.

`JSON.SET` at `$` creates the document. JSON numbers, booleans, and nested arrays retain their types:

```sh
redis> JSON.SET product:5001 $ '{"name":"Laptop","price":1200,"available":true,"tags":["portable","work"]}'
OK
```

`JSON.GET` selects only the first tag. With a JSONPath beginning with `$`, the RESP2 bulk-string reply encodes an array of matches, even when the path matches only one value; the JSON payload here is `["portable"]`:

```sh
redis> JSON.GET product:5001 $.tags[0]
"[\"portable\"]"
```

`JSON.OBJKEYS` reads member names from an object, not keys from the Redis keyspace or the members' values. The root `$` matches one object, so the reply contains one nested list of its member names (the order shown is illustrative):

```sh
redis> JSON.OBJKEYS product:5001 $
1) 1) "name"
   2) "price"
   3) "available"
   4) "tags"
```

With a path matching several values, the reply has one result per match; a matched non-object produces `nil`. [JSON.OBJKEYS](https://redis.io/docs/latest/commands/json.objkeys/)

`JSON.SET` also replaces a selected sub-element. This changes `available` without replacing the product's other properties:

```sh
redis> JSON.SET product:5001 $.available false
OK
```

The root and nested-path forms use the same command, but operate at different document scopes. [JSON.SET](https://redis.io/docs/latest/commands/json.set/), [JSON.GET](https://redis.io/docs/latest/commands/json.get/)

`JSON.ARRAPPEND` adds one or more JSON values after the last element of each array selected by the path. Here it appends the JSON string `"sale"` to `tags`; the single-quoted shell argument preserves the double quotes required by JSON. The `$`-path reply reports the new length for each matched array:

```sh
redis> JSON.ARRAPPEND product:5001 $.tags '"sale"'
1) (integer) 3
```

A matched value that is not an array yields `nil` in its reply position. [JSON.ARRAPPEND](https://redis.io/docs/latest/commands/json.arrappend/)

## Atomic typed updates

`JSON.NUMINCRBY` increments a numeric value directly on the server. For the product above, subtracting `100` changes `price` from `1200` to `1100`. With a `$` path, RESP2 returns a bulk string containing a JSON array of updated values, as shown below; RESP3 instead returns an array reply:

```sh
redis> JSON.NUMINCRBY product:5001 $.price -100
"[1100]"
```

The numeric read–modify–write happens within one atomic command, so the application does not need to fetch the price and send back a computed replacement. Concurrent increments do not overwrite each other through that client-side read–modify–write pattern. [JSON.NUMINCRBY](https://redis.io/docs/latest/commands/json.numincrby/)

Atomicity applies to each command, not automatically to a sequence. For example, reading `available` and then conditionally decrementing `price` in separate commands does not make the condition and update one atomic operation. Likewise, the separate writes in the example above do not form a transaction. [Redis JSON atomic operations](https://redis.io/docs/latest/develop/data-types/json/)
