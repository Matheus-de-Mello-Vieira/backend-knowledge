# Layered Security Techniques

Network protection is not just a logical function; it begins with physical access. Imagine creating a state-of-the-art data protection system with dozens of firewalls and control systems, only for an attacker to simply walk in, physically steal the server, remove the hard drive, and gain access to all your files. Why? Because the physical access to the equipment was left undefended. Network protection must be designed in layers, and the very first is the Access Layer. This is where our studies and projects must begin.

This note covers broad security techniques applied across layers. For the narrower firewall-specific view of what can be inspected and enforced at each OSI layer, see [Firewalls Across the OSI Model Layers](Firewall%20Technologies.md#Firewalls%20Across%20the%20OSI%20Model%20Layers).

**1. Access Layer (Physical Security)**

Securing physical access to equipment is accomplished in two main stages:

- **Facility Physical Security:** Protecting sensitive corporate information is a major challenge, as various threats have the potential to cause massive financial losses.
	- Therefore, integration between IT (responsible for logical security) and Facility Security (responsible for the physical security of the premises) is crucial. Information security is not exclusively an IT activity; it is everyone's responsibility.
	- The facility's physical security is the network's first line of defense. This consists of a perimeter barrier (fences, walls), access points (reception areas) equipped with mechanical controls (gates, barriers) or electronic controls (electronic locks, turnstiles), physical security policies, alarm systems, and security cameras.
- **Equipment Physical Security:** Once the facility is secure, you must protect the equipment itself.
	- A fully exposed switch is useless if anyone can just plug a cable into an open port.
	- All active and passive equipment must be physically secured.
	- Server racks and telecom closets must be locked with keys or padlocks, and access must be strictly controlled.
		- It is unacceptably careless to have a locked rack where the side panel can be easily popped open without a key.
	- All network cables must run through closed conduits—no cable should be exposed, accessible, or even visible.

**2. Data Link Layer Techniques (OSI Layer 2) **

When discussing network layer protection techniques at this level, we are referring to Layer 2 of the [OSI model](../../../Networking/03%20Network%20Models.md#The%20OSI%20%28Open%20Systems%20Interconnection%29%20Model). The primary equipment here is the switch, which forms the backbone of the company's Local Area Network (LAN). The most important Layer 2 protocol is the [Ethernet](../../../Networking/02%20Protocols/02%20Ethernet.md).
- **Device Inventory & Port Binding:** The foundation of a "[Layer 2 firewalls](Firewall%20Technologies.md#Layer%202%3A%20Data%20Link%20Layer)" is maintaining a strict registry that maps authorized MAC addresses to their designated physical switch ports. While this tracking is an excellent control measure, it is unfortunately often neglected. 
- **MAC Filtering & Limiting:** Using the device inventory, administrators can statically bind a specific [MAC address](../../../Networking/02%20Protocols/02%20Ethernet.md#MAC%20Addressing)  to its assigned port and restrict the total number of allowed MACs per port (which prevents attackers from plugging in unmanaged switches). If frames arrive from an unauthorized MAC, or if an authorized MAC transmits on the wrong port, the switch automatically drops the traffic.
- **Untrusted CoS Markings:** Edge switches should never blindly trust [Class of Service (CoS)](02%20Ethernet.md#Class%20of%20Service%20%28CoS%29) markings from endpoints. Because 802.1Q tags are easily spoofed, an attacker or misconfigured device can artificially elevate standard traffic to a critical priority queue, starving the network. To prevent this, edge ports should strip or rewrite incoming CoS values, reserving inherent trust exclusively for trunk links between core networking devices.

These controls can reduce accidental misuse and raise the bar for simple attacks, but they are not strong identity guarantees by themselves because [MAC addresses can be spoofed](../../../Networking/02%20Protocols/02%20Ethernet.md#MAC%20Spoofing%20and%20Randomization).

**3. Internet Layer Techniques (TCP/IP Layer 3)**

The main protocols operating at this layer are IPv4 and IPv6. In the [TCP/IP model](../../../Networking/03%20Network%20Models.md#The%20TCP%2FIP%20Model), this is the Internet Layer, and the physical device representing it is the router.

- **IP Filtering:** Techniques at this layer rely on understanding how these protocols function. Instead of filtering by MAC addresses, filters are implemented based on source and destination IPv4 or IPv6 addresses.
- **Dual-Stack Implementation:** Because IPv4 and IPv6 operate simultaneously and completely independently on modern networks, all security techniques and filters must be implemented as a "dual-stack" (configured separately for both protocols) to ensure full coverage.

**4. Transport Layer Techniques (OSI Layer 4)**

This layer is primarily governed by the TCP and UDP protocols described in the [network communication models](../../../Networking/03%20Network%20Models.md#The%207%20Layers%20of%20OSI).

- **Port Filtering:** Security techniques here are based on understanding these transport protocols. Filters are implemented based on source and destination _ports_, correlating them with the previously established MAC or IP filters. The firewall or router inspects the port number and other specific protocol parameters to permit or deny traffic.

**5. Application Layer Techniques (OSI Layer 7)**

This layer encompasses a wide variety of distinct applications, and understanding how each works is essential for implementing proper defenses. For the broader conceptual breakdown of these layers, see [Network Communication Models](../../../Networking/03%20Network%20Models.md).

- **Application-Specific Defenses:** The techniques used are highly specific to the protocol. For example, the defense mechanisms for HTTP (web traffic) are vastly different from those used for SMTP (email). Email systems face unique problems like spam, which does not affect HTTP. DNS (Domain Name System) traffic also has its own unique vulnerabilities and required security measures. In short, each application requires highly particular, tailor-made security techniques.
