# Developing GraphQL Server

*   Two components in Graphq

    *   **GraphQL Client**: Sends operations to the GraphQL Server and handles the results

    *   **GraphQL Server**: Exposes the GraphQL endpoint, receives the operations and returns results

## Server Roles

A GraphQL server must follow GraphQL Specifications to do:

*   Define GraphQL Schema

    *   The GraphQL Server defines the schema using code elements in the server or explicitly using the Schema Definition Language
        *   Usually based on classes / modules
        *   Each server has its own schema definition mechanism

*   Expose GraphQL Endpoint

    *   All GraphQL operations are sent to a specific, single, endpoint
        -   As opposed to REST API which exposes an endpoint for each operation
            -   `GET /api/v1/books/{id}`
            -   `POST /api/v1/employee`
    *   The endpoint is usually named `graphql`, and is accessed with a `POST` verb.
    *   The server expects to receive JSON payload in this endpoint.

*   Validate GraphQL Operations

    *   The server receives the JSON payload and validates it against the schema
        *   If a mismatch is found: the server returns a standard error message.
        *   normally no coding is required for this validation.

*   Route GraphQL Operations to Code

    *   The server converts the JSON payload to objects and triggers methods to process the operations and return the data.

        *   These methods are called `Resolvers`

    *   The server traverses thought the query and runs a resolver **for every field**.

        *   If the field returns a scalar value: this is what's returned
        *   If the field returns a object value: the server runs resolvers for each field in the object.

    *   Most implementations automatically create resolvers for fields

    *   Custom resolvers can be specified

    *   Resolvers can accept arguments with context data about the query

    *   Resolvers in the same hierarchy run in parallel. 

        *   So you can't assume one will run before the other.

            *   So you never use data from one resolver in another.

        *   Given:

            ```apl
            books {
              name
              pages
              author {
                name
              }
            }
            ```

        *   it will run:

            ```mermaid
            graph LR
              A["Query.books resolver"] --> B["Book[] list"]
            
              %% Example for one list item (repeats for each Book in the list)
              B --> C["Book[0] object"]
            
              %% Book[0] field resolvers (same-level fields can execute in parallel)
              C --> C1["Book.name resolver (default)"]
              C --> C2["Book.pages resolver (default)"]
              C --> C3["Book.author resolver"]
            
              %% Nested field requires its parent first
              C3 --> C3a["Author.name resolver (default)"]
            ```

*   Return GraphQL Results

    *   After running the resolvers and merging the results the server converts the object to JSON and returns it to the client.