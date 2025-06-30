# Architecture

## Definitions

* **listener** is the thread or process that calls the `listen` and passing the port and address, gets back the socket ID.
* **acceptor**: is however have a access to the socket ID and calls `accept` on it, to get back file descriptor pointing to the connection.
* **worker**: responsible to read or write the data

A single thread can do these tree jobs, but you can split then strategically.

## Single listerner/Single Worker Thread

* Node.JS is one of them
  * you can spawn multiple nodes, each one in a separated process with a single thread each.
  * One single thread that is the listener, the acceptor, and the reader.
  * If you have many connections, that single thread can get overloaded.

## Single listener/multiple worker threads

* Memcached is one example of them

  * We have a single process with fixed number of threads
    * the process is the listener and accepter
      * in memcached, it is a infinite loop that keep accepting.
    * Each thread handles a set of connections.
      * the main process is responsible to load balance them, however it is tricky because the workload and duration of a connection can vary a lot.

* RAMCloud is another example of them, but know with loadbalancing

  * > RAMCloud is a new class of super-high-speed storage for large-scale datacenter applications. It is designed for applications in which a large number of servers in a datacenter need low-latency access to a large durable datastore.

  * The process is the listener, acceptor and reader, and offload the requests to the threads

    * the process will decrypt, parse, etc.
    * the problem is that that single process can be overloaded.
      * you can spawn multiple instances of RAMCloud, 
    * unlike the Memcached, whose threads gets files descriptions of connections.
      * so there is fairer load balancing.

## Multiple Threads single socket

* Nginx is a example of it (need configuration)
  * it used to be default, but no more.
* one single listener on the main worker process, and many threads
  * every thread have access to the socket object, because they a children of the main processing.
  * every thread try to accept from the same socket, with a complex system of lock to avoid two of them accept at same time
  * once a thread accepts a connection, it owns it.

## Multiple Listeners on the same port and address

* The OS will create SYN and accept queues for each process (or threads), and will distribute the connection between them.
  * So you can spawn multiple threads that handles with everything, and none of them will step on someone else's toes. 
* it is default in almost all proxies, including Nginx.
* You need to enable `SO_REUSEPORT` to set that configuration
* The problems are:
  * the load balancing can be unfair, because the workload that each connection will demand isn't considered by the OS.
  * working with QUIC, as it is UDP, the OS can distribute the datagrams of the same layer-7 request along with many listeners.
  * port hijack: if a foreign process starts to listen on the port, some load will be headed to there.
    * The SO usually use a key system to avoid it.