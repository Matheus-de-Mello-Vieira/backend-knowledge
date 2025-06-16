# HTTP/v1.1

## Client / Server

* Client: Browser, python or javascript app, or any app that makes HTTP request
* Server: HTTP Web Server, e.g. ISS, Apache Tomacat, NodeJs, Python Tornado

## HTTP Request

Five parts:

* Method: GET, POST, DELETE, etc
* PATH
  * webservers can limit it with different ways, for example by number of characters or number of bits.
* Protocol: HTTP/v1.1, HTTP/v2, HTTP/v3 
* Headers
  * One of them is "Host", with the DNS used
    * for example, if you request `http://husseinnasser.com/about`, the host is `husseinnasser.com`
    * it allows one server host multiple Web Servers
* Body

## HTTP Response

* Protocol
* Code (200, 404, 500, etc)
* Code Text ("OK", "NOT FOUND", "INTERNAL ERROR", etc)
  * yes, it is redundant, and it was removed on the HTTP/v2
* Headers
* Body

## HTTP 1.0

HTTP/v1.0 came from a time when keep a TCP connection open actually consumed a considerable amount of memory (because file descriptor). So:

* Every request you open a brand new connection.
  * Slow
  * We can't chunk the response.
  * No multi-homed websites, because there the HOST header was optional.
  * Handle the connection opening and closing consumes a lot of CPU.

## HTTP 1.1

Add the option of use the same connection for multiple requests.

* Persisted TCP connection
* Low Latency
* Low CPU: the CPU only cares to seek the start and end of each request
* Streaming with Chunked transfer
* Pipeline (disabled by default)
  * The client makes multiple requests sequentially, without waiting response
  * The server ensures that the order of response is the same of the order of requests
    * it makes the servers hold responses to maintain the correct order. It jeopardize the whole propose
    * if there a backend's proxy, we can't ensure that it will keep the same order of request as we sent.
  * You can build a request ID system
* Proxying & Multi-homed website