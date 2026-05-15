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

While incidents are managed through an **[Incident Response Plan (IRP)](#Incident%20Response%20Plan)**, disasters require a formal [Disaster Recovery Plan (DRP)](#Disaster%20Recovery%20Plan) to regain the use of critical IT infrastructure as quickly as possible.

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
---

## SOC, SIEM, and Threat Detection

## Security Operations Center

A **SOC** is the function responsible for continuous monitoring, triage, and escalation.

### SOC content to include

Keep this section focused on how monitoring turns into triage, escalation, investigation, and measurable response performance.

Related notes: [Intrusion Detection and Prevention](01%20Intrusion%20Detection%20and%20Prevention.md), [Zero Trust Architecture](../02%20Identity%20and%20Access/03%20Zero%20Trust%20Architecture.md), [Cybersecurity Governance](../01%20Foundations%20and%20Risk/04%20Cybersecurity%20Governance.md)
Write there: expand SOC operating model, handoff rules, and SIEM-to-SOAR workflow details in the linked notes.

## SOC analysis levels

|Level|Function|
|---|---|
|Level 1|Basic alert triage|
|Level 2|Deeper investigation and containment|
|Level 3|Advanced threat analysis and hunting|

## SIEM

A **SIEM** centralizes and correlates security-relevant telemetry.

### SIEM content to include

Keep this section focused on centralized visibility and correlation, not on SIEM feature catalogs.

## Important metrics

|Metric|Meaning|
|---|---|
|MTTD|Mean Time to Detect|
|MTTR|Mean Time to Respond or Recover|

---

## Digital Forensics

## What digital forensics is

Digital forensics preserves and analyzes digital evidence to reconstruct what happened.

Related notes: [File and Filesystem Security](../03%20Cryptography%20and%20Data%20Protection/File%20and%20Filesystem%20Security.md), [Cryptography](../03%20Cryptography%20and%20Data%20Protection/01%20Cryptography.md)
Write there: add forensic hashing, storage integrity, and evidence-preservation considerations to the linked foundational notes.

## Purpose of digital forensics

Keep this section focused on reconstructing what happened, preserving evidence, and supporting both legal review and root-cause analysis.

---

## Core forensic principles

|Principle|Meaning|
|---|---|
|Integrity|Evidence is not altered|
|Authenticity|Evidence is provably genuine|
|Chain of custody|Handling is documented|
|Preservation|Evidence is protected|
|Documentation|Actions and findings are recorded|

---

## Forensic investigation phases

Use a simple sequence:

> Identify → Preserve → Collect → Examine → Analyze → Document → Present

---

## Types of digital forensics

Mention types only when they affect evidence sources or tooling choices for the incident at hand.

---

## Forensic techniques

Mention techniques only when they materially affect containment, evidence preservation, or scope determination.

---

## Evidence Preservation During Incidents

## The response-versus-evidence tension

During an active incident, responders must balance stopping the attack with preserving evidence.

## Volatile evidence

Volatile evidence can disappear when a system is shut down, especially memory, live sessions, active connections, and temporary runtime state.

## Safer containment principle

Prefer:

> Isolate the system before destroying the state of the system.

Example:

- Better: disconnect from the network.
- Riskier: immediately power off the system.

## Chain of custody

Record who collected the evidence, when, where it was stored, who accessed it, and what changed.

Related notes: [Cryptography](../03%20Cryptography%20and%20Data%20Protection/01%20Cryptography.md), [Legal Frameworks and Compliance](Legal%20Frameworks%20and%20Compliance.md)
Write there: add how hashes, signatures, and documentation practices support admissibility and integrity claims.

---

## Backup and Recovery Strategy

## Why backups matter

Backups make controlled recovery possible after destructive events.

## Backup principles

Keep this section focused on qualities that make recovery trustworthy: separation, testing, integrity, and resilience against attacker access.

## Recovery risks

Recovery fails when backups are stale, unsafe, or restored before the environment is trustworthy.

## Safe recovery process

Use this structure:

1. Confirm threat containment.
2. Identify root cause.
3. Patch or reconfigure affected systems.
4. Validate backup integrity.
5. Restore systems.
6. Monitor closely.
7. Document actions.

Related notes: [Backup and Restore](../03%20Cryptography%20and%20Data%20Protection/Backup%20and%20Restore.md), [Patch Management and Security Updates](../05%20Architecture%20and%20Infrastructure%20Security/Patch%20Management%20and%20Security%20Updates.md)
Write there: add ransomware-safe restore validation and clean-room rebuild guidance.

---

## Disaster Recovery

## What disaster recovery is

Disaster Recovery, or **DR**, is the capability to restore critical systems after major disruption.

## Disaster Recovery Plan

A **Disaster Recovery Plan**, or **DRP**, defines how restoration will be executed after serious disruption.

## Goals of disaster recovery

Keep this section focused on restoring prioritized services within acceptable downtime and data-loss limits.

Related notes: [Backup and Restore](../03%20Cryptography%20and%20Data%20Protection/Backup%20and%20Restore.md), [Cybersecurity Governance](../01%20Foundations%20and%20Risk/04%20Cybersecurity%20Governance.md), [Legal Frameworks and Compliance](Legal%20Frameworks%20and%20Compliance.md)
Write there: add accountability for recovery prioritization, approval paths, and compliance-driven restoration deadlines.

---

## Risk Analysis and Business Impact Analysis

## Risk Analysis

Use this section only to connect incident planning with prioritization, not to restate the full risk-management process.

## Business Impact Analysis

Use this section only to justify recovery order and tolerated downtime.

Related notes: [Risk Management and Threat Modeling](../01%20Foundations%20and%20Risk/02%20Risk%20Management%20and%20Threat%20Modeling.md), [Cybersecurity Governance](../01%20Foundations%20and%20Risk/04%20Cybersecurity%20Governance.md)
Write there: add service-tiering and dependency mapping that translate business impact into recovery order.

## Difference between Risk Analysis and BIA

|Concept|Main focus|
|---|---|
|Risk Analysis|What could happen and how likely it is|
|BIA|What damage would happen if it occurs|

---

## RPO and RTO

## Recovery Point Objective

**RPO** defines the maximum acceptable amount of data loss.

## Recovery Time Objective

**RTO** defines the maximum acceptable downtime.

## RPO/RTO table

| System            | RPO        | RTO     | Meaning                                   |
| ----------------- | ---------- | ------- | ----------------------------------------- |
| Payment system    | 15 minutes | 1 hour  | Very little data loss or downtime allowed |
| Internal wiki     | 24 hours   | 2 days  | Longer outage acceptable                  |
| Customer database | 30 minutes | 2 hours | High business impact                      |

Related notes: [Backup and Restore](../03%20Cryptography%20and%20Data%20Protection/Backup%20and%20Restore.md), [Cloud Security](../05%20Architecture%20and%20Infrastructure%20Security/Cloud%20Security.md)
Write there: add how backup frequency, replication, and failover design choices determine achievable RPO and RTO.

---

## Disaster Recovery Methods

## Virtualized Disaster Recovery

Use when workloads can be restored or failed over as portable compute instances.

## Network Disaster Recovery

Focus on recovering the network dependencies that other restoration steps rely on.

Related notes: [Network Security](../05%20Architecture%20and%20Infrastructure%20Security/Network%20Security/01%20Network%20Security.md), [Firewall](../05%20Architecture%20and%20Infrastructure%20Security/Network%20Security/Firewall%20Technologies.md)
Write there: add recovery sequencing for DNS, VPN, firewall policy restoration, and segmented network bring-up.

## Cloud Disaster Recovery

Use when cloud replication or failover materially reduces downtime.

Related notes: [Cloud Security](../05%20Architecture%20and%20Infrastructure%20Security/Cloud%20Security.md), [Backup and Restore](../03%20Cryptography%20and%20Data%20Protection/Backup%20and%20Restore.md)
Write there: add shared-responsibility implications for failover, restoration testing, and key/secret recovery in cloud DR.

## Disaster Recovery as a Service

**DRaaS** is a third-party managed disaster recovery service.

Use when recovery capability is outsourced under provider-operated processes and service levels.

## Data Center Disaster Recovery

Focuses on recovering physical facilities and infrastructure.

Use when facility-level failure drives the outage, including power, cooling, hardware, and site access dependencies.

---

## Business Continuity

## What business continuity is

Business continuity keeps the organization operating during disruption.

## Difference between business continuity and disaster recovery

|Concept|Focus|
|---|---|
|Business Continuity|Keep the business running|
|Disaster Recovery|Restore IT systems and infrastructure|

## Business continuity examples

Examples should stay business-oriented, such as temporary workarounds, alternate suppliers, fallback communications, or relocation.

Related notes: [Cybersecurity Governance](../01%20Foundations%20and%20Risk/04%20Cybersecurity%20Governance.md), [Cloud Security](../05%20Architecture%20and%20Infrastructure%20Security/Cloud%20Security.md)
Write there: add the distinction between continuity workarounds and full technical recovery milestones.

---

## Standards and Frameworks

## NIST Cybersecurity Framework

Use the framework here only as an organizing lens: Identify, Protect, Detect, Respond, Recover.

## NIST SP 800-34

Reference it as a contingency-planning standard for recovery preparation and system-specific restoration planning.

## ISO 22301

Reference it as the business continuity management standard behind recovery governance and continuous improvement.

## ISO 22313

Guidance for applying ISO 22301.

## ISO 22320

Emergency and incident management guidance.

## ISO 22300

Vocabulary for security and resilience.
