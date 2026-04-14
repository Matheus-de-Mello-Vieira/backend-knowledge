# Network Management

- **Purpose of Monitoring:** Computer networks are complex structures that must be constantly monitored to minimize problems such as network unavailability, slowness, and congestion.
- **Definition:** This continuous monitoring practice is known as network management.
- **Asset Tracking:** It involves monitoring all active assets within the environment to thoroughly understand their technical characteristics, capacities, applicability, and overall performance.
- **Data Analysis:** Beyond the existing hardware and software, the task of network management includes understanding all types of information circulating on the network to determine the total volume of data flowing through the environment.
- **Proper Scaling:** Effective network management allows for the correct scaling of network components to prevent potential issues.

### **The ISO Network Management Model**

The International Organization for Standardization (ISO - /ˈaɪsoʊ/) developed a comprehensive network management model consisting of five key areas (often referred to as FCAPS - /ˌɛf siː eɪ piː ɛs/):

- **F — Fault Management** Logs, detects, and responds to network error conditions, ensuring that errors occurring in the network are treated immediately.
- **C — Configuration Management** Allows administrators to view all devices present on the network, along with their specific hardware and software configurations.
- **A — Accounting Management** Logs and controls the access of users and devices to network resources, such as calculating the consumption of usage quotas.
- **P — Performance Management** Primarily features functions to measure, quantify, notify, analyze, and control the performance of network links, such as routers and terminals.
- **S — Security Management** Controls access to network resources strictly according to defined security policies.

**The Role of the Administrator and Tools**

- **Asset Tracking and Expertise:** Every asset and node is critical to the overall network performance and must be properly tracked and monitored. A network administrator must have in-depth knowledge of each piece of hardware, including its capabilities, advantages, disadvantages, and limitations, to scale the equipment accurately.
- **The Limit of Management Tools:** While network tools support administrative tasks, they do not replace the administrator. Tools provide a foundation for making decisions and taking action, but they cannot independently resolve service outages. Administrators must know exactly how and where to apply these tools to achieve maximum efficiency and effectiveness in their computing environment.

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

Here are the structured notes regarding the Protocol Analysis and Types of Analyzers section, translated into English:

### Protocol Analysis

- **Definition:** A protocol analyzer is a tool used to observe and capture information traffic within a network.
- **How it works:** The device's network interface intercepts and captures all valid packets transmitted on the physical communication medium so they can be analyzed by the application.
- **Packet Decoding and Parsing:** The analyzer automatically pre-groups the captured data based on its communication protocol. The process of taking these raw network packets—which travel across the network simply as streams of bits—and translating them into a readable, useful format for the administrator is known as packet decoding or parsing. 
- **Advantages and Metrics:** The tool allows network managers to accurately measure average network traffic in real-time, understand what users are using the network for, and identify which hosts are moving the most data at the moment.
- **Decision Making:** This information provides a complete view of the environment, allowing for corrective and preventive administrative decisions, such as network expansion, content blocking, and ensuring information security.
- **Physical Requirement:** To function, the analyzer must be connected directly to the same physical network (host) that you want to monitor or spy on.
- **Common Tools:** Most of these tools are free downloads, with the most well-known being Wireshark, TCPDUMP, and IPTRAF.

### Types of Protocol Analyzers

#### **1. Wireshark**

- It is a widely used, free protocol analyzer with versions available for Windows, MAC OS X, Linux, and Unix platforms.
- It works across all layers of the TCP/IP stack and features a *sniffer* tool, allowing real-time packet capture for further analysis.
- The captured files are processed in the *pcap* format, as the tool is also based on *libcap* and *tcpdump*.
- **Main Advantage:** It displays captured packets in detail through a real-time graphical interface and includes features for deep log inspection.
- **Attention:** In most cases, it is not recommended to use the capture feature simultaneously with packet analysis, as this can affect the resources of the machine being used.

**Note:** For practical, step-by-step examples of how to use Wireshark and tcpdump to diagnose backend latency, TLS handshakes, and TCP window issues, see [Troubleshooting Performance](03%20Troubleshooting%20Performance.md).

#### **2. Tcpdump**

- **Description:** A powerful, command-line packet capture utility designed for Unix-based systems.

- **How it Works:** It operates by placing the host's network interface card (NIC) into promiscuous mode, allowing it to intercept, capture, and translate raw TCP/IP network traffic passing through that interface.

- **Data Storage and Analysis:** Captured traffic is typically saved to a file so it can be standardized, forwarded to a relational database, or opened in graphical tools (like Wireshark) to easily locate necessary information for later analysis.

- **Command Example:**

  ```bash
  tcpdump -i ens33 -c 200 -nn "tcp or udp" -w capture.pcap
  ```

  *(Note: Using the `-w capture.pcap` flag correctly writes the raw binary packet data to a file. Do not use the `>` operator, as it only saves the plain-text terminal output, which cannot be opened by graphical analyzers later).*

#### **3. IPTraf**

- **Description:** A monitoring platform designed to act as a query source for analyzing the characteristics of network flows across IP backbones.
- **Architecture:** The system utilizes a distributed architecture consisting of collector modules and associated analysis tools. In practice, edge routers export the collected network data flows to the Collector module hosted on the IPTraf server.
- **Anomaly Detection:** The server processes this flow to generate metadata, which is then utilized by downstream tools to detect network anomalies.
- **Unified Monitoring:** Finally, the Guardian system integrates these anomaly detection tools and alerts, providing administrators with a single, centralized monitoring interface.
