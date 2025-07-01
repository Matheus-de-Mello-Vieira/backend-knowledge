# Layer 4 vs Layer 7 Load balancers

* Most said here can apply to any type of reverse proxy.
  * Load balancers is a kind of reverse proxy

## Layer 4

a Layer 4 load have many modes:

* **direct-route**:  The load balancer keeps a permanent one TCP connection with each server. When the client establishment a connection with load-balancer, it forward all its segments to one, and only one, of those connections .
  * one permanent connection can handle only one client.
* **nat-mode**:  Uses only one TCP connection, because the load-balancer only readdresses and relays the segments.
  * the loadbalance uses a table that relate the connection with the both ends, so one connection uses one, and only one, server.
  * some reverse proxies uses buffers to take advantaged of the difference between the external MTU and internal MTU.

### Pros:

* Simpler load balancing
* Efficient (no data lookup): it only looks at IP and port, and something it buffers the data
* Mode secure
* Works with any protocol
* If nat-mode, one TCP connection

### Cons

* No smart load balancing
  * the only trick you can play in config the load balancer to listen multiple ports, and configure the destination acording to it,.
* NA microservices
* Sticky per connection
* No caching
* Protocol unaware (can be dangerous) bypass rules.

## Layer 7

* When a client connections to a L7 Load balancer, it becomes protocol specific.
  * any logical "request" will be forwarded to a new backend server. This could be one or more segments.
    * it means that the load balancer have to store all segments, parse the request and so forward it to the backend.
* So layer 7 load balancers can downgrade to a layer 4 one because a upgrade header, for example, to handle websockets.
* the loadbalancer have to decrypt the data, so the certificate have to be there.

### Pros

* Smart load balacing
* Caching
* Great for microservices
* API Gateway logic
* Authentication

### Cons

* Expensive (looks at data)
* Decrypts (terminates TLS)
* Two TCP connections
* Must share TLS certificate
* Needs to buffer
* Needs to understand protocol, for example nginx and postgres.
