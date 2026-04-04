# Open System Interconnection Model

## Why do we need a communication model?

* Agnostic applications
  * Without a standard model, your application must have knowledge of the underlying network medium.
    * Image if you have to author different version of your applications so that it works on wifi vs ethernet vs LTE vs fiber
* Network Equipment Management
  * Without a standard model, upgrading network equipment becomes difficult
* Decoupled Innovation
  * Innovations can be done in each layer separately without affecting the rest of the models.

## What is the OSI Model?

7 layers each describe a specific networking component

* **Layer 7 - Application**: HTTP/FTP/gRPC
  * Usually backend engineers uses libraries to abstract that layer
* **Layer 6 - Presentation**: Encoding, Serialization
  * Transform your data into a binary
* **Layer 5 - Session**: Connection establishment, TLS
  * If it is a stateful protocol, here it sets a state in the client, and sets a state in the server
  * a stateless protocol doesn't have this
  * It seems simple, but it is important to have a separated layer. For example, some proxies (e.g.: Likerd) build logic only on the Session layer. 
* **Layer 4 - Transport**: UDP/TCP
  * You can configure your application to be a layer 4 application, so it will be aware about the transportation.
  * Honestly, there are only UDP and TCP here.
  * Here we send segments in TCP and datagrams in UDP.
  * Here we hand the ports
* **Layer 3 - Network**: IP
  * Here there is no 'transport' concept, even the port isn't important.
  * This layer only cares about the routing and cares only about the IP addresses.
  * Here we send packets
* **Layer 2 - Data link**: Frames, Mac address Ethernet
  * Close to the medium, for example send a frame to a router that have a specific Mac address.
  *  Here we send frames
* **Layer 1 - Physical** - Electric signal, fiber or radio waves
  * bare metal


As a backend engineer, you usually will worry only about the 7th and 4th layers. If you are a DevOps engineer, maybe also 2nd and 3rd layers.

### Example

Example sending a POST request to an HTTPs webpage

* **Layer 7 - Application**: Post request with JSON data to HTTPs server.
* **Layer 6 - Presentation**: Serialize JSON to flat byte strings
* **Layer 5 - Session**: Request to establish TCP connection/TLS
* **Layer 4 - Transport**: Send SYN request target port 443.
* **Layer 3 - Network**: SYN is placed an IP packet(s) and adds the source/dest IPs
* **Layer 2 - Data link**: each packet goes into a single frame and adds the source/dest MAC addresses
* **Layer 1 - Physical**: Each frame becomes string of bits which converted into either a radio signal (wifi), electric signal (ethernet), or light (fiber).

The receive computer receives the POST request the other way around

* **Layer 1 - Physical**: Radio, electric is  received and converted into digital bits
* **Layer 2 - Data link**: The bits from layer 1 is assembled into frames
* **Layer 3 - Network**: The frames from layer 2 are assembled into IP packet.
* **Layer 4 - Transport**: The IP packet from layer 3 are assembled into TCP segments.
  * Deals with Congestion control/flow control/retransmission in case of TCP
  * If Segment is SYN we don't need to go further into more layer as we are still processing
* **Layer 5 - Session**: The connection session is established or identified
  * We only arrive at this layer when necessary (three way handshake is done)
* **Layer 6 - Presentation**: Deserialize flat byte strings back to JSON for the application to consume
  * For example, you can serialize from javascript and deserialize to python
* **Layer 7 - Application**: Application understands the JSON POST request and your express json or apache request event is triggered

Take it with a grain of salt, it's not always cut and dried:

* For example:
  * receivers stop on Layer 5 to establish a connection because they only need to activate the state machine responsible for managing the connection.
  * switches stop on Layer 2 because they forward frames based on only MAC addresses
    * so switches are Layer 2 devices
  * routers stop on Layer 3 because they forward packets based on only IP addresses
    * so routes are Layer 3 devices
    * a VPN can be a Layer 3 system, because it can forward the traffic based on only IP addresses
  * transparent firewalls and proxies stop on Layer 4 because firewalls block and proxies forward traffic based only on IP addresses and ports 
    * some firewalls look at the application to judge the blocking.
    * transparent firewalls and proxies are named on this way because it is publicly available, because it doesn't undergo encryption.
    * Layer 4 load balancers do their work bases only on IP addresses and ports criteria.
  * Layer 7 Load Balancer/CDN
    * Normally the data of this layer is all encrypted
    * for example, using Nginx you can forward to different servers based on the HTTP route. 
    * it is way slower that the application of inferior layers.
    * 5+ layers proxies need to remake the request to the server because it give the illusion to client that the proxy makes the response by its own.

## The Shortcomings of th OSI model

* OSI Model has too many layers which can be hard to comprehend.
* Hard to argue about which layers does what
* Simpler to deal with Layers 5-6-7 as just one layer, application.
  * TCP/IP Model does just that

## TCP/IP Model

Much simples than OSI just 4 layers

* Application: Layer 5, 6 and 7
* Transport: Layer 4
* Internet: Layer 3
* Data link: Layer 2
* Physical layer is not officially covered in the model.
