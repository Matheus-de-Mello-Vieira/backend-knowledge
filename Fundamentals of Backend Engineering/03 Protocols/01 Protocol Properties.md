# Propotocol Properties

## What is a protocol?

* A system of rules that allows tow parties to communicate.
* A protocol is designed with a set of properties.
* Depending on the purpose of the protocol: they was made thinking about the problem of that time, so nowadays it can be not be updated.

## Properties

* Data format
  * Text based
    * plain text
    * JSON
    * XML
  * Binary
    * protobuf
    * RESP: a protocol designed specifically for Redis, that can be used for other client-server software projects
    * h2
    * h3
* Transfer mode
  * Message based: each mesage have start and end.
    * UDP
    * HTTP
  * Stream: just a stream of bytes, one after another, there is neither start or end.
    * TCP
      * as TCP is stream based and HTTP is message based, the client have to parse the stream into a message
    * WebRTC: designed for video
* Addressing: how to describe the destination and origin
  * DNS
  * IP
  * MAC
* Directionality
  * Bidirectional (TCP)
  * Unidirectional (HTTP)
  * Full/Half duplex
    * Half duplex is a communication mode where data flows in both directions, but only one direction at a time.
* State
  * Stateful (TCP, gRPC, apache thrift)
  * Stateless (UDP, HTTP)
* Routing
  * Proxies, Gateways
* Flow and Congestion control
  * TCP: Flow and Congestion
  * UDP: No control
* Error management
  *  Error code
  * Retries and timeouts
  * 