# Proxy and Reverse Proxy

* A proxy is a server that makes requests on your behalf.
  * The layer 7 proxy can optionally put headers `X-Forwarded-For` to identify the client.
  * The main use cases are:
    * Caching
    * Anonymity
    * Logging
    * Block Sites
    * Micro services
* A reverse proxy is a server that forward the requests to another servers.
  * The main use cases are:
    * Caching
    * load balancer
    * Ingress
    * Canary Deployment
    * Microservices