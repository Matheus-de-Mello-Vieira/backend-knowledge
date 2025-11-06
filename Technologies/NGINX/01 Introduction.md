# Introduction

* NGINX is a open source web server written in C, also can be used as a reserve proxy and load-balancer.

We will talk about:

* What is Nginx
* Current and Desired Architecture
* Layer 4 and Layer 7 Proxying in Nginx
* TLS Termination vs TLS Passthough
* Timeouts in NGINX
* Example
  * Nginx as a Web Server, Layer 7 and Layer 4 Proxy
  * Enable HTTPS, TLS 1.3 and HTTP/2 on Nginx

## What is NGINX?

* Web server: serves web content
* Reverse Proxy
  * Load balancing
  * Backend Routing
    * Redirect a request according to layer 7 info, as the path or host.
    * it can change the request
    * Fail-over
    * Cache
    * API Gateway
* The Nginx have to parts:
  * frontend: the interfaces that handles the communications Nginx <-> clients
  * backend;  the interfaces that handles the communication Nginx <-> servers

## Layer 4 vs Layer 7 proxying

* In layer 4 we see TCP/IP stack only nothing about the app, we have access to
  * Source IP, Source IP
  * Destination IP, Destination Port
  * Simple packet inspection (SYN/TLS hello)
    * it is not default, but you can log when these events happens.
  * no cache
* In layer 7 we see the application, HTTP/gRPC etc
  * We have access to more context
  * I know where the client is going, which page they are visiting
  * Require decryption, that can be a security problem.
    * for example, CDNs decrypt the data

Nginx can operate in L4 or L7.

* Layer 4 proxying is useful when Nginx doesn't understand the protocol, for example MySQL database protocol.
  * the layer 4 are always sticky, each client connection sticks with only one backend connection.
  * use `stream` for layer 4 proxyd 
* Layer 7 proxying is useful when Nginx want to share backend connections and cache results.
  * use `http` for layer 7 proxy

## TLS Termination and TLS Pass-through

* TLS termination is someone on the middle of connection pass its own keys, pretending to be the server or client.
  * Layer 7
  * Nginx can do it, for example Nginx has TLS (e.g. HTTPs) and backend is not (http).
    * Nginx terminates TLS and decrypts and send unenctypted.
  * Nginx is TLS and backend is also TLS 
    * recommended at the cloud, because you share the same machines with many other people, so can exists a security fault on your private net.
    * Nginx terminates TLS and decrypted, optionally rewrite and then re-encrypt the content to the backend
      * additional latency.
  * Nginx needs the backend certificate or at least has its own
* TLS Pass-through
  * Layer 4
  * more secure, NGINX doesn't need the backend certificate.

## Internal Architecture

* Nginx uses worker process
  * Nginx spins up a worker process per hardware thread on auto-mode, that is default
  * the kernel sit right behind on worker process
  * the nginx tries to accept the connections as fast as possible. So one worker become its reader. [see more](../../Backend Engineering/Fundamentals of Backend Engineering/05 Backend Execution Patterns/05 Architecture.md)
    
    * you choose "Multiple Threads Multiple Acceptors Architecture" or "Multiple Threads with Socket Sharding"
      * until version 1.9.1, the default is the first one, otherwise it is the second one.
  * the workers will read the connection.
  * Ideally, each worker need to stay on the CPU maximum possible.
  * the worker takes a action, for example read a content from disk or read from upstream backend
    * at this time, the worker can exit from the CPU, because it is only waiting.
  * each worker can have thousands of clients.
