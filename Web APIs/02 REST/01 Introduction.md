# Rest

* Stands for Representational State Transfer
  * It means that REST API enables transfer of representation of a resource’s state
    * state is:
      * the current resource properties
      * result of an action on the resource
* REST isn't restricted on HTTP, because any API that follows the REST Architecture Constrains is considered RESTful.

## Structure

### Request

* **Method**: HTTP Verb (GET, POST, PUT, DELETE, ...)
* **URL**: Location of the resource + parameters
* **Header**: Meta-data of the request (User Agent, ...)
* **Body**: contents of the request (optional)

### Response

* **Status code**: 200 (Success), 404 (Not Found), etc
* **Headers**: Meta-data of the request (Content Type, ...)
* **Body**: Contents of the response (optional)
  * Usually it is a JSON, but rarely can be also XML or HTML

## REST Architecture Constrains

To a architecture be deemed as restful, it needs to follow 6 design rules:

* **Client-Server**: "The application must have Client-Server architecture"
  
  * A client request a resource, that is responded by the server.
  * We can have multiple servers, and multiple clients.
  * Client-Server must not have run in same process
    * it means that Client-Server must communicate using IP.
    * it creates too much coupling 
    * it makes the Uniform Interface impossible
    * makes the creation of new clients much harder
  
* **Uniform Interface**: "Client and Server share a common Technical Interface"

  * The contract between client and server have to be well defined.

  * 4 guiding principles:

    * Individual Resources are identified in the Request (URI/URL)

      * `GET /cars/12345/`
      * `GET /cars/67890`
      * `GET /vacations/21/reviews`

    * Representation of the Resources

      * Client receives the representation of the resource

        * ```json
          {
          	"VIN": 12345,
              "Make": "BMW",
              "Model": "X5",
              "Year": 2015
          }
          ```

      * Client receives the representation of the resource

        * `DELETE /car/12345`

    * Self descriptive messages - metadata

      * For example, the HTTP headers `Accept`, `Content-Type`, `Host` and the status code.

    * Server sends hydermedia [(HATEAOS)](08 Advanced Topics.md#HateOAS)

* **Statelessness**: Client must manage its own state thus making the server stateless

  * it means:
    * server don't have session data
    * server treats each request as independent
    * server receives all session data from client on each request.
      * it increases the chattiness, that can lead to performance impact. It can be minimized by caching

  * it makes easier to backend scaly horizontally.

* **Caching**: "Use Caching to achieve higher Scalability and Performance"

  * Cache counter balances the negative effect of Statelessness
  * We can use cache in:
    * Database
    * Server
    * Client: "Server should specify Cache-Control Directives in responses to control Caching behavior" (see [HTTP cache headers](../../HTTP headers.md))
      * For example, for stock prices, that isn't cacheable, the server must include on response that it isn't cacheable 

    * Proxies and Gateways

* **Layered**: The server should be layered, and each layer should be independently manageable

* **Code on Demand **(optional): the server can not only send data to the client, but also code to be executed by the client.

You can measure the RESTfulness using Richardson Maturity Model (RMM) of your HTTP API

* There is 4 levels, that begins with 0 (lowest level of REST compliance) and ends with 3 (highest level of REST compliance)
