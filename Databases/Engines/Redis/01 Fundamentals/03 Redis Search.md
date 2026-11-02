# Redis Search

Redis Search adds **secondary indexes** over [Hashes](../02%20Data%20Types/Hashes.md) and [JSON documents](../02%20Data%20Types/JSON.md). Instead of retrieving a value only by its exact Redis key, applications query indexed fields to find matching documents.

A **document** is a hash or JSON value identified by its Redis key, such as `product:123`. Documents contain multiple fields and do not need identical field sets. The source value remains in Redis; the search index is an additional structure built from selected fields, not a replacement for that value.

## Index Selection and Schema

An index definition establishes which documents participate and how their fields are interpreted:

- **Document type:** `ON HASH` or `ON JSON` selects the source representation.
- **Key selection:** `PREFIX` selects key-name prefixes; an optional `FILTER` further restricts eligible documents by their values.
- **Schema:** Declares the fields to index, their search types, and field-specific options. A field stored in the source document is not automatically searchable merely because the document participates in an index.

Redis indexes existing eligible documents in the background when the index is created; those documents are not necessarily searchable immediately. Subsequent document writes update the index synchronously, so their indexed changes are available when the write command completes. Creating an index does not require copying documents into a separate application-managed collection. Index construction and maintenance nevertheless consume memory and processing work. The [indexing tutorial](https://redis.io/docs/latest/develop/get-started/search-tutorial/indexing/) illustrates this relationship between source documents and their index.

## Field Types

The schema assigns search semantics to field values. A string containing a price, for example, needs a `NUMERIC` declaration for numeric range queries rather than word matching.

- **`TEXT`:** Full-text search over tokenized text. Language-aware processing includes normalization and stemming, which relates word forms such as singulars and plurals. Text fields support relevance ranking rather than only exact-value lookup.
- **`TAG`:** Category or label matching, such as colors, product types, or flags. Tags are not tokenized and stemmed as full text; configured separators or JSON arrays determine individual tags. “Exact value” does not imply case sensitivity: tag matching is case-insensitive by default.
- **`NUMERIC`:** Numeric values, including integers and floating-point values, for range filtering and ordering.
- **`GEO`:** Longitude/latitude coordinates for geographic distance and radius queries.
- **`VECTOR`:** Numeric vectors, such as embeddings, for similarity search using a declared vector algorithm, dimensionality, and distance metric.

These are common types rather than an exhaustive list. Supported types and options are documented under [field and type options](https://redis.io/docs/latest/develop/ai/search-and-query/indexing/field-and-type-options/).

## Creating a Hash Index

The following definition creates an index named `ecommerce-products` over hashes whose keys start with `product:`. Only the three declared fields acquire search semantics; other fields remain part of their source hashes.

```redis
FT.CREATE ecommerce-products
  ON HASH
  PREFIX 1 product:
  SCHEMA
    name TEXT
    price NUMERIC
    color TAG
```

- **`PREFIX 1 product:`:** Declares one key prefix, not one document.
- **`name TEXT`:** Indexes words in the product name.
- **`price NUMERIC`:** Enables numeric price filters.
- **`color TAG`:** Indexes colors as category values rather than words in prose.

`FT.SEARCH` queries the index, while `FT.AGGREGATE` processes matching documents through aggregation operations. Neither command turns undeclared source fields into indexed search criteria. The full definition syntax is specified by [`FT.CREATE`](https://redis.io/docs/latest/commands/ft.create/).

## Automatic Index Maintenance

Applications write source documents with ordinary Redis commands; Search maintains the corresponding index without a separate indexing command. The following lifecycle uses the hash index above. The JSON commands are alternatives for a separate JSON-based scenario, not commands to run against the same hash key: they require an `ON JSON` index with the `product:` prefix and a schema such as `$.name AS name TEXT $.price AS price NUMERIC`. An `ON HASH` index does not index JSON documents.

### Create the Document

Its type and prefix match the index definition, so Redis indexes the declared fields synchronously as part of the write. The document has a name and price even though the hash schema also declares an absent `color` field.

```redis
HSET product:1 name "Audio B" price 1250
```

Alternatively, in the JSON scenario:

```redis
JSON.SET product:1 $ '{"name":"Audio B","price":1250}'
```

### Modify an Indexed Field

Updating the price also updates its indexed numeric value from `1250` to `1700`; applications do not rebuild the index themselves.

```redis
HSET product:1 price 1700
```

Alternatively, in the JSON scenario:

```redis
JSON.SET product:1 $.price 1700
```

### Delete the Document

Deleting the source key also removes the document from search results, for either representation.

```redis
DEL product:1
```

Deletion from search results is distinct from immediate memory reclamation: obsolete index entries are reclaimed by background garbage collection.

## Query Capabilities

Query behavior depends on the indexed field types, their options, and the query itself:

- **Full-text matching:** Word and phrase queries, fuzzy matching, and relevance-ranked results. TF-IDF is an example of a scoring method, not a universal description of every Search ranking mode.
- **Boolean composition:** AND, OR, and NOT combine or exclude matching conditions.
- **Structured filtering:** Numeric ranges, tag categories, and geographic constraints restrict results using their respective field types.
- **Vector similarity:** Vector queries retrieve neighbors according to the configured distance metric; they also support combinations with structured filters.
- **Aggregation and ordering:** Grouping, computed values, reductions, and sorting support analysis beyond returning individual matching documents.

> [!note] Autocomplete and spell checking
> Search also provides suggestion dictionaries for autocomplete, including fuzzy prefix matching, and spelling suggestions with dictionary support. Defining a document index does not automatically populate an autocomplete dictionary or make every query perform spell checking; applications invoke and configure these capabilities separately.

### Query Syntax and Examples

`FT.SEARCH index query` evaluates a query against the named index. The following commands illustrate query shapes, not guaranteed matches or result output. They use the `ecommerce-products` schema above unless stated otherwise; a document must contain matching indexed values to appear in the results.

#### Field Filters and Unfielded Terms

A field modifier, `@field:expression`, restricts an expression to a declared field. The expression's syntax follows the field's search type:

| Query | Meaning |
| --- | --- |
| `FT.SEARCH ecommerce-products "@name:TV"` | Matches the term `TV` in the `name` TEXT field. |
| `FT.SEARCH ecommerce-products "@price:[500 1000]"` | Matches NUMERIC prices from `500` through `1000`, inclusive. |
| `FT.SEARCH ecommerce-products "@color:{black}"` | Matches the `black` category in the `color` TAG field. |
| `FT.SEARCH ecommerce-products "TV"` | Matches `TV` across indexed TEXT fields; here, only `name` is declared as TEXT. |

Unfielded text does not search every stored property: NUMERIC and TAG fields retain their distinct query semantics.

> [!example] Geographic radius
> A separate `cities` index must declare `coords GEO`; the product index above has no geographic field. For example, hashes with a `city:` prefix could use this definition:
>
> ```redis
> FT.CREATE cities ON HASH PREFIX 1 city: SCHEMA coords GEO
> ```
>
> The radius query then selects indexed coordinates within `1000 km` of longitude `2.34`, latitude `48.86`:
>
> ```redis
> FT.SEARCH cities "@coords:[2.34 48.86 1000 km]"
> ```
>
> The order is longitude, latitude, radius, unit. Supported units are `m`, `km`, `mi`, and `ft`; creating the index alone does not populate it with city documents.

#### Boolean Expressions

Boolean operators combine matching sets rather than changing a field's search type:

- **AND:** Adjacent expressions require both conditions. The first query requires a black product with a price from `100` through `500`; the second requires both text terms anywhere in the indexed TEXT fields, not necessarily together or in order.

  ```redis
  FT.SEARCH ecommerce-products "@color:{black} @price:[100 500]"
  FT.SEARCH ecommerce-products "TV 4K"
  ```

- **OR:** A pipe (`|`) accepts either condition. It also separates alternatives inside a TAG expression. These queries respectively accept either the color or price condition, either color, and either text term.

  ```redis
  FT.SEARCH ecommerce-products "(@color:{black}) | (@price:[100 500])"
  FT.SEARCH ecommerce-products "@color:{black|white}"
  FT.SEARCH ecommerce-products "TV | Smart"
  ```

- **NOT:** A minus sign excludes the following expression's matches. The first query excludes the black tag; the second requires `TV` while excluding `smart`.

  ```redis
  FT.SEARCH ecommerce-products "-@color:{black}"
  FT.SEARCH ecommerce-products "TV -smart"
  ```

Use parentheses to make complex combinations explicit. Query dialects differ in precedence and field-modifier scope: for example, `@name:TV 4K` scopes both terms to `name` in dialect 1, but only `TV` in dialect 2 or later. `@name:(TV 4K)` explicitly scopes both terms to `name`. The [query syntax reference](https://redis.io/docs/latest/develop/ai/search-and-query/advanced-concepts/query_syntax/) describes these parser differences.

#### Phrase Matching and Command Quoting

The outer quotes keep the query together as one command argument; they do not themselves request a phrase match. Double quotes **inside the query value** require the phrase's words together and in order. With a double-quoted outer argument, escape those inner quotes:

```redis
FT.SEARCH ecommerce-products "\"Bright star\""
```

Alternatively, single quotes around the command argument preserve the inner double quotes:

```redis
FT.SEARCH ecommerce-products '"Bright star"'
```

This is phrase matching within indexed TEXT, not whole-field TAG equality or byte-for-byte comparison of the source string. Redis's [exact-match documentation](https://redis.io/docs/latest/develop/ai/search-and-query/query/exact-match/) also specifies that a phrase cannot start with a stop word; phrase construction must respect the index's stop-word configuration.

## Schema Options

Field options refine how indexed values participate in queries and results:

- **`SORTABLE`:** Retains additional information for efficient sorting, at a memory cost. It is an optimization for ordering, not a prerequisite for indexing a numeric range.
- **`NOSTEM`:** Disables stemming for a `TEXT` field. It does not disable tokenization or turn the field into a `TAG` field.
- **`WEIGHT`:** Sets a text field's relative contribution to relevance scoring for scorers that use field weights. For example, a product name can receive more weight than its description.
- **`PHONETIC`:** Enables phonetic text matching with an explicit algorithm/language matcher, such as `PHONETIC dm:en` for English Double Metaphone.
- **`AS`:** Gives an indexed attribute a query-facing alias. For JSON, `$.embedding AS embedding` maps a JSON path to the name used in queries without renaming the source property.

> [!example] Vector field declaration
> Within an `ON JSON` schema, the following declaration indexes a JSON embedding array:
>
> ```redis
> $.embedding AS embedding VECTOR HNSW 6 TYPE FLOAT32 DIM 384 DISTANCE_METRIC L2
> ```
>
> `HNSW` selects an approximate nearest-neighbor index. The `6` counts the six following option tokens: three name/value pairs. `TYPE FLOAT32` selects the vector element representation, `DIM 384` requires 384 components, and `DISTANCE_METRIC L2` selects Euclidean distance. These choices must match the stored embeddings and intended similarity comparison; they are not universal defaults.
