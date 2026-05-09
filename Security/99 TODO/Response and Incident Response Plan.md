# Response and Incident Response Plan

## Introduction

One of the greatest concerns for any organization is, without a doubt, the response time, recovery, and resilience regarding an incident, regardless of its nature. For this response to be satisfactory, certain procedures and plans must be carefully established, tested, and known by everyone. When it comes to cybersecurity, the risks are even higher; therefore, the process must be well-crafted, and the document must be directed toward coordinated action so that risk mitigation occurs in the best possible way.
## Summary

### What is a Security Incident?

A security incident is an event that may indicate that an organization's systems or data have been compromised or that the measures implemented to protect them have failed.

In IT, an **event** is anything that has significance for the system's hardware or software. An **incident**, however, is an event that disrupts normal operations. Security events are generally differentiated by the degree of severity and the potential risk associated with the organization.

For example, if a single user is denied access to a requested service, this might be considered a security event because it could indicate a compromised system, but the access failure could also be caused by many other things. The common factor for most security events, regardless of their cause, is that they typically do not have a severe impact on the organization. However, if many users are denied access, this likely indicates a more serious problem, such as a Distributed Denial of Service (DDoS) attack. Thus, this event can be classified as a security incident due to its damaging impact on operations.

An incident can also be defined as a violation or threat of violation of computer security policies, acceptable use policies, or standard security practices.

### How to Prevent a Security Incident

Common methods and tools used to prevent security incidents include the following:

* **Regularly train employees** to ensure they are familiar with corporate security standards and practices.
* **Use internal and external IT auditors**; regularly review IT security policies and practices to ensure they are up to date, including penetration and vulnerability testing of networks and systems.
* **Ensure security patches** for hardware and software are implemented and constantly updated.
* **Monitor physical facilities**, including secure access to data centers, wiring closets, file cabinets, and other storage areas that may contain sensitive printed documents.
* **Monitor and log user and data activity** across networks, system workstations, and IoT devices. Use real-time automated alerts to detect potential security breaches.
* **Encrypt laptops and mobile devices**, and lock down any equipment lost or stolen in the field.

### How to Respond to a Security Incident

Because security breaches are actually a subset of security incidents, the tools and techniques used to resolve them are similar. In all cases, the goal is to subdue or resolve the incident as quickly as possible.

Below are some common techniques organizations can use to respond to security incidents:

* **Gather the team:** Coordinate the team of security experts who will assess the severity of the incident, communicate with management, and perform mitigation.
* **Identify, assess, and contain the incident:** Identify what was compromised. If a specific network is infected but others are not, isolate the affected network immediately to prevent the infection from spreading. Simultaneously, preserve all data from the infected network for later analysis.
* **Recover and restore:** If systems or networks are so severely affected that they cannot be operated reliably, perform a full disaster recovery and **failover**. *(Failover is a backup operational mode in which the functions of a system component are assumed by a secondary component when the primary component becomes unavailable)*.
* **Notify those affected by the incident:** If customer data was compromised during the incident, notify the affected individuals.
* **Resolve internal issues:** If a malicious act was perpetrated by a company employee, notify Human Resources so that appropriate actions can be taken.
* **Perform a security incident post-mortem:** After the security incident is resolved, analyze what happened, how it happened, and what measures can be taken to prevent similar incidents in the future. Review policies and practices to reflect any changes.
* **Evaluate your team's performance:** How long did it take to detect the incident? How long did it take to resolve? Is there anything that could have been done better?

### Types of Incidents

When discussing types of incidents, they are directly related to specific types of attacks, which can have different origins and response strategies. Cyberattacks have not only become more common but also easier to execute.

According to a report by NETSCOUT Threat Intelligence, there were 4.83 million cyberattacks in the first half of this year alone.

Below are some types of attacks that can become security incidents:

* **Malware-based attacks (ransomware, spyware, viruses, trojans, etc.):** Malware refers to "malicious software" designed to disrupt or steal data from a computer, network, or server. Malware is one of the most commonly used cyberattacks. **Ransomware** is the most utilized and feared malware in organizations in recent years. This type of malware encrypts files on your system so you cannot access them until you pay a "ransom" (usually in cryptocurrency). There was an 1,885% increase in ransomware attacks worldwide starting in 2021.
* **Phishing attacks:** A phishing attack occurs when a cybercriminal sends you a fraudulent email, message, text (called "smishing"), or phone call (called "vishing"). Phishing and smishing messages may instruct you to click a link or open an email attachment that will download malware onto your device or send you to a fake website designed to steal your information. In many cases, phishing attacks cast a wide net and do not target specific individuals. However, there are newer phishing attacks that are more targeted and harder to detect.
* **Man-in-the-middle:** A Man-in-the-Middle (MitM) attack occurs when attackers intercept data or compromise your network to "eavesdrop" on you. These attacks are especially common when using public Wi-Fi networks, which can be easily hacked because they lack strong encryption. For example, if you are using open Wi-Fi to check your bank balance, a hacker could intercept your data and capture your username and password.
* **Denial of Service (DoS) and Distributed Denial of Service (DDoS):** Many cyberattacks aim to overwhelm servers, forcing services to shut down. A Denial of Service (DoS) attack occurs when hackers use fake requests and traffic to overload a system. A Distributed Denial of Service (DDoS) attack is the same, except the hacker uses multiple compromised devices simultaneously.
* **SQL Injection attacks:** Most websites use SQL databases to store sensitive information like logins and passwords. Hackers use an SQL injection attack to "trick" the database into providing this information. These commands can read sensitive data, modify database data, or even add fraudulent functions.
* **Zero-day exploits and attacks:** Zero-day exploits are cybersecurity vulnerabilities that exist in software or a network without the manufacturer's knowledge. Upon discovering the flaw, the attacked company has "zero days" to fix it because it is already vulnerable.
* **IoT Attacks:** Internet of Things devices—like smart speakers, TVs, and toys—can also be targets. An IoT attack occurs when hackers steal data from a device or group multiple IoT devices into a **botnet** to be used for DDoS attacks. Even a "smart fridge" can be an unwitting soldier in a cyberattack.
* **Insider threats:** Cyberattacks often come from external threats, but there is also the possibility of insider threats. These occur when someone working for a company intentionally steals data, provides unauthorized access, or leaks passwords.

---

### Incident Response Plan

An **Incident Response Plan (IRP)** is a document that describes the procedures, steps, and responsibilities of an organization’s incident response program. The goal is to prevent cyberattacks before they happen and minimize the cost and business disruption resulting from any attacks that do occur.

Ideally, an organization defines incident response processes and technologies in a formal IRP that specifies exactly how different types of cyberattacks should be identified, contained, and resolved.

**Incident response planning generally includes the following steps:**

1. **Preparation or Planning:** This first phase is ongoing to ensure the CSIRT (Computer Security Incident Response Team) always has the best procedures and tools to respond. Through regular risk assessments, the CSIRT identifies network vulnerabilities and prioritizes incident types based on potential impact.
2. **Identification, Detection, and Analysis:** The second phase is determining if an incident occurred, its severity, and its type. Monitoring IT assets—endpoints, cloud resources, email, servers, and internal networks—is used to detect abnormal behavior patterns.
3. **Containment:** The goal is to stop the effects of an incident before it causes further damage. During containment, the attack is mitigated, and the team avoids losing evidence that could help identify future attack patterns.
4. **Eradication:** Once the threat is contained, the team moves to full remediation and removal of the threat. This involves destroying malware, booting unauthorized users from the network, and ensuring no traces of the breach remain.
5. **Recovery:** A "lessons learned" meeting should be mandatory after a major incident. When the team is confident the threat is eradicated, they restore systems to normal operations. This may involve deploying patches, rebuilding systems from backups, and bringing systems back online.
6. **Reviews and Documentation:** Throughout every phase, evidence is collected, and the steps taken are documented. This information is critical for preventing and quickly correcting future incidents.

---

### NIST Cybersecurity Framework

The **NIST Cybersecurity Framework**, released in 2014, provides a model for reducing risks to critical infrastructure. It is designed to help organizations understand, manage, and better reduce their cybersecurity risks.

NIST standards are based on international best practices, are technologically neutral, and can be implemented by organizations of all sizes.

The framework includes five core concepts:


*Source: [https://nist.gov](https://nist.gov) (accessed 01/13/2023)*

* **Identify:** Determines how cybersecurity risk is managed, along with which systems, data, and resources are necessary.
* **Protect:** Provides safeguards to contain data security incidents so an organization can continue providing critical services.
* **Detect:** Determines the protocols in place to identify security events.
* **Respond:** Describes the actions to be taken during a cybersecurity incident.
* **Recover:** Identifies what to do after an attack to maintain business continuity and initiate disaster recovery.
