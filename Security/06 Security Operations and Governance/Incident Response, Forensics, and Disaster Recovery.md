# Incident Response, Forensics, and Disaster Recovery

## Introduction to Cybersecurity Resilience

While prevention is a critical first step, modern cybersecurity is built on the principle of resilience: the ability to not only withstand an attack but to effectively bounce back from one. Relying solely on "building higher walls" is no longer sufficient; organizations must operate under the assumption that a breach will eventually occur.

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

<hr>
### Why organizations need formal plans

Keep this section focused on why coordinated, documented, and tested response matters under operational, legal, and business pressure.

Related notes: [Cybersecurity Governance](../01%20Foundations%20and%20Risk/04%20Cybersecurity%20Governance.md), [Risk Management and Threat Modeling](../01%20Foundations%20and%20Risk/02%20Risk%20Management%20and%20Threat%20Modeling.md), [Legal Frameworks and Compliance](Legal%20Frameworks%20and%20Compliance.md)
Write there: connect governance and compliance guidance more explicitly to incident escalation, crisis communications, and recovery accountability.

## Events, Incidents, and Disasters

### Security event

A security event is a notable occurrence that may or may not require response.

### Security incident

A security incident is an event that creates real risk or disruption and requires coordinated handling.

### Disaster

A disaster is a major disruption that materially affects critical business operations and recovery priorities.

### Key distinction

|Concept|Scope|Example|
|---|---|---|
|Event|Something happened|One failed login|
|Incident|Response is required|Compromised account or active malware|
|Disaster|Major business disruption|Critical systems unavailable|

---

## Types of Security Incidents and Disasters

### Cybersecurity incidents

### Malware

Use malware here only as an incident category. Keep the focus on response impact, especially ransomware-driven containment and recovery.

Related notes: [Common Threats and Attacks](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md), [Endpoint Security](../05%20Architecture%20and%20Infrastructure%20Security/02%20Endpoint%20Security.md), [Linux Endpoint Security](../05%20Architecture%20and%20Infrastructure%20Security/Linux%20Endpoint%20Security.md), [Windows Endpoint Security](../05%20Architecture%20and%20Infrastructure%20Security/Windows%20Endpoint%20Security.md)
Write there: add incident-response-specific material for ransomware containment, persistence removal, and safe host reintroduction after recovery.

### Phishing

Use phishing here only as an entry point to account compromise and broader incident escalation.

Related notes: [Common Threats and Attacks](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md), [Authentication](../02%20Identity%20and%20Access/01%20Authentication.md)
Write there: add phishing-triggered account takeover response steps such as token revocation, session invalidation, and MFA re-registration.

### Man-in-the-Middle attacks

Use this as a reminder that communication interception can turn into credential theft, session hijacking, or data exposure.

Related notes: [Common Threats and Attacks](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md), [Cryptography](../03%20Cryptography%20and%20Data%20Protection/01%20Cryptography.md), [Network Security](../05%20Architecture%20and%20Infrastructure%20Security/Network%20Security/01%20Network%20Security.md), [Mobile Device Security](../05%20Architecture%20and%20Infrastructure%20Security/Mobile%20Device%20Security.md)
Write there: add detection and containment guidance for certificate abuse, insecure Wi-Fi exposure, and session interception.

### DoS and DDoS

Use this as a service-availability incident category rather than a network-defense deep dive.

Related notes: [Common Threats and Attacks](../01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md), [Network Security](../05%20Architecture%20and%20Infrastructure%20Security/Network%20Security/01%20Network%20Security.md), [Firewall](../05%20Architecture%20and%20Infrastructure%20Security/Network%20Security/Firewall%20Technologies.md), [Cloud Security](../05%20Architecture%20and%20Infrastructure%20Security/Cloud%20Security.md)
Write there: add response patterns for traffic scrubbing, rate limiting, failover, and provider coordination during service exhaustion incidents.

### SQL Injection

Use this as an example of an application-layer incident that requires both technical containment and impact scoping.

Related notes: [OWASP](../04%20Application%20and%20API%20Security/OWASP.md), [Security Principles](../01%20Foundations%20and%20Risk/01%20Security%20Principles.md)
Write there: add investigation guidance for database impact scoping, log review, credential rotation, and application rollback after exploitation.

### Zero-day exploits

Use this category to emphasize compensating controls and fast containment when no patch exists yet.

Related notes: [Risk Management and Threat Modeling](../01%20Foundations%20and%20Risk/02%20Risk%20Management%20and%20Threat%20Modeling.md), [Patch Management and Security Updates](../05%20Architecture%20and%20Infrastructure%20Security/Patch%20Management%20and%20Security%20Updates.md), [Emerging Security Challenges](Emerging%20Security%20Challenges.md)
Write there: add compensating-control guidance for periods when no vendor patch exists.

### IoT attacks

Use this as a fleet-management incident category where scale and device visibility matter.

Related notes: [IoT Security](../05%20Architecture%20and%20Infrastructure%20Security/IoT%20Security.md), [Intrusion Detection and Prevention](01%20Intrusion%20Detection%20and%20Prevention.md), [Emerging Security Challenges](Emerging%20Security%20Challenges.md)
Write there: add incident-response guidance for device isolation, firmware validation, and fleet-wide compromise assessment.

### Insider threats

Use this as a reminder that valid credentials do not imply safe behavior.

Related notes: [Intrusion Detection and Prevention](01%20Intrusion%20Detection%20and%20Prevention.md), [Authorization and Access Control](../02%20Identity%20and%20Access/02%20Authorization%20and%20Access%20Control.md), [Zero Trust Architecture](../02%20Identity%20and%20Access/03%20Zero%20Trust%20Architecture.md)
Write there: add evidence-handling and containment guidance for privileged misuse and abnormal but authenticated behavior.

---

### Disaster categories

### Natural disasters

Environmental disruption affecting operations or facilities.

### Physical disasters

Facility or infrastructure failure affecting system availability.

### Technological disasters

Technology-driven outage or destructive compromise.

---

## Incident Response Plan

## What an Incident Response Plan is

An **Incident Response Plan**, or **IRP**, defines how the organization handles incidents from detection through closure.

## Purpose of an IRP

Keep this section focused on speed, coordination, evidence handling, and controlled restoration.

## What an IRP should include

### Roles and responsibilities

Define ownership across security, IT, legal, management, communications, HR, and external responders when needed.

### Severity levels

Keep only a practical severity model.

|Severity|Description|
|---|---|
|Low|Minor event with limited impact|
|Medium|Confirmed issue affecting one system or user group|
|High|Major incident affecting critical systems or sensitive data|
|Critical|Business-wide disruption or active large-scale compromise|

### Escalation procedures

Define who is informed, when escalation happens, and which actions need approval.

### Communication plan

Define internal, customer, regulator, law-enforcement, and public-communications paths.

### Playbooks

Reference scenario-specific playbooks rather than embedding them here.

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

|System|RPO|RTO|Meaning|
|---|---|---|---|
|Payment system|15 minutes|1 hour|Very little data loss or downtime allowed|
|Internal wiki|24 hours|2 days|Longer outage acceptable|
|Customer database|30 minutes|2 hours|High business impact|

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

Related notes: [Cybersecurity Governance](../01%20Foundations%20and%20Risk/04%20Cybersecurity%20Governance.md), [Risk Management and Threat Modeling](../01%20Foundations%20and%20Risk/02%20Risk%20Management%20and%20Threat%20Modeling.md)
Write there: map the incident-response lifecycle in this note directly to Identify, Protect, Detect, Respond, and Recover.

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

---

## Final Integrated Model

Use this as the condensed operating model.

### Before an incident

- Risk analysis.
- Business impact analysis.
- IRP.
- DRP.
- Backups.
- SIEM.
- SOC.
- Training.
- Policies.
- Testing.

### During an incident

- Detect.
- Classify.
- Escalate.
- Communicate.
- Contain.
- Preserve evidence.
- Investigate.
- Eradicate.

### After containment

- Identify root cause.
- Validate backups.
- Patch weaknesses.
- Restore systems.
- Monitor.
- Document.

### After recovery

- Post-mortem.
- Lessons learned.
- Update plans.
- Improve controls.
- Test again.
