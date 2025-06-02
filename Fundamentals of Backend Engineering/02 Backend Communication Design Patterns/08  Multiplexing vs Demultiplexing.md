# Multiplexing vs Demultiplexing

* Multiplexing is transform many multiple signal lines into one signal line
  * in our case, imagine a service that handles multiple connections from different points and transform it into one unique request to another service.
  * Example: Google Chrome
    * In HTTP/1.1, if the user makes three requests to the server, Google Chrome will open exactly three connections. Note that it can open up to six simultaneous connections. Conversely, in HTTP/2, under the same conditions, Google Chrome will multiplex the three requests and open only one connection. 
  * Example: HTTP/2 on the Backend
    * A reverse proxy, such as Nginx, can be used to aggregate multiple HTTP/1.1 connections into one HTTP/2 connection. So, an HTTP/1.1 client can communicate with an HTTP/2 server because the reverse proxy acts as an intermediary, translating between protocols and managing multiplexing.
* Demultiplexing is the inverse of multiplexing, transform one to many
  * Example: HTTP/2 on the Backend
    * A reverse proxy, such as Nginx, can be used to split a single HTTP/2 connection into multiple HTTP/1.1 connections. So, an HTTP/2 client can communicate with an HTTP/1 server because the reverse proxy acts as an intermediary, translating between protocols and managing demultiplexing.

The advantage of having multiple HTTP/1.1 requests is that each request can have its own rules, such as timeout. On the other hand, HTTP/2 aggregates those requests, so they are mutually dependent. It also adds processing overhead to the server, as it has to parse the different requests from the same connection. 

# Connection Pooling

The user makes multiple requests to the backend. Each one results in a individual database query. Connection pooling is designed to handle this kind of load efficiently. It keeps a pool of open connections. These can be reused to serve requests in sequence instead of opening a new connection per request. When no connections are idle and a request arrives, the backend keeps that request active until one becomes available. Notice that if the user uses the same HTTP/2 connection to make multiple requests, the backend will act as a demultiplexer and transform one connection into multiple ones.



