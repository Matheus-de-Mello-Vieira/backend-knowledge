# Network Services

## What is a Network Service?

A network service is a distributed application whose components run on two or more computers connected by a network.

In practice, many network services are implemented as:

* a server-side process listening on an open port
* a transport protocol such as TCP or UDP
* a protocol that defines the dialogue and data formats
* one or more clients that consume the service

Examples include websites, email systems, peer-to-peer systems, VoIP, RPC systems, and file sharing.

## Broad Categories of Network Services

Network services can be grouped in broad ways such as:

* **Internet services:** services exposed through Internet protocols, such as websites and email.
* **Client-server services:** services where a client requests work from a server.
* **WAN-oriented services:** services built to operate across geographically distributed networks.

These categories overlap. A web API, for example, can be both an Internet service and a client-server service.

## Core Elements of a Network Service

Every network service usually depends on at least four elements:

* **Server:** the computer or process that performs the main part of the service.
* **Client:** the computer or process that requests the service.
* **Protocol:** the rules, message sequence, and data formats that define the dialogue.
* **Middleware:** the execution and communication support that lets the service operate.

### Middleware

Middleware is the support layer that helps the service run and communicate.

It commonly includes:

* operating system facilities
* transport protocols
* runtime libraries
* frameworks that carry requests from client to server and responses back again

Middleware is the glue between business logic and the network.

## Client Styles

* **Thin client**:  A thin client mainly displays data and depends heavily on the server for logic and state.

* **Fat client**: A fat client is responsible for a larger part of the application logic. Traditional desktop applications are common examples.

## Architectural Styles

### Client-server

In client-server architecture:

* the client requests the service
* the server performs the main logic or resource handling

This is the dominant structure for most web and enterprise systems.

### Three-tier architecture

Three-tier architecture separates the system into:

* **client tier:** user interface
* **application tier:** business logic
* **data tier:** repositories or databases

This helps separate presentation, processing, and persistence concerns.

### Peer-to-peer

In peer-to-peer architecture, each participant can act as both client and server.

This is common in some file-sharing and user-to-user communication systems.

## Ports and Service Exposure

A network service usually needs a port to be reachable.

Important points:

* a service can run on almost any port
* legacy and common protocols often use default ports so clients can find them more easily
* the transport protocol also matters, because `TCP/80` and `UDP/80` are different sockets

The application layer uses ports through the transport layer to identify which process should receive the traffic.

### Standard Ports

Ports are conventions, not hard requirements, but many classic services have well-known defaults.

Common examples:

* `HTTP`: `80/TCP`
* `HTTPS`: `443/TCP`
* `DNS`: `53/UDP` and sometimes `53/TCP`
* `SMTP`: `25/TCP`
* `SSH`: `22/TCP`
* `FTP`: `21/TCP`

## Services on Top of TCP and UDP

Most common IP network services use TCP or UDP as their communication support.

Examples:

* WWW
* email
* peer-to-peer systems
* VoIP

The higher-level service protocol defines the behavior, while TCP or UDP provides the transport.

## Higher-Level Communication Systems

Some services build an additional communication layer on top of TCP or UDP.

Examples:

* **RPC**
* **Web Services**
* **Java RMI**
* **CORBA**

These systems rely on libraries, runtimes, or frameworks so that clients and servers communicate through higher-level method or procedure calls rather than raw transport primitives.

### Operational consequence

These higher-level systems can make firewalling and filtering harder:

* ports are not always fixed or standardized
* different versions may use different port ranges
* the firewall may need protocol-aware rules instead of simple static port matching

## Industrial Communication Protocols

Outside traditional IT systems, industrial environments also use specialized communication protocols.

These protocols are designed for:

* machine-to-machine communication
* monitoring and control on factory floors
* process automation
* reliable orchestration of connected industrial equipment

This is a separate branch of communication protocols, but it follows the same general idea: standardized rules that allow heterogeneous devices to exchange data safely and predictably.
