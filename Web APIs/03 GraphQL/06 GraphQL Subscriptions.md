# Subscriptions

*   Allow subscribing to events in the GraphQL Server
*   When an event is triggered the subscription gets a notification
*   Usually used in conjunction with Mutations
*   Rarely used

```apl
subscription {
  bookAdded {
    bookId
    name
  }
}
```

There are three main parts:

*   subscription object type: `subscription`
    *   Defines that we're running a subscription
*   subscription name: `bookAdded`
    *   The name of the subscription we want to subscribe to
*   returned data: `bookId` `name`
    *   Reflect the new object that was added

obs.: You should check if the servers allows websocket connections.

On the schema

```apl
type Subscription {
  """Triggered whenever a new book is added."""
  bookAdded: Book!
}
```

in one client:

```apl
subscription {
  bookAdded {
    bookId
    name
  }
}
```

*   It will create a web socket connection

in another client:

```apl
mutation ($book: BookInput!) {
	addBook(input: $book) {
    bookId
    name
    pages
  }
}
```

The server will send to the first client:

```json
{
  "data": {
    "bookAdded": {
      "bookId": "9778",
      "name": "Rich dad Poor dad"
    }
  }
}
```

