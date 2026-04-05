# Proxying and Load Balancing

## Proxy vs Reverse Proxy

### Proxy

A proxy is a server that makes requests on behalf of the client.

Typical uses:

* Caching
* Anonymity
* Logging
* Site blocking
* Access mediation for microservices or external services

A Layer 7 proxy can also add headers such as `X-Forwarded-For` to identify the original client.

### Reverse proxy

A reverse proxy is a server that receives requests intended for backend servers and forwards them internally.

Typical uses:

* Caching
* Load balancing
* Ingress
* Canary deployments
* Microservice routing

Load balancers are a specific kind of reverse proxy.

## Layer 4 vs Layer 7 Load Balancers

Most of the trade-offs here apply to reverse proxies in general, not just dedicated load balancers.

### Layer 4

Layer 4 load balancers route traffic by evaluating transport-level metadata—specifically source/destination IP addresses and port numbers. Because they do not decrypt or parse application data (like HTTP headers), they offer high throughput and low latency.

Common Operational Modes

1. **Direct Connection Proxying (`direct-route`)**: In this implementation, the load balancer acts as a high-speed intermediary that maintains persistent, long-lived TCP connections with the backend server pool.

  - **Segment Forwarding**: When a client initiates a connection, the balancer maps that session to an existing backend connection. All subsequent segments for that client are forwarded through the same pipe.

  - **1:1 Mapping**: To maintain state and performance, one backend connection effectively dedicated to serving one active client connection at a time.

  - **Efficiency**: This reduces the overhead of constant TCP handshakes between the balancer and the backends.

2. **Network Address Translation (`nat-mode`)**: In NAT mode, the load balancer functions by intercepting and readdressing packets at the IP layer rather than proxying the connection entirely.

   - **Header Manipulation**: The balancer modifies the destination IP of incoming packets to match a backend server (DNAT) and translates it back when the server responds (SNAT).

   - **Connection Tracking**: The balancer maintains a state table to track these mappings, ensuring that all packets belonging to a specific client session are consistently routed to the same backend.

   - **Buffering**: Certain reverse proxies utilize buffering to reconcile MTU discrepancies between external and internal networks, ensuring optimal packet sizing for each environment.

#### Pros

* Simpler load balancing
* Efficient, because it only needs IP and port metadata
* More protocol-agnostic
* Works with many protocols
* In `nat-mode`, it may preserve a single TCP connection path

#### Cons

* No smart request-aware load balancing
* Weak fit for microservice routing
* Sticky per connection
* No application-layer caching
* Protocol-unaware forwarding can bypass rules you might want at higher layers

### Layer 7

A Layer 7 load balancer is protocol-aware.

* It understands the application protocol, such as HTTP.
* A single logical request may span one or more segments.
* The balancer has to buffer and parse the incoming data before forwarding it.

Because it understands the protocol:

* It can route based on paths, methods, headers, cookies, or hostnames.
* It can sometimes downgrade into more transport-like forwarding after an upgrade, such as with WebSockets.
* It usually has to terminate TLS, which means the certificate and decryption happen on the balancer.

#### Pros

* Smart load balancing
* Caching
* Strong fit for microservices
* API gateway logic
* Authentication and policy enforcement

#### Cons

* More expensive, because it inspects and parses data
* Terminates TLS
* Usually means two TCP connections, one on each side
* Requires certificate handling on the balancer
* Needs buffering
* Needs protocol-specific understanding

## Practical summary

Use Layer 4 when you want simple, efficient, protocol-agnostic traffic distribution.

Use Layer 7 when you need routing and policy decisions based on application data, especially for HTTP-based systems, APIs, and microservice platforms.
