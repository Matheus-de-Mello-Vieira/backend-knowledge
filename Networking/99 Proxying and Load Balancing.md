# Proxying and Load Balancing

## Proxy vs Reverse Proxy

### (forward) Proxy

At its core, a proxy acts as an intermediary server that intercepts and makes network requests on behalf of a client. By sitting between the user and the destination server, it can control, modify, or observe the traffic passing through it.

Here are the most common use cases for a proxy:

- **Caching:** Storing frequently requested content (like images or web pages) locally on the proxy to speed up response times and reduce the load on the backend servers.
- **Anonymity:** Hiding the client's original IP address from the destination server to protect user privacy and secure their identity.
- **Logging and Auditing:** Capturing detailed records of all outgoing and incoming network traffic for security monitoring, debugging, and compliance.
- **Site Blocking and Filtering:** Intercepting requests to restrict access to specific websites or malicious content based on organizational policies.
- **Access Mediation:** Managing, routing, and securing communication between internal microservices or when connecting to external, third-party APIs.

**Handling Client Identity at Layer 7**
Because a proxy makes requests on the client's behalf, the destination server usually only sees the proxy's IP address. However, when operating at the application layer (Layer 7), a proxy can read and modify HTTP traffic. To solve the identity problem, a Layer 7 proxy will often inject specific HTTP headers—most notably `X-Forwarded-For`. This passes the original client's IP address down the chain, ensuring the backend server still knows exactly who initiated the request.

### Reverse proxy

While a standard proxy (forward proxy) sits in front of clients to route their outgoing traffic, a **reverse proxy** sits in front of backend servers to manage incoming traffic. It acts as the public face of your application, intercepting all client requests and forwarding them internally to the appropriate backend systems. This completely hides your internal architecture from the public internet, adding a crucial layer of security and control.

Here are the most common use cases for a reverse proxy:

- **Caching:** Storing static assets or frequently accessed dynamic content. If a request comes in for a cached resource, the reverse proxy serves it directly, significantly reducing the burden on your backend servers and speeding up response times for the user.
- **Load Balancing:** Evenly distributing incoming network traffic across a pool of backend servers. This ensures that no single machine becomes overwhelmed, maximizing application uptime and overall reliability.
- **Ingress and Security:** Acting as the single, fortified entry point into a private network. A reverse proxy often handles CPU-intensive tasks like SSL/TLS encryption termination, filters out malicious requests, and protects backend servers from direct exposure to DDoS attacks.
- **Canary Deployments:** Facilitating safe release strategies by intelligently routing a small, controlled percentage of user traffic to a newly deployed version of a service, while keeping the majority of traffic on the stable version.
- **Microservice Routing (API Gateway):** Inspecting incoming requests and directing them to different internal microservices based on URL paths, headers, or domains (for example, seamlessly routing traffic for `/api/users` to the User Service and `/api/billing` to the Billing Service).

#### Relationship with Load Balancers

It is important to note that load balancers are a specific, specialized type of reverse proxy. While a standard reverse proxy might sit in front of just one server simply to handle SSL encryption and caching, a load balancer is explicitly designed to take that incoming proxied traffic and distribute it across _multiple_ backend instances.

#### Relationship with API Gateways

Much like load balancers, an API Gateway is a specialized, highly intelligent evolution of a reverse proxy. While a standard reverse proxy primarily focuses on routing traffic, hiding backend servers, or providing caching, an API Gateway operates with a deep understanding of your application's specific logic and APIs.

It sits between external clients and your internal microservices, acting as a centralized control plane. Instead of just blindly forwarding requests, an API Gateway handles complex, cross-cutting concerns such as user authentication, rate limiting, request throttling, payload transformation, and API versioning.

## Traffic Distribution Without a Dedicated Load Balancer

A dedicated reverse proxy is not the only place where traffic can be distributed. Endpoint selection can happen before a connection reaches the server pool, either in the client or in the network's routing layer.

### Client-Side Selection

Client-side load balancing gives the client a set of service endpoints and makes the client responsible for selecting one before opening a connection. The endpoint set can come from different discovery mechanisms:

- **Service registry:** A registry such as ZooKeeper stores the available instance addresses so clients can discover them.
- **Multi-address DNS:** One DNS name resolves to several addresses, and the client selects or attempts one of the returned addresses.

A client that measures endpoint latency can prefer a lower-latency address, producing location-aware distribution when network latency corresponds to proximity.

### Routing-Based Selection

[Anycast routing](02%20Protocols/03%20Internet%20Protocol.md#Anycast%20Routing) exposes one IP address from multiple network locations. The routing system selects a path before the connection reaches a service instance, so the client does not need the address of every location.

## Layer 4 vs Layer 7 Load Balancers

When configuring your network architecture, it is important to remember that these routing trade-offs apply to reverse proxies in general, not just dedicated load balancers. The decision fundamentally comes down to choosing between raw speed and routing intelligence:

- **Layer 4:** Use this when you want simple, efficient, and application-level-protocol-agnostic traffic distribution.
- **Layer 7:** Use this when you need intelligent routing and policy decisions based on application data, making it the standard for HTTP-based systems, APIs, and microservice platforms.

### Layer 4 Load Balancing

Layer 4 load balancers route traffic by evaluating transport-level metadata, such as IP addresses and port numbers. Because they do not decrypt the payload or parse application data (like HTTP headers), they offer incredibly high throughput and extremely low latency.

#### Common Operational Modes

##### Direct Connection Proxying (Direct Route)

In this implementation, the load balancer acts as a high-speed intermediary that maintains persistent, long-lived TCP connections with the backend server pool.

- **Segment Forwarding:** When a client initiates a connection, the balancer maps that session to an existing backend connection. All subsequent segments for that client are seamlessly forwarded through the same pipe.
- **1:1 Mapping:** To maintain state and performance, one backend connection is effectively dedicated to serving one active client connection at a time.
- **Efficiency:** This architecture significantly reduces the latency and computational overhead of constant TCP handshakes between the balancer and the backend servers.

##### Network Address Translation (NAT Mode)

In NAT mode, the load balancer functions by intercepting and readdressing packets at the IP layer rather than proxying the connection entirely.

- **Header Manipulation:** The balancer modifies the destination IP of incoming packets to match a specific backend server (DNAT) and translates the source IP back to the balancer's IP when the server responds (SNAT).
- **Connection Tracking:** It maintains a detailed state table to track these mappings, ensuring that all packets belonging to a specific client session are consistently routed to the correct backend.
- **Buffering:** Certain reverse proxies utilize buffering to reconcile Maximum Transmission Unit (MTU) discrepancies between external and internal networks, ensuring optimal packet sizing for each environment.

#### Layer 4 Trade-Offs

##### Layer 4 Advantages

- **Simpler & Highly Efficient:** Routing decisions are incredibly fast and computationally inexpensive because they only rely on basic IP and port metadata.
- **Protocol-Agnostic:** Capable of handling a wide variety of transport protocols effortlessly, without needing to understand the underlying application data.
- **Streamlined Paths:** In NAT mode, the architecture can preserve a single, direct TCP connection path.

##### Layer 4 Limitations

- **Lacks Smart Routing:** Cannot perform request-aware load balancing, meaning it cannot route traffic based on URL paths, HTTP headers, or cookies.
- **Weak for Microservices:** Not well-suited for modern, API-driven architectures that require intelligent routing based on application-layer context.
- **Sticky Per Connection:** Traffic distribution is tied to the TCP connection, not individual requests. If one client sends a massive number of requests over a single long-lived connection, it can unevenly overload a single backend server.
- **No Application Caching:** Cannot cache responses, read payloads, or modify application data.
- **Bypasses Higher-Layer Rules:** Protocol-unaware forwarding means application-layer security policies or business logic rules cannot be enforced at the balancer level.

### Layer 7 Load Balancing

Unlike Layer 4, a Layer 7 load balancer is highly protocol-aware. It explicitly understands application-layer protocols, most commonly HTTP. Because a single logical request at this layer may span one or multiple network segments, the load balancer must actively buffer and parse the incoming data to make sense of it before forwarding it along.

**Because it understands the protocol, it can:**

- **Perform Intelligent Routing:** Direct traffic based on specific application data like URL paths, HTTP methods, headers, cookies, or hostnames.
- **Handle Protocol Upgrades:** It can manage connections that start as HTTP and upgrade to other protocols, sometimes downgrading into more transport-like forwarding (such as with WebSockets).
- **Manage TLS Termination:** It usually sits at the edge and terminates TLS connections. This means the SSL/TLS certificate resides on the load balancer, which takes on the computational work of decrypting incoming requests before sending them to the backend.

#### Layer 7 Trade-Offs

##### Layer 7 Advantages

- **Smart Load Balancing:** Distributes traffic based on the actual content and context of the request, preventing uneven loads on backend servers.
- **Application-Layer Caching:** Can cache HTTP responses directly at the proxy to reduce backend load and speed up delivery.
- **Microservice Alignment:** An exceptionally strong fit for modern microservice architectures, allowing for precise API routing.
- **Advanced Logic:** Enables API gateway capabilities, including centralized authentication, rate limiting, and policy enforcement.

##### Layer 7 Limitations

- **Computationally Expensive:** Inspecting, buffering, and parsing application data consumes significantly more CPU and memory than simple IP/port routing.
- **Dual TCP Connections:** It typically requires maintaining two separate TCP connections per request—one between the client and the balancer, and another between the balancer and the backend server.
- **Certificate Management:** Terminating TLS requires actively managing, storing, and rotating certificates on the load balancer itself.
- **Mandatory Buffering:** It must hold data in memory to read full headers or payloads before it can make a routing decision, which can slightly increase latency.
- **Protocol Dependency:** It strictly needs to understand the specific application protocol it is proxying; it cannot easily route custom or unrecognized application protocols.

## Load Balancer Algorithms

Having a load balancer in place is only half the battle; the other half is determining exactly _how_ it should distribute incoming traffic across your backend infrastructure. This decision-making process is governed by a **load balancing algorithm**.

- **Round Robin:** The simplest and most widely used algorithm. It distributes incoming requests sequentially across the pool of available servers in a repeating cycle (Server A, then Server B, then Server C, and back to Server A). It assumes all servers have equal capacity and processing power.
- **Weighted Round Robin:** A variation of Round Robin designed for server pools with different hardware capabilities. Administrators assign a "weight" to each server based on its processing power. A server with double the weight will receive twice as many sequential requests as a lower-weighted server.
- **Least Connections:** This algorithm routes new requests to the server with the fewest active, concurrent connections at that exact moment. It is highly effective for traffic with long-lived connections (like WebSockets or heavy database queries) where a simple Round Robin might accidentally overload a server that is stuck processing complex tasks.
- **Weighted Least Connections:** Similar to Weighted Round Robin, this combines the Least Connections logic with pre-assigned server capacities. It routes traffic to the server that has the lowest ratio of active connections to its assigned weight.
- **IP Hash (or Source IP Hash):** This algorithm generates a unique cryptographic hash based on the client's source IP address (and sometimes the destination IP). The resulting hash key dictates which backend server receives the request. This ensures that a specific user is consistently routed to the exact same server every time, which is crucial for maintaining session state or "sticky sessions."
- **Least Response Time (or Least Latency):** A highly dynamic algorithm that actively monitors both the number of active connections and the average response time of each server. It routes the next request to the server that is currently responding the fastest and has the fewest active connections, ensuring optimal performance from the user's perspective.
- **Random:** As the name implies, this simply routes incoming requests to a random server in the pool. While it sounds chaotic, it can actually perform quite well in massive clusters where all servers have identical capacity and the sheer volume of traffic naturally distributes the load evenly over time.

### Adaptive Load Balancing

**Adaptive (or Resource-Based) Load Balancing** is one of the smartest—and most complex—routing strategies. Instead of just looking at external network metrics like active connection counts or response times, an adaptive algorithm actually looks _inside_ the backend servers to make its decisions.

Here is how it works and why it matters:

- **Real-Time Metric Polling:** The load balancer continuously queries a health endpoint or an agent installed on each backend server to gather real-time data on its actual resource utilization. This includes metrics like CPU load, available memory (RAM), disk I/O, or thread pool queues.
- **Intelligent Routing:** When a new request comes in, the load balancer evaluates these metrics and dynamically routes the traffic to the server with the most available processing capacity at that exact fraction of a second.
- **The Use Case:** This algorithm is incredibly powerful for applications where the "weight" of a request is highly unpredictable. For example, if Server A receives a request that requires massive, CPU-heavy video transcoding, a "Least Connections" algorithm might still send it traffic because it only has one active connection. An Adaptive algorithm, however, will see that Server A's CPU is pegged at 99% and smartly route all new traffic to Server B until Server A finishes its heavy task.
