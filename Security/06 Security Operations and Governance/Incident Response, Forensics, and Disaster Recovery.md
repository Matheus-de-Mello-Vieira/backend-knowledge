# Incident Response, Forensics, and Disaster Recovery

## Introduction to Cybersecurity Resilience

While prevention is a critical first step, modern cybersecurity is built on the principle of resilience: the ability to not only withstand an attack but to effectively bounce back from one. Relying solely on "building higher walls" is no longer sufficient; organizations must operate under the assumption that a breach will eventually occur.

### Core cybersecurity lifecycle
The core cybersecurity lifecycle transforms "emergency mode" into a structured, repeatable process. By following these stages, an organization ensures that its response to a crisis is calculated rather than chaotic:

1. [**Prepare**](#Preparation): This phase is an ongoing effort to ensure the organization has the necessary tools, procedures, and personnel ready before an incident occurs.
	- [**Risk & Impact Analysis**](#Risk%20Analysis%20and%20Business%20Impact%20Analysis): Evaluating potential hazards and quantifying the maximum tolerable downtime through Business Impact Analysis (BIA).
	- [**Documentation**](#Incident%20Response%20Plan): Creating a formal [Disaster Recovery Plan](#Disaster%20Recovery%20Plan) (DRP) and [Incident Response Plan](#Incident%20Response%20Plan) (IRP) that outline specific responsibilities.
	- [**Training**](#Standards%20and%20Frameworks): Regularly educating employees on security standards to reduce human error.
2. [**Detect**](#Identification,%20Detection,%20and%20Analysis): Detection involves identifying abnormal behavior patterns across IT assets, including cloud resources and internal networks.
	- [**SIEM & SOC**](#SOC,%20SIEM,%20and%20Threat%20Detection): Utilizing [Security Information and Event Management](#SIEM) (SIEM) systems for log aggregation and 24/7 monitoring via a [Security Operations Center](#Security%20Operations%20Center) (SOC).
	- [**Alerting**](#Identification,%20Detection,%20and%20Analysis): Using automated alerts to flag potential breaches, such as multiple failed login attempts or unauthorized access to data centers.
3. [**Respond**](#Containment): Once a threat is identified, the primary goal is to stop its effects before it causes further damage.
	- [**Containment & Isolation**](#Types%20of%20containment): Disconnecting compromised systems from the network or disabling affected user accounts to prevent "lateral movement".
	- [**Team Coordination**](#Roles%20and%20responsibilities): Gathering a cross-functional team (legal, technical, and management) to lead the mitigation effort.
4. [**Investigate**](#Digital%20Forensics): Investigation, or digital forensics, focuses on discovering and interpreting electronic data to reconstruct past events.
	- [**Evidence Preservation**](#Evidence%20Preservation%20During%20Incidents): Creating "bit-for-bit" forensic images of affected storage devices while maintaining a strict [**chain of custody**](#Chain%20of%20custody) for legal admissibility.
	- [**Live Analysis**](#Volatile%20evidence): Extracting volatile data from RAM (like active network connections) before a system is shut down and the evidence is lost.
5. [**Recover**](#Recovery): Recovery focuses on returning systems to normal operations safely and with minimal loss.
	- [**Failover & Restoration**](#Backup%20and%20Recovery%20Strategy): Moving workloads to secondary components or rebuilding systems from offsite backups.
	- [**Patching**](#Eradication): Ensuring the original vulnerability is closed before the system goes live to prevent an immediate re-attack.
6. [**Improve**](#Lessons%20Learned%20and%20Documentation): The lifecycle is only complete when the organization turns the failure into a learning opportunity.
	- [**Post-Mortem Analysis**](#Root%20Cause%20Analysis%20and%20Post-Mortem): Conducting a "lessons learned" meeting to evaluate the team's performance and the effectiveness of the response tools.
	- [**Plan Updates**](#Preventing%20recurrence): Refining the architectural model and updating the IRP to reflect new insights gained from the incident.

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
- **Cyberattack Integration**: This category includes a broad range of malicious activities that have become increasingly common and easier to execute, including [Ransomware](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#Ransomware), [Phishing](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#Phishing), and [Man-in-the-Middle (MitM)](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#Man-in-the-Middle%20(MitM)) attacks.
- **Comprehensive Examples**:
    - **Malware-based Attacks**: [Ransomware](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#Ransomware), [Spyware](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#Spyware), and [Computer Viruses](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#Computer%20Viruses) designed to steal or encrypt data.
    - **Infrastructure Failures**: [Hardware and Power Failures](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#Hardware%20and%20Power%20Failures) and network infrastructure collapses.
    - **Network Attacks**: [DoS (Denial of Service)](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#DoS%20(Denial%20of%20Service)), [DDoS (Distributed Denial of Service)](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#DDoS%20(Distributed%20Denial%20of%20Service)), and [Injection Attacks](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#Injection%20Attacks) that overwhelm or compromise databases.
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

### What an IRP should include

#### Roles and Responsibilities

A comprehensive IRP requires a cross-functional **Incident Response Team (IRT)** with clearly defined ownership:

* **Security & IT**: Security analysts and system administrators handle the technical identification, containment, and eradication of threats.
* **Management**: Responsible for coordinating the overall process, providing necessary resources, and ensuring the plan's effectiveness.
* **Legal Counsel**: Manages regulatory requirements and ensures that evidence collection follows legal guidelines.
* **Communications**: Manages the flow of information to internal stakeholders, customers, and the media.
* **Human Resources**: Involved specifically if the incident involves an "insider threat" or a malicious act by an employee.

#### Severity Levels

To prioritize resources, incidents are classified using a practical severity model based on impact and urgency:

- **Low**: Minor event with limited impact; typically handled through standard procedures.
- **Medium**: Confirmed issue affecting a single system or specific user group; requires active mitigation.    
- **High**: Major incident affecting critical systems or sensitive data; requires the full IRT (Incident Response Team).
- **Critical**: Business-wide disruption, large-scale data breach, or active compromise of the entire infrastructure.

#### Escalation Procedures

The IRP must define clear criteria for when an incident should be escalated to higher management or specialized teams:

* **Defined Thresholds**: Triggers for escalation based on severity level, potential financial impact, or regulatory significance.
* **Approval Paths**: Explicitly stating who has the authority to approve high-impact actions, such as disconnecting a production database from the network.
* **Communication Chains**: Ensuring the right people are informed at the right time to avoid response delays.

#### Communication Plan

Effective communication prevents panic and preserves the organization's reputation. The plan defines paths for:

* **Internal Stakeholders**: Keeping employees and leadership updated on the status of the response.
* **Customers & Partners**: Notifying those whose data or services may be compromised as a result of the incident.
* **Regulators & Law Enforcement**: Providing mandatory reports to comply with data protection laws and assisting in criminal investigations.
* **Public/Media**: Using pre-defined strategies to manage the external narrative of the incident.

#### Playbooks

The IRP references specialized playbooks that provide step-by-step instructions for common scenarios:

* **[Malware](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#Malware) & [Ransomware](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#Ransomware)**: Steps for isolating infected segments and restoring from offsite backups.
* **[DDoS](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#DDoS%20(Distributed%20Denial%20of%20Service)) Attacks**: Procedures for filtering malicious traffic and maintaining service availability.
* **Data Leaks/[Phishing](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#Phishing)**: Methods for containing compromised credentials and identifying the extent of data exfiltration.
* **Post-Mortem Analysis**: Standardized procedures for a "lessons learned" meeting to refine the IRP after an incident is resolved.
---

## Incident Response Lifecycle

## Preparation

### Purpose of preparation

Prepare people, tooling, access, and procedures before an incident happens.

### Preparation content to include

Keep this section limited to readiness prerequisites: people, tooling, logging, backups, access, contacts, and tested procedures.

Related notes: [Patch Management and Security Updates](../05%20Architecture%20and%20Infrastructure%20Security/Patch%20Management%20and%20Security%20Updates.md), [Backup and Restore](../03%20Cryptography%20and%20Data%20Protection/Backup%20and%20Restore.md), [Risk Management and Threat Modeling](../01%20Foundations%20and%20Risk/02%20Risk%20Management%20and%20Threat%20Modeling.md), [Cybersecurity Governance](../01%20Foundations%20and%20Risk/04%20Cybersecurity%20Governance.md)
Write there: add playbook ownership, response-team contact hygiene, and exercise/testing cadence where those notes discuss operational readiness.

---

## Identification, Detection, and Analysis

### Purpose of identification, detection, and analysis

Determine whether an incident occurred, what type it is, and how severe it is.

### Identification, detection, and analysis content to include

Keep this section focused on confirming scope, severity, and whether the threat is still active.

Related notes: [Intrusion Detection and Prevention](01%20Intrusion%20Detection%20and%20Prevention.md), [Zero Trust Architecture](../02%20Identity%20and%20Access/03%20Zero%20Trust%20Architecture.md), [Security Principles](../01%20Foundations%20and%20Risk/01%20Security%20Principles.md)
Write there: expand SIEM correlation, anomaly triage, and evidence-oriented logging requirements in the linked notes.

### Key questions

Keep the questions limited to what happened, scope, exposure, and whether the threat is still active.

---

## Containment

### Purpose of containment

Stop the incident from spreading while preserving recovery and investigation options.

### Types of containment

|Type|Example|
|---|---|
|Network isolation|Disconnect affected host or subnet|
|Account isolation|Disable compromised accounts|
|Process isolation|Stop malicious processes|
|Service isolation|Take affected service offline or redirect traffic|

Related notes: [Network Security](../05%20Architecture%20and%20Infrastructure%20Security/Network%20Security/01%20Network%20Security.md), [Firewall](../05%20Architecture%20and%20Infrastructure%20Security/Network%20Security/Firewall%20Technologies.md), [Authorization and Access Control](../02%20Identity%20and%20Access/02%20Authorization%20and%20Access%20Control.md), [Zero Trust Architecture](../02%20Identity%20and%20Access/03%20Zero%20Trust%20Architecture.md)
Write there: add emergency segmentation, quarantine patterns, and temporary access-restriction procedures for active incidents.

### Important idea

Containment should reduce harm without unnecessarily destroying volatile evidence.

---

## Eradication

### Purpose of eradication

Remove the attacker foothold and the weakness that enabled it.

### Eradication content to include

Keep this section focused on removing the attacker foothold, fixing the enabling weakness, and validating that compromise no longer persists.

Related notes: [Patch Management and Security Updates](../05%20Architecture%20and%20Infrastructure%20Security/Patch%20Management%20and%20Security%20Updates.md), [Authentication](../02%20Identity%20and%20Access/01%20Authentication.md), [Authorization and Access Control](../02%20Identity%20and%20Access/02%20Authorization%20and%20Access%20Control.md), [Endpoint Security](../05%20Architecture%20and%20Infrastructure%20Security/02%20Endpoint%20Security.md)
Write there: add credential reset sequencing, key rotation, persistence checks, and validation criteria before systems are declared clean.

---

## Recovery

### Purpose of recovery

Restore prioritized services safely.

### Recovery content to include

Keep this section focused on safe restoration, integrity validation, gradual service return, and close monitoring.

Related notes: [Backup and Restore](../03%20Cryptography%20and%20Data%20Protection/Backup%20and%20Restore.md), [Cloud Security](../05%20Architecture%20and%20Infrastructure%20Security/Cloud%20Security.md), [File and Filesystem Security](../03%20Cryptography%20and%20Data%20Protection/File%20and%20Filesystem%20Security.md)
Write there: add restore validation, integrity verification, and phased service reintroduction guidance.

### Recovery reminder

Do not recover into the same vulnerable state.

---

## Lessons Learned and Documentation

### Purpose of lessons learned and documentation

Use the incident to drive verified follow-up improvements.

### Lessons learned content to include

Keep this section focused on timeline, root cause, impact, response quality, and concrete follow-up actions.

Related notes: [Cybersecurity Governance](../01%20Foundations%20and%20Risk/04%20Cybersecurity%20Governance.md), [Risk Management and Threat Modeling](../01%20Foundations%20and%20Risk/02%20Risk%20Management%20and%20Threat%20Modeling.md)
Write there: add how post-incident findings feed back into governance reviews, control owners, and risk register updates.

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

## Root Cause Analysis and Post-Mortem

## Root Cause Analysis

Root Cause Analysis, or **RCA**, identifies the original weakness that allowed the incident.

## Post-mortem analysis

A post-mortem evaluates the response itself.

## Preventing recurrence

Keep this section focused on verified remediation actions, not a broad control catalog.

Related notes: [Risk Management and Threat Modeling](../01%20Foundations%20and%20Risk/02%20Risk%20Management%20and%20Threat%20Modeling.md), [Patch Management and Security Updates](../05%20Architecture%20and%20Infrastructure%20Security/Patch%20Management%20and%20Security%20Updates.md), [Cybersecurity Governance](../01%20Foundations%20and%20Risk/04%20Cybersecurity%20Governance.md)
Write there: add explicit linkage from RCA outputs to remediation backlog, exception handling, and control verification.

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