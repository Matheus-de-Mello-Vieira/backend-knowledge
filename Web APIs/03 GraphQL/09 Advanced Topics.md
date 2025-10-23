# Advanced Topics

## Error Handling

*   Errors in GraphQL are returned as JSON
*   Your code should plan for that and catch these errors
*   Errors can be:
    *   Thrown automatically by server when it cannot parse or validate the message
    *   Thrown by our own  code
*   You should plan for errors and act accordingly
    *   Usually: log the error and show generic message to the user
*   Avoid exposing sensitive data in production APIs (e.g., in tracebacks).

## Authorization

First, remember:

*   Authentication: Who is the user
*   Authorization; What the user is allowed to do

Now:

*   GraphQL offers no special treatment to authentication and authorization
    *   however, it can be configured to pass the user to the resolvers.
*   GraphQL not care how the authentication is actually executed.

Best pratice:

*   Block early in HTTP middleware (HTTP 401/403) for requests that shouldn’t reach GraphQL at all (e.g., missing/invalid token).
*   Use GraphQL errors (e.g., `UNAUTHENTICATED`, `FORBIDDEN`) for field-level or business-rule checks once inside execution.