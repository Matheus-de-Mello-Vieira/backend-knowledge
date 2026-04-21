# Network Security

Network security encompasses a comprehensive set of technologies and practices designed to protect network infrastructure and the data transmitted across it. Modern network security goes far beyond traditional perimeter defense to include advanced threat detection, network segmentation, and continuous monitoring.
ms
#### **Firewall Technologies**

A firewall is a network security mechanism designed to protect a communication channel by restricting access based on predefined security rules. It serves as a critical defense layer, particularly for ensuring Availability—a tenet that Authentication and Encryption alone do not guarantee.

In a communication utilizing the **TCP/IP protocol**, entities often have static IP addresses provided by their Internet Service Providers (ISPs). A firewall can be configured to allow traffic only from specific, authorized addresses—a process known as **whitelisting**.

Using the communication example introduced in [Risk Management and Threat Modeling](02%20Risk%20Management%20and%20Threat%20Modeling.md), we can apply firewall rules to protect the link between the endpoints and the cloud service:

- **Authorized Access:** Approved IP addresses are allowed to reach the communication channel.
- **Unauthorized Access:** Requests from unapproved addresses are blocked before the connection is established.

**Modern Firewall Types:**
- **Packet-Filtering Firewalls:** Examine individual packets based on source/destination IP, port numbers, and protocol types.
- **Stateful Inspection Firewalls:** Track the state of network connections and make decisions based on connection context.
- **Application Layer Firewalls:** Inspect traffic at the application layer, understanding specific protocols like HTTP, FTP, and SMTP.
- **Next-Generation Firewalls (NGFW):** Integrate traditional firewall capabilities with intrusion prevention, application awareness, and threat intelligence.

#### **Network Segmentation Strategies**

Network segmentation divides a network into smaller, isolated segments to limit the spread of security breaches and improve overall network security.

- **VLAN Segmentation:** Using Virtual Local Area Networks to logically separate network traffic based on function, department, or security requirements.
- **Subnet Segmentation:** Physical or logical division of networks into smaller subnets with controlled inter-subnet communication.
- **Demilitarized Zones (DMZ):** Isolated network segments that contain public-facing services, separated from internal networks.
- **[Zero Trust Network Access (ZTNA)](03%20Zero%20Trust%20Architecture.md):** Assumption that no network location is inherently trustworthy, requiring authentication and authorization for all access requests.

#### **Micro-Segmentation**

Advanced network segmentation that creates granular security zones around individual workloads or applications:

- **Software-Defined Perimeters:** Dynamic creation of encrypted network tunnels based on user identity and device trust.
- **Container Network Security:** Specialized segmentation for containerized applications and microservices architectures.
- **East-West Traffic Control:** Monitoring and controlling lateral movement within the network, not just north-south traffic.
- **Application-Centric Policies:** Security policies that follow applications regardless of their network location.

#### **Network Access Control (NAC)**

Comprehensive systems for controlling device access to network resources:

- **Device Authentication:** Verifying the identity and security posture of devices before granting network access.
- **Compliance Checking:** Ensuring devices meet security requirements (patches, antivirus, configuration) before network admission.
- **Guest Network Management:** Secure, isolated network access for visitors and temporary users.
- **Quarantine Mechanisms:** Automatically isolating non-compliant devices until security issues are resolved.

#### **Intrusion Prevention Systems (IPS)**

Active network security systems that monitor traffic and automatically block detected threats:

- **Signature-Based Detection:** Identifying known attack patterns and malicious traffic signatures.
- **Behavioral Analysis:** Detecting anomalous network behavior that may indicate new or unknown threats.
- **Protocol Analysis:** Deep inspection of network protocols to identify violations or attacks.
- **Automated Response:** Immediate blocking of malicious traffic and notification of security teams.

#### **Network Monitoring and Analysis**

Continuous surveillance of network traffic for security threats and performance issues:

- **Deep Packet Inspection (DPI):** Comprehensive analysis of packet contents to identify threats and policy violations.
- **Flow Analysis:** Statistical analysis of network traffic patterns to identify anomalies and trends.
- **Network Forensics:** Detailed investigation of network incidents using captured traffic and log data.
- **Bandwidth and Performance Monitoring:** Tracking network utilization to identify potential security issues or attacks.

#### **Types of Network Defense**

Network defense can be understood in three complementary categories. The goal is not to rely on only one of them, but to combine them so the network can prevent known attacks, identify early warning signs, and reduce damage when an incident succeeds.

- **Preventive Defense:** Used when a type of attack is already known and there are established controls to reduce the probability of compromise. Firewalls, [segmentation](03%20Zero%20Trust%20Architecture.md#Network%20Micro-Segmentation), [access control](02%20Authorization%20and%20Access%20Control.md), [hardening](01%20Security%20Principles.md#System%20Hardening), and patching are preventive because they aim to stop the attack before it succeeds.
- **Predictive Defense:** Used when there is still no confirmed breach, but there are early indicators, anomalies, or suspicious patterns that suggest a potential attack. This includes behavioral baselines, anomaly monitoring, reconnaissance detection, and systems such as [Intrusion Detection](01%20Intrusion%20Detection.md).
- **Reactive Defense:** Used after the attack has already happened and the focus shifts to containment, impact reduction, service restoration, and learning. This includes isolating compromised systems, preserving evidence, and following formal [Incident Response and Recovery](02%20Incident%20Response%20and%20Recovery.md) procedures.

In practice, mature network security combines all three approaches. Preventive controls reduce exposure, predictive controls improve detection speed, and reactive controls limit blast radius and support recovery.

#### **Mixed Network Defense**

Real environments often combine traditional computing assets with wireless devices, IP telephony, surveillance systems, and IoT equipment. This convergence improves operational efficiency, but it also increases the attack surface because devices with very different security maturity levels start sharing the same infrastructure.

- **Wireless Exposure:** Wi-Fi extends the network beyond walls, which increases the importance of strong encryption, authentication, and guest isolation.
- **IP Telephony Risk:** VoIP and PBX platforms can suffer from interception, weak administrative interfaces, toll fraud, and poor segmentation from user workstations.
- **CCTV and Recorder Risk:** IP cameras, DVRs, and NVRs are frequent targets because they are often Internet-exposed, poorly updated, and rich in sensitive operational data.
- **Shared Infrastructure Risk:** When cameras, phones, laptops, and servers coexist on the same flat network, one compromised device may become a pivot point for lateral movement.

For that reason, mixed environments should apply controls such as:

- **Segmentation:** Separate user devices, servers, cameras, telephony, and guest access into distinct VLANs or trust zones.
- **Access Control:** Restrict which users, devices, and systems can reach management interfaces and sensitive internal services.
- **Continuous Monitoring:** Detect abnormal behavior such as unexpected scans, unusual outbound traffic, or device-to-device communication outside the normal baseline.
- **Remote Access Hardening:** Avoid exposing administrative interfaces directly to the Internet; prefer VPNs, strong authentication, and tightly scoped access paths.
