# HTTP/v2

On HTTP/v1.1, a connection can handle only one request per time, because pipeline almost isn't used.

* To execute multiple requests in parallel, the client need to create multiple connections.

On the other hand, on HTTP/v2, a connection can handle multiple request in parallel. Each one is called a "stream".

* Every request is tagged with a unique stream ID
  * for instance `stream1` or `stream3`, the clients picks odd number and the server picks even numbers.
  * the servers can process in concurrency and respond in any order.

## HTTP/v2 with push

It is legacy, was discontinued

The client requests only `GET /index.html`, and the server assumes that the client needs a lot more information, so it responds not only with `index.html`, but also with `Main.css`, `Main.js`, `img.jpg`, etc.

* Many clients can't handle it, because they expect only one response

## Pros and Cons

* Pros

  * Multiplexing over Single Connection (save resources)

  * Compression (Headers & Data)

  * Server Push

  * Secure by default
    * it uses TLS
* Cons

  * TCP head of line blocking
    * As we are multiplexing multiple requests into one connection, at the TCP level, if a single segment of one request is lost, the server can't process any subsequent segment, affecting other HTTP requests.
  * Server push never picked up
  * High CPU usage
    * the server and client need to parse multiple requests from the connection.
      * at HTTP/v1.1, we need only look when the request starts and end
      * at HTTP/v2.2 we need to care about stream headers, and the the connection intercalates different streams, so it is a lot more work.

## When use HTTPv2

* HTTP/v2 heavier, but process multiple requests in parallel time a lot better.
* The HTTP/v2.2 was designed for scenarios when the client makes a lot requests at same time
  * if it isn't your case, or you can make it don't be your case, you can avoid HTTP/v2 altogether