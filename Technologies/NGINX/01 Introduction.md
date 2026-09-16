# Introduction

NGINX is an open-source web server written in C. It can also act as a [reverse proxy and load balancer](../../Networking/99%20Proxying%20and%20Load%20Balancing.md).

* **Web server:** serves static content and can route HTTP requests.
* **Reverse proxy:** receives client traffic and forwards it to upstream services. It can route by host, path, headers, or other HTTP information; cache responses; and distribute traffic across backends.
* **Traffic boundary:** exposes a client-facing interface while upstream services communicate through a separate backend interface.

NGINX can proxy at Layer 4 or Layer 7:

* Use the `stream` context for TCP or UDP proxying, including protocols NGINX does not interpret, such as a database protocol.
* Use the `http` context for HTTP-aware proxying, including request routing, response caching, and TLS termination.

NGINX's [master-and-worker architecture](02%20NGINX%20Internals.md#The%20Worker%20Process%20Model) separates process control from event-driven client-connection handling.

## Scaling an NGINX Fleet

Every connection consumes resources in an NGINX instance. When traffic exceeds an instance's connection, CPU, or memory capacity, additional NGINX instances increase total capacity. Each instance is a separate network endpoint, so a distribution mechanism must select an instance before it handles a client connection.

* **[Client-side selection](../../Networking/99%20Proxying%20and%20Load%20Balancing.md#Client-Side%20Selection):** Clients discover the available NGINX addresses through a service registry or multi-address DNS and select an endpoint before connecting.
* **[Anycast routing](../../Networking/02%20Protocols/03%20Internet%20Protocol.md#Anycast%20Routing):** Multiple NGINX deployments are reachable through the same public IP address, and Internet routing selects a destination.

These mechanisms distribute client connections among NGINX deployments. They operate before NGINX applies its own reverse-proxy or upstream load-balancing configuration.
