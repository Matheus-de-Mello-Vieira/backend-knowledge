# Network Security

Network security encompasses a comprehensive set of technologies and practices designed to protect network infrastructure and the data transmitted across it. Modern network security goes far beyond traditional perimeter defense to include advanced threat detection, network segmentation, and continuous monitoring.

## Firewall

Firewall-specific concepts are covered in [Firewall Technologies](Firewall%20Technologies.md).

## Network Segmentation Strategies

Network segmentation is one of the most effective ways to stop a cyberattack from turning into a company-wide catastrophe. Think of it like the bulkhead doors on a ship: if water floods one compartment, the doors seal it off so the whole ship doesn't sink.

Here is a deeper look into each of those strategies, including how they work, their real-world use cases, and how they fit together.

## VLAN Segmentation (Layer 2)

- It uses [Virtual Local Area Networks (VLANs)](02%20Ethernet.md#VLAN%20Tagging) to segment a network at the Layer 2
- **Best Used For:** Internal departmental separation (e.g., keeping Guest Wi-Fi, HR, and Engineering traffic completely isolated from each other on the same physical hardware).

## 2. Subnet Segmentation (Layer 3)

- **How it works:** It uses [Subnetting](03%20Internet%20Protocol.md#Subnetting) to segment a network at the Layer 2
- **Best Used For:** Creating distinct boundaries for different types of infrastructure—for example, putting all IP security cameras on one subnet, VoIP phones on another, and critical database servers on a highly restricted third subnet.

### Demilitarized Zones (DMZ)

A DMZ (`/ˌdiː ɛm ˈziː/`) acts as a neutral buffer zone between your untrusted public internet and your highly trusted internal corporate network.

- **How it works:** Typically structured using a "triple-homed firewall" or two separate firewalls (external and internal). Public-facing servers sit in the middle. If a hacker compromises your public web server in the DMZ, the internal firewall still blocks them from jumping deeper into your private Active Directory or customer databases.
- **Best Used For:** Hosting external-facing services like web servers, mail gateways, external APIs, and reverse proxies.

## 4. Zero Trust Network Access (ZTNA)

ZTNA shifts the focus from _network location_ to _identity and context_. Traditional segmentation assumes that if you are inside the network, you are safe. ZTNA assumes the network is already hostile, whether you are sitting in the office or at a coffee shop.

- **How it works:** ZTNA creates a "dark network"—infrastructure is invisible to the public internet until a user is authenticated. It uses a trust broker to verify the user's identity, multi-factor authentication (MFA), device health, and location _before_ granting a temporary, encrypted tunnel to just **one specific application**, rather than the whole network.
- This is part of the broader [Zero Trust Architecture](03%20Zero%20Trust%20Architecture.md).
- **Best Used For:** Remote workforces, third-party vendor access, and replacing traditional, overly permissive corporate VPNs.

## Micro-Segmentation

Micro-segmentation is advanced network segmentation that creates granular security zones around individual workloads, applications, services, or identities. Instead of relying on a broad trusted internal network, it applies internal controls that limit which systems can communicate and under what conditions.

- **Software-Defined Perimeters (SDP):** Dynamic creation of secure network segments or encrypted tunnels based on user identity, device trust, and resource requirements.
- **Application-Level Segmentation:** Isolation of individual applications and services rather than broad network segments.
- **Container Network Security:** Specialized segmentation for containerized applications and microservices architectures.
- **East-West Traffic Control:** Monitoring, inspecting, and controlling lateral (internal) traffic between internal systems, not just north-south traffic crossing the perimeter.
- **Application-Centric Policies:** Security policies that follow applications regardless of their network location.
- **Encrypted Communication:** Internal traffic should be [encrypted in transit](../../03%20Cryptography%20and%20Data%20Protection/01%20Cryptography.md#3.%20The%20States%20of%20Encryption), including service-to-service communication inside the network.

## Wireless Network Security Standards

In the scope of wireless networks (Wi-Fi), perimeter security relies on the continuous technical evolution of encryption protocols. These standards have developed over the decades to mitigate historical vulnerabilities and adapt to increasing adversarial computational power:

- **WEP (Wired Equivalent Privacy - 1997):** The original wireless security standard. It utilized weak, static cryptographic keys (based on the RC4 cipher) that rarely changed. Due to fundamental mathematical flaws in how it generated its encryption variables, attackers can easily capture wireless packets and crack the static key in minutes, rendering it completely obsolete.
- **WPA (Wi-Fi Protected Access - 2003):** Developed as a rapid, temporary replacement to mitigate WEP's critical flaws without requiring organizations to buy new router hardware. It introduced dynamic security elements (like TKIP) to generate new keys for every packet, significantly raising the difficulty of eavesdropping.
- **WPA2 (Wi-Fi Protected Access II - 2004):** The long-standing industry standard. It advanced wireless security by abandoning older ciphers and making the highly secure **AES** (Advanced Encryption Standard) algorithm mandatory. While it significantly raised perimeter security, its initial authentication handshake remains vulnerable to offline dictionary and brute-force attacks if weak passwords are used.
- **WPA3 (Wi-Fi Protected Access III - 2018):** The contemporary standard built to resolve WPA2's lingering vulnerabilities. It implements a new handshake protocol (Simultaneous Authentication of Equals, or SAE) that makes offline brute-force and dictionary attacks mathematically unfeasible, even if users choose weak passwords. For enterprise environments, it mandates highly robust encryption (such as GCMP at 192 or 256 bits), locking down modern wireless perimeters against advanced protocol breaches.

## Network Access Control (NAC)

Comprehensive systems for controlling device access to network resources:

- **Device Authentication:** Verifying the identity and security posture of devices before granting network access.
- **Compliance Checking:** Ensuring devices meet security requirements (patches, antivirus, configuration) before network admission.
- **Guest Network Management:** Secure, isolated network access for visitors and temporary users.
- **Quarantine Mechanisms:** Automatically isolating non-compliant devices until security issues are resolved.

## Intrusion Prevention Systems (IPS)

See [Intrusion Detection and Prevention](Intrusion%20Detection%20and%20Prevention.md).

## Network Monitoring and Analysis

Continuous surveillance of network traffic for security threats and performance issues:

- **Deep Packet Inspection (DPI):** Comprehensive analysis of packet contents to identify threats and policy violations.
- **Flow Analysis:** Statistical analysis of network traffic patterns to identify anomalies and trends.
- **Network Forensics:** Detailed investigation of network incidents using captured traffic and log data.
- **Bandwidth and Performance Monitoring:** Tracking network utilization to identify potential security issues or attacks.

## Types of Network Defense

Network defense can be understood in three complementary categories. The goal is not to rely on only one of them, but to combine them so the network can prevent known attacks, identify early warning signs, and reduce damage when an incident succeeds.

- **Preventive Defense:** Used when a type of attack is already known and there are established controls to reduce the probability of compromise. Firewalls, [segmentation](#Micro-Segmentation), [access control](../../02%20Identity%20and%20Access/02%20Authorization%20and%20Access%20Control.md), [hardening](../../01%20Foundations%20and%20Risk/01%20Security%20Principles.md#System%20Hardening), and patching are preventive because they aim to stop the attack before it succeeds.
- **Predictive Defense:** Used when there is still no confirmed breach, but there are early indicators, anomalies, or suspicious patterns that suggest a potential attack. This includes behavioral baselines, anomaly monitoring, reconnaissance detection, and systems such as [Intrusion Detection and Prevention](Intrusion%20Detection%20and%20Prevention.md).
- **Reactive Defense:** Used after the attack has already happened and the focus shifts to containment, impact reduction, service restoration, and learning. This includes isolating compromised systems, preserving evidence, and following formal [Incident Response and Recovery](Incident%20Response%20and%20Recovery.md) procedures.

In practice, mature network security combines all three approaches. Preventive controls reduce exposure, predictive controls improve detection speed, and reactive controls limit blast radius and support recovery.

## Mixed Network Defense

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
