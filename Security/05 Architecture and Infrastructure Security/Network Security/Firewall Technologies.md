# Firewall

A firewall is a network security mechanism designed to protect a communication channel by restricting access based on predefined security rules. It serves as a critical defense layer, particularly for ensuring Availability—a tenet that [Authentication](../../02%20Identity%20and%20Access/01%20Authentication.md) and [Encryption](../../03%20Cryptography%20and%20Data%20Protection/01%20Cryptography.md) alone do not guarantee.

In a communication utilizing the **TCP/IP protocol**, entities often have static IP addresses provided by their Internet Service Providers (ISPs). A firewall can be configured to allow traffic only from specific, authorized addresses—a process known as **whitelisting**.

The term "firewall" is derived from physical construction—a firebreak wall or fire door designed to prevent a fire from spreading from one room or floor to another.

- In computer networks, a firewall is a hardware or software mechanism that applies security policies to control traffic flowing through a specific point in the network.
- When a firewall is deployed as a dedicated, specialized piece of hardware running built-in software, it is referred to as an **Appliance**.

Using the communication example introduced in [Risk Management and Threat Modeling](../../01%20Foundations%20and%20Risk/02%20Risk%20Management%20and%20Threat%20Modeling.md), we can apply firewall rules to protect the link between the endpoints and the cloud service:

- **Authorized Access:** Approved IP addresses are allowed to reach the communication channel.
- **Unauthorized Access:** Requests from unapproved addresses are blocked before the connection is established.

## The History and Evolution of Firewalls

Firewalls emerged in the late 1980s out of a critical need to control network access and implement security policies. As the TCP/IP protocol suite saw mass adoption, networks increasingly became targets for the first generation of hackers (a reality famously anticipated by the 1983 movie _WarGames_).

The true catalyst for change occurred in 1988 when the internet experienced its first major "blackout" due to a rapidly spreading computer worm. In response, firewalls were conceptually adopted to act just like physical fire doors—preventing an infection in one network from spreading to others.

From this point, the technology rapidly evolved across distinct "generations." However, it is crucial to understand that **this evolution is not a story of replacement, but of accumulation**. Newer generations of firewalls did not render the older ones obsolete. Instead, each generation introduced a deeper level of inspection. Today, these distinct technologies do not compete with one another; rather, they are positioned at different points in the network to create a comprehensive "Defense in Depth" strategy.

The OSI-layer perspective appears later in [Firewalls Across the OSI Model Layers](#Firewalls%20Across%20the%20OSI%20Model%20Layers). This section focuses on how firewall capabilities evolved over time.

### First Generation: Stateless Packet Filters (Late 1980s)

The earliest firewalls, promoted by DEC in 1988 and pioneered by Bill Cheswick and Steve Bellovin, were simple packet filters for the TCP/IP suite.

- **How it worked:** They controlled traffic purely by inspecting individual packets against basic rules (e.g., checking source/destination IP addresses or TCP/UDP ports).
- **Where they live today:** Inside network routers and Layer 3 switches. They are almost universally implemented as standard Access Control Lists (ACLs).
- **Why we still use them:** Because they do not need to memorize connection states, they process traffic at wire-speed with virtually zero CPU or memory cost. Administrators use them at the absolute outermost edge of the network to immediately drop obvious "junk" traffic (like spoofed IPs or known malicious subnets) before that traffic wastes the processing power of the more expensive inner firewalls.
- **The Limitation:** The main criticism of this model is that it is **Stateless** (without connection state). The firewall evaluated every single packet in complete isolation. Because it could not remember the context of an ongoing conversation, it was rigid and easily bypassed by certain spoofing techniques.
  
### Second Generation: Stateful Inspection (Early 1990s)

To address the flaws of early packet filters, the second generation introduced the ability to maintain a connection state table.

- **How it worked:** These firewalls leveraged TCP's connection-oriented nature. Instead of looking at packets in isolation, they tracked the entire state of active connections (sessions).
- **The Advantage:** Because they filtered traffic per _session_ rather than per packet, they were vastly superior and much more efficient. This dynamic technology is known as **Stateful** (with connection state).
- **Where they live today:** Inside cloud infrastructure (like AWS Security Groups or Azure Network Security Groups), host-based firewalls (like Windows Defender Firewall or Linux iptables), and standard small-office/home-office (SOHO) routers.
- **Why we still use them:** They provide reliable, low-overhead directional access control. They are perfect for fast internal network segmentation—for example, safely allowing devices on the HR VLAN to connect to the Engineering VLAN, but blocking the Engineering VLAN from initiating connections back into HR. They handle this efficiently without needing to deeply analyze the application data.
- **The Limitation:** While stateful firewalls understood the context of a connection, they did not inspect the actual content (the payload) of the data packets.
    - If an attacker hid malware or a malicious command within seemingly legitimate traffic (such as standard web traffic on an allowed port like 80), the firewall would let it pass because the connection state itself was valid.
    - Furthermore, the requirement to store every active session in memory made them vulnerable to state table exhaustion attacks (like SYN floods), where an attacker could overwhelm the firewall's memory capacity and cause a Denial of Service (DoS).

### Third Generation: Application Layer Firewalls / Proxies (Mid-to-Late 1990s)

Directly addressing the second generation's inability to inspect packet payloads, the third generation was developed to look deep into the actual content of the network traffic.

- **How it works:** These firewalls operate all the way up to OSI Layer 7 (the Application Layer). Instead of just tracking the connection state and routing packets, they act as an intermediary or "proxy" between the internal client and the external server. The firewall intercepts the connection, completely reconstructs and inspects the data payload for malicious content or unauthorized commands, and then establishes a separate connection with the destination on the user's behalf.
- **The Advantage:** By understanding specific application protocols (like HTTP, FTP, or SMTP), they eliminate the blind spots of the previous generation. They can filter traffic based on actual application commands—for example, allowing a user to read a webpage (HTTP GET) but blocking them from uploading a file to it (HTTP POST). Additionally, by acting as a proxy, they completely hide the internal network's IP structure from the outside world.
- **Where they live today:** They evolved into specialized devices like **Web Application Firewalls (WAFs)** and Reverse Proxies (like Nginx or HAProxy).
- **Why we still use them:** While an NGFW is great for general office traffic, if a company hosts its own web application or API, they will place a dedicated 3rd generation proxy firewall directly in front of that specific server. It is the only way to get the absolute deepest, most specialized inspection of HTTP/HTTPS traffic to prevent things like SQL injection or cross-site scripting.
- **The Limitation:** Because the firewall must intercept, tear down, deeply inspect, and reconstruct every single connection at the application layer, this generation introduced significant processing overhead and network latency, often creating a performance bottleneck for high-speed networks.

### Fourth Generation and Beyond: Next-Generation Firewalls (NGFW) (2000s to Present)

To solve the performance limitations of traditional proxies while tackling highly sophisticated modern threats, the industry evolved toward **Unified Threat Management (UTM)** and **Next-Generation Firewalls (NGFW)**. These systems act as a high-speed security detail for your network, combining traditional defenses with advanced intelligence.

Here is how modern NGFWs transform network security:

#### 1. From Ports and IPs to Applications and Identities

Traditional firewalls look at "doors" (ports) and "addresses" (IPs). NGFWs shift the focus to **who** is doing **what**.

- **Granular Control:** Instead of just blocking port 80 or 443, an NGFW recognizes the specific application. For example, it can allow an employee to access Facebook (the application) but specifically block them from using Facebook Messenger or playing embedded games.
- **Active Directory Integration:** Rules are created based on actual usernames rather than temporary IP addresses, allowing for consistent policy enforcement regardless of where a user logs in.
    

#### 2. Advanced Security and Breach Prevention

The number one job of a firewall is to prevent breaches, but because no defense is 100% effective, modern systems include multi-layered "fail-safes":

- **[Deep Packet Inspection (DPI)](01%20Network%20Security.md#Network%20Monitoring%20and%20Analysis) & [Intrusion Prevention System (IPS)](../../06%20Security%20Operations%20and%20Governance/01%20Intrusion%20Detection%20and%20Prevention.md#Intrusion%20Prevention%20System%20%28IPS%29):** By combining high-speed stateful inspection with a built-in **IPS**, the firewall can detect and stop stealthy, "in-the-flow" attacks.
- **Integrated Sandboxing:** This promotes advanced protection by continuously analyzing the behavior of suspicious files in a safe environment to detect and eliminate malware before it spreads.
- **URL Filtering:** Policies are enforced across hundreds of millions of URLs to prevent users from reaching malicious sites in the first place.

#### 3. Comprehensive Network Visibility

**You cannot protect what you cannot see.** To identify and stop bad behavior, you need total awareness of your network’s "context."

- **Activity Monitoring:** Track threat activity across users, devices, hosts, and virtual machines.
- **Threat Forensics:** Identify where and when a threat originated, where else it has traveled within your network, and what it is doing in real-time.

#### 4. SYN Flood Mitigation (The Defensive Shield)

While earlier stateful firewalls were revolutionary, they were vulnerable to **state table exhaustion (SYN floods)**—attacks that abuse the [TCP handshake](../../../Networking/03%20Connections/01%20How%20Connections%20are%20Established.md#Connection%20Establishment) to overwhelm a firewall's memory. Modern NGFWs implement intelligent, hardware-accelerated defenses:

- **SYN Proxying (TCP Intercept):** The firewall acts as a shield, completing the 3-way handshake with the client itself. It only opens a connection to the internal server after the client proves it is legitimate.
- **SYN Cookies:** A cryptographic method that allows the firewall to handle connection requests without allocating memory until the connection is fully validated.
- **Hardware Acceleration (ASICs):** Specialized chips process and drop millions of fake packets per second at wire-speed, ensuring the main CPU remains available for critical tasks.
    

#### 5. Faster Detection and Automated Intelligence

The current industry standard for detecting a threat is often too slow. A modern NGFW bridges this gap through:

- **Real-time Cloud Threat Intelligence:** Firewalls connect to global intelligence organizations to receive the latest data on emerging threats, often detecting new attacks in seconds.
- **SSL/TLS Decryption:** Since most web traffic is now encrypted, NGFWs decrypt and inspect traffic to ensure malware isn't hiding inside a "secure" connection.
- **Alert Prioritization:** Instead of drowning you in notifications, the system prioritizes critical alerts so you can take swift, accurate action.
    

#### 6. Ecosystem Integration and Management

A firewall should not be an isolated tool; it should be the "brain" of your security architecture.

- **Seamless Sharing:** Automatically share event data and threat info with your email, web, and endpoint security tools.
- **Workflow Automation:** These systems can automate security tasks, tune policies, and perform impact assessments, reducing the manual burden on your IT team.
- **Flexible Deployment:** Whether you are a small business or a massive enterprise, you can deploy on-premises or in the cloud via **virtual firewalls**, with a choice of centralized or on-box management.

## Firewalls Across the OSI Model Layers

A firewall can act across multiple layers of the OSI model. For the broader catalog of security controls applied at each layer, see [Layered Security Techniques](Layered%20Security%20Techniques.md). This section focuses only on what a firewall can inspect and enforce.

### Layer 1: Physical Layer

At **Layer 1** (the Physical Layer), firewalling is limited because there are no packets to inspect yet. Controls at this layer monitor physical quantities:

- **Connectivity:** Is a cable physically plugged in?    
- **Signaling:** Is there measurable electrical energy or optical light present?
- **Port Status:** Is the administrative state (on/off) consistent with actual usage?

By tracking these signals, systems can implement **Physical Firewalls**. For example, if a switch port designated as "unused" suddenly detects an electrical signal, the system can automatically block the port to prevent a breach.

### Layer 2: Data Link Layer

At **Layer 2**, firewalls and switch-level controls can inspect Ethernet frame information, especially the **MAC (Media Access Control) address**. This allows policies such as MAC-based filtering, where traffic is allowed or blocked based on the hardware address seen on a switch port.

### Layer 3: Network Layer

At **Layer 3** (the Network Layer), security mechanisms focus on **logical addressing** through the **IP (Internet Protocol)**.

- **Packet Filtering:** Firewalls at this layer inspect [IP headers](../../../Networking/02%20Protocols/03%20Internet%20Protocol.md#Anatomy%20of%20the%20IP%20packet) to filter traffic based on source and destination IP addresses. They can also analyze additional header fields, such as **TTL (Time to Live)** and **DSCP (Differentiated Services Code Point)**.
- **Access Rules:** This visibility allows administrators to build firewall rules and access control lists (ACLs) that govern which specific hosts, networks, or subnets are permitted to communicate with one another.

### Layer 4: Transport Layer

At **Layer 4** (the Transport Layer), the firewall advances to inspecting **protocols (TCP and UDP)** and **logical ports**. This allows the security system to move beyond identifying machines and start identifying specific services.

- **Port Filtering:** Because ports identify specific services (e.g., Port 80 for HTTP, Port 443 for HTTPS, Port 25 for SMTP), firewalls can refine their rules. Instead of blocking a host entirely—which might disrupt multiple services—an administrator can allow web traffic while blocking file transfers or remote login attempts.
- **Protocol Analysis:** The firewall differentiates between **TCP** (transmission control protocol), which is connection-oriented and reliable, and **UDP** (user datagram protocol), which is faster but lacks error recovery.

However, the port number no longer strictly defines the application. For example, **Port 80 (HTTP)** is traditionally for web browsing, but it is now used to transport many different services:

- **Webmail:** Accessing email through a browser instead of a dedicated POP client.
- **Collaboration Tools:** Services like Google Meet or TeamViewer.
- **Streaming:** Video platforms like YouTube.

A Layer 4 firewall cannot distinguish between these services because they all appear as Port 80 traffic.

### Layer 7: Application Layer

At **Layer 7** (the Application Layer), the firewall inspects the actual data within the packet to identify the specific application being used.

Analyzing traffic at Layer 7 is significantly more "expensive" in terms of hardware resources.

- **Layer 1-3:** The system only needs to read the outermost headers, which is fast and uses minimal memory.
- **Layer 7:** The firewall must "peel back" every single header (Layers 1 through 6) to reach the application data.

Because this requires more processing power and time, Layer 7 analysis is usually reserved for complex security policies, while simpler filters are handled at lower layers for maximum efficiency.

## Mapping Firewall Generations to OSI Layers

The two perspectives overlap, but they answer different questions: generations explain how firewall technology evolved, while OSI layers explain what information a control can inspect.

| Firewall generation | Main inspection level | Typical controls |
| --- | --- | --- |
| Stateless packet filters | Layers 3-4 | Source/destination IP addresses, protocols, ports, ACLs |
| Stateful inspection | Layer 4 | TCP/UDP sessions, connection state tables, directional access control |
| Application layer firewalls / proxies | Layer 7 | HTTP/FTP/SMTP commands, payload inspection, reverse proxying, WAF-style controls |
| Next-generation firewalls (NGFW) | Layers 3-7 | Application identity, user identity, DPI, IPS, URL filtering, sandboxing, threat intelligence |
