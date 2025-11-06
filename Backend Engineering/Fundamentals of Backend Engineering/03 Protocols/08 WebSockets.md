# Web Sockets

* Bidirectional communication designed to web
* TCP is also bidirectional, but unsafe
* Websocket stay on top of HTTP, can you can bypass to a TCP connection
* The HTTP1.1 keep a connection alive for many requests, so it create the opportunity to create web sockets.
* It begins with a WebSocket handshake, allowing both ends to send messages to each other without waiting for a response from the other side.

## Handshake

1) One side send a request HTTP1.1 GET with the headers `Upgrade: websocket` and `Sec-WebSocket-Key` as passport 
2) The response is also HTTP1.1, with status code 101 (Switching protocol), also with the header `Upgrade: websocket`.
3) now both sides agree that it isn't HTTP anymore, and now it is web socket

## Use cases

* Chatting
* Live feed
* Multiplayer gaming
* Showing client progress/logging

### Pros and Cons

* Pros
  * Full-duplex (no polling)
  * HTTP compatible
    * Firewall friendly
* Cons
  * Proxying is tricky: the proxy have the intermediate two websocket connections
    * Layer 7 load balancer challenging (timeouts)
      * intermediates   can simply drop the knowledge about the connection
      * we have to make a ping-pong to keep the connection up.
    * Stateful, difficult to horizontally scale.

### When use websockets?

* Rule of thumb: do you absolutely need bidirectional communication?
* before think websockets, think long polling or Server Sent Events