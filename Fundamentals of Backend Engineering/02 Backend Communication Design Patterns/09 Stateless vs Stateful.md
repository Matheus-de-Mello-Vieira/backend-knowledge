# Stateless vs Stateful

* Stateful
  * Stores state about clients in its memory
  * Depends on the information being there
* Stateless
  * Client is responsible to "transfer the state" with every request
  * May store but can safely lose it

## Stateless Backends

* If the stateless backend relies on a database, the entire system is stateful.
* Stateless backends can still store data somewhere else

### What makes a backend stateless

* Stateless backends can store states somewhere else (such as databases).
* The backend remains stateless but the system is stateful
* Can you restart the backend during idle time while the client workflow continue to work? If so, your backend is stateless.

## Stateful Backend

* Sometimes you need a load balancer with stick sessions, because the season is stored at backend

## Stateless vs Stateful protocols

* The Protocols can be designed to store state
* TCP is stateful: there are information about the client and the server about the state of the connection (open, close, etc).
  * Sequences, Connection file descriptor
* UDP is stateless: it can have a file descriptor, but it is not needed. You can send multiple datagrams that are received by different servers.
  * DNS send queryID in UDP to identify queries.
    * The TCP have a connection so it is easy to identify which datagrams belongs on the same thing.  However in UDP you are responsible to do it, for example the DNS uses the queryID.
* You can build a stateless protocol on topo of a stateful one and vise versa
  * HTTP on top of TCP
    * if TCP breaks, HTTP blindly create another on
  * QUIC on top UDP

## Complete Stateless System

* really rare
* state is carries with every request
* a backend service that relies completely on the input
  * check if input param is a prime number
* JWT (JSON Web Token)
  * it is even a security problem because you can't block manually a token from a server