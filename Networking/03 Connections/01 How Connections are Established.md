# How connections are Established

* on TCP perspective:
    * Client →Server: `SYN`
    * Server → Client: `SYN-ACK`
    * Client → Server: `ACK`
* But at a backend perspective:
    * Server Listens on an `address:port`
        * your computer have many Internet interfaces, and every one have it's own IP address
            * always specify the address, because if you only listen to `0.0.0.0`, you will be listen on all of the Internet interfaces, that can jeopardize the performance and security.
                * it can expose your API to the public access, because you a listen through the IP address.
            * The IP that you listen is the IP that represents you on the network
    * Kernel does the handshake creating a connection
    * Backend process "accepts" the connection, moving it from kernel to the backend process.

## Connection Establishment

Kernel creates a socket and two queue `SYN` and Accept

* socket: a unique identifier
    * connections are instances of a socket
    * one socket can have multiple connections
        * a connection is just a file descriptor - and the overhead for its upkeep.
    * think sockets as ways that connections can pass through.
    * Informally, "socket" and "connection" are sometimes used interchangeably, though they have distinct technical meanings.
    * You get a connection from a socket
* When a physical bytes arrives on your computer:
    * The network interface handles Layer 2, receiving all frames addressed to its MAC address and forwarding them to the operating system.
        * Most network interfaces handle this in hardware through a [NIC](../02%20Network%20Components.md#The%20Network%20Interface%20Card%20%28NIC%29), and smart NICs with reprogrammable firmware can offload work from the CPU.
    * The OS handles the layer 3, parsing the IPs and forwarning it to the Kernel
    * The Kernel handles the layer 4, distributing it along with the listening processes according to the ports.

* When working with computer with many CPUs cores, as 48, some people allocates dedicated cores just for networking.

The process is:

1) When client sends a `SYN` → the Kernel add to `SYN` queue, replies the client with `SYN-ACK`.
2) When the client sends a `ACK` → Kernel finish the connection
3) Kernel removes `SYN` from `SYN` queue
4) Kernel adds full connection to Accept queue
5) The backend accepts a connection, removed from accept queue
   * If the backend calls `accept` and there is no connection, it is blocked. So you should call it asynchronously.
   * if the accept queue is full (because backend accept connection slower than Kernel put them on the queue), the `SYN` queue also will eventually get full, so connections won't be accepted.
     * It is the number one problem that reverse proxies try to solve, they try to accept connections as faster as possible
       * mainly if you are on the edge, as API gateway, that is the most important thing
6) A file descriptor is created for the connection, that uniquely identifies the connection.

### Problems with accepting connections

* Backend doesn't accept fast enough
    * If the backend accept rate is slower than the kernel enqueuing rate, then the accept queue will eventually get full, then the SYN queue will also eventually get full, and then the kernel will stop sending SYN-ACK, so any new attempts to establish new connections will be frustrated
* Client who don't `ACK`
* Small backlog

### SYN flood

A SYN flood is a denial-of-service attack that abuses the TCP handshake. The attacker sends many `SYN` packets but does not finish the handshake with the final `ACK`, forcing the server or firewall to keep half-open connection state until the `SYN` queue or state table is exhausted.

Modern [Firewall Technologies](../../Security/05%20Architecture%20and%20Infrastructure%20Security/Network%20Security/Firewall%20Technologies.md#Fourth%20Generation%20and%20Beyond:%20Next-Generation%20Firewalls%20%28NGFW%29%20%282000s%20to%20Present%29) can mitigate SYN floods with techniques like SYN proxying, SYN cookies, and hardware acceleration.
