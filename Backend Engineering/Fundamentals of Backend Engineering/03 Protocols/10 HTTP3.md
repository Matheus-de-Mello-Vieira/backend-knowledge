# HTTP/3 

* HTTP over QUIC
  * QUIC is a transport protocol like TCP and UDP, but it runs over UDP.
* implements the streams of HTTP2, but over QUIC instead of TCP
  * both HTTP/v2 and TCP have congestion and flow control, leading to competition.

## Streams

On HTTP/2. because it runs over TCP, if a single segment of one request is lost, the server can't process any subsequent segment, affecting other HTTP requests.

On other hand, HTTP/3 controls the transport layer through QUIP. Effectively, if a data segment get lost, only its requests will be affected.

* The HTTP/3 even keeps the successful datagrams of the very failed request, requesting only the lost datagrams again.

## Pros and Cons

### Pros

* QUIC has many other benefits
* Merges Connection setup + TLS in one handshake
* Has congestion control at stream level
* Connection migration
  * every datagram is labeled with `connectionID`
  * it allows you change the IP of client and keep the connection alive.
    * ex.: chage wifi to 5G

### Cons

* takes a lot of CPU, due to parsing logic (same of HTTP2)
* UDP could be blocked on firewalls.
* IP Fragmentations is the enemy
  * IP Fragmentation is disabled by default.
* connection hijacking
  * `connectionID` is plain text, so a attacker can send own data with that value
