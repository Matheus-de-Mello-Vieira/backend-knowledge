# Network Management

Network management is the broader administrative discipline responsible for keeping a network available, secure, correctly configured, and aligned with business needs.

* It includes planning, configuration, fault handling, performance oversight, accounting, and security control.
* [Monitoring](06%20Network%20Monitoring.md) is one part of network management, not a synonym for it.
* In practice, [monitoring](06%20Network%20Monitoring.md) provides the visibility that management uses to make operational and architectural decisions.

### **The ISO Network Management Model**

The International Organization for Standardization (ISO - /ˈaɪsoʊ/) developed a comprehensive network management model consisting of five key areas (often referred to as FCAPS - /ˌɛf siː eɪ piː ɛs/):

- **F — Fault Management** Logs, detects, and responds to network error conditions, ensuring that errors occurring in the network are treated immediately.
- **C — Configuration Management** Allows administrators to view all devices present on the network, along with their specific hardware and software configurations.
- **A — Accounting Management** Logs and controls the access of users and devices to network resources, such as calculating the consumption of usage quotas.
- **P — Performance Management** Primarily features functions to measure, quantify, notify, analyze, and control the performance of network links, such as routers and terminals.
- **S — Security Management** Controls access to network resources strictly according to defined security policies.

> [!architecture] Architectural Synergy: The AAA Core
> While the FCAPS model splits **Security Management** and **Accounting Management** into separate administrative categories, modern network architecture unifies them using the **AAA framework**. 
> 
> As a network grows in scale and complexity, managing access control locally on every individual node becomes impossible. AAA solves this by centralizing the entire lifecycle: **Authentication** identifies who is on the network, **Authorization** dynamically applies the security policy to their connection, and **Accounting** tracks their resource consumption. It transforms isolated device configurations into a cohesive, network-wide management system.

**The Role of the Administrator and Tools**

- **Asset Tracking and Expertise:** Every asset and node is critical to overall network operation and must be inventoried and understood. A network administrator must know the capabilities, limits, and tradeoffs of the hardware and software in the environment in order to scale and operate it correctly.
- **The Limit of Management Tools:** Tools support administration, but they do not replace the administrator. They provide information and automation hooks, while the administrator remains responsible for interpreting signals, choosing tradeoffs, and applying corrective actions.

### History of Network Management

- **Network Complexity:** A computer network consists of hardware (such as computers, routers, and other physical devices) and software that interact to establish connections using protocols, which translate complex information into something the end-user can understand.
- **The Need for Monitoring:** As more components are added to an environment, the network grows in width and size, increasing the potential for problems and failures. This creates a need to understand the environment's complexity and monitor it to anticipate future issues.
- **The Birth of Network Administrators:** The demand for highly qualified professionals capable of preventing unscheduled media interruptions led to the creation of network administrators. Their first interventions occurred in the 1980s during the early days of computer networks.
- **ARPANET's Experimental Nature:** The first computer network, known as ARPANET, was designed and built based on experimentation.  Because of this, there were no subject matter experts, and the network faced several problems and obstacles, with no hardware or software components being controlled or monitored.
- **The Turning Point (October 27, 1981):** The most severe problem occurred on October 27, 1981, when the network failed. This specific moment was crucial for the emergence of the network management concept.
- **The Incident's Impact:** Because there was no monitoring in place, the incident—a communication error between network protocols—could not be diagnosed quickly, resulting in a prolonged operational outage. It took hours after the discovery of the problem for the involved experts to resolve and correct it.
- **Modern Administrative Responsibilities:** Consequently, network administrators are now required to monitor, manage, and control all components in their computing environment to anticipate incidents and minimize potential service interruptions.
- **Corporate Impact:** If administrative tasks are not performed efficiently, network nodes may fail to communicate, and users may lose connectivity. In a corporate environment, a lack of connectivity makes a company highly uncommunicative, which drastically increases negative organizational indicators.
- **Tool Evolution:** Over the years, network management tools have evolved, with each tool becoming specialized in a specific management area.

## Relationship to Monitoring

Monitoring is one operational mechanism inside network management:

* **Management** defines what must be controlled, why it matters, and which actions are available.
* **Monitoring** collects the measurements, events, and alerts that reveal the current state of the network.
* Good management depends on good monitoring, but also includes configuration, access control, policy, capacity decisions, and incident response.
## Network Operations Center (NOC)

A Network Operations Center (NOC) is a dedicated engineering unit tasked with monitoring and managing corporate network infrastructure. Composed of network engineering specialists, a NOC ensures infrastructure uptime, stability, and adherence to Service Level Agreements (SLAs).

The primary responsibilities of a NOC encompass:

* Tracking throughput, latency, and packet performance across data and VoIP networks.
* Managing critical storage and recovery infrastructure, including [Network-Attached Storage (NAS)](../Operating%20Systems/06%20Storage%20Management.md#Network-Attached%20Storage%20(NAS)) and Disaster Recovery (DR) systems.
* Preventing downtime and link saturation through real-time traffic analysis and active load balancing.

Organizations lacking the resources to sustain a 24/7 internal network infrastructure team frequently utilize outsourced NOC providers to maintain operational availability.
