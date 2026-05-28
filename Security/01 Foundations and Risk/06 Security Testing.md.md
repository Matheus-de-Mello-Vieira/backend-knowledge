# Security Testing

This note should stay as an overview and routing note for security testing. It is the right place to explain what testing is, how the major testing modes differ, and how they connect to the rest of the security learning path. Deeper domain content already belongs in the more specialized notes linked below.

## Foundations of Security Testing

Study what security testing is, how it differs from QA testing, and why it exists. Focus on the goals: finding weaknesses, reducing risk, validating controls, and preventing abuse before attackers can exploit issues.

- **Keep here, but only as an introduction.** This note is the right home for what security testing is, why it exists, and how it reduces risk. The deeper assessment process already belongs in [Vulnerability Assessment](05%20Vulnerability%20Assessment.md).
- **Bring in:** a condensed `discover -> verify -> assess -> prioritize` flow from [Vulnerability Assessment](05%20Vulnerability%20Assessment.md), plus a short `vulnerability / threat / risk` distinction from [Risk Management and Threat Modeling](02%20Risk%20Management%20and%20Threat%20Modeling.md).
- **Worth linking:** [Vulnerability Assessment](05%20Vulnerability%20Assessment.md) because it turns the intro into an actionable workflow, [Risk Management and Threat Modeling](02%20Risk%20Management%20and%20Threat%20Modeling.md) because testing should be framed as risk reduction, and [OWASP](../04%20Application%20and%20API%20Security/OWASP.md) because it is the strongest application-testing baseline already in the vault.

## Core Security Concepts

Learn the basic vocabulary first: vulnerability, threat, risk, exploit, attack surface, asset, control, authentication, authorization, confidentiality, integrity, and availability. These terms show up everywhere.

- **Keep here only as a testing-oriented vocabulary bridge.** The canonical homes are [Security Principles](01%20Security%20Principles.md) and [Risk Management and Threat Modeling](02%20Risk%20Management%20and%20Threat%20Modeling.md).
- **Bring in:** the security tenets and key principles most reused in testing from [Security Principles](01%20Security%20Principles.md), plus testing-relevant definitions like `asset`, `attack surface`, `control`, `threat`, `vulnerability`, and `risk` from [Risk Management and Threat Modeling](02%20Risk%20Management%20and%20Threat%20Modeling.md).
- **Worth linking:** [Security Principles](01%20Security%20Principles.md) because it is the main home for foundational vocabulary, [Risk Management and Threat Modeling](02%20Risk%20Management%20and%20Threat%20Modeling.md) because it explains how those concepts drive prioritization, and [Authentication](../02%20Identity%20and%20Access/01%20Authentication.md) plus [Authorization and Access Control](../02%20Identity%20and%20Access/02%20Authorization%20and%20Access%20Control.md) because those terms should be referenced rather than re-explained here.

## Web Application Security

Study common web vulnerabilities such as injection, broken access control, authentication flaws, cross-site scripting, insecure file handling, and insecure session management. This is one of the most practical starting points.

- **Keep here only as a short testing-focused subsection.** The broader subject clusters much better around [OWASP](../04%20Application%20and%20API%20Security/OWASP.md) and the adjacent application-security notes.
- **Bring in:** the idea that OWASP Top 10 is the baseline checklist for web testing, plus a compact mapping to broken access control, injection, auth/session failures, misconfiguration, and SSRF from [OWASP](../04%20Application%20and%20API%20Security/OWASP.md). It is also worth borrowing the `SAST` / `DAST` framing from [Vulnerability Assessment](05%20Vulnerability%20Assessment.md).
- **Worth linking:** [OWASP](../04%20Application%20and%20API%20Security/OWASP.md) because it is the main anchor for the topic, [CSRF Tokens](../04%20Application%20and%20API%20Security/CSRF%20Tokens.md) and [CORS](../04%20Application%20and%20API%20Security/CORS.md) because they are focused web-testing targets, and [Backend Security Checklist](../99%20References%20and%20Checklists/Backend%20Security%20Checklist.md) because it translates the topic into concrete checks.

## API Security Testing

Learn how APIs are attacked and tested. Focus on authentication, authorization, rate limiting, object-level access control, input validation, token handling, and excessive data exposure.

- **Keep here as an overview, not as the main content home.** The closest existing deep note is [OWASP](../04%20Application%20and%20API%20Security/OWASP.md).
- **Bring in:** a compact list of API test targets from [OWASP](../04%20Application%20and%20API%20Security/OWASP.md): broken object-level access, auth/session failures, excessive data exposure, and input-validation problems. It is also worth pulling in a small testing checklist subset from [Backend Security Checklist](../99%20References%20and%20Checklists/Backend%20Security%20Checklist.md): rate limiting, token handling, JWT/OAuth misuse, and request/response validation.
- **Worth linking:** [OWASP](../04%20Application%20and%20API%20Security/OWASP.md) because it has the strongest API-adjacent attack classes, [Authentication](../02%20Identity%20and%20Access/01%20Authentication.md) and [Authorization and Access Control](../02%20Identity%20and%20Access/02%20Authorization%20and%20Access%20Control.md) because API testing often collapses into those two concerns, and [API Management](../../Web%20APIs/02%20REST/06%20API%20Management.md) plus [Proxying and Load Balancing](../../Networking/99%20Proxying%20and%20Load%20Balancing.md) because gateways and proxies enforce many of the edge controls being tested.

## Secure Code Review

Study how to inspect source code for security problems. Learn to identify unsafe patterns, missing validation, insecure crypto usage, hardcoded secrets, poor error handling, and dangerous dependency usage.

- **Keep here.** This topic fits the note because code review is a core security-testing activity, not just a separate coding practice.
- **Bring in:** the review targets already defined in [Security Principles](01%20Security%20Principles.md), especially input validation, hardcoded secrets, and information leakage, plus the review-process expectations from [Backend Security Checklist](../99%20References%20and%20Checklists/Backend%20Security%20Checklist.md) such as avoiding self-approvals and continuously running static and dependency checks. [OWASP](../04%20Application%20and%20API%20Security/OWASP.md) is also worth using as a review baseline.
- **Worth linking:** [Backend Security Checklist](../99%20References%20and%20Checklists/Backend%20Security%20Checklist.md) because it turns the section into review gates, [OWASP](../04%20Application%20and%20API%20Security/OWASP.md) because reviewers need a flaw taxonomy, and [Vulnerability Assessment](05%20Vulnerability%20Assessment.md) because it places review alongside `SAST`, `DAST`, and manual validation.

## Automated Security Testing

Learn the main automated testing categories: **SAST**, **DAST**, **SCA**, secret scanning, container scanning, and infrastructure-as-code scanning. Understand what each tool can and cannot detect.

- **Keep here.** This is one of the main responsibilities of a security-testing overview note.
- **Bring in:** the distinction from [Vulnerability Assessment](05%20Vulnerability%20Assessment.md) that application assessment combines automated scanning, manual testing, `SAST`, and `DAST`. It is also worth pulling in examples from [OWASP](../04%20Application%20and%20API%20Security/OWASP.md) around `SCA`, dependency scanning, container scanning, CI/CD integration, and `DAST`, plus the `Shift Security Left` idea from [Security Principles](01%20Security%20Principles.md).
- **Worth linking:** [Vulnerability Assessment](05%20Vulnerability%20Assessment.md) because automated output still needs validation and prioritization, [OWASP](../04%20Application%20and%20API%20Security/OWASP.md) because it contains the best concrete examples, and [Cloud Security](../05%20Architecture%20and%20Infrastructure%20Security/Cloud%20Security.md) because infra-oriented automation like IaC and container scanning belongs there in depth.

## Vulnerability Scanning

tudy how scanners detect known issues in applications, dependencies, servers, cloud resources, and network services. Learn how to validate findings, remove false positives, and prioritize remediation.

- **Keep the testing-technique view here, but split the management/process layer out.** The broader assessment and remediation discipline belongs with [Vulnerability Assessment](05%20Vulnerability%20Assessment.md).
- **Bring in:** the assessment-type distinctions and the vulnerability-management lifecycle from [Vulnerability Assessment](05%20Vulnerability%20Assessment.md), especially how findings move from identification to verification and remediation. Only bring tool examples from [Backend Security Checklist](../99%20References%20and%20Checklists/Backend%20Security%20Checklist.md) if you want this note to become more practical.
- **Worth linking:** [Vulnerability Assessment](05%20Vulnerability%20Assessment.md) because scanning findings need context and prioritization, [Patch Management and Security Updates](../05%20Architecture%20and%20Infrastructure%20Security/Patch%20Management%20and%20Security%20Updates.md) because many scan findings end in patching, and [Cloud Security](../05%20Architecture%20and%20Infrastructure%20Security/Cloud%20Security.md) because cloud resources and container images are explicit scanning targets.

## Threat Modeling

Learn how to think about security before testing begins. Study how to map assets, trust boundaries, data flows, likely attackers, abuse cases, and possible mitigations.

- **Move the main content elsewhere.** This topic should stay here only as a short pointer explaining that threat modeling is a design-time input to testing. Its real home is [Risk Management and Threat Modeling](02%20Risk%20Management%20and%20Threat%20Modeling.md).
- **Bring in:** only a compact summary of how testing uses threat modeling: assets, trust boundaries, data flows, attacker assumptions, and risk prioritization. The backlog/process reminder from [Backend Security Checklist](../99%20References%20and%20Checklists/Backend%20Security%20Checklist.md) is also useful.
- **Worth linking:** [Risk Management and Threat Modeling](02%20Risk%20Management%20and%20Threat%20Modeling.md) because it is the dedicated home, [Common Threats and Attacks](03%20Common%20Threats%20and%20Attacks.md) because it informs abuse-case design, and [OWASP](../04%20Application%20and%20API%20Security/OWASP.md) because threat modeling often feeds directly into application test design.

## Penetration Testing

Study pentesting after you understand the basics. Focus on scope, authorization, methodology, reconnaissance, exploitation validation, impact demonstration, documentation, and responsible reporting.

- **Keep here.** This note is a good home for the overview distinction between pentesting and the rest of security testing.
- **Bring in:** a short explicit distinction from [Vulnerability Assessment](05%20Vulnerability%20Assessment.md) between vulnerability assessment and penetration testing, plus brief methodology anchors from [OWASP](../04%20Application%20and%20API%20Security/OWASP.md) such as `OWASP Testing Guide`, `ASVS`, and `ZAP`.
- **Worth linking:** [Vulnerability Assessment](05%20Vulnerability%20Assessment.md) because readers need the assessment-vs-exploitation boundary, [Risk Management and Threat Modeling](02%20Risk%20Management%20and%20Threat%20Modeling.md) because scope should be threat-driven, and [Common Threats and Attacks](03%20Common%20Threats%20and%20Attacks.md) because pentests validate realistic attack paths rather than random probes.

## Cloud and Infrastructure Security Testing

Learn how to assess cloud configurations, identity permissions, storage exposure, network rules, logging, secrets management, and deployment pipelines.

- **Keep here only as an overview.** The main deep-dive home is [Cloud Security](../05%20Architecture%20and%20Infrastructure%20Security/Cloud%20Security.md).
- **Bring in:** a tighter testing-oriented summary from [Cloud Security](../05%20Architecture%20and%20Infrastructure%20Security/Cloud%20Security.md): IAM/RBAC validation, storage exposure, network-rule review, logging coverage, secrets handling, IaC scanning, container and Kubernetes checks, CSPM/config-drift review, and CI/CD pipeline controls.
- **Worth linking:** [Cloud Security](../05%20Architecture%20and%20Infrastructure%20Security/Cloud%20Security.md) because it already contains the strongest material, [Network Security](../05%20Architecture%20and%20Infrastructure%20Security/Network%20Security/01%20Network%20Security.md) because segmentation and exposure are central test targets, and [Zero Trust Architecture](../02%20Identity%20and%20Access/03%20Zero%20Trust%20Architecture.md) because cloud testing repeatedly comes back to least privilege and continuous verification.

## Mobile Security Testing

Study mobile-specific risks such as insecure local storage, weak certificate validation, hardcoded secrets, insecure API communication, and platform permission misuse.

- **Keep here as a thin testing lens, but split the platform-specific depth out.** The broader domain belongs in [Mobile Device Security](../05%20Architecture%20and%20Infrastructure%20Security/Mobile%20Device%20Security.md).
- **Bring in:** only the testing-relevant mobile-application risks from [Mobile Device Security](../05%20Architecture%20and%20Infrastructure%20Security/Mobile%20Device%20Security.md): local storage, permission misuse, runtime protection, and secure communication. It is also worth reusing the concrete mobile examples from [OWASP](../04%20Application%20and%20API%20Security/OWASP.md), especially disabled certificate validation and embedded keys.
- **Worth linking:** [Mobile Device Security](../05%20Architecture%20and%20Infrastructure%20Security/Mobile%20Device%20Security.md) because it is the best deep note, [OWASP](../04%20Application%20and%20API%20Security/OWASP.md) because it contains mobile-relevant testing examples, and [Common Threats and Attacks](03%20Common%20Threats%20and%20Attacks.md) because mobile tests are usually driven by concrete threats like malware, MitM, and phishing.

## Reporting and Risk Communication

Learn how to write clear findings. A good report explains the issue, affected asset, impact, evidence, severity, reproduction steps, and remediation guidance.

- **Split this topic.** The reporting mechanics belong here, but the broader risk-communication model belongs mainly in [Risk Management and Threat Modeling](02%20Risk%20Management%20and%20Threat%20Modeling.md).
- **Bring in:** the severity, prioritization, and treatment framing from [Risk Management and Threat Modeling](02%20Risk%20Management%20and%20Threat%20Modeling.md), especially `likelihood x impact`, residual risk, and remediation treatment options. Keep this note focused on how to write findings clearly: issue, asset, impact, evidence, severity, reproduction, and remediation.
- **Worth linking:** [Risk Management and Threat Modeling](02%20Risk%20Management%20and%20Threat%20Modeling.md) because it translates findings into business risk, [Cybersecurity Governance](04%20Cybersecurity%20Governance.md) because reports are also governance artifacts, and [Incident Response, Forensics, and Disaster Recovery](../06%20Security%20Operations%20and%20Governance/Incident%20Response,%20Forensics,%20and%20Disaster%20Recovery.md) because testing reports should be clearly distinguished from incident communications.

## Security Testing in the SDLC

Study where security testing fits into software development: design review, threat modeling, code review, CI/CD scanning, pre-release testing, production monitoring, and post-release vulnerability management.

- **Keep here.** This is a framing subsection of security testing and no stronger existing primary home surfaced in the vault.
- **Bring in:** the `Shift Security Left` idea from [Security Principles](01%20Security%20Principles.md), the pipeline gates from [Backend Security Checklist](../99%20References%20and%20Checklists/Backend%20Security%20Checklist.md), and the `validate closure` idea from [Vulnerability Assessment](05%20Vulnerability%20Assessment.md).
- **Worth linking:** [Security Principles](01%20Security%20Principles.md) because it gives the rationale for early integration, [Risk Management and Threat Modeling](02%20Risk%20Management%20and%20Threat%20Modeling.md) because threat modeling is the earliest SDLC activity named here, and [OWASP](../04%20Application%20and%20API%20Security/OWASP.md) because it provides the main application-security verification baseline.

## Ethics, Scope, and Legal Boundaries

Learn the rules before doing practical testing. Only test systems where you have permission, follow the agreed scope, avoid unnecessary disruption, and document actions carefully.

- **Keep the testing-specific boundary layer here, but split the broader legal/governance substance out.**
- **Bring in:** a short summary from [Legal Frameworks and Compliance](../06%20Security%20Operations%20and%20Governance/Legal%20Frameworks%20and%20Compliance.md) about privacy, data handling, and regulatory consequences, plus a short summary from [Cybersecurity Governance](04%20Cybersecurity%20Governance.md) about formal authorization, accountable ownership, and documented approval paths. The core of this section should stay operational: permission, scope, non-disruption, and documentation.
- **Worth linking:** [Legal Frameworks and Compliance](../06%20Security%20Operations%20and%20Governance/Legal%20Frameworks%20and%20Compliance.md) because the legal detail lives there, [Cybersecurity Governance](04%20Cybersecurity%20Governance.md) because scope enforcement depends on governance, and [Incident Response, Forensics, and Disaster Recovery](../06%20Security%20Operations%20and%20Governance/Incident%20Response,%20Forensics,%20and%20Disaster%20Recovery.md) because testing can surface real incidents and evidence-handling concerns.
