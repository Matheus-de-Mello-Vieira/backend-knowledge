# Horizontally Scaling NGINX

Every connection consumes resources in an NGINX instance. When traffic exceeds the instance's connection, CPU, or memory capacity, the instance becomes a bottleneck. Horizontal scaling adds NGINX instances, but each instance introduces another network address, so traffic must be distributed across the resulting endpoints.

## Client-Side Traffic Distribution

Client-side load balancing exposes the available NGINX addresses to clients and makes each client responsible for selecting an endpoint.

- **Service discovery:** Systems built on a registry such as ZooKeeper use this pattern by allowing clients to discover the current instance addresses.
- **Multi-address DNS:** One DNS name can resolve to the addresses of several NGINX instances. The resolver returns the address set, and the client selects or attempts one of those addresses.

A client that measures endpoint latency can prefer a lower-latency address, producing location-aware distribution when network latency corresponds to proximity.

## Anycast Routing

Anycast makes multiple NGINX deployments reachable through the same public IP address. The networks hosting those deployments advertise routes for the same address, and Internet routing selects one advertisement according to its routing policies and path information.

Clients therefore connect to one shared address rather than discovering every NGINX instance. The selected destination is the routing system's preferred path, which is not necessarily the geographically closest or lowest-latency instance.
