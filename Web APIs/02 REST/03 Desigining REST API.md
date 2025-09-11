# Designing REST API

## Pratices

### Resources naming

* entities must be nouns, they should be in plural 
* you should use the appropriate HTTP method
  * CRUD
    * Create - POST
    * read - GET
    * update - PUT
    * delete - DELETE
  * if the operation is not a CRUD operation, you may use a verb
    * you should put that action as part of resource hierarchy 
    * example
      * spotify: `"https://api.spotify.com/v1/search?query=tania+bowra&offset`
      * uber: `/estimates/prices`
      * twitter: `frindships/lookup`

### Resources relationship

* avoid deep nesting, you should keep it up to 3 levels.
  * you may use queries parameters to accomplish it.
* examples:
  * Orders have Items: `/orders/{id}/items`
  * People have followers: `/people/{id}/followers`
  * `properties/{id}/roomTypes/{id}/amenities`
  * `geocode/{latitude}/{longitude}/forecast/daily/{days}`

## Uniform Interface

The API developer should provide these following information to the client for each route:

* endpoint: the url
* query parameters
* request
  * Standard or Custom header
  * Data format e.g.: JSON
  * Request Schema
* response
  * HTTP Status Code
  * Header
  * Standard or Custom header
  * Data format e.g. JSON
  * Response Schema

## Anatomy of URL

* Defines the structure of the API
* The most important part of the API
  * developers will decide if they use your APIs or not based on URL structure

* Should be
  * Self explanatory
  * Consistent across the API
  * Predictable

```url
https://domain/product/version/resource/{id}
```

1. `https://domain` is the "base url"
2. the `product` is the logic grouping of resources, it helps you to distribute the API into multiple machines, so each logic group have it's own code, so it's own versioning. It is optional.
3. `https://domain/product/version`is the "root url" or "base path" (up to the version)

### Domain name

* The first part of the URL
* Also know as "Base URL"
* Usually contains FQDN (Fully Qualified Domain Name) or server name
  * Protocol should be HTTPS
  * For FQDN - should have `api` in its name
    * for example:
      * `https://api.myapp.com`
      * `https://language.googleapis.com/v1/documents:analyzeEntities`
    * if not, you can put on the url, as `https://www.myapp.com/api`

### Version

* Assumes that your API will be updated

* Versioning is specially important when we don't control our clients

  * you can't force version upgrade

* Set version support policy (for example, minimum three years from the data of first release).

* Only natural number (positive integer)

* could be prefixed with `v`

* You should create a new version always that a change may break the already existent clients.

  * for example
    * non breaking change - there is **no** need to new version
      * add a attribute on the payload
      * add a new operation or resource
      * adding optional parameters or properties 
    *  breaking change - there is need to new version
      * rename a attribute on the payload is a breaking change
      * change the HTTP verb
      * Delete a route

* good practices:

  * 

    when changing a API try avoid breaking change as much as you can.

  * provide planning opportunity to the app developers

  * support backward compatibility

  * provide support to app developers with the changes

  * minimize change frequency, e.g, once per 6 months.

  * version your API right from day 1

* It can be many strategies

  * URI Path Version: `http://www.myapp.com/api/v1`.

    * Default choose for public developers
      * Simple
      * Familiar to most developers
      * Easy to manage with minimal infrastructure support
    * Pros
      * Easy to understand and use.
      * Clear separation between versions.
      * Caches well and works with most proxies and CDNs.
    * Cons
      * Violates RESTful principle of resource uniformity.
      * Forces clients to change base URLs when upgrading.

  * Query Parameter: `https://api.example.com/resource?version=1`

    * Not recommended

    * Pros

      * Easy to implement and test.
      * Keeps the URI path clean.

    * Cons

      - Less visible in logs and documentation.

      - Can be problematic with caching proxies.

      - Not considered RESTful by some purists.

  * Header Parameter:

    ```http
    GET /resource
    Accept: application/vnd.example.v1+json
    ```

    * Good when:
      * You need fine-grained control over representations.
      * Your clients are sophisticated or under your control (e.g., internal apps).
    * Pros
      * Clean and REST-compliant.
      * Allows content negotiation and flexible representation.
    * Cons
      * Harder to test/debug in browsers and CLI tools like curl.
      * Not always supported or handled well by intermediate systems (e.g., proxies, CDNs).

  * Subdomain Versioning: `https://v1.api.example.com/resource`
    * Pros:
      * Clear separation, useful for large organizations.
      * Can support independent infrastructure for each version.
    * Cons:
      * More complex DNS and routing configuration.
      * Uncommon; may confuse clients.

* Use URI Path Versioning for most public APIs

### Entity

* REST deals with resources, or entities
* Should be one word, no more
* Always use nouns to name entities
* Examples:
  * `/orders`: entity orders
  * `employees`: entity employees
  * `travels`: entity travels

* When dealing with a specific entity, use entity ID
  * The ID is part of the URL
  * Example: `/orders/17`
  * Relevant for GET, PUT and DELETE
    * not for PST because the client can't know the ID of a to-be-entity
* When dealing with a entities that are dependent on other entities, use sub entities
  * Example: Get all items of order 17 `GET /orders/17/items`
  * Same goes for sub-sub-entity, etc
*  you should generally use plural nouns for resource names. This is a widely accepted convention.
  * `GET /books` Get all books
  * `POST /books` Create a new book
  * `GET /books/1` Get book with ID 1
  * `PUT /books/1` Update book with ID 1
  * `DELETE /books/1` Delete book with ID 1

### Query Parameters

* Used to query the entities in GET method
* Come at the end of the URL, after `?`, and are concatenates with `&`
  * `/api/v1/orders?fromDate=12/12/2018&toDate=2/2/2019`
* Good to query a list of entities, instead of query exactly one entity (as on id parameter)
  * It no entities is found, it response a empty list.
    * on the other error, if you query using id, it should response a 404.

## HTTP Verbs

* It is part HTTP standard, not necessarily REST 

* Set the action to be performed

  * Retrieve a resource

  * Add a resource

  * Update a resource

  * Delete a resource

* Always use the correct verb

  * Improves readability

| **Verb**   | **Role**             | **Body?** | **Params In...** | **Idempotent?** |
| ---------- | -------------------- | --------- | ---------------- | --------------- |
| **GET**    | Retrieve resource(s) | No        | URL              | Yes             |
| **POST**   | Add resource(s)      | Yes       | Body             | No              |
| **PUT**    | Modify resource(s)   | Yes       | Body             | Yes             |
| **DELETE** | Delete resource(s)   | No        | URL              | Yes             |

### GET

* Used to retrieve resource(s)
* Never use it to add / update / delete resources
* The default verb of the browser's address bar
* Usually combined with parameters
* Should not include body
* Sometimes GET cannot be used for retrieval. For example if there is too may parameters. In these cases, is OK using POST.
* GET is idempotent.

### POST

* Used to add resource
* Could contain a message body that specifies the resource to be added
* Should not contain query string parameters
* Used to modify resource(s)
* POST isn't idempotent, because duplicated requests will cause duplicated resources.

### PUT

* Used to modify resource(s)
* Should contain a message body that specifies the resource to be modified
* Should not container query string parameter
* A new resource should be created if is requested to modify one that doesn't exists
  * But you can use your own discretion, for example response 404.
* PUT is idempotent.

### DELETE

* Used to delete resources
* never use it to add / update / retrieve resources
* Almost always combined with parameters.
* Should not include body.
* DELETE is idempotent.

### Rarely Used Verbs

* **PATCH**: Similar to put, but with partial updates

* **HEAD**: Same as GET, but without the body in the response

* **OPTIONS**: Describes the available verbs for the URL
  
  ```bash
  $ curl -X OPTIONS http://example.org -i
  HTTP/1.1 204 No Content
  Allow: OPTIONS, GET, HEAD, POST
  ```
  
  

## Status code

* Server always sends it back in header
* The status code consists in 3 digit number
* Its purpose is inform the client about the status of the request.
* Most clients check for response code and act accordingly
* Monitoring tools check response codes and report it
* Makes the API easier to sue and understand
* Very easy to implement, often overlooked.
* Not invent new codes - use the standard HTTP codes
* Dividend into 5 groups
  * Each group represent specific response type
* standardinized on https://datatracker.ietf.org/doc/html/rfc2616
* There is many fancy status code, but it is recommended use only the most basic (approximately 8 status code)
  * it will be hard to a team of developers keep consistency if have too many status code.
  * good a ballpark is the session "Cheat Sheet: When use each one"


### `1xx` Information Response

`1xx` status codes are provisional responses that indicate the request was received and is being processed, but no final response is ready yet.

They are low level, hardly you will need directly operate it.

* `100 Continue` lets the client confirm server approval before sending the request body.
  * Before sending a large payload, the client sends only the headers, including the header `Expect: 100-continue`.
  * The server checks the headers.
    * If everything is OK, it sends a `100` status code;
    * otherwise, it sends a final `4xx` or `5xx` status code.
      * mainly `417 Expectation Failed` status code.
  * If the server sends `100 Continue`, the client sends the body, and the server processes the request normally.
  
* `101 Switching Protocols` indicates that the server is switching to a different protocol as requested by the client.
  * The client sends a request with an `Upgrade` header, specifying the protocol it wants to switch to (for example, `Upgrade: websocket`).
    * Some example of protocols are:
      * `websocket`: Used to upgrade an HTTP connection to a WebSocket connection for real-time communication.
      * `h2c`: Stands for “HTTP/2 Cleartext.” Used to upgrade from HTTP/1.1 to HTTP/2 without TLS encryption.
      * `TLS/1.0`, `TLS/1.1`, `TLS/1.2`: Used for switching to TLS-encrypted communication (rarely used this way nowadays).
      * `HTTP/2.0` To upgrade from HTTP/1.1 to HTTP/2 (now, ALPN is used instead for HTTPS).
      * `IRC/6.9`, `RTA/x11`, etc.: These are historical or experimental protocols you might see in documentation, but they’re almost never used in practice.
  * The server examines the request. If it agrees to the protocol change, it responds with a `101` status code and includes the `Upgrade` header in its response.
  * After receiving `101 Switching Protocols`, both the client and server start communicating using the new protocol.
* `103 Early Hint` lets the server send some preliminary response headers to the client before the final response is ready.
  * It’s mainly used to help browsers (or clients) get a head start on things like loading CSS, JavaScript, or images, even before the server finishes generating the full page.
  * process:
    1) Server receives a request for a web page.
    2) The server knows that the final response will include links to resources like stylesheets or scripts.
    3) Before generating the full response, the server sends a 103 Early Hints response, including headers like Link: `<style.css>; rel=preload`.
    4) The browser sees these headers and can start fetching those resources immediately.
    5) When the final response is ready, the server sends the normal status code (like 200 OK) and the full content.


### `2xx` Success

* `200 OK`
  * default status code
    * many developers aren't aware of that, who use 200 status code for every response
  * The request was successful
  * The response body should be:
    * for `GET`: response the requested entity or entities.
    * for: `POST` response the requested entity or entities.
      * despite it being the correct, most people frowns upon using `200` for POST. You can settle this polemic by using `201` and sending both body and `Location` header.
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

### `3xx` Redirection

`3xx` status codes indicate that further action is needed from the client to complete the request, usually in the form of a redirection to a different URL.

* They are low level, hardly you will need directly operate it.
* All HTTP redirections use the `Location` header to indicate the new URL. However, whether the original request method, headers, or body are preserved depends on the specific status code used.

Some examples are:

* `300 Multiple Choices` The request has more than one possible response. The user (or user agent) should choose one of them. For example, different file formats for a resource, or multiple languages.
* `301 Moved Permanently` The resource requested has been permanently moved to a new URL.
  * Future requests should use the new URL.
  * Browsers will redirect to the new URL automatically.
* `302 Found` The resource is temporarily located at a different URL.
  * Browsers will redirect to the new URL, but future requests should still use the original URL.
  * previously it was known as "Moved Temporarily"
  * Many clients (including browsers) will change the HTTP method from POST to GET when following a 302.
    * This can be a problem if you want to preserve the original method (e.g., POST should stay POST).
    * To reduce this risk, use  `307 Temporary Redirect` instead of `302 Found`.
* `303 See Other` The response to the request can be found under a different URL and should be retrieved using a GET method.
  * Often used after a POST operation to redirect the client to a confirmation page.
* `304 Not Modified` Indicates that the resource has not been modified since the last request.
  * The client can use the cached version.
* `305 User Proxy` The requested resource is only available through a **proxy**, whose address is provided in the response. 
  * This is rarely used today, and support is deprecated in many browsers for security reasons
    * If a malicious server responds with `305 Use Proxy`, it can direct clients to use a proxy controlled by an attacker.
* `307 Temporary Redirect` The requested resource is temporarily at a different URL, and the client should use the original method for the next request (unlike 302, which may change POST to GET).
  * More precise than 302 for HTTP/1.1.

### `4xx` Client Errors

* `400 Bad request` 

  * The client sent a bad request

    * Parameters are invalid (i.e. negative age)
    * JSON can't be parsed

  * Used with all verbs

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
* `415 Unsupported type`
* `422 Unprocessable Content`  indicates that the server understood the content type of the request content, and the syntax of the request content was correct, but it was unable to process the contained instructions.
  * Clients that receive a `422` response should expect that repeating the request without modification will fail with the same error.
* `428 Precondition Required` The HTTP 428 Precondition Required client error response status code indicates that the server requires the request to be conditional.
  * Typically, a `428 response` means that a required precondition header such as `If-Match` is missing.
    * When a precondition header does not match the server-side state, the response should be `412 Precondition Failed`.

### `5xx` Server Errors

* `500 - Internal Server Error`
  * Something bad happened while processing the request
  * Don't inform nothing about the error beyond that it happened
    * it is a good thing at security perspective
  * Used with all verbs
* other `5xx` status code are usually not used, or are low level.

### There a also many non-standard code

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

### Cheat Sheet: When use each one

#### **GET**

| Code      | Description                               |
| --------- | ----------------------------------------- |
| 200       | Content was found and returned            |
| 400       | Bad Request – Error validating parameters |
| 401 / 403 | Authorization required / Not authorized   |
| 404       | Not Found – Entity not found              |
| 500       | Internal Server Error                     |

#### **POST**

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

#### **PUT**

| Code      | Description                                                  |
| --------- | ------------------------------------------------------------ |
| 200       | Request completed successfully                               |
| 202       | Request received and is pending processing                   |
| 204       | No Content – Request successful but server has nothing to return |
| 400       | Bad Request – Error validating parameters                    |
| 401 / 403 | Authorization required / Not authorized                      |
| 404       | Not Found – Entity to update not found; also for updating sub-entity using ID param |
| 500       | Internal Server Error                                        |

#### **DELETE**

| Code      | Description                                                  |
| --------- | ------------------------------------------------------------ |
| 200       | Content was found and deleted                                |
| 204       | No Content – Request successful but server has nothing to return |
| 400       | Bad Request – Error validating parameters                    |
| 401 / 403 | Authorization required / Not authorized                      |
| 404       | Not Found – Entity to delete not found                       |
| 500       | Internal Server Error                                        |

## Data Formats

The best data format for your response is the one that brings the most value to the client.

* Build support for multiple format, or at least make your API flexible enough to support multiple formats in the future,
  * in this case, the client can choose which format the server should send.
    * by query parameters `/news?output=json`, `/news?output=csv`
    * by HTTP headers `Accept: application/json`, `Accept: application/csv`
    * resource format suffix `/forecast/daily/{days}day.json`
  * If the client request a format that you don't support, send `415 Unsupported type` as response
  * ensure documentation of supported formats

## Error Handling Patterns

### Error information only in HTTP header

* Sends back only:
  * status-code: for example, `404`, `400`
  * reason-phrase (for example, `Not Found` or `Bad Request`)
  * X-Custom-Header For additional information
    * for example, the API of etys.com uses the header `X-Error-Detail`

### Error information only in body

* Always return HTTP status code `200`
* Error information in standard format
* Older versions of facebook used this approach
* Least preferred approach
* It creates a "response envelop", for example every response have:
  * a attribute `payload` with the response if successful, `{}` otherwise
  * and a attribute `errors` with a list of errors representations if not successful, `[]` otherwise


### Error information in Header + Body

* When the client resceives the response, it can read the error code:
  * if it is `2xx`, read body for resource information on link
  * otherwise, read body for error information

* it is most preferred approach

* Uber's API uses it
  * Sends the status code:
    * `401`: No authentication provided
    * `422` One the input values is not int he correct format
    * `503` The service is currently unavailable 
  * Body
    * `code` string: Machine-readable code for error
    * `message`string: Human-readable message for error.

* You can include:

  * the field `link` with a link that explain the issue

  * the field `hints` with hints on the potential issues and solutions.
    * `"Please check that user has provided the non-null value for 'name'"`
    * `"Please check that user has provided a number (between 1 and 31)"`

* Tip: Centralize the info of errors, so you can keep consistency along with the whole API

  ```json
  exports.errors = {
      UNKNOWN_ERROR : {
          code:5000,
          text:"Unknown error !!!",
          hints:["Please contact development team wit information on 'how to reproduce this error'. Thank you for your help!"],
          info:"http://developer.acme.com/unknownerror"
      },
      PACKAGE_ALREADY_EXISTS :{
          code:6000,
          text:"Vacation package with the provided 'code' already exist",
          hints:["Please use PUT for update instead of POST"],
          info:"http://developer.acme.com/errors#6000"
      },
  }
  ```

#### RFC7807 - Problem Details

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
    * **`invalid-params`**
    
      * Lists which request parameters failed validation.
      * Often used as an array of objects with keys like `name` and `reason`.
      * Helps clients pinpoint exactly what's wrong with user input.
    
      ```json
      "invalid-params": [
        {
          "name": "email",
          "reason": "must be a valid email address"
        },
        {
          "name": "age",
          "reason": "must be a positive integer"
        }
      ]
      ```
    * **`error_code`**
    
      * An internal or application-specific error identifier
    
      *  Useful for developers or support staff to map the issue quickly.
    
      ```json
      "error_code": "USR_0012"
      ```
    * **`timestamp`**
      * A UTC ISO 8601 string marking when the error occurred.
      * Helpful for logging and debugging.
      ```json
      "timestamp": "2025-07-29T15:23:00Z"
      ```
    * **`request_id`**
      * A unique identifier for tracing the request across distributed systems.
      * Can be useful for logging and user support.
      ```json
      "request_id": "abc123-def456"
      ```
    * **`debug`**
      * Developer-facing detail that should be omitted in production or hidden from end users.
      * Can include stack traces or internal diagnostics.

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