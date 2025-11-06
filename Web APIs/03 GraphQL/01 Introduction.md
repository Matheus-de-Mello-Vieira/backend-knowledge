# GraphQL

GraphQL is a specification built around HTTP where you receive info from a server.

## Problems with REST

During the years it was found that there are some major problems with REST

*   **Fixed Entity Structure**
    *   With REST, the client cannot specify the entity parts it want to retrieve
        *   in other words, there's not way to retrieve only the fields we need
        *   It increases load time and network latency
        *   Sometimes forces to create specialized entity types just for specific queries.
            *   Bad for maintenance and data model.
    *   The entity returned is set by the backend developer and cannot be modifies on a per-query basis.
*   **Request-Response Only**
    *   Modern web apps require more types of client-server communication
        *   For example, push notifications have become increasingly useful. They can be implemented using techniques like polling or WebSockets, neither is RESTful.

## History of GraphQL

*   Facebook developed GraphQL as replacement of REST API  for internal use.
*   First used in 2012
*   Specification was open sourced in 2015
*   Currently managed by the GraphQL Foundation

## GraphQL Basics

GraphQL is:

*   A specification

    *   GraphQL defines the semantics and componentes of a GraphQL API
    *   Does not provide concrete implementations
    *   Other parties implementations in many languages.
    *   Full specs can be found here: https://github.com/graphql/graphql-spec

*   Defines structure of data returned

    *   Perhaps the most important feature of GraphQL
    *   Can specify the part(s) of entity to return
    *   Can specify related entities to be returned.
    *   Can specify filtering in the query

*   JSON based

    *   Extensive usage of JSON
    *   Query sent to server in JSON
    *   Data is returned in JSON
    *   Technically can be used with other protocols, nobody does it.

*   3 types of operations

    *   With GraphQL we can:
        *   Retrieve data
        *   Write / Change Data
        *   Subscribe to Changes in Data

*   Schema-based

    *   GraphQL works with schema

    *   Defines the entities, fields and attributes

    *   Operations are build on the schema

        ```apl
        type Character {
        	name: string!
        	appearsIn: [Episode!]!
        }
        ```

*   Cross-plataform

    *   Supported by JavaScript, Go, PHP, Java / Kotlin, C# / .NET, Python, Swift / Objective-C, Rust, Ruby, Elixir, Scala, Flutter, Clojure, Haskell, C / C++, Elm, OCaml / Reason, Erlang, Julia, R, Groovy, Perl, D, and so on and so forth.


## Working with GraphQL

*   Four main steps
    *    Defining Schema
    *   Defining Queries
    *   Defining Mutations and Subscriptions (optional)

## Demo

Unlike a classic REST API, with GraphQL you have a fine-grained control of the information you receive.

*   For example, if you need to obtain all author with all their books's names

    *   in REST you normally need to make many requests:

        *   with `GET /authors` you get all authors id, along with a bunch of unrequested useless information

            ```json
            [
              {
                "id": 1,
                "name": "Brent Weeks",
                "age": 30,
                "state": "Montana",
                "country": "USA",
                "email": "brent.weeks@example.com",
                "phone": "+1-406-555-1234",
                "website": "https://brentweeks.com",
                "twitterHandle": "@brentweeks",
                "genres": ["Fantasy", "Adventure"],
                "awards": ["David Gemmell Award", "NYT Bestseller"],
                "biography": "Brent Weeks is an American fantasy writer, author of the Night Angel trilogy...",
                "profileImageUrl": "https://example.com/authors/brent-weeks.jpg",
                "booksPublished": 12,
                "averageRating": 4.4,
                "followersCount": 58200,
                "birthDate": "1977-03-07",
                "createdAt": "2005-06-15T00:00:00Z",
                "updatedAt": "2023-12-10T14:45:00Z"
              },
              {
                "id": 2,
                "name": "Patrick Rothfuss",
                "age": 35,
                "state": "Wisconsin",
                "country": "USA",
                "email": "patrick.rothfuss@example.com",
                "phone": "+1-608-555-5678",
                "website": "https://patrickrothfuss.com",
                "twitterHandle": "@patrickrothfuss",
                "genres": ["Fantasy", "Epic"],
                "awards": ["Quill Award", "Locus Award"],
                "biography": "Patrick Rothfuss is the author of The Kingkiller Chronicle...",
                "profileImageUrl": "https://example.com/authors/patrick-rothfuss.jpg",
                "booksPublished": 6,
                "averageRating": 4.7,
                "followersCount": 101200,
                "birthDate": "1973-06-06",
                "createdAt": "2007-04-01T00:00:00Z",
                "updatedAt": "2023-11-30T18:20:00Z"
              }
            ]
            ```

        *   now can you need to iterate all ids calling `GET /authors/:id/books `for each one, with the same problem of unrequested useless information. 

            ```json
            [
              {
                "id": 1,
                "name": "Way of Shadows",
                "authorId": 1,
                "publishedYear": 2008,
                "isbn": "9780316033671",
                "pageCount": 645,
                "language": "English",
                "publisher": "Orbit",
                "format": "Hardcover",
                "weightGrams": 780,
                "dimensions": {
                  "width": 15.2,
                  "height": 22.9,
                  "depth": 4.1
                },
                "coverImageUrl": "https://example.com/way-of-shadows.jpg",
                "rating": 4.5,
                "reviewsCount": 1823,
                "tags": ["Fantasy", "Adventure", "Magic"],
                "priceUSD": 24.99,
                "stockCount": 42,
                "warehouseLocation": "Montana",
                "createdAt": "2008-10-01T00:00:00Z",
                "updatedAt": "2023-12-15T12:30:00Z"
              },
              {
                "id": 2,
                "name": "Beyond the Shadows",
                "authorId": 1,
                "publishedYear": 2008,
                "isbn": "9780316033732",
                "pageCount": 720,
                "language": "English",
                "publisher": "Orbit",
                "format": "Paperback",
                "weightGrams": 650,
                "dimensions": {
                  "width": 14.5,
                  "height": 21.5,
                  "depth": 3.8
                },
                "coverImageUrl": "https://example.com/beyond-the-shadows.jpg",
                "rating": 4.6,
                "reviewsCount": 1475,
                "tags": ["Fantasy", "Epic", "Dark"],
                "priceUSD": 19.99,
                "stockCount": 36,
                "warehouseLocation": "Montana",
                "createdAt": "2008-12-01T00:00:00Z",
                "updatedAt": "2023-11-28T09:45:00Z"
              }
            ]
            ```

    *   in GraphQL, on other side:

        ```apl
        query {
          authors {
            name
            books {
              name
            }
          }
        }
        
        ```

        ```javascript
        {
          "data": {
            "authors": [
              {
                "name": "Brent Weeks",
                "books": [
                  { "name": "Way of Shadows" },
                  { "name": "Beyond the Shadows" }
                ]
              },
              {
                "name": "Patrick Rothfuss",
                "books": [
                  { "name": "The Name of the Wind" },
                  { "name": "The Wise Man's Fear" }
                ]
              }
            ]
          }
        }
        
        ```

There is a lot of libraries that supports GraphQL

## Drawbacks of GraphQL

* GraphQL doesn’t handle caching very well, since even slightly different queries need to be re-run.
