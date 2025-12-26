https://graphql.org/learn/best-practices/

# GraphQL Best Practices

## Don’t Build GraphQL APIs Like REST or RPC

GraphQL is fundamentally different from REST, and mostly different from RPC.
* While REST is centered around resources and RPC is centered around operations, GraphQL is centered around the client’s data requirements.
* While REST returns representations of addressable resources and RPC returns the result of a procedure call, GraphQL returns a graph shaped to the client’s query.

Example:

```go
type Query {
  getProduct(id: ID!): Product
  getAllProducts: [Product!]!

  getUser(id: ID!): User
  getAllUsers: [User!]!

  getSale(id: ID!): Sale
  getAllSales: [Sale!]!
}
```

What is wrong with this code?

* Verb-prefixed fields (`getX`)

  - In GraphQL, fields are typically **nouns** (what you can fetch), not verbs (actions you perform).

  - `getProduct` reads like an RPC method, not a graph field.

* “All” endpoints (`getAllProducts`)

  - This mirrors REST endpoints like `/products` and encourages “dump everything” queries.

  - GraphQL usually wants query parameters (filtering/pagination) instead of “all”.

* Inconsistent API shape / weak composability

  - You’ve got separate fields for “one” and “many” that don’t compose.

  - GraphQL’s strength is letting clients select **subfields** and traverse relationships; endpoint-style naming fights that mental model.

* Encodes transport thinking into the schema

  * `getAllX` is basically an endpoint name. In GraphQL, the schema should describe the **domain graph**, not a set of fetch operations.

Intead, do it:

```go
type Query {
  product(id: ID!): Product
  products: [Product!]!

  user(id: ID!): User
  users: [User!]!

  sale(id: ID!): Sale
  sales: [Sale!]!
}
```

## Adopt a Ubiquitous Language

In Domain-Driven Design (DDD), a *ubiquitous language* is a shared vocabulary used consistently by developers, domain experts, and the system itself. GraphQL schemas naturally encourage this practice by making the API surface **the language of the domain**.

* Instead of exposing technical concepts or implementation details, a GraphQL schema names types and fields after **real domain concepts**: `Product`, `User`, `Sale`, `price`, `createdAt`, `user`. These names become the common language spoken across teams, documentation, and client applications.
* Because the schema is strongly typed and introspectable, this language is not just informal—it is **enforced**. Clients can only ask questions using the terms defined in the schema, which keeps communication precise and aligned.
* Establishing a ubiquitous language requires deliberate effort. Naming types, fields, and relationships is not a cosmetic concern—it is how the domain is expressed in the API. Teams should invest time in developing a shared understanding of the domain rules and concepts before encoding them into the schema, because these names become long-lived and difficult to change.
  * In GraphQL, every node and relationship is part of the domain’s public vocabulary. Choosing clear, durable names means thinking in terms of **how users describe the domain**, not how data happens to be stored or fetched. A useful exercise is to imagine the questions clients will naturally want to ask and ensure the schema allows those questions to be expressed directly, using the same language domain experts would use.

This has several effects:

- The API reflects the **mental model of the domain**, not backend structure
- Backend and frontend teams speak the **same vocabulary**
- Changes in understanding of the domain naturally drive schema evolution
- Documentation becomes largely self-explanatory

By acting as a single source of truth for domain terminology, a GraphQL schema functions as an executable form of ubiquitous language. The result is less translation between layers, fewer misunderstandings, and an API that stays close to the business concepts it represents.

## Authentication

Most modern web frameworks use a pipeline model where requests are passed through a stack of middleware, also known as filters or plugins. As the request flows through the pipeline, it can be inspected, transformed, modified, or terminated with a response. GraphQL should be placed after all authentication middleware so that you have access to the same session and user information you would in your other HTTP endpoint handlers.

## Authorization

Authorization determines **what an authenticated user is allowed to access**. Unlike authentication, authorization decisions should generally **not** be made before GraphQL execution begins.

Instead, authorization should be enforced **during execution**, at the level of fields and business logic. This allows GraphQL to produce **partial responses** when access to specific fields is denied, rather than failing the entire request.

Key principles:

- Authentication happens before GraphQL execution
- Authorization happens inside resolvers or domain logic
- Unauthorized fields can resolve to `null` or raise field-level errors
- Other authorized fields can still be returned

> GraphQL execution should begin only after authentication middleware has confirmed the user’s identity and provided that information to the GraphQL context.

### Example domain

```apl
type Post {
  authorId: ID!
  body: String
}
```

Business rule: **Only authors can see their drafts**

### Enforcing Authorization in Resolvers

One way to enforce this rule is directly in the field resolver.

```javascript
function Post_body(obj, args, context, info) {
  // Only return the body if the current user is the author
  if (context.user && context.user.id === obj.authorId) {
    return obj.body;
  }
  return null;
}
```

This approach ensures:

- Authorization is evaluated **only if the field is requested**
- Unauthorized access does not break the entire query
- The response accurately reflects what the user is allowed to see

#### Delegating Authorization to Domain Logic

To avoid duplicating authorization checks across resolvers, it is often better to delegate authorization to a **single source of truth** in the business or data access layer.

```javascript
export const postRepository = {
  getBody({ user, post }) {
    const isAuthor = user?.id === post.authorId;
    return isAuthor ? post.body : null;
  },
};
```

Benefits of this approach:

- Authorization rules are centralized
- Business logic remains consistent across GraphQL and non-GraphQL consumers
- Resolvers stay thin and declarative

### Schema-Level Authorization with Directives

Another common pattern is to express authorization rules declaratively using **schema directives**.

```apl
directive @auth(rule: Rule) on FIELD_DEFINITION

enum Rule {
  IS_AUTHOR
}

type Post {
  authorId: ID!
  body: String @auth(rule: IS_AUTHOR)
}
```

In this model:

- The schema documents authorization requirements explicitly
- A directive implementation enforces the rule at runtime
- Authorization logic can be reused across fields and types

Directives are especially useful when:

- Authorization rules are consistent and role-based
- You want authorization to be visible at the schema level
- You have infrastructure to enforce directives reliably

## Paginate Your Queries

Pagination exists to limit response size, control execution cost, and keep queries predictable as datasets grow. Even when a client technically *can* request everything, doing so quickly becomes inefficient and brittle as data volume increases.

In GraphQL, pagination is expressed through field arguments, allowing clients to control how much data they fetch without changing the structure of the schema.

* Instead of introducing new fields for different result sizes or access patterns, a single field can support pagination by accepting arguments such as limits, offsets, or cursors.

```go
type Query {
  product(id: ID!): Product
  products(filter: ProductFilter, limit: Int, offset: Int): [Product!]!
}
```

Key ideas:

- Pagination prevents unbounded result sets
- It keeps query execution efficient and predictable
- Pagination is part of the query, not the schema shape
- Field names remain stable as requirements evolve
- Arguments refine *how much* data is returned
- Clients request only the data they need, when they need it

This approach keeps the schema focused on modeling the domain while giving clients control over performance and data volume. As needs grow, this model can naturally evolve toward cursor-based pagination (connections) without changing the way clients think about querying the API.

### Returning Pagination Metadata

In some cases, returning a plain list is sufficient. In others, clients also need metadata such as the total number of items, paging boundaries, or execution hints.

This can be handled by returning a dedicated result type instead of a raw list. The field continues to represent a single concept (`products`), while its return value describes both the items and the context in which they were fetched.

```apl
type Query {
  products(
    filter: ProductFilter
    limit: Int
    offset: Int
  ): ProductsQueryResults!
}

type ProductsQueryResults {
  items: [Product!]!
  count: Int!
}
```

Key points:

- This is an **extension**, not a replacement, of list-based pagination
- Metadata is modeled explicitly in the schema
- Clients select exactly which metadata they need
- New fields can be added over time without changing the query entry point

This pattern is especially useful when pagination needs to surface more than just slices of data, while preserving the same query semantics and client-driven response shaping.

## Schema Design

### Schema Evolution (Versioning)

- GraphQL allows schema evolution without traditional versioning.
- Unlike REST endpoints where changing response shapes often requires version bumps, GraphQL only returns the fields clients explicitly request.
- You can add new types or fields without breaking existing clients, as long as previously existing fields remain unchanged.
- This encourages a versionless API, where growth and new features don’t force new major API versions.

### Nullability and Failure Semantics

- In GraphQL, every field is nullable by default. 
- This default exists because many things can go wrong in distributed systems (database failures, remote service issues, authorization rules, etc.).
- When a nullable field fails (for any reason), GraphQL returns `null` for just that field, and the rest of the response can still resolve normally.
- If your business model requires a field never be null, you can mark it with a non-null type (`!`) to enforce that guarantee. 
- Choosing between nullable and non-null should be a design decision, informed by whether `null` is an acceptable result in real failure scenarios.

## Use Input Types for Mutations

Mutations tend to accumulate arguments fast. As soon as a model grows (more fields, optional fields, nested data), long argument lists become noisy, hard to version, and easy to misuse.

```apl
type Mutation {
  createProduct(name: String!, description: String!, price: Float!): Product!
  updateProduct(id: ID!, name: String, description: String, price: Float): Product!
  deleteProduct(id: ID!): Boolean!
}
```

Using `input` types solves that by bundling arguments into a single, named shape.

- **Improves readability:** one `input` parameter instead of many scalar args
- **Easier evolution:** you can add new fields to an input type without changing the mutation signature
- **Better validation and reuse:** share input types across mutations (or across related models)
- **Supports nesting cleanly:** inputs can contain other input objects

A typical refactor looks like this:

```apl
input CreateProductInput {
  name: String!
  description: String!
  price: Float!
}

input UpdateProductInput {
  name: String
  description: String
  price: Float
}

type Mutation {
  createProduct(input: CreateProductInput!): Product!
  updateProduct(id: ID!, input: UpdateProductInput!): Product!
  deleteProduct(id: ID!): Boolean!
}
```

A useful rule of thumb:

> **Use an input type whenever a mutation has more than ~2–3 arguments**, or whenever you expect the payload to grow over time.

## Return the Modified Object

Mutations are not only about performing a change; they are also an opportunity to return the updated state of the affected data.

* Returning the modified object allows clients to immediately consume the result of a mutation without issuing a follow-up query. This keeps interactions efficient and reduces unnecessary round trips.

A common anti-pattern is to replace domain data with a generic “result” object that only reports whether the operation succeeded.

```apl
type CreateProductResult {
  success: Boolean
  message: String
}

type Mutation {
  createProduct(
    name: String!
    description: String!
    price: Float!
  ): CreateProductResult
}
```

This approach weakens the API for several reasons:

- The created object is not returned, forcing clients to perform an additional query
- `success` conveys *that something happened*, but not *what changed*
- `message` is unstructured and difficult to handle programmatically
- The mutation result does not compose with the rest of the graph
- Outcome reporting is mixed with data modeling

In GraphQL, the preferred approach is to return the affected domain object directly:

```apl
type Mutation {
  createProduct(input: CreateProductInput!): Product!
}
```

This allows the mutation to participate in the graph like any other field: clients can select exactly the fields they need, and the response reflects the authoritative state after the change.

In cases where additional context is needed (e.g. validation errors or side effects), this approach can be extended by returning a result object instead of the domain object directly, without changing the underlying intent.

## Use field resolvers

One of GraphQL’s biggest advantages is that relationships are modeled directly in the schema, and **resolved on demand**. You don’t need separate “get user for product” queries—clients can just traverse the graph.

A common GraphQL anti-pattern is resolving relationships too early, usually inside top-level query resolvers, instead of modeling them as fields on the graph.

For example, instead of exposing a relationship like this:

```apl
type Product {
  id: ID!
  name: String!
  user: User
}
```

the API is designed so that the `user` is fetched eagerly inside `Query.product`, or exposed via a separate query such as `productUser(productId: ID!)`.

This approach has several drawbacks:

- The relationship is hidden from the schema, making it less discoverable
- Data is fetched whether or not the client asked for it
- Queries become tightly coupled to specific access patterns
- The graph becomes shallow, forcing clients to orchestrate traversal manually

By contrast, modeling `user` as a field on `Product` and resolving it with a field resolver preserves GraphQL’s core abstraction: clients traverse a graph, not a set of endpoints.

With field resolvers:

- `Query.product(id)` is responsible only for returning a `Product`
- The `Product.user` field defines *how* the related `User` is fetched
- The relationship is resolved only if the client selects it

This separation is crucial. It allows the schema to describe relationships declaratively, while the server controls *when* and *how* data is fetched behind the scenes.

Field resolvers also provide a clear boundary for optimization. Concerns like batching, caching, or authorization can be applied at the field level without leaking into query logic or forcing clients to change how they query the API.

## Don’t Create Multiple Queries for the Same Node Type

A common schema design mistake is creating **multiple query fields that all return the same node type**, each tailored to a specific lookup strategy.

```apl
input ProductByNameFilter {
  name: String!
}

input ProductByIdInputFilter {
  id: String!
}

type Query {
  productByName(input: GetProductByNameInput)
  productById(input: GetProductByIdInput)
}
```

This approach encodes how the server fetches data directly into the schema. Each new lookup requirement results in another query field, even though the underlying node type (`Product`) is the same.

Problems with this pattern:

- The schema grows horizontally with near-duplicate entry points
- Lookup strategies are baked into the API surface
- Clients must choose *which query* instead of *what data*
- The graph becomes fragmented and harder to reason about

In GraphQL, a node type should usually have a single, canonical entry point, with arguments used to express different ways of identifying or filtering it.

A more idiomatic design looks like this:

```apl
type Query {
  product(id: ID, name: String): Product
}
```

or, more explicitly:

```apl
input ProductFilter {
  id: ID
  name: String
}

type Query {
  products(filter: ProductFilter): [Product!]!
}
```

Here, the schema describes what exists (`product`, `products`), while arguments describe **how to narrow the result**. This keeps the API stable as new lookup requirements emerge and avoids multiplying query fields that all lead to the same node.

## Prefer Using Signed URLs for File Uploads

File uploads are not a first-class concern in the GraphQL specification. GraphQL is designed to model and query structured data, not to efficiently transport large binary payloads.

For this reason, a common and recommended approach is to **handle file uploads outside of GraphQL**, using mechanisms such as **signed URLs** (for example, direct uploads to object storage).

In this pattern:

- GraphQL is used to **request an upload authorization** (e.g. a signed URL)
- The client uploads the file directly to the storage service
- A follow-up mutation associates the uploaded file with domain data in the graph

This approach has several advantages:

- Large files bypass the GraphQL execution layer
- Uploads can be streamed directly to storage
- Resource limits, retries, and resumable uploads are handled by systems designed for them
- The GraphQL API remains focused on modeling domain relationships

### Caveat: Community-Supported Upload Patterns

There are community conventions that enable file uploads through GraphQL itself, most notably multipart request–based approaches. These are widely implemented and can be practical in controlled environments.

However, it’s important to note that:

- These patterns are **not part of the GraphQL specification**
- They rely on transport-level conventions rather than query semantics
- They introduce additional complexity around memory usage, security, and request handling

As a result, they should be treated as **opt-in extensions**, not default design choices.

In short:
 GraphQL excels at describing *what data exists and how it is connected*. For moving large binary payloads, **prefer specialized upload mechanisms**, and use GraphQL to coordinate and reference them rather than to transport them directly.