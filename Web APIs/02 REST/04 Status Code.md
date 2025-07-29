# Status code

* Its purpose is inform the client about the status of the request.

* Most clients check for response code and act accordingly

* Monitoring tools check response codes and report it

* Makes the API easier to sue and understand

* Very easy to implement, often overlooked.

* Dividend into 5 groups
  * Each group represent specific response type
  
  * Each group consists of 3 digits status code
  
  * They are
    * `1xx` Information Response
      * do not use
    
    * `2xx` Success
      * `200 OK`
        * default status code
          * many developers aren't aware of that, who use 200 status code for every response
        * The request was successful
        * The response body should be:
          * for `GET`: response the requested entity or entities.
          * for: `POST` response the requested entity or entities.
      * `201 Created` 
        * There request has been fulfilled, a new entity has been created
        * Response might contain `Location` header pointing to the entity
          * So differentially from `200`, `201` usually sends only the reference, not the whole object.
        *  The expected status code of POST request
      * `202 Accepted` 
        * The request has been accepted and is pending processing
        * Processing might not be complete
        * No notification is given when processing completes
        * Usually used for POST, PUT, request
      * `204 No Content` 
        * Request was fulfilled but no content was sent back
        * Should not include body
        * Used mainly when updating large entity
        * If a `GET` response have no content because there was no entities suitable to the queries parameters, you should use `200`, not `204`
    
    * `3xx` Redirection
    
      * low level
    
    * `4xx` Client Errors
    
      * `400 Bad request` 
    
        * The client sent a bad request
    
          * Parameters are invalid (i.e. negative age)
          * JSON can't be parsed
    
        * Used with all verbs
    
        * Consider using response `RFC7807` - Problem Details
    
          * Defines a media type: `application/problem+json`
    
          * Aimed at standardizing error messages from RESTful APIs.
    
          * Gives a clear structure to error responses with fields like:
    
            * `type` *(string, URI)*
    
              * A URI that identifies the general category of the error.
              * Helps both humans and machines understand what kind of error occurred.
              * Typically links to documentation or a help page.
              * Defaults to `"about:blank"` if omitted.
    
            * `title` *(string)*
    
              * A short, readable label for the error type.
              * Provides a consistent summary of the error.
              * Should remain static for each kind of error.
    
            * `status` *(number, HTTP status code)*
    
              * The HTTP status code associated with the error.
    
              * Clarifies what went wrong at the protocol level.
    
              * Should match the actual HTTP response status.
              * It brings several benefits
                * **Client-side consistency**: Some HTTP libraries may strip or mishandle the response status code; including it in the body ensures reliable access
                * **Logging/Debugging**: Tools that only process the response body can still access the error code without parsing HTTP headers
                * **Non-HTTP transport**: When used outside of HTTP (e.g. GraphQL, WebSockets), the status field retains its meaning
                * **Self-contained error**: The error response describes itself fully without relying on HTTP metadata, useful for logging and error propagation across systems
    
            * `detail` *(string)*
    
              * A human-readable explanation specific to this error occurrence.
    
              * Offers helpful context for troubleshooting.
    
              * Should not reveal sensitive or internal system details.
    
            * `instance` *(string, URI)*
    
              * **Purpose**: Provides a URI reference that identifies the specific occurrence of the error
              * **Format**: Usually a path or URL, like `/orders/1234/errors/abc123` or `https://api.example.com/errors/abc123`
              * **Use case**: Lets the server expose a unique ID or reference for the error, which clients can use for tracking or support
              * **Client benefit**: Clients can include this ID in bug reports or support tickets to help server operators trace the issue
              * **Server benefit**: Helps correlate the error with logs, trace IDs, or monitoring systems
              * **Optional**: It's not required by the spec, but it's useful when errors are logged or traced in production
              * **Behavior**: The URI does not have to be resolvable, but it **can** point to a page with more info or error details
    
            * Custom fields *(application-specific extensions)*
    
              - You can safely add your own fields to the JSON response to provide extra context or structure.
              - These fields are not defined by RFC 7807 but are fully allowed and encouraged.
              - Common use cases include validation errors, timestamps, internal error codes, or any field helpful to clients.
    
              * Examples of useful custom fields:
    
                - **`invalid-params`**
    
                  - Lists which request parameters failed validation.
                  - Often used as an array of objects with keys like `name` and `reason`.
                  - Helps clients pinpoint exactly what's wrong with user input.
    
                  ```json
                  "invalid-params": [
                    { "name": "email", "reason": "must be a valid email address" },
                    { "name": "age", "reason": "must be a positive integer" }
                  ]
                  ```
    
                - **`error_code`**
    
                  - An internal or application-specific error identifier.
    
                  - Useful for developers or support staff to map the issue quickly.
    
                    ```json
                    "error_code": "USR_0012"
                    ```
    
                - **`timestamp`**
    
                  - A UTC ISO 8601 string marking when the error occurred.
    
                  - Helpful for logging and debugging.
    
                    ```json
                    "timestamp": "2025-07-29T15:23:00Z"
                    ```
    
                - **`request_id`**
    
                  - A unique identifier for tracing the request across distributed systems.
    
                  - Can be useful for logging and user support.
    
                    ```json
                    "request_id": "abc123-def456"
                    ```
    
                - **`debug`**
    
                  - Developer-facing detail that should be omitted in production or hidden from end users.
    
                  - Can include stack traces or internal diagnostics.
    
                    ```json
                    "debug": {
                      "stack_trace": "...",
                      "internal_note": "Null reference in UserService"
                    }
                    ```
    
            * Examples
    
              * ```json
                {
                  "type": "https://example.com/probs/out-of-credit",
                  "title": "You do not have enough credit.",
                  "detail": "Your current balance is 30, but that costs 50.",
                  "instance": "/account/12345/msgs/abc",
                  "balance": 30,
                  "accounts": [
                    "/account/12345",
                    "/account/67890"
                  ]
                }
                ```
    
              * ```json
                {
                  "type": "https://example.net/validation-error",
                  "title": "Your request parameters didn't validate.",
                  "invalid-params": [
                    {
                      "name": "age",
                      "reason": "must be a positive integer"
                    },
                    {
                      "name": "color",
                      "reason": "must be 'green', 'red' or 'blue'"
                    }
                  ]
                }
                ```
    
      * `401 Unauthorized`
    
        * The client is not authorized to access the entity
        * Authentication issue: The user has not proven their identity (e.g., missing or invalid credentials).
        * Not to be confused with `403 - Forbidden`
          * `401` Authentication issue
          * `403 `Authorization issue
    
      * `403 - Forbidden`
    
        * The client is not authorized to access the entity
        * Authorization issue: The user is identified but not allowed to access the resource.
    
      * `404 Not Found`
    
        * The entity specified in the request was not found
        * Used when a specific entity was looked for
          * If a `GET` response have no content because there was no entities suitable to the queries parameters, you should use `200`, not `404`
        * Used with all verb
          * even in `POST` because you can trying a sub-entity to a non-existent entity.
    
    * `5xx` Server Errors
    
      * `500 - Internal Server Error`
        * Something bad happened while processing the request
        * Don't inform nothing about the error beyond that it happened
          * it is a good thing at security perspective
        * Used with all verbs
      * other `5xx` status code are usually not used, or are low level.

There a also many non-standard code

* Introduced by various companies and organizations

  * ie. Twitter, Apache, Shopify, and more

* WebDAV extends the standard for document editing

  * `207` - Multi-Status

    * Used for case where multiple entities are handled, each has it own status

      * ie;: Adding a list of 10 entities. Some might fail

      ```xml
      HTTP/1.1 207 Multi-Status
      Content-Type: application/xml; charset="utf-8"
      Content-Length: 1241
      
      <?xml version="1.0" encoding="utf-8" ?>
      <D:multistatus xmlns:D="DAV:">
        <D:response>
          <D:href>http://www.example.com/Coll/</D:href>
          <D:propstat>
            <D:prop>
              <D:displayname>Loop Demo</D:displayname>
              <D:resource-id>
                <D:href>urn:uuid:f81d4fae-7dec-11d0-a765-00a0c91e6bf8</D:href>
              </D:resource-id>
            </D:prop>
            <D:status>HTTP/1.1 200 OK</D:status>
          </D:propstat>
        </D:response>
        <D:response>
          <D:href>http://www.example.com/Coll/Bar</D:href>
          <D:propstat>
            <D:prop>
              <D:displayname>Loop Demo</D:displayname>
              <D:resource-id>
                <D:href>urn:uuid:f81d4fae-7dec-11d0-a765-00a0c91e6bf8</D:href>
              </D:resource-id>
            </D:prop>
            <D:status>HTTP/1.1 208 Already Reported</D:status>
          </D:propstat>
        </D:response>
      </D:multistatus>
      ```

## Cheat Sheet: When use each one

### **GET**

| Code      | Description                               |
| --------- | ----------------------------------------- |
| 200       | Content was found and returned            |
| 400       | Bad Request – Error validating parameters |
| 401 / 403 | Authorization required / Not authorized   |
| 404       | Not Found – Entity not found              |
| 500       | Internal Server Error                     |

### **POST**

| Code      | Description                                                  |
| --------- | ------------------------------------------------------------ |
| 200       | Request completed successfully                               |
| 201       | Entity was added successfully                                |
| 202       | Request received and is pending processing                   |
| 204       | No Content – Request successful but server has nothing to return |
| 400       | Bad Request – Error validating parameters                    |
| 401 / 403 | Authorization required / Not authorized                      |
| 404       | Not Found – When adding sub-entity using an ID parameter     |
| 500       | Internal Server Error                                        |

### **PUT**

| Code      | Description                                                  |
| --------- | ------------------------------------------------------------ |
| 200       | Request completed successfully                               |
| 202       | Request received and is pending processing                   |
| 204       | No Content – Request successful but server has nothing to return |
| 400       | Bad Request – Error validating parameters                    |
| 401 / 403 | Authorization required / Not authorized                      |
| 404       | Not Found – Entity to update not found; also for updating sub-entity using ID param |
| 500       | Internal Server Error                                        |

### **DELETE**

| Code      | Description                               |
| --------- | ----------------------------------------- |
| 200       | Content was found and deleted             |
| 400       | Bad Request – Error validating parameters |
| 401 / 403 | Authorization required / Not authorized   |
| 404       | Not Found – Entity to delete not found    |
| 500       | Internal Server Error                     |
