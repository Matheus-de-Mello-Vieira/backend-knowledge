# GraphQL Mutations

Most uses GraphQL are around queries, but it also can be used to change data. This is called mutation.

```apl
mutation ($book: BookInput!) {
  addBook (input: $book) {
    bookId
  }
}
```

There are three main parts in the mutation request:

1.  Mutation Object Type: `mutation`
    *   Defines that we're running a mutation and not a query
2.  Mutation Parameters: `$book: BookInput!`
    *   The objects that we want to create / modify. 
    *   Can be more than one
3.  Returned Data: `bookId`
    *   Reflects the new object that was added

On the schema:

```apl
input BookInput {
  name: String!
  pages: Int!
  price: Float!
  publishData: DateTime
  genre: BookGenre
}

...

type Mutation {
  addBook(input: BookInput): Book!
}
```

So, on cl:

```apl
mutation ($book: BookInput) {
	addBook(input: $book) {
    bookId
    name
    pages
  }
}
```

With the variables:

```json
{
  "book": {
    "name": "Rich dad Poor dad",
    "pages": 10,
    "genre": "NON_FICTION",
    "price": 1.4
  }
}
```

We get:

```json
{
  "data": {
    "addBook": {
      "bookId": "4859",
      "name": "Rich dad Poor dad",
      "pages": 10
    }
  }
}
```

