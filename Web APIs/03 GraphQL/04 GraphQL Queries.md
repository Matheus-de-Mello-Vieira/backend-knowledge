# GraphQL Queries

```apl
query {
  books {
    name
    genre
    author {
      name
    }
    reviews {
      rating
      description
    }
  }
  magazines {
    name
  }
}
```

## Operation Type and Name

### Operation Type

You can omit the `query` keyword, for example, the following two codes are the produces the same resutls:

*   ```apl
    {
      books {
        name
      }
    }
    ```

*   ```apl
    query {
      books {
        name
      }
    }
    ```

However, it is a good practice to specify the **Operation Type** when calling GraphQL, so that it'll be clear what we're trying to do.

### Operation Name

When calling GraphQL multiple queries, it's a good practice to name the query.

*   This helps when debugging and logging the query on the server side
*   Simple to implement: just add the name after the query keyword.

```apl
query GetBookNames {
  books {
    name
  }
}
```

## Arguments

Use arguments to filter the query

### Arguments Declaration

Is there two ways to declare the arguments

#### Option 1: Arguments directly on the field

```apl
type Query {
  books(id: ID, nameContains: String): [Book!]!
}
```

##### Pros

-   **Simpler and shorter** for a few filters.

-   Ideal for small APIs or queries with 1–3 arguments.

-   Easy for clients to call:

    ```apl
    query {
      books(nameContains: "Go") { name }
    }
    ```

##### Cons

-   If filters grow, this field can become **bloated** (`books(id, name, priceGT, priceLT, publishedBefore, …)`).
-   You can’t reuse the same argument group elsewhere (e.g., on `magazines`).

#### Option 2: Single `filter` input object

```apl
input BookFilter {
  id: ID
  nameContains: String
}

type Query {
  books(filter: BookFilter): [Book!]!
}
```

##### Pros

-   **Scalable and organized** for many optional filters.

-   **Reusable** — you can use `BookFilter` for other queries (e.g. `searchBooks`, `countBooks`, etc.).

-   Plays nicely with **typed variables** on the client side:

    ```apl
    query GetBooks($filter: BookFilter) {
      books(filter: $filter) { name }
    }
    ```

    with variables:

    ```apl
    { "filter": { "nameContains": "Go" } }
    ```

##### Cons

-   Slightly more verbose for simple cases.
-   Requires clients to wrap filters inside `filter:`.

### Arguments Names

GraphQL doesn’t enforce naming rules, but there are conventions that make your API feel natural and predictable.

| Pattern                           | Meaning                                          | Example                                         |
| --------------------------------- | ------------------------------------------------ | ----------------------------------------------- |
| `id`                              | Exact match by unique identifier                 | `book(id: "123")`                               |
| `name`                            | Exact match by full string                       | `books(name: "Go in Action")`                   |
| `nameContains`                    | Partial / substring match                        | `books(nameContains: "Go")`                     |
| `nameStartsWith` / `nameEndsWith` | Prefix or suffix match                           | `books(nameStartsWith: "Go")`                   |
| `nameIn`                          | One of several values                            | `books(nameIn: ["Go in Action", "The Go Way"])` |
| `search`                          | Generic text search (applies to multiple fields) | `books(search: "Go")`                           |

## Variables

Usually, we want to define the value of the argument separately from the query string. For that we can use Variables.

```apl
query GetBooks ($bookNameContains: String) {
  books(nameContains: $bookNameContains) {
    name
  }
}
```

In most GraphQL playgrounds, there is a place for `Variables`:

```apl
{
  "bookNameContains":"H"
}
```

You can place a `!` to make the variable non-nullable:

```apl
query GetBooks ($bookNameContains: String!) { ...
```



## Aliases

When you query the same object type multiple times in the same query call, it causes a conflict in the result, as the result is named after the object type queries.

```apl
query GetBookNames {
  books (nameContains: "H") {
    name
  }
  books (nameContains: "M") {
    name
  }
}
```

```
Fields \"books\" conflict because they have differing arguments. Use different aliases on the fields to fetch both if this was intentional.
```

With alias, we give a unique name to each query in the request

*   The result is named after the alias, and not after the object type.
*   This way we avoid conflits

```apl
query GetBookNames {
  booksWithH: books (nameContains: "H") {
    bookId
    name
    genre
  }
  booksWithM: books (nameContains: "M") {
    bookId
    name
    genre
  }
}
```

```json
{
  "data": {
    "booksWithH": [
      {
        "bookId": "",
        "name": "Harry Potter",
        "genre": "FANTASY"
      }
    ],
    "booksWithM": [
      {
        "bookId": "",
        "name": "Memory Man",
        "genre": ""
      }
    ]
  }
}
```

## Fragments

Look at:

```apl
query GetBookNames {
  booksWithH: books (nameContains: "Harry") {
    bookId
    name
    genre
  }
  booksWithM: books (nameContains: "Memory") {
    bookId
    name
    genre
  }
}
```

We queried for the same field, and it is repetitive. Fix it using fragments:

```apl
query GetBookNames {
  booksWithH: books (nameContains: "H") {
    ...bookFields
  }
  booksWithM: books (nameContains: "M") {
    ...bookFields
  }
}

fragment bookFields on Book {
  bookId
  name
  genre
}
```

You can query for more elements than the fragment:

```apl
booksWithH: books (nameContains: "H") {
  ...bookFields
  author {
    name
  }
}
```

## Directives

Make the query to return different set of fields based on the specific scenario.

*   For example, a list of entities we would need less fields than a detailed view of the entity.

It can be achieved using Directaves

*   With directives, we can dynamically change the structure and shape of the query based on variables passes to the query.
*   Each directive checks whether a given argument is `true` and then executes its instructions.
*   Currently two directives are part of GraphQL specification:
    *   `@include (if: Boolean)` Include the `field` if argument is `true`
    *   `@skip (if: Boolean)` Skip the field if argument is `true`

```apl
query GetBookNames($withAuthor: Boolean!) {
  books(nameContains: "H") {
    bookId
    name
    author @include(if: $withAuthor) {
      name
    }
  }
}
```

When `withAuthor` is:

*   `false`

    ```json
    {"data":{"books":[{
        "bookId":"",
        "name":"Harry Potter"
    }]}}
    ```

*   `true`

    ```json
    {"data":{"books":[{
        "bookId":"",
        "name":"Harry Potter",
        "author": {
            "name": "J.K. Rowling"
        }
    }]}}
    ```

### Directives on fragments

```apl
query GetBookNames($noGenre: Boolean!) {
  booksWithH: books (nameContains: "H") {
    ...bookFields
  }
  booksWithM: books (nameContains: "M") {
    ...bookFields
  }
}

fragment bookFields on Book {
  bookId
  name
  genre @skip(if: $noGenre)
}
```

## Inline fragments

Sometimes we might want to retrieve specific type fields even when querying interfaces

*   For that we can use Inline Fragments

With Inline fragments we define which fields should be retrieved in addition to the fields included in the interface

*   Use `...` type syntax, similar to regular fragments

Given

```apl
interface IReadingMaterials {
  name: String!
  genre: BookGenre!
}

type Book implements IReadingMaterials {
  bookId: Int!
  name: String!
  pages: Int!
  price: Float!
  publishDate: DateTime
  genre: BookGenre!
  author: Author
}

type Magazine implements IReadingMaterials {
  magId: ID!
  name: String!
  genre: BookGenre!
  issueNo: Int!
}
```

```apl
query {
  IReadingMaterials {
    name
    ...on Book {
      pages
    }
    ...on Magazine {
      issueNo
    }
  }
}
```

## Introspection

Introspection allows us to explore the schema and learn about its objects and fields.

*   Used as query, with GraphQL keywords.

```apl
query {
  __schema {
    types {
      name
      kind
    }
  }
}
```

```json
{
  "data": {
    "__schema": {
      "types": [
        { "name": "Author", "kind": "OBJECT" },
        { "name": "Book", "kind": "OBJECT" },
        { "name": "BookGenre", "kind": "ENUM" },
        { "name": "BookReview", "kind": "OBJECT" },
        { "name": "Boolean", "kind": "SCALAR" },
        { "name": "DateTime", "kind": "SCALAR" },
        { "name": "Float", "kind": "SCALAR" },
        { "name": "ID", "kind": "SCALAR" },
        { "name": "IReadingMaterials", "kind": "INTERFACE" },
        { "name": "Int", "kind": "SCALAR" },
        { "name": "Magazine", "kind": "OBJECT" },
        { "name": "Query", "kind": "OBJECT" },
        { "name": "String", "kind": "SCALAR" },
        { "name": "Things", "kind": "UNION" },
        { "name": "__Directive", "kind": "OBJECT" },
        { "name": "__DirectiveLocation", "kind": "ENUM" },
        { "name": "__EnumValue", "kind": "OBJECT" },
        { "name": "__Field", "kind": "OBJECT" },
        { "name": "__InputValue", "kind": "OBJECT" },
        { "name": "__Schema", "kind": "OBJECT" },
        { "name": "__Type", "kind": "OBJECT" },
        { "name": "__TypeKind", "kind": "ENUM" }
      ]
    }
  }
}

```

Other example:

```apl
query {
  __schema {
    types {
      name
      kind
      description
      fields {
        name
        type {
          name
          kind
          ofType {
            name
          }
        }
      }
    }
  }
}
```

you can search:

```apl
query {
  __type(name: "Book") {
    name
    description
  }
}
```

### Meta fields

When retrieving multiple object type in a single result, could be useful if the query explicitly tell us what is the object type of each item in the results

Meta fields provide data about the type returned, and are part of the Introspection mechanism.

*   The most useful meta field is `__typename`, which indicates the name of the object type returned

```apl
query {
  IReadingMaterials {
    name
    __typename
    ...on Book {
      pages
    }
    ...on Magazine {
      issueNo
    }
  }
}
```

```json
{
  "data": {
    "IReadingMaterials": [
      {
        "name": "Harry Potter",
        "__typename": "Book",
        "pages": 267
      },
      {
        "name": "Memory Man",
        "__typename": "Book",
        "pages": 560
      },
      {
        "name": "Exhalation",
        "__typename": "Book",
        "pages": 368
      },
      {
        "name": "Car and Driver",
        "__typename": "Magazine",
        "issueNo": 18
      }
    ]
  }
}
```

