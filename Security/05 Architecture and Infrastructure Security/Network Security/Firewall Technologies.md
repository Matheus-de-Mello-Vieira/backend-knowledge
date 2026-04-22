# Firewall

A firewall is a network security mechanism designed to protect a communication channel by restricting access based on predefined security rules. It serves as a critical defense layer, particularly for ensuring Availability—a tenet that [Authentication](../../02%20Identity%20and%20Access/01%20Authentication.md) and [Encryption](../../03%20Cryptography%20and%20Data%20Protection/01%20Cryptography.md) alone do not guarantee.

In a communication utilizing the **TCP/IP protocol**, entities often have static IP addresses provided by their Internet Service Providers (ISPs). A firewall can be configured to allow traffic only from specific, authorized addresses—a process known as **whitelisting**.

The term "firewall" is derived from physical construction—a firebreak wall or fire door designed to prevent a fire from spreading from one room or floor to another.

- In computer networks, a firewall is a hardware or software mechanism that applies security policies to control traffic flowing through a specific point in the network.
- When a firewall is deployed as a dedicated, specialized piece of hardware running built-in software, it is referred to as an **Appliance**.

Using the communication example introduced in [Risk Management and Threat Modeling](02%20Risk%20Management%20and%20Threat%20Modeling.md), we can apply firewall rules to protect the link between the endpoints and the cloud service:

- **Authorized Access:** Approved IP addresses are allowed to reach the communication channel.
- **Unauthorized Access:** Requests from unapproved addresses are blocked before the connection is established.

## The History and Evolution of Firewalls

Firewalls emerged in the late 1980s out of a critical need to control network access and implement security policies. As the TCP/IP protocol suite saw mass adoption, networks increasingly became targets for the first generation of hackers (a reality famously anticipated by the 1983 movie _WarGames_).

The true catalyst for change occurred in 1988 when the internet experienced its first major "blackout" due to a rapidly spreading computer worm. In response, firewalls were conceptually adopted to act just like physical fire doors—preventing an infection in one network from spreading to others.

From this point, the technology rapidly evolved across distinct "generations." However, it is crucial to understand that **this evolution is not a story of replacement, but of accumulation**. Newer generations of firewalls did not render the older ones obsolete. Instead, each generation introduced a deeper level of inspection. Today, these distinct technologies do not compete with one another; rather, they are positioned at different points in the network to create a comprehensive "Defense in Depth" strategy:

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

To solve the performance issues of proxies while dealing with highly sophisticated modern threats, the industry evolved toward Unified Threat Management (UTM) and Next-Generation Firewalls (NGFW).

- **How it works:** NGFWs combine the high-speed stateful inspection of the 2nd generation with [Deep Packet Inspection (DPI)](01%20Network%20Security.md#Network%20Monitoring%20and%20Analysis) and built-in [Intrusion Prevention Systems (IPS)](../../06%20Security%20Operations%20and%20Governance/01%20Intrusion%20Detection%20and%20Prevention.md#Intrusion%20Prevention%20Systems%20%28IPS%29). Most importantly, they shift the focus from _IP addresses and ports_ to _applications and user identities_.
- **The Advantage:** NGFWs offer incredibly granular control. Instead of just blocking port 80 or 443, an NGFW can recognize the specific app being used. For example, it can allow an employee to access Facebook (the application) but specifically block them from using Facebook Messenger or playing embedded games.
- **SYN Flood Mitigation**: While 2nd generation stateful firewalls were revolutionary, their need to allocate memory for every new connection request made them highly vulnerable to state table exhaustion (SYN floods). This attack abuses the TCP handshake described in [How connections are Established](../../../Networking/03%20Connections/01%20How%20Connections%20are%20Established.md#Connection%20Establishment). Modern 4th generation firewalls (NGFWs) solved this by implementing intelligent, memory-saving defenses at the firewall layer:
    - **SYN Proxying (TCP Intercept):** Instead of immediately passing an inbound connection request to the internal server, the firewall intercepts the initial SYN packet. It acts as a shield, completing the 3-way handshake with the client itself. Only _after_ the client proves it is legitimate (by completing the handshake) does the firewall open a connection to the internal server and stitch the two connections together.
    - **SYN Cookies:** This is a cryptographic method to avoid using memory during a flood. When the firewall receives a SYN request, it calculates a cryptographic hash (a "cookie") based on the connection details and sends it back to the client, allocating _zero_ memory in its state table. If the client is legitimate, it replies with that exact cookie, and only then does the firewall allocate memory to permit the connection.
    - **Hardware Acceleration (ASICs):** Modern firewalls use specialized hardware chips designed to process and drop millions of fake SYN packets per second at wire-speed, preventing the main CPU from being overwhelmed.
- **Modern Features:** Today's NGFWs also integrate with Active Directory (to create rules based on usernames rather than IPs), perform SSL/TLS decryption to inspect encrypted traffic for hidden malware, and constantly update their rules via real-time cloud threat intelligence.
