# Backend Communication Design Patterns

## Request-Response Model

* Client sends a request.
* Server parses the request.
  * Parsing is not cheap.
  * Data arrives as a stream, so the server must identify where each request begins and ends.
* Server processes the request.
  * Serialization belongs here.
  * XML is usually more expensive to parse than JSON, which is usually more expensive than Protocol Buffers.
* Server sends a response.
* Client parses and consumes the response.

### Where it is used

* Web and HTTP.
* DNS.
  * DNS commonly uses UDP.
  * The client sends a request with a query ID and matches the response by that ID.
* SSH.
* RPC.
  * RPC made remote calls feel like local calls, but that abstraction can hide latency and failure costs.
* SQL and database protocols.
* APIs such as REST, SOAP, and GraphQL.
  * GraphQL bundles multiple data requirements into one client-facing request, even if the backend still fans out internally.

### Anatomy of a request and response

A request structure is defined by the protocol and message format used by both client and server.

```text
GET / HTTP/1.1
Headers
<CRLF>
Body
```

`CRLF` means carriage return plus line feed, written as `\r\n`.

* Each protocol line ends with `CRLF`.
* A blank line marks the end of headers and the beginning of the body.

Example:

```text
GET / HTTP/1.1\r\n
Host: example.com\r\n
User-Agent: curl/7.64.1\r\n
\r\n
<optional body>
```

### Large payloads

There are two common approaches:

* Simple upload.
  * Send the whole payload in one request.
  * Easier, but harder to resume after failure.
* Resumable upload.
  * Chunk the payload and send it in pieces.
  * More complex, but more robust.

### Where request-response is a bad fit

* Notification systems.
  * The server knows when the event happens, not the client.
* Chat systems.
  * Polling creates too much traffic.
* Very long-running requests.
  * Keeping the connection open for too long wastes resources and complicates failure handling.

## Synchronous vs Asynchronous Workloads

### Synchronous

In synchronous communication, the caller waits for the receiver to finish.

* The caller keeps the connection or execution flow open.
* While waiting, the caller may be idle.

Example of synchronous OS I/O:

* Program asks the OS to read from disk.
* The main thread is blocked.
* The kernel schedules something else meanwhile.
* When the read completes, the program resumes.

### Asynchronous

In asynchronous communication, the caller does not need to stay blocked while the work completes.

* Caller sends a request.
* Caller continues doing other work.
* The result may arrive later through polling, callbacks, futures, or another event mechanism.

Example of asynchronous execution in Node.js:

```javascript
doWork();
readFile("largefile.dat", onReadFinished);
doWork2();
// later: onReadFinished(theFile)
```

### Important distinction

Synchronicity is mostly a caller-side property:

* Can the caller continue to work while waiting?

A system can mix both styles:

* A client makes an asynchronous request to start a job.
* The overall business workflow still behaves synchronously if the user keeps polling for the result.

### Where asynchronous workloads show up

* Asynchronous programming with promises and futures.
* Backend job queues.
* Asynchronous commits in databases.
* Asynchronous replication.
* OS-level buffering and delayed flushes.

## Push

Push solves cases where the server knows when data should be delivered.

* Client connects to the server.
* Server sends data to the client when needed.
* Client does not need to keep asking.

This usually requires a bidirectional transport, even if the data flow is primarily server-to-client.

Examples:

* Real-time notifications.
* Chat.
* Brokers such as RabbitMQ.

### Pros

* Real time.
* Server can send data immediately when events happen.

### Cons

* Clients must stay online.
* Slow clients can be overrun.
* Requires a transport that supports this model well.

For transport-level examples, pair this with [Networking/02 Protocols/08 WebSockets](../../../Networking/02%20Protocols/08%20WebSockets.md).

## Short Polling

Short polling is useful when work takes time and the client checks back repeatedly.

* Client sends a request.
* Server immediately returns a handle such as a job ID.
* Server keeps processing.
* Client sends repeated status requests.

### Pros

* Simple.
* Good for long-running tasks.
* Client can disconnect between polls.

### Cons

* Too chatty.
* Most polls do not bring useful information.
* Wastes backend and network resources.

## Long Polling

Long polling reduces the chattiness of short polling.

* Client sends a request.
* Server waits before responding.
* The server returns only when data is ready or a timeout is reached.
* Client then issues the next long-poll request.

Kafka-style consumers are a common example:

* Client asks for messages.
* Broker holds the request open until a message arrives or a timeout expires.

### Pros

* Less chatty than short polling.
* More backend-friendly.
* Client can still disconnect and retry.

### Cons

* Not guaranteed real time.
* It only feels real time if a poll is already open when the event arrives.

## Server-Sent Events

Server-Sent Events keep one request open and stream multiple logical events back in the response.

* Client sends one request.
* Server starts a response.
* Server writes event messages over time.
* Server intentionally does not finish the response.

This stays inside the HTTP request-response model.

### Pros

* Real time for server-to-client delivery.
* HTTP-compatible.

### Cons

* Client must remain connected.
* Slow clients can still be a problem.
* Browser limits on open HTTP/1.1 connections can constrain usage.

SSE works particularly well with HTTP/2, so this also connects to:

* [Networking/02 Protocols/07 HTTP1.1](../../../Networking/02%20Protocols/07%20HTTP1.1.md)
* [Networking/02 Protocols/09 HTTP2](../../../Networking/02%20Protocols/09%20HTTP2.md)

## Publish-Subscribe

Publish-subscribe solves the problem of too many services talking to each other directly.

Without a broker:

* Services form a communication mesh.
* Coupling grows quickly as the number of services increases.

With a broker:

* Producers publish events.
* Consumers subscribe to the topics or queues they need.
* Services do not need to know about each other directly.

### Pros

* Scales well for multiple receivers.
* Good for microservices.
* Looser coupling.
* Works even when consumers are temporarily offline, depending on the broker.

### Cons

* Delivery guarantees are complex.
* Adds operational and conceptual complexity.
* Broker traffic can become a bottleneck.

## Multiplexing vs Demultiplexing

### Multiplexing

Multiplexing combines multiple logical streams into one shared channel.

Examples:

* Browsers using one HTTP/2 connection for multiple requests.
* Reverse proxies aggregating many HTTP/1.1 client connections into fewer upstream HTTP/2 connections.

### Demultiplexing

Demultiplexing is the reverse:

* One shared channel is split into multiple downstream operations or connections.

Examples:

* Reverse proxies splitting one HTTP/2 connection into multiple HTTP/1.1 requests.

### Trade-offs

* HTTP/1.1 gives each request separate connection-level behavior.
* HTTP/2 reduces connection overhead but introduces mutual dependence inside one shared connection and more parsing complexity.

For the protocol side of this, see:

* [Networking/02 Protocols/07 HTTP1.1](../../../Networking/02%20Protocols/07%20HTTP1.1.md)
* [Networking/02 Protocols/09 HTTP2](../../../Networking/02%20Protocols/09%20HTTP2.md)

### Connection pooling

Connection pooling is a related backend optimization:

* The backend keeps a pool of open database connections.
* Requests reuse them instead of opening a new one each time.
* If no connection is idle, work waits until one becomes available.

## Stateless vs Stateful

### Stateful

* The service stores client-related state in memory.
* It depends on that state continuing to exist.

### Stateless

* The client or another durable system carries the state.
* The backend may cache data, but it can safely lose it and continue.

### What makes a backend stateless

A backend can still use a database and remain stateless at the application tier.

Useful test:

* Can you restart the backend during idle time and have client workflows still work correctly?

If yes, the backend tier is likely stateless.

### Protocols can also be stateful or stateless

* TCP is stateful.
  * It tracks sequence numbers, acknowledgments, and connection state.
* UDP is stateless.
  * The application must match requests and responses itself, such as DNS with query IDs.

You can still build:

* A stateless protocol on top of a stateful transport, such as HTTP over TCP.
* A stateful protocol on top of a stateless transport, such as QUIC over UDP.

Relevant protocol references:

* [Networking/02 Protocols/04 UDP](../../../Networking/02%20Protocols/04%20UDP.md)
* [Networking/02 Protocols/05 TCP](../../../Networking/02%20Protocols/05%20TCP.md)

### Completely stateless systems

These are rare.

Examples:

* A pure computation service such as checking whether a number is prime.
* JWT-based flows where the token carries most of the session context.

## Sidecar Pattern

The sidecar pattern solves protocol and client-library complexity by moving advanced communication behavior into a colocated proxy.

### What it solves

* Every protocol needs libraries on both sides.
* Application code becomes dependent on those libraries.
* Library upgrades are costly to retest.
* Polyglot microservices suffer from duplicated transport concerns.

### What it is

* A proxy sits beside the application.
* The application uses a thin, simple interface.
* The sidecar handles richer transport concerns.
* Client and server sidecars talk to each other using the advanced protocol.

This lets you upgrade the transport without changing application code on both sides.

### Examples

* Service mesh proxies.
* Sidecar containers.
* Envoy, Linkerd, and Istio-style deployments.

### Pros

* Language agnostic.
* Easier protocol upgrades.
* Security improvements can happen in the proxy layer.
* Better tracing and monitoring.
* Shared service discovery.
* Optional caching.

### Cons

* More complexity.
* Extra latency due to additional hops.
