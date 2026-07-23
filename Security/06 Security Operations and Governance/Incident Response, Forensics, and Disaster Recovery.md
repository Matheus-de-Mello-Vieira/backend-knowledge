# Incident Response, Forensics, and Disaster Recovery

## Introduction to Cybersecurity Resilience

While prevention is a critical first step, modern cybersecurity is built on the principle of resilience: the ability to not only withstand an attack but to effectively bounce back from one. Relying solely on "building higher walls" is no longer sufficient; organizations must operate under the assumption that a breach will eventually occur.

### Core cybersecurity lifecycle
The core cybersecurity lifecycle transforms "emergency mode" into a structured, repeatable process. By following these stages, an organization ensures that its response to a crisis is calculated rather than chaotic:

1. [**Prepare**](#Preparation): This phase is an ongoing effort to ensure the organization has the necessary tools, procedures, and personnel ready before an incident occurs.
2. [**Detect**](#Identification,%20Detection,%20and%20Analysis): Detection involves identifying abnormal behavior patterns across IT assets, including cloud resources and internal networks.
3. [**Containment**](#Containment): Once a threat is identified, the primary goal is to stop its effects before it causes further damage.
4. [**Investigate**](#Digital%20Forensics): Investigation, or digital forensics, focuses on discovering and interpreting electronic data to reconstruct past events.
	- [**Evidence Preservation**](#Evidence%20Preservation%20During%20Incidents): Creating "bit-for-bit" forensic images of affected storage devices while maintaining a strict [**chain of custody**](#Chain%20of%20custody) for legal admissibility.
	- [**Live Analysis**](#Volatile%20evidence): Extracting volatile data from RAM (like active network connections) before a system is shut down and the evidence is lost.
5. [**Recover**](#Recovery): Recovery focuses on returning systems to normal operations safely and with minimal loss.
6. [**Improve**](#Lessons%20Learned%20and%20Documentation): The lifecycle is only complete when the organization turns the failure into a learning opportunity, for example with [**Post-Mortem Analysis**](#Post-mortem%20analysis) and [**Plan Updates**](#Preventing%20recurrence)
### Why organizations need formal plans

Organizations need formal plans because incidents create time pressure, uncertainty, and competing priorities.
* [Cybersecurity Governance](../01%20Foundations%20and%20Risk/04%20Cybersecurity%20Governance.md) defines who can escalate decisions and lead crisis communications
* [Risk Management and Threat Modeling](../01%20Foundations%20and%20Risk/02%20Risk%20Management%20and%20Threat%20Modeling.md) helps prioritize the systems and business functions that matter most.
* Formal plans also support [Legal Frameworks and Compliance](Legal%20Frameworks%20and%20Compliance.md) by documenting notification duties, evidence handling, and recovery accountability so the response is coordinated, defensible, and repeatable.

## Events, Incidents, and Disasters

Distinguishing between these three terms is essential for determining the appropriate level of response and the specific resources required to maintain business continuity.

* **Security Event**: A security event is any occurrence that has significance for an organization's hardware or software.
	* These are typically minor and do not cause severe impacts on the organization.
	* For example, a single user being denied access to a requested service is a security event.
	* While it could indicate a deeper issue, it is often just a signal that requires monitoring rather than an immediate emergency response.
* **Security Incident**: An incident is a specific type of event that actively disrupts normal operations or violates computer security policies.
	* The key differentiator between an event and an incident is the degree of severity and the potential risk to the organization.
	* If the previous example of a login failure escalated into a Distributed Denial of Service (DDoS) attack that blocked access for many users, it would be reclassified as a security incident due to its damaging impact.
	* See the most [common type of threats](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md).
* **Disaster**: A disaster is a serious event of any nature—natural, physical, or technological—that negatively affects operations and the business life cycle. Unlike a standard incident, a disaster is significant enough to completely disrupt critical business operations for an unmeasured period.
	- **Natural Disasters**: Events like fires, floods, or pandemics that often require changes to workflow and infrastructure.
	- **Physical Disasters**: Incidents such as power loss, structural failure, or terrorism that may require relocating personnel and technology.
	- **Technological Disasters**: Large-scale failures such as ransomware attacks or hardware failures that require a high degree of expertise to mitigate.

While incidents are managed through an **[Incident Response Plan (IRP)](#Incident%20Response%20Plan)**, disasters require a formal [Disaster Recovery Plan (DRP)](#Disaster%20Recovery%20Plan) to regain the use of [critical IT infrastructure](Critical%20Infrastructure%20Security.md) as quickly as possible.

## Categories of Security Disasters
### Natural disasters

Environmental disruption affecting operations or facilities.

- **Adaptation Strategies**: When dealing with natural disasters, the focus is generally on infrastructure preservation, potential relocation, and implementing new methods of working.
- **Workflow Modifications**: A primary example is a pandemic; while the physical technology (routers, servers, workstations) may remain functional, the organization's daily routine and workflow must be modified to ensure continuity.
- **Common Examples**: This category includes fires, storms, floods, hurricanes, tornadoes, and pandemics.

### Physical disasters

Facility or infrastructure failure affecting system availability.

- **Operational Flexibility**: Depending on the severity, a physical disaster—such as a power outage—may only require employees to work from home for a short period.    
- **Resource Relocation**: For more severe structural issues, organizations may be forced to relocate both their personnel and their entire technological infrastructure to a secondary site.
- **Continuity Planning**: It is essential to understand not only how to recreate work environments temporarily but also to determine exactly how long these temporary measures can be maintained.
- **Common Examples**: Key physical disasters include power loss, structural failure, extreme temperature fluctuations, physical intrusions, and terrorism.

### Technological disasters

Technology-driven outage or destructive compromise.

- **High Probability**: These are statistically the most likely disasters an organization will face.
- **Management Complexity**: They vary in impact and typically require a high level of technical expertise to plan for, control, and mitigate effectively.
- **Cyberattack Integration**: This category includes a broad range of malicious activities that have become increasingly common and easier to execute, including [Ransomware](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#Ransomware), [Phishing](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#Phishing), and [Man-in-the-Middle (MitM)](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#Man-in-the-Middle%20%28MitM%29) attacks.
- **Comprehensive Examples**:
    - **Malware-based Attacks**: [Ransomware](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#Ransomware), [Spyware](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#Spyware), and [Computer Viruses](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#Computer%20Viruses) designed to steal or encrypt data.
    - **Infrastructure Failures**: [Hardware and Power Failures](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#Hardware%20and%20Power%20Failures) and network infrastructure collapses.
    - **Network Attacks**: [DoS (Denial of Service)](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#DoS%20%28Denial%20of%20Service%29), [DDoS (Distributed Denial of Service)](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#DDoS%20%28Distributed%20Denial%20of%20Service%29), and [Injection Attacks](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#Injection%20Attacks) that overwhelm or compromise databases.
    - **Modern Threats**: [Zero-Day Vulnerabilities](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#Zero-Day%20Vulnerabilities), IoT device compromises, and intentional [Insider Threats](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#Insider%20Threats).

---
## Incident Response Plan

### What an Incident Response Plan is

An **Incident Response Plan**, or **IRP**, is a formal document that describes the procedures, steps, and responsibilities involved in an organization’s incident response program. It serves as a coordinated roadmap to ensure that when a security event disrupts normal operations, the organization can react with speed and precision.

### Purpose of an IRP

The primary objective of an IRP is to minimize the cost, damage, and business disruption resulting from a cyberattack or technical failure. It focuses on several key functional goals:

* **Speed and Agility**: Ensuring the organization can regain use of critical systems and IT infrastructure as quickly as possible after a disaster.
* **Coordinated Action**: Defining a structured process so that security experts, management, and other departments act in unison rather than in isolation.
* **Evidence Handling**: Preserving digital evidence in its most original form—such as capturing volatile RAM data before a shutdown—to ensure it remains admissible for forensic analysis or legal proceedings.
* **Controlled Restoration**: Facilitating a recovery process that identifies the root cause of a breach, ensuring the "gap" is patched before systems are brought back online to prevent immediate re-incidence.

### Roles and Responsibilities

Organizing your response strategy into two distinct groups—the broader **IRT** and the technical **CSIRT**—clarifies who manages the business impact versus who handles the technical "firefighting."

#### **Incident Response Team (IRT)**

The IRT is a cross-functional group responsible for the high-level management, coordination, and non-technical decision-making during a crisis. This team ensures the business remains resilient and compliant throughout the incident lifecycle.

- **Management**: Provides the necessary resources and leadership to execute the plan. They are responsible for coordinating the overall disaster recovery process and ensuring that all departments are aligned with the response goals.
- **Legal Counsel**: Manages regulatory requirements and ensures that all actions, particularly evidence collection, follow legal guidelines to maintain a proper **chain of custody**.
- **Communications**: Acts as the primary point of contact for internal stakeholders, customers, partners, and the media. Their goal is to manage the flow of information to prevent brand damage and provide transparency.
- **Human Resources**: Involved when an incident is linked to an "insider threat" or a malicious act by an employee, ensuring that internal personnel policies are followed.
#### **Computer Security Incident Response Team (CSIRT)**

The CSIRT is the specialized, technical arm of the response effort. They are the "front line" staff who possess the expertise to identify, analyze, and neutralize digital threats directly.

- **Security Analysts**: Monitor IT assets (endpoints, cloud resources, and networks) to identify abnormal behavior patterns and determine the severity of a potential incident. They also perform [forensic analysis](#Forensic%20techniques) to understand the attack's scope. 
- **System Administrators**: Responsible for the technical containment of the threat, such as isolating infected networks or terminating malicious processes. They also handle the **recovery** phase by rebuilding systems from backups and deploying security patches.
- **Threat Hunters**: Proactively search for indicators of advanced threats (APTs) that may have evaded automated detection systems.
- **Forensic Specialists**: Focus on preserving the "crime scene" by performing **memory imaging** and capturing volatile data before it is lost due to a system shutdown.
### Severity Levels

To prioritize resources, incidents are classified using a practical severity model based on impact and urgency:

- **Low**: Minor event with limited impact; typically handled through standard procedures.
- **Medium**: Confirmed issue affecting a single system or specific user group; requires active mitigation.    
- **High**: Major incident affecting critical systems or sensitive data; requires the full IRT (Incident Response Team).
- **Critical**: Business-wide disruption, large-scale data breach, or active compromise of the entire infrastructure.

The IRP must define clear criteria for when an incident should be escalated to higher management or specialized teams:

* **Defined Thresholds**: Triggers for escalation based on severity level, potential financial impact, or regulatory significance.
* **Approval Paths**: Explicitly stating who has the authority to approve high-impact actions, such as disconnecting a production database from the network.
* **Communication Chains**: Ensuring the right people are informed at the right time to avoid response delays.

### Communication Plan

Effective communication prevents panic and preserves the organization's reputation. The plan defines paths for:

* **Internal Stakeholders**: Keeping employees and leadership updated on the status of the response.
* **Customers & Partners**: Notifying those whose data or services may be compromised as a result of the incident.
* **Regulators & Law Enforcement**: Providing mandatory reports to comply with data protection laws and assisting in criminal investigations.
* **Public/Media**: Using pre-defined strategies to manage the external narrative of the incident.

### Playbooks

The IRP references specialized playbooks that provide step-by-step instructions for common scenarios:

* **[Malware](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#Malware) & [Ransomware](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#Ransomware)**: Steps for isolating infected segments and restoring from offsite backups.
* **[DDoS](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#DDoS%20%28Distributed%20Denial%20of%20Service%29) Attacks**: Procedures for filtering malicious traffic and maintaining service availability.
* **Data Leaks/[Phishing](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#Phishing)**: Methods for containing compromised credentials and identifying the extent of data exfiltration.
* **Post-Mortem Analysis**: Standardized procedures for a "lessons learned" meeting to refine the IRP after an incident is resolved.
## Incident Response Lifecycle

The **Incident Response Lifecycle** provides a structured, standardized framework for handling active attacks and mitigating damage. Because threat actors are increasingly sophisticated, organizations must move beyond simple prevention and focus on **resilience**—the ability to identify, contain, and recover from an event with minimal loss. This lifecycle is not a one-time reaction but a continuous process designed to turn every security failure into a learning opportunity.

Effective execution of this lifecycle requires a cross-functional [Incident Response Team (IRT)](#Incident%20Response%20Team%20%28IRT%29), comprising security analysts, system administrators, legal counsel, and management representatives. By following a calculated approach—even under the pressure of an active breach—the team can reduce human error and ensure that the response is organized and thorough.

The lifecycle typically revolves around several core functional goals:

- **Minimizing Impact**: Reducing the cost and business disruption caused by any attack that occurs.
- **Structured Resolution**: Using pre-defined playbooks to ensure every phase of the incident is addressed systematically.
- **Forensic Preservation**: Balancing the need to stop an attack with the preservation of volatile data (like RAM) necessary for a proper root cause analysis.
- **Continuous Improvement**: Conducting post-incident reviews to ensure the same vulnerability cannot be exploited twice.

The following sections detail the specific phases of the lifecycle, as defined by industry standards such as the [NIST Cybersecurity Framework](#NIST%20Cybersecurity%20Framework) and [ISO 22301](#ISO%2022301).

## Preparation

The **Preparation** phase is the foundational stage of the Incident Response Lifecycle. It is an ongoing, proactive process designed to ensure that the organization is ready to respond effectively before a security incident or disaster occurs.

### Key Objectives

- **Readiness and Tools**: Ensuring the [**Computer Security Incident Response Team (CSIRT)**](#Computer%20Security%20Incident%20Response%20Team%20%28CSIRT%29) or [**Incident Response Team (IRT)**](#Incident%20Response%20Team%20%28IRT%29) has the best procedures, tools, and expertise available to respond to a crisis.
- **Vulnerability Identification**: Using regular risk assessments to identify network vulnerabilities and prioritize potential incident types based on their potential business impact.
- **Standardization**: Establishing documented outlines and [playbooks](#Playbooks) to guide detailed steps and reduce human error during high-stress situations.

### Essential Preparatory Activities

- **Defining Scope and Objectives**: Outlining exactly which assets, structures, and services require protection and identifying the critical needs of each department.
- [**Risk & Impact Analysis**](#Risk%20Analysis%20and%20Business%20Impact%20Analysis): Evaluating potential hazards and quantifying the maximum tolerable downtime through Business Impact Analysis (BIA).
- **Team Assembly**: Appointing a planning commission or a cross-functional IRT that includes security analysts, system administrators, legal counsel, and management.
- **Management Involvement**: Securing the support and involvement of senior management to coordinate the planning process and ensure it is effective organization-wide.
- **Preventive Security Measures**: Implementing controls to minimize the likelihood of an incident, such as:
    - Regular employee training on security standards.
    - Implementing and constantly updating security patches.
    - Monitoring and logging user and data activity across the network.
    - Encrypting mobile devices and laptops.
- **Documentation**: Creating a formal [Disaster Recovery Plan](#Disaster%20Recovery%20Plan) (DRP), [Incident Response Plan](#Incident%20Response%20Plan) (IRP) and [**Communication Plan**](#Communication%20Plan) that outline specific responsibilities.
	- **Testing**: Evaluate the documentation regularly—at least annually—to ensure all necessary steps are functional.
- [**Training**](#Standards%20and%20Frameworks): Regularly educating employees on security standards to reduce human error.
---

## Identification, Detection, and Analysis

Once the preparation is in place, the organization enters the active phase of the lifecycle: determining if a threat exists and understanding its scope. This stage is a transition from passive monitoring to an active investigation, where the goal is to confirm whether a security **event**—anything significant to hardware or software—has crossed the threshold into a security **incident** that disrupts normal operations.

### Detection: Finding the Signal in the Noise

Detection is the first line of defense, relying on constant surveillance to spot abnormal behavior patterns across endpoints, cloud resources, email, and internal networks.

- [Security Information and Event Management (SIEM)](#SIEM): These centralized systems perform log aggregation from firewalls, servers, and applications, using automated correlation rules to identify patterns that might seem unrelated to the naked eye.
- [Security Operations Center (SOC)](#Security%20Operations%20Center): A dedicated team provides 24/7 monitoring, performing tiered analysis that starts with event triage (Level 1) and escalates to advanced threat analysis (Level 3).
- **Threat Hunting**: This is a proactive search for indicators of compromise (IOCs) or advanced persistent threats (APTs) that may have successfully evaded automated detection tools.
### Identification and Triage

Not every alert is a crisis. Identification involves determining the severity and type of the incident to ensure the response is proportionate.

- **Event vs. Incident**: A single denied access attempt may be a security event, but a massive spike in denied access (like a DDoS attack) is classified as a security incident due to its impact on operations.
- **Evidence Scoping**: Investigators must identify what evidence is present, where it is stored (e.g., hard drives, cloud services, or mobile devices), and what format it is in.
- **Diagnostic Visibility**: Without diagnostic tools, it is impossible to isolate or recover a system; the team must first understand exactly which part of the infrastructure is under attack and how the breach occurred.

### Analysis

Analysis is the deep-dive phase where the team pieces together fragments to prove or refute a security case.

- **Live Forensics**: Crucial data, such as active network connections and running processes, exists only in **RAM (Volatile Memory)**. Analysts must capture this data while the system is still running, as a "hard shutdown" can destroy the very evidence needed for a full investigation.
- **Timeline Analysis**: Investigators reconstruct the sequence of events to understand the progression of the attack and its ultimate impact on the business.
- **Behavioral and TTP Analysis**: Security teams analyze the tactics, techniques, and procedures (TTPs) used by the attacker to create a profile of the threat actor and prevent future similar attacks.

The accuracy of this phase is critical; if the analysis is flawed, the subsequent **Containment** steps may fail to stop the spread of the threat or inadvertently tip off the attacker.

### Malware Analysis

Malware analysis determines whether a suspicious file or artifact is malicious, what it does, and how far the compromise may have spread. Never execute a suspicious sample in production; preserve the original, record its hash, and work from controlled copies.

- **Static analysis**: Inspect file properties, metadata, hashes, strings, and threat-intelligence results without running the sample.
- **Dynamic analysis**: When necessary, observe the sample only in an isolated sandbox to identify process, file-system, and network behavior.
- **Response outcome**: Use the resulting indicators and observed behavior to scope the incident, guide containment and eradication, and escalate advanced reverse engineering to specialist responders when needed.

For endpoint capabilities that support this work—NGAV/EDR behavioral detection, cloud sandboxing, quarantine, and automatic host isolation—see [NGAV, EDR, and XDR](../05%20Architecture%20and%20Infrastructure%20Security/NGAV,%20EDR,%20and%20XDR.md.md#Behavioral%20Analysis%20and%20Cloud%20Integration).

## Containment

The **Containment** phase is a critical turning point where the focus shifts from observation to active mitigation. The primary goal is to stop the effects of an incident before it causes further damage while simultaneously ensuring that the team avoids losing evidence that could help identify future attack patterns. During this stage, the attack is actively neutralized, and specific components are "cut off" to protect the remaining infrastructure.

### Strategic Isolation Methods

Effective containment relies on a clear understanding of the project's architecture to identify trust boundaries and isolate compromised segments. Common strategies include:

- **Network Isolation**: Immediately disconnecting compromised systems from the network to prevent lateral movement to other segments.
- **Account Isolation**: Disabling compromised user accounts and related access credentials to prevent the attacker from maintaining access.
- **Process Isolation**: Terminating malicious processes while carefully preserving the underlying evidence for forensic analysis.
- **Service Isolation**: Taking affected services offline while maintaining business continuity through redundant systems or failover modes.

### The Forensic Dilemma: Isolation vs. Shutdown

A major challenge during containment is the tension between stopping the attack and preserving the data necessary to understand it. While a "hard shutdown" (unplugging a server) stops immediate data exfiltration, it can also lead to the permanent loss of volatile data.

- **Volatile Data Loss**: Critical footprints—such as active network connections, running processes, and decrypted encryption keys—often exist only in the system's **RAM (Volatile Memory)**.
- **The Risk of Blindness**: Shutting down prematurely can leave the security team "blind," making it impossible to determine how the attacker gained entry, what other systems they touched, or if they left a "backdoor" for a future return.
- **A Balanced Approach**: Security professionals often recommend isolation via firewall or network disconnection as a middle ground. This stops the "leak" or communication with the attacker's command-and-control server while keeping the "crime scene" intact for diagnostics and live forensics.

By using these controlled isolation techniques, the team ensures that the incident is contained without sabotaging the subsequent **Eradication** and **Analysis** phases.

## Eradication

Once the threat has been successfully contained, the organization moves into the **Eradication** phase. The primary goal of this stage is the full remediation and permanent removal of the threat from the environment. It is a deep-cleaning process designed to ensure that no traces of the breach remain that could allow an attacker to regain access.

During eradication, the [Incident Response Team (IRT)](#Incident%20Response%20Team%20%28IRT%29) executes specific technical actions based on the findings from the **Analysis** phase:

- **Threat Removal**: This involves destroying identified malware, viruses, or worms and deleting malicious artifacts left behind by the attacker.
- **Access Revocation**: Security teams must boot unauthorized users from the network and invalidate any compromised credentials.
- **System Sanitization**: In many cases, this requires a complete wipe and rebuild of affected systems to guarantee that hidden backdoors or persistent malicious code are fully eliminated.
- [**Root Cause Analysis (RCA)**](#Root%20Cause%20Analysis): Eradication is not just about removing the symptoms of an attack; it is about curing the underlying "disease".
By ensuring that both the attacker and the vulnerability are removed, the organization can move toward the **Recovery** phase with confidence that the system's integrity has been restored.
## Recovery

The **Recovery** phase focuses on identifying the necessary actions to maintain business continuity and initiate disaster recovery after an attack. During this stage, the organization restores systems to normal operations only after the team is fully confident that the threat has been eradicated.

Restoring operations safely depends on robust backup mechanisms and a calculated approach to prevent further disruption:

- **System Restoration**: This may involve rebuilding systems from clean backups and bringing them back online in a controlled manner.    
- **Patch Deployment**: Before a system is fully operational, security teams must deploy necessary patches to ensure the environment is no longer vulnerable.
- **Failover and Failback**: If primary systems were severely affected, the organization may use **failover**—a backup operational mode where secondary components assume the functions of the primary system—until reliable operations can be resumed on the main infrastructure.
---
## Lessons Learned and Documentation

The goal of this final phase is to turn a security failure into a strategic learning opportunity to strengthen the system's overall resilience. By documenting every step taken and evidence collected, the organization ensures it has the necessary data to prevent and quickly correct future incidents. This phase is considered mandatory after any major incident to drive verified follow-up improvements and ensure the recovery process is truly complete.

### Lessons learned content to include

A comprehensive "lessons learned" report must go beyond a simple summary to include granular details that inform future strategy:

- **Timeline Reconstruction**: Reconstructing the sequence of events to understand exactly how the attack progressed and how the response unfolded.
- **Root Cause**: A definitive identification of the technical or procedural "gap" that allowed the breach to occur.
- **Impact Assessment**: A detailed analysis of the damage to operations, finances, brand reputation, or data integrity.
- **Response Quality**: Evaluation of the team's performance, specifically measuring metrics like Mean Time to Detection (MTTD) and Mean Time to Response (MTTR).
- **Concrete Follow-up Actions**: A list of specific remediation steps, such as patching vulnerabilities or updating outdated security standards.

### Governance and Risk Integration

Post-incident findings are a critical feedback loop for the organization's broader security posture. Findings should be integrated into the following areas:

- **Governance Reviews**: Use the results to update corporate security policies and standard practices to reflect the "real-world" friction points encountered during the incident.
- **Control Owners**: Assign responsibility to management and technical leads to ensure that identified gaps are closed and that new safeguards are effective.
- **Risk Register Updates**: Update the organization's risk management model and architectural projections to reflect the new understanding of threats gained during the attack.

### Root Cause Analysis

Root Cause Analysis, or **RCA**, identifies the original weakness that allowed the incident to occur.

- **Identifying the "Gap"**: A deep-dive investigation must be conducted to identify the exact vulnerability or security gap that the threat actor exploited.
- **Eliminating Vulnerabilities**: Before the system can be considered clean, it must be patched or reconfigured to eliminate the original vulnerability.
- **Preventing Re-incidence**: Without addressing the root cause, any recovery effort is temporary, as the restoration process could inadvertently recreate the same flawed environment that led to the attack in the first place.
    

### Post-mortem analysis

A post-mortem evaluates the response itself to refine future readiness.

- **Response Review**: Assess what worked and what failed in the "heat of the moment," specifically looking for coordination or decision-making delays.
- **Timeline Validation**: Reconstruct the incident and response timeline so the team can verify their assumptions against the gathered digital evidence.
- **Procedure Refinement**: Update playbooks, escalation rules, and diagnostic tools based on the actual difficulties encountered during the response.
    

### Preventing recurrence

Rather than a broad catalog of controls, prevention focuses on verified, high-impact remediation.

- **Verified Remediation**: Ensure that the specific "gap" identified in the RCA is closed—whether through a software patch, network reconfiguration, or physical security update—before the incident is marked as closed.
- **Tracked Actions**: Convert every lesson learned into a formal follow-up action with an assigned owner, clear deadline, and specific validation criteria.
- **Ongoing Testing**: Integrate the incident scenario into future disaster recovery tests to ensure that the newly implemented safeguards remain functional over time.
## SOC, SIEM, and Threat Detection

## Security Operations Center

A **Security Operations Center (SOC - /sɑːk/)** acts as the central command hub for an organization's defensive operations, providing a dedicated facility and team for continuous monitoring and incident response.
- It is essentially the "neighborhood watch" for your infrastructure—if the neighborhood watch had a 24/7 surveillance room and a forensics lab.
- The SOC is responsible for converting raw security telemetry into a structured pipeline of triage, investigation, and measurable response.

### SOC Operating Model

The SOC operates through a standardized workflow designed to ensure that no critical alert is missed and that every incident is handled with consistency:

- **Continuous Monitoring**: Providing 24/7 surveillance of security events and alerts across the entire organization, including endpoints, servers, and cloud environments.
- **Event Triage**: Differentiating between standard security events (e.g., a single denied login) and actual security incidents that disrupt normal operations.
- **Standardized Procedures**: Following pre-defined, step-by-step playbooks to reduce human error and ensure response agility during high-stress situations.
- **Threat Hunting**: Proactively searching for indicators of advanced threats or "hidden" malicious activity that may have evaded automated detection tools.
- **Forensic Handoff**: When a breach is confirmed, the SOC facilitates the collection of digital evidence, such as capturing volatile RAM data, while maintaining a clear chain of custody.

## SOC Analysis Levels

To manage the volume of alerts effectively, a SOC typically utilizes a tiered analysis structure:

| **Level**   | **Function**                                                                                                                            |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| **Level 1** | **Basic Alert Triage**: Responsible for initial event monitoring and determining the severity of incoming alerts.                       |
| **Level 2** | **Deeper Investigation**: Handles escalated alerts, performing containment actions and detailed analysis of compromised systems.        |
| **Level 3** | **Advanced Threat Analysis**: Focuses on complex threat hunting, malware forensics, and responding to sophisticated persistent threats. |

## SIEM

A **SIEM (Security Information and Event Management)** provides the technological backbone for the SOC by centralizing and correlating security-relevant telemetry from across the entire infrastructure. While the SOC is the "team," the SIEM is the "engine" that powers their visibility.

> [!info]
> IoT devices are a strong case for SIEM because they produce a lot of logs. See [SIEM and IoT support](#SIEM%20and%20IoT%20support).

### Centralized Visibility and Correlation

Security Information and Event Management (SIEM) systems function as centralized collectors and correlators for security logs and events. The platform aggregates data streams from diverse network hardware and software applications—including servers, firewalls, switches, antivirus engines, and endpoints—into a unified console.

The investigative logic of a SIEM mirrors that of Business Intelligence (BI) platforms. While an individual log entry represents isolated data, the SIEM constructs an integrated security overview through a structured operational funnel:

* **Ingestion and Centralization**: Integrates network assets and devices that support API logs or event forwarding.
* **Normalization and Sanitization**: Cleanses raw data inputs, eliminating redundant or irrelevant records to isolate actionable events.
* **Analysis and Correlation**: Applies algorithmic correlation rules to cross-reference data points from separate assets. For instance, if an endpoint antivirus detects malware, the firewall logs port-scanning activity from that same IP, and the switch detects protocol anomalies, the SIEM cross-references these events.
* **Actionable Insights**: Delivers consolidated alerts indicating a coordinated security incident, allowing analysts to deploy defensive countermeasures immediately.
## Important Metrics

The effectiveness of a SOC and its SIEM integration is measured through performance metrics that track the speed and quality of the response:
- **Mean Time to Detect (MTTD)**: The average time it takes for the security team to become aware of a potential incident.
- **Mean Time to Respond or Recover (MTTR)**: The average time taken to mitigate a threat and restore systems to normal operations.

> **Note**: A successful SOC aims to minimize both metrics. Reducing MTTD limits the attacker's "dwell time," while reducing MTTR minimizes the overall impact and cost to the business.

## Digital Forensics

Digital forensics is a specialized branch of forensic science and cybersecurity dedicated to the recovery, investigation, and analysis of material found on electronic devices.
- While it was once synonymous with "computer forensics," the field has expanded to encompass any device capable of storing digital data—including mobile phones, IoT devices, and cloud infrastructure.
- It is a structured process of discovering and interpreting electronic data to build a factual account of past actions.
* The activities of a computer forensics laboratory take place within a secure, controlled environment that is protected against external interference. This setup ensures the management and preservation of electronic data with a significantly reduced risk of damage or modification to the evidence.
### Purpose of digital forensics

The primary objective of digital forensics is to translate raw digital data into actionable intelligence and legal proof. While the principles define _how_ the work is done, the purpose defines _why_ the organization invests in the process:

- **Fact-Based Reconstruction**: The core purpose is to build a chronological and factual account of a security event to understand the attacker's methods and movements.
- **Determining Data Impact**: It identifies the specific scope of a breach, specifically determining if sensitive data or **Personally Identifiable Information (PII)** was accessed, lost, or stolen.
- **Legal and Regulatory Admissibility**: It ensures that findings meet the evidentiary standards required for use in a court of law, police investigations, or regulatory filings.
- **Operational Diagnostic Visibility**: It provides the visibility needed to confirm whether a standard security **event** has escalated into a formal **incident**, allowing management to make informed decisions about response levels.
- **Informing Remediation**: By identifying the technical or procedural "gap" that was exploited, forensics provides the necessary data for a successful **Root Cause Analysis (RCA)**, ensuring that recovery efforts address the actual vulnerability.
- **Support for Corporate Accountability**: It provides clear evidence for internal disciplinary actions, insurance claims, or the enforcement of service level agreements (SLAs) with third-party partners.
### Core forensic principles

To ensure that digital evidence is reliable, credible, and admissible in a professional or legal setting, investigators must adhere to five core principles. These principles shift the process from simple "data recovery" to a scientifically sound forensic investigation.

#### 1. Integrity: Maintaining the "Bit-for-Bit" Match

Integrity ensures that the evidence analyzed in the lab is an identical replica of the data found at the scene.

- **[Hashing](01%20Cryptography.md#4.%20Hashing%20The%20"One-Way"%20Trap)**: Investigators use mathematical algorithms (like SHA-256) to create a "digital fingerprint" of the original drive. If even a single character changes, the hash will fail, signaling that the evidence has been tampered with.
- **Write Blockers**: During collection, specialized hardware is used to prevent the investigator's computer from accidentally writing any data back to the original device.

#### 2. Authenticity: Proving the Source

Authenticity focuses on the origin of the data. It answers the question: _"Can we prove this file actually came from this specific user's computer at this specific time?"_ This involves analyzing metadata, system logs, and digital signatures to confirm that the evidence is what it purports to be.

#### 3. Chain of Custody: The Paper Trail

The preservation of evidence is a primary activity in cyber forensics. The principal strategy to ensure the legal admissibility in a judicial process is the Evidence Chain of Custody, which consists of a detailed log of how the elements were handled from collection to final results.

An evidence chain of custody record must contain, at a minimum, the following items:

* Date and time of the evidence collection;
* Identification of the person from whom the evidence was seized;
* Hardware information, including manufacturer, model, and serial numbers;
* Name of the professional responsible for collecting the evidence;
* Detailed description of the evidence;
* Name and signature of the individuals involved;
* Case identification and evidence identification through markings or tags;
* MD5 or SHA-1 digital signatures of the evidence, whenever possible;
* Pertinent technical information.

Collection must respect the order of data volatility to mitigate the risk of loss. This process begins with the most ephemeral elements (such as RAM, caches, and command-line shell session variables) and extends to persistent data stored on hardware and printed documents. This ordering enables the reconstruction of user history, running processes, network connections, and audit logs.
#### 4. Preservation: The Race Against Time

Preservation involves protecting the digital "crime scene" from environmental or technical factors that could destroy evidence.

- **Order of Volatility**: Investigators must prioritize data that disappears quickly. Data in the **RAM (Volatile Memory)** is collected first, followed by temporary files, and finally the data on hard drives.
- **Static Imaging**: Once the volatile data is captured, a static image (a forensic copy) of the hard drive is made so the original can be safely stored in a secure, climate-controlled environment.

#### 5. Documentation: The Investigative Roadmap

A forensic investigation is only as good as its documentation. This principle requires that every action taken—from the moment the device is seized to the moment the final report is written—is recorded in detail.

- **Reproducibility**: Documentation must be so thorough that another forensic expert could follow the notes and reach the exact same conclusions.
- **Transparency**: Clear documentation prevents "black box" accusations, showing that no hidden or biased methods were used to manipulate the findings.
### Forensic investigation phases

The forensic investigation process follows a structured sequence to transform raw data into credible evidence:

1. **Identify**: Determine what evidence is present, where it is located, and its specific format.
2. **Preserve**: Isolate and protect the data immediately to prevent tampering or accidental loss.
3. **Collect**: Acquire the digital evidence, typically by seizing physical assets like hard drives, phones, or capturing volatile RAM.
4. **Examine**: Perform a precursor inspection to identify secondary details and prepare the data for deeper study.
5. **Analyze**: Piece together fragments and recover deleted files to prove or refute the case.
6. **Document**: Maintain a detailed, step-by-step report of the entire investigation and the chain of custody.
7. **Present**: Summarize the conclusions in clear, natural language for a hearing or court of law.

### Types of digital forensics

When selecting the specific type of forensic investigation, the choice is driven by the specific **evidence sources** involved and the **specialized tooling** required to process them:

* **Computer Forensics**: Applied when evidence is found on computers or digital storage media. Tooling must include write-blockers to ensure the act of seizing or acquiring media does not modify the original evidence.
* **Network Forensics**: Chosen when the incident involves network events, intrusions, or transmitted data packets. This requires tools for analyzing packets and logs from firewalls or intrusion detection systems.
* **Mobile Device Forensics**: Required for recovering evidence from phones, tablets, or GPS devices. It utilizes sound forensic methods specifically designed for mobile hardware and software.
* **Malware Forensics**: Used to identify and study malicious code (viruses or worms) to determine its payload and behavior. This often involves specialized reverse engineering tools and isolated sandbox environments.
* **Live Forensics (Memory Forensics)**: Necessary for capturing **volatile data**—such as active network connections and running processes—stored in RAM or cache. It requires memory imaging tools used while the system is still running to prevent the permanent loss of evidence that occurs during a shutdown.
* **Forensic Data Analysis**: Focuses on the study of databases and their associated metadata. Tooling is centered on examining data patterns to uncover fraudulent activity.

By matching the forensic type to the specific data source, the Incident Response Team ensures they have the correct diagnostic tools to gain visibility and maintain the **chain of custody** throughout the investigation.

### Forensic techniques

The selection of forensic techniques is a strategic decision based on the need to maintain system integrity, prevent the loss of fragile evidence, and define the full boundaries of a breach.

#### Preservation and Containment Techniques

- **Live Analysis**: This technique involves extracting volatile data stored in **RAM** or cache while the device is still running. It is a critical preservation step because a "hard shutdown" destroys active network connections, running processes, and decrypted encryption keys. By using live analysis, teams can perform a **Balanced Response**, choosing network isolation over a full power-off to keep the "crime scene" intact for diagnostics.
- **Forensic Imaging**: This process creates bit-for-bit copies of affected systems and storage devices. It is the primary technique for preservation, ensuring that the original media remains untouched while investigators work on an identical replica to maintain the integrity of the evidence.

#### Scope Determination Techniques

- **Cross-drive Analysis (Anomaly Detection)**: This technique finds similarities and correlates information across multiple data sources. It is used to determine the scope of an incident by identifying lateral movement or hidden connections between seemingly unrelated systems.
- **Timeline Analysis**: Investigators reconstruct the sequence of events to map out the attack's progression. This is essential for scope determination, as it reveals the duration of the breach and the total impact on business operations.
- **Deleted File Recovery (Data Carving)**: This involves searching for file fragments that were partially deleted but left traces in unallocated disk space. It materially affects scope determination by uncovering artifacts—such as logs or staging files—that the threat actor intentionally tried to erase to hide their footprint.

By prioritizing these techniques, the response team ensures that the most time-sensitive evidence is captured and that the remediation plan addresses the full extent of the compromise.

#### File System Analysis

Files represent non-volatile data and constitute fundamental assets for forensic analysis. Every investigation must be conducted on images of the original files (bit-by-bit cloning), since simply copying a file alters its structure, composition, and metadata.

Operating systems record chronological attributes, known as MACtimes, which describe the history of files:

* **mtime (Modification time):** Indicates the last date and time the content of the file was modified.
* **atime (Access time):** Records the last date and time a file or directory was accessed or read.
* **ctime (Creation time):** Points to the date and time the file was created.

Journaling techniques, which define how file system updates are performed, are utilized to recover deleted files and substantiate the chain of custody. Analysis also encompasses local logs, configuration files, service files, and the MBR (Master Boot Record).

#### Network and Log Analysis

Network analysis deals with volatile data that circulates during the execution of processes and services. For this monitoring, specific tools are employed, such as Wireshark (for reading MAC addresses, gateways, and packets), Aircrack (focused on Wi-Fi networks), Nessus (a vulnerability scanner), TCPdump (packet capture and hexadecimal display), and Snort (an intrusion detection system). Techniques like Network Sniffing assist in packet capture, user identification, and mapping attack patterns to protect networks.

Log analysis presents performance information and system events in a comprehensible manner, serving as a technique to determine security violations after the fact (*a posteriori*). The types of logs essential for auditing are system, application, firewall, and intrusion detection logs. A structured audit log system is composed of a log generator, an analyzer, and a notifier.

Log management faces challenges such as the massive volume of raw data originating from servers, routers, and firewalls. To mitigate this complexity, automated tools are used to condense duplicate lines and filter out irrelevant events. The primary tools applied include:

* **General systems and services:** Syslogd, Logwatch, and Syslog Summary in Linux;
* **Firewalls:** PixLog and FWLogWatch;
* **E-mail:** PFLogSum and SMTPStats;
* **Web Servers:** Analog;
* **Alerts:** LogSurf and SWatch.
## Business Continuity

### What Business Continuity Is

**Business Continuity (BC)** is the overarching strategy and set of capabilities an organization must possess to respond to and recover from any event that negatively affects operations and the business life cycle.
- It is a fundamental component of organizational **resilience**, focusing on the ability to survive a crisis with minimal losses.
- While technical systems may fail, business continuity ensures that the core functions of the organization—its people, processes, and essential services—remain functional or can be quickly restored.

### Business Continuity vs. Disaster Recovery

It is critical to distinguish between business continuity and disaster recovery, as they address different layers of an incident. While they are closely linked, their primary objectives and scopes differ:

| **Concept** | **Focus** | **Primary Objective** |
| --- | --- | --- |
| **Business Continuity** | **The Business Lifecycle**: Managing the organizational impact of a disruption to ensure survival. | Operational survival, loss minimization, and maintaining essential business functions through temporary workarounds. |
| **Disaster Recovery** | **IT Infrastructure**: Regaining the use of critical systems, hardware, and data. | Technical resolution, restoring IT systems agilely, and returning the environment to its normal state. |

### Business Continuity Examples

Business continuity plans (BCP) are primarily business-oriented, focusing on how work gets done when the primary "technical" path is blocked. These plans often rely on non-technical or redundant strategies:

* **Manual Workarounds**: Establishing paper-based processes or manual entry systems to maintain operations while databases or applications are offline.
* **Resource Relocation**: Moving essential staff to alternate sites or enabling remote work to bypass physical infrastructure failures.
* **Redundant Service Delivery**: Utilizing secondary suppliers or failover services to maintain the flow of goods and information.
* **Communication Fallbacks**: Activating pre-defined, alternate communication channels for internal stakeholders, customers, and regulators.

**Note on Workarounds vs. Recovery:** A clear distinction must be made between **continuity workarounds** and **technical recovery milestones**:
- Continuity workarounds are designed to allow the business to function in a degraded state temporarily.
- In contrast, technical recovery milestones—often defined within a **[Disaster Recovery Plan (DRP)](#Disaster%20Recovery%20Plan%20(DRP))**—dictate the specific sequence and timing for bringing actual IT systems back online.

## Business Impact Analysis (BIA)

The **Business Impact Analysis (BIA)** is the foundational assessment that bridges the gap between high-level business goals and specific technical requirements for **Business Continuity (BC)** and **Disaster Recovery (DR)**. Its primary purpose is to perform a deep analysis of systems, services, and organizational structure to identify what is truly "critical" for survival.

By evaluating the potential consequences of a disruption, the BIA determines the priority of recovery and sets the performance standards that technical teams must meet.

### The Core Metrics: RPO and RTO

The BIA identifies two critical thresholds that define the success or failure of a recovery effort:

- **Recovery Point Objective (RPO)**: Defines the **maximum acceptable amount of data loss** measured in time before the disaster occurs. For example, an RPO of 15 minutes means the system must be restored with data that is no older than 15 minutes prior to the outage.
- **Recovery Time Objective (RTO)**: Defines the **maximum acceptable downtime**, or the duration of time from the moment a disaster strikes to the moment the service is restored to the user.

### Architectural Impact on Metrics

Achieving low RPO and RTO values is not just a policy decision; it is an architectural challenge. The technical design of the system must support these requirements:

- **Data Protection Strategies**: High-impact systems require preventive measures and recovery strategies tailored to their specific confidentiality, integrity, and availability (CIA) needs.    
- **Replication Choices**: To achieve near-zero RPO, organizations often use **synchronous replication** (real-time data copying), whereas systems with more flexible RPOs might use **asynchronous replication** or traditional offsite backups.
- **Failover Design**: Meeting an aggressive RTO (e.g., 1 hour) typically requires automated failover to a secondary site or redundant environment, whereas manual restoration from backups is only suitable for systems with high RTO tolerances.

### RPO/RTO Table Examples

The BIA categorizes systems based on their impact level to prioritize resource allocation:

|**System**|**RPO**|**RTO**|**Meaning**|
|---|---|---|---|
|**Payment System**|15 minutes|1 hour|**Critical Impact**: Requires near-continuous data protection and rapid failover.|
|**Customer Database**|30 minutes|2 hours|**High Impact**: Requires frequent backups and a structured, tested recovery plan.|
|**Internal Wiki**|24 hours|2 days|**Low Impact**: Can be restored from daily offsite backups with minimal business disruption.|

By aligning these technical metrics with business needs, the BIA ensures that the organization invests in the right level of resilience for every system, avoiding the "trap of self-sabotage" where a lack of diagnostic visibility or poor planning leads to unnecessary data loss during a crisis.

---

## Disaster Recovery

**Disaster Recovery (DR)** is the technical capability an organization must possess to respond to and recover from an event of any nature—natural, technical, or human-driven—that negatively affects operations and the business life cycle. While Business Continuity focuses on high-level organizational survival, DR specifically addresses the ability to regain use of critical systems and IT infrastructure as quickly and agilely as possible.

### Goals of Disaster Recovery

The primary focus of DR is restoring prioritized services within the acceptable downtime (**RTO**) and data-loss (**RPO**) limits established during the Business Impact Analysis.

- **System Restoration**: Returning hardware, software, and data to a functional state after a serious disruption.
- **Minimized Losses**: Ensuring the duration and impact of the outage do not lead to catastrophic business failure.
- **Accountability and Prioritization**: Establishing a structured approach where the most critical systems, based on their impact level, are recovered first.
- **Compliance Alignment**: Meeting regulatory and governance requirements for data availability and security.
- 
### Disaster Recovery Plan (DRP)

A **Disaster Recovery Plan (DRP)** is a formalized document created after a deep analysis of an organization's systems, services, and structure.

- **Document Content**: It involves everything from manual procedures to the specific technologies and services required for restoration. 
- **Readiness**: For the response to be satisfactory, these plans must be carefully established, tested, and known by everyone in the organization.
- **Framework Alignment**: Many DRPs utilize the **NIST Cybersecurity Framework**, specifically the "Recover" function, to identify necessary actions for maintaining continuity and initiating restoration.

### Disaster Recovery Methods

The choice of methodology depends on the organization's architecture and the technical considerations appropriate to the confidentiality, integrity, and availability (CIA) of the systems.

* **Virtualized**: This method allows for the replication of workloads at an alternative site or in the cloud, offering high flexibility, efficiency, and speed through frequent replication and rapid failover.
* **Network**: This strategy focuses on restoring essential network services—such as internal/external communication, data sharing, and application access—to ensure connectivity to websites and backup data during an incident.
* **Cloud**: This goes beyond basic cloud backup by configuring the automatic failover of entire workloads to a public cloud platform in the event of an interruption.
* **DRaaS (Disaster Recovery as a Service)**: A third-party provider replicates and hosts physical and virtual servers, assuming the responsibility for implementing the recovery plan based on a predefined service level agreement (SLA).
* **Data Center**: This approach focuses on the recovery of the organization’s entire internal IT infrastructure and the physical facility itself.

## Standards and Frameworks

- **NIST Cybersecurity Framework (CSF)**: The "Rosetta Stone" of security. It provides a common language for managing cybersecurity risk across the [entire lifecycle.](#Core%20cybersecurity%20lifecycle)
- **NIST SP 800-34**: The tactical "How-To" for **IT Contingency Planning**. While ISO looks at the whole business, this gets into the weeds of restoring specific IT systems (servers, networks, applications).
	- Seven-step process including the Business Impact Analysis (BIA), preventive controls, and rigorous testing/maintenance.
- **ISO 22301**: The **"What"** of Business Continuity Management Systems (BCMS). It is the requirements standard used for certification.
	- Uses a "Plan-Do-Check-Act" (PDCA) cycle to ensure the organization can continue operating (at a predefined level) following a disruption. It’s about governance, leadership commitment, and setting measurable objectives.
- **ISO 22313**: The **"How"** of ISO 22301.
	* Since ISO 22301 is a list of requirements (e.g., "You must have a BIA"), ISO 22313 provides the descriptive guidance and best practices on how to actually implement those requirements effectively.
- **ISO 22320**: The manual for **Incident Management**.
	- Focuses on the "heat of the moment." It outlines requirements for incident response, including command and control structures, operational information sharing, and how to coordinate with external agencies or partners.
- **ISO 22300**: The **Official Dictionary**.
	- A foundational document that defines the specific terminology used across all ISO security and resilience standards. It ensures that when one person says "Recovery Time Objective," everyone else knows exactly what that means.
