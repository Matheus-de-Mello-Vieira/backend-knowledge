# Windows Endpoint Security

Microsoft Windows provides a comprehensive security ecosystem designed to protect endpoints through multiple layers of defense. Understanding these tools and their integration is crucial for securing Windows-based infrastructure effectively.

### **Zero Trust Implementation in Windows**

Microsoft integrates [Zero Trust Architecture](../02 Identity and Access/03 Zero Trust Architecture.md) principles through Azure Active Directory, Conditional Access policies, and Microsoft 365 security features that work together to verify identity, device health, and application integrity before granting access to corporate resources.

**Windows-Specific Zero Trust Features:**
- **Azure Active Directory Integration:** Centralized identity management with conditional access policies
- **Device Compliance Policies:** Automated assessment of device security posture before granting access
- **Microsoft Intune Integration:** Mobile device management and application protection policies
- **Windows Hello for Business:** Passwordless authentication using biometrics and hardware tokens

### **Microsoft Defender Antivirus**

- **Definition:** Microsoft Defender Antivirus is a built-in, real-time protection solution that comes standard with Windows 10 and Windows 11, designed to defend against viruses, malware, spyware, and other security threats.
- **Real-Time Protection Features:**
  - **Always-On Scanning:** Continuously monitors file system activity, downloads, and program execution.
  - **Background Scanning:** Performs automatic scans during system idle times to minimize performance impact.
  - **Boot-Time Protection:** Scans the system during startup before other applications can load.
- **Detection Methods:**
  - **Signature-Based Detection:** Uses a database of known malware signatures to identify threats based on unique code patterns.
  - **Behavior-Based Detection:** Monitors application behavior and system changes to identify suspicious activities that may indicate unknown threats.
  - **Cloud-Powered Intelligence:** Leverages Microsoft's global threat intelligence network to provide real-time protection against emerging threats, often detecting new malware variants within milliseconds of discovery.
- **Microsoft Defender Ecosystem Integration:** Works seamlessly with Microsoft Defender for Endpoint, Microsoft 365 Defender, and Azure Sentinel to provide enterprise-grade threat detection and response capabilities.

### **Microsoft Defender and Encryption**

Microsoft Defender works in conjunction with Windows encryption technologies to provide comprehensive data protection. For detailed information about encryption concepts and key management, see [Cryptography and Data Protection](../03 Cryptography and Data Protection/01 Cryptography.md).

**Windows-Specific Encryption Integration:**
- **BitLocker Integration:**
  - **Full Disk Encryption:** BitLocker encrypts entire drives using AES encryption to protect against data theft
  - **TPM Integration:** Trusted Platform Module provides hardware-based key protection and secure boot
  - **Recovery Key Management:** Azure Active Directory integration for enterprise key recovery
- **EFS (Encrypting File System) Protection:**
  - **File-Level Encryption:** Transparent encryption for individual files and folders at the NTFS level
  - **Certificate-Based Keys:** Uses public key cryptography for file encryption keys
  - **Ransomware Defense:** Provides additional protection layer against ransomware attacks

### **Windows Defender Firewall**

- **Definition:** Windows Defender Firewall is a host-based firewall that monitors and controls incoming and outgoing network traffic based on predetermined security rules.
- **Traffic Control Mechanisms:**
  - **Packet Filtering:** Examines individual network packets and allows or blocks them based on source/destination addresses, ports, and protocols.
  - **Stateful Inspection:** Tracks the state of network connections and makes decisions based on connection context and history.
  - **Application-Based Rules:** Controls network access on a per-application basis, allowing granular control over which programs can access the network.
- **Firewall Profiles:**
  - **Domain Profile:** Applied when connected to a domain network (corporate environment). Typically allows more network services and has specific rules for domain resources.
  - **Private Profile:** Used for trusted private networks (home networks). Provides moderate security with some network discovery enabled.
  - **Public Profile:** The most restrictive profile for untrusted networks (public Wi-Fi, airports). Blocks most inbound connections and limits network discovery.
- **Network Segmentation Role:** Works with Group Policy and enterprise management tools to create network zones, isolate critical systems, and prevent lateral movement during security incidents.

### **Application Guard and Microsoft Defender SmartScreen**

#### **Microsoft Defender Application Guard**
- **Definition:** A hardware isolation security feature that uses virtualization-based security (VBS) to isolate untrusted websites and documents in a secure container.
- **Virtualization-Based Isolation:**
  - **Hyper-V Container:** Creates an isolated virtual machine specifically for running untrusted content.
  - **Hardware Requirements:** Requires modern processors with virtualization support and sufficient RAM for container creation.
  - **Resource Management:** Automatically manages container lifecycle, creating and destroying isolated environments as needed.
- **Untrusted Website Protection:** When users navigate to potentially dangerous websites, Application Guard opens them in an isolated browser instance that cannot access the host operating system or corporate network resources.

#### **Microsoft Defender SmartScreen**
- **Definition:** A cloud-based anti-phishing and anti-malware component that helps protect users from malicious websites, downloads, and applications.
- **Malicious Download Protection:**
  - **File Reputation Analysis:** Checks downloaded files against a global reputation database before execution.
  - **URL Reputation:** Evaluates website URLs in real-time to identify phishing sites and malware distribution points.
  - **Behavioral Analysis:** Monitors download patterns and user behavior to identify potential social engineering attacks.
- **Application and Website Reputation System:**
  - **SmartScreen Filter:** Analyzes website content, URL patterns, and user reports to maintain an updated reputation database.
  - **Application Reputation:** Checks executable files and applications against known good and bad software databases.
  - **User Feedback Integration:** Incorporates user reports and Microsoft's global telemetry to improve threat detection accuracy.

### **Windows Defender Credential Guard**

- **Definition:** A virtualization-based security feature that isolates secrets so that only privileged system software can access them, protecting against credential theft attacks.
- **Virtualization-Based Security (VBS):**
  - **Secure Kernel:** Uses the Windows hypervisor to create a secure environment that is isolated from the normal operating system.
  - **Hardware Requirements:** Requires UEFI firmware, Secure Boot, and modern processors with virtualization extensions (Intel VT-x or AMD-V).
  - **Memory Protection:** Utilizes hardware features like SMEP (Supervisor Mode Execution Prevention) and SMAP (Supervisor Mode Access Prevention) for additional security.
- **System Credential Protection:**
  - **NTLM Hash Protection:** Prevents the storage of NTLM password hashes in the Local Security Authority (LSA) process memory.
    - *NTLM (NT LAN Manager): Microsoft's legacy challenge-response authentication protocol that uses MD4 password hashes*
  - **Kerberos Ticket Protection:** Secures Kerberos Ticket Granting Tickets (TGTs) in the isolated environment.
  - **Certificate Protection:** Protects private keys and certificates used for authentication.
- **Attack Mitigation:**
  - **Pass-the-Hash Prevention:** By isolating NTLM hashes, attackers cannot extract and reuse them even with administrative privileges.
  - **Pass-the-Ticket Prevention:** Kerberos tickets are protected in the secure environment, preventing their theft and reuse.
  - **Golden Ticket Defense:** Makes it significantly harder for attackers to create forged Kerberos tickets for persistent access.
  - **Memory Dumping Protection:** Prevents credential harvesting tools like Mimikatz from accessing secrets stored in memory.
