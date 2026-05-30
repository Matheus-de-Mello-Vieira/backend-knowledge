# Security Testing

Security testing is a specialized software testing discipline dedicated to evaluating an application, system, or network infrastructure to uncover hidden vulnerabilities, flaws, and security gaps. Unlike standard development practices that focus on making software work, security testing focuses on ensuring the software cannot be intentionally broken or abused by malicious actors.

In an era of relentless cyber threats and complex compliance regulations, security testing shifts an organization from a reactive posture (responding to a breach) to a proactive posture (hardening defenses in advance).

While both Quality Assurance (QA) and Security Testing aim to improve software quality, they operate with fundamentally different mindsets, methodologies, and objectives.

| **Feature**         | **QA Testing (Functional/Performance)**                                                                | **Security Testing**                                                                                                        |
| ------------------- | ------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| **Primary Focus**   | **What the system _should_ do.** Validates features, user experience, performance, and business logic. | **What the system _should not_ do.** Identifies hidden behaviors, technical vulnerabilities, and logic flaws.               |
| **Testing Mindset** | Assumes the user acts in good faith, inputting valid data to achieve a standard goal.                  | Assumes the user acts with malice, intentionally entering corrupted data or manipulating parameters to bypass rules.        |
| **Success Metric**  | The application meets business specifications, functions smoothly, and doesn't crash under load.       | The application successfully resists unauthorized access, protects data integrity, and maintains availability under attack. |
| **Core Question**   | _"Does the software work correctly for the user?"_                                                     | _"Can the software be exploited or abused by an attacker?"_                                                                 |

## Core Goals

Software systems are inherently complex, and complexity is the enemy of security. Security testing exists to actively simulate the adversarial perspective, focusing heavily on four critical goals:

- **Identifying Hidden Weaknesses:** Actively uncovers technical flaws, misconfigurations, and architectural gaps buried within the system. This continuous discovery provides the raw data necessary to perform a comprehensive [Vulnerability Assessment](05%20Vulnerability%20Assessment.md), mapping out the software's true attack surface.
- **Proactively Reducing Risk:** Acts as the practical execution arm of your [Risk Management and Threat Modeling](02%20Risk%20Management%20and%20Threat%20Modeling.md) strategies. By testing early in the development lifecycle, it proves whether theoretical threat scenarios can actually be realized, allowing teams to prioritize and neutralize risks when they are cheapest to fix.
- **Preventing System Abuse:** Stops attackers from manipulating application logic, APIs, or data entry points. It ensures the software is hardened against the most critical and statistically common attack vectors, specifically targeting the industry-standard vulnerabilities categorized by [OWASP](../04%20Application%20and%20API%20Security/OWASP.md).
- **Validating Security Controls:** Stresses your deployed defenses—from firewalls and data encryption to access tokens—under hostile, real-world conditions to definitively prove that your security mechanisms function as intended
- **Regulatory & Framework Adherence**: Security assessments also validate whether the requirements demanded by industry frameworks and standards—such as ISO 27001, MITRE, LGPD, and NIST—are being properly met.

## Assessments vs. Testing

In the cybersecurity industry, the terms "assessment" and "testing" are often used interchangeably, but they represent two fundamentally different approaches to evaluating a security posture. Understanding the distinction is critical for scoping the right activity for the organization's current maturity level.

| **Feature**           | **Security Assessment**                                                                                 | **Security Testing**                                                                   |
| --------------------- | ------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| **Mindset**           | Defensive and Strategic                                                                                 | Offensive and Tactical                                                                 |
| **Primary Action**    | Evaluating, scanning, and auditing the current state of defenses against a known baseline or framework. | Actively attempting to bypass controls, chain vulnerabilities, and compromise systems. |
| **Question Answered** | _"What are our theoretical risks, and are we compliant with our policies?"_                             | _"Can a real-world attacker actually breach our systems right now?"_                   |
| **Typical Outputs**   | Risk scorecards, compliance gaps, and maturity roadmaps.                                                | Proof of compromise, attack narrative logs, and remediation code snippets.             |

While testing methodologies (like Penetration Testing or SAST/DAST) focus on execution, assessments focus on program-wide evaluation. The two most critical types of assessments in an organization's security lifecycle include:

- **Vulnerability and Risk Assessment:** The continuous, programmatic [Vulnerability Assessment](05%20Vulnerability%20Assessment.md) effort of scanning the environment to catalog technical flaws. This data feeds directly into broader [Risk Management and Threat Modeling](02%20Risk%20Management%20and%20Threat%20Modeling.md) strategies to generate a prioritized risk scorecard for corrections.
- **Maturity Assessment:** A strategic evaluation of the organization's [Cybersecurity Governance](04%20Cybersecurity%20Governance.md) that measures the overarching security posture—including policies, culture, and processes—against industry frameworks to better direct executive investments in protection.

## Security Testing Lifecycle  

Security testing is rarely a one-off event; to be effective, it must be treated as a continuous, structured lifecycle. Approaching it as a rigid methodology ensures that testing is comprehensive, legal, and translates directly into actionable security improvements rather than just a list of raw vulnerabilities.

Here is how you can break down the eight phases of the lifecycle for your notes:

**1. Plan and Scope**

- **The Goal:** Define exactly what is being tested and, just as importantly, what is _out of bounds_.
- **Key Actions:** Establishing the "Rules of Engagement" (RoE). This involves deciding if the test will happen in a production or staging environment, identifying the specific IP ranges or application URLs involved, and obtaining formal, written authorization to prevent the testing from being legally classified as a cyberattack.

**2. Model Threats**

- **The Goal:** Understand the ahttps://www.google.com/search?q=%23dversary before launching any tools, by [Risk Management and Threat Modeling](02%20Risk%20Management%20and%20Threat%20Modeling.md).
- **Key Actions:** Identifying the most critical business assets (e.g., the customer database) and determining the most likely threat actors (e.g., financially motivated hackers or malicious insiders). This ensures the subsequent tests mimic realistic attack scenarios.

**3. Select Test Strategy**

- **The Goal:** Match the right testing methodologies to the scope and threat model.
- **Key Actions:** Deciding the blend of automated and manual testing required. For example, selecting SAST for early-stage code review, DAST for a live web application, or full-scope manual penetration testing for complex business logic.

**4. Execute Tests**

- **The Goal:** The active engagement phase where the system is actually probed for weaknesses.
- **Key Actions:** Running automated vulnerability scanners, fuzzing input fields, and manually attempting to bypass authentication, escalate privileges, or exfiltrate data based on the chosen strategy.

**5. Validate Findings**

- **The Goal:** Ensure accuracy and build trust with the development team.
- **Key Actions:** Automated tools generate a massive amount of "noise." Security analysts must manually review the output to filter out **false positives** (things the scanner flagged as a risk, but actually aren't) and consolidate duplicate findings.

**6. Report Risk**

- **The Goal:** Translate technical flaws into business context.
- **Key Actions:** Delivering a structured report that ranks vulnerabilities based on severity (often using frameworks like [CVSS](05%20Vulnerability%20Assessment.md#CVSS)). It explains _how_ the flaw was found, the potential business impact if exploited, and provides actionable remediation guidance.

**7. Remediate**

- **The Goal:** Fix the broken defenses.
- **Key Actions:** This phase shifts the responsibility to the development, network, or IT operations teams. They apply patches, rewrite vulnerable source code, or adjust firewall configurations based on the recommendations in the risk report.

**8. Retest and Verify Closure**

- **The Goal:** Prove that the bleeding has stopped.
- **Key Actions:** Security testers return to the specific vulnerabilities identified in the report and attempt the exact same exploits again. This validates that the remediation was successful, the flaw is truly closed, and the patch didn't accidentally break another part of the application.
## Planning, Scope, and Authorization  

Before a single line of code is scanned or a packet is sent, the foundational parameters of the assessment must be legally and operationally defined. Phase 1 establishes the structural boundaries of the security test, serving as both a project roadmap and a vital legal shield for the testing team.

-  **Permission and Legal Boundaries**

	- **The "Get Out of Jail Free" Card:** Formal, written authorization—signed by an executive with the legal authority to bind the organization—is the most critical requirement of any security test. Without explicit written consent, security testing can be legally classified as unauthorized computer access or criminal hacking under statutes like the Computer Fraud and Abuse Act (CFAA).
	- **Third-Party Providers:** If the target infrastructure is hosted on cloud platforms (e.g., AWS, Azure, GCP) or managed by a third-party data center, their explicit policies and notification requirements must be verified and followed before testing begins.

- **Rules of Engagement (RoE)**

	- **The Operational Contract:** The RoE is a mutually agreed-upon document that dictates _how_ the test will be performed
	- **Core Logistics:** It defines the exact timelines (dates and specific hours of testing), communication channels, contact information for emergencies, and whether the internal security team (Blue Team) should be notified in advance or left in the dark to test their detection capabilities.

- **In-Scope and Out-of-Scope Systems**

	- **Strict Perimeters:** A precise, immutable list of assets to be tested must be compiled. This typically includes specific domain names, IP addresses, network subnets, API endpoints, or source code repositories.
	- **Out-of-Scope Restrictions:** Any asset, server, or subnet not explicitly listed is strictly off-limits. Accidentally touching an out-of-scope system (such as a shared server belonging to a different tenant in a cloud environment) represents a severe breach of contract and legal risk.

- **Test Depth**

	- **Defining the Intensity:** Sets expectations regarding how far an analyst should go upon discovering a flaw.
	- **Vulnerability vs. Exploitation:** Does the strategy require the tester to merely identify and document a vulnerability (e.g., proving SQL injection exists), or are they authorized to actively exploit it to pivot deeper into the internal corporate network and demonstrate maximum business impact? 

 - **Data Handling**

	- **Protecting Sensitive Findings:** Security testing inherently uncovers highly sensitive data, including unpatched vulnerabilities, proprietary source code, and potentially exposed customer Personally Identifiable Information (PII).
	- **Secure Storage and Disposal:** The planning phase must define how the testing team will encrypt data at rest during the assessment, who has access to the findings, how long the data will be retained, and the secure sanitization method used to destroy the data once the final report is accepted.

-  **Non-Disruption Requirements**

	- **Preserving Business Continuity:** Tests must be engineered to avoid causing a Denial of Service (DoS) or disrupting daily business operations.
	- **Operational Guardrails:** This involves specifying time windows (e.g., conducting invasive network scans only between 11:00 PM and 4:00 AM) and restricting the use of automated testing tools that are known to crash legacy systems or saturate network bandwidth.

-  **When to Stop Testing**

	- **Emergency Thresholds:** Clear criteria must be established for immediately halting the assessment.
	- **Trigger Conditions:** Testing must stop instantly if a production system crashes, if data corruption is detected, or if the testing team accidentally discovers evidence of an _actual_, active malicious breach by an unauthorized third party. In the case of a real-world breach, the test pivots immediately into incident response mode.
## Security Testing Techniques

While automated tools are excellent at rapidly scanning for known vulnerabilities at scale, they lack human intuition, contextual awareness, and an understanding of organizational workflows. This is where manual security techniques become indispensable.

### Manual Security Review

Manual security reviews involve human experts analyzing the system's underlying foundations, logic, and configurations. Because it relies on human intellect rather than automated signatures, this phase is critical for identifying complex, multi-step flaws that automated scanners inherently miss.

- **Secure Code Review:** A meticulous, line-by-line examination of the application's source code by a security expert.
    - **The Goal:** To uncover complex coding errors, race conditions, hardcoded secrets, and nuanced injection vulnerabilities that automated Static Application Security Testing (SAST) tools either miss or flag incorrectly. It ensures the code adheres to secure coding standards before it is ever compiled.
- **Architecture Review:** Taking a step back to analyze the "big picture" system design and infrastructure diagrams.
    - **The Goal:** To identify structural design flaws early in the project. Reviewers map out trust boundaries, evaluate data flow between components, and ensure that defense-in-depth principles (like putting the database on a private, isolated subnet rather than the public web tier) are properly integrated into the blueprint.
- **Configuration Review:** A deep dive into the settings and parameters of servers, cloud environments, databases, and network appliances.
    - **The Goal:** To hunt down misconfigurations that scanners might overlook. This includes checking for default vendor passwords, overly permissive firewall rules, unencrypted cloud storage buckets (like AWS S3), and ensuring that security headers and TLS certificates are strictly enforced.
- **Access-Control Review:** An evaluation of how the system grants, tracks, and restricts user permissions.
    - **The Goal:** To definitively prove that the system enforces the Principle of Least Privilege. Reviewers manually verify that **horizontal privilege escalation** (User A accessing User B's private data) and **vertical privilege escalation** (a standard user finding a backdoor to become an Administrator) are mathematically and logically impossible.
- **Business-Logic Review:** The testing of the unique, bespoke rules that govern how the application is _supposed_ to operate.
    - **The Goal:** To find ways an attacker could manipulate legitimate workflows for malicious gain. Because every app's business logic is unique, automated scanners cannot test for this. Examples include manipulating an e-commerce checkout to accept a negative price, skipping a mandatory identity verification step, or exploiting a temporal flaw to apply a single discount code fifty times.

### Vulnerability Scanning

While manual reviews rely on human intuition to find complex logic flaws, **Vulnerability Scanning** relies on high-speed automation to identify known, documented security weaknesses across a massive scale. By cross-referencing system configurations and software versions against global threat databases (like the Common Vulnerabilities and Exposures, or CVE, list), these tools act as an organization's broad, continuous radar for low-hanging fruit.

#### Types of Scanning

- **Application Scanning:** [Automated tools (like the DAST and SAST) ](#Application%20Scanning%20(SAST,%20DAST,%20and%20IAST)) that actively crawl and probe custom-built web applications and APIs, hunting for standard coding vulnerabilities like injection flaws or cross-site scripting.
- **Dependency Scanning (Software Composition Analysis):** Modern software is rarely built from scratch; it relies heavily on third-party, open-source libraries. Dependency scanners parse the application's manifest files to identify outdated or vulnerable open-source components, preventing supply chain attacks.
- **Infrastructure Scanning:** Focuses on the underlying host operating systems, hypervisors, and server environments. It checks for missing security patches, outdated legacy protocols (like SMBv1), and weak default configurations across the internal network.
- **Cloud-Resource Scanning (CSPM):** Specifically designed for dynamic cloud environments (AWS, Azure, GCP). Instead of scanning traditional IP addresses, it evaluates cloud infrastructure APIs to find exposed storage buckets (e.g., public AWS S3 buckets), overly permissive Identity and Access Management (IAM) roles, and misconfigured virtual private clouds.
- **Network-Service Scanning:** Scans external and internal IP ranges to discover active hosts and open ports. Once it finds a running service (like an SSH or FTP server), it attempts to grab the service's version banner and matches it against databases of known vulnerabilities.
#### Application Scanning (SAST, DAST, and IAST)

Automated application scanning is broken down into distinct methodologies based on _when_ and _how_ the application is tested during the development lifecycle:

- **SAST (Static Application Security Testing)** — /sæst/ or /ˌɛs ˌeɪ ˌɛs ˈtiː/:

	- **The Approach:** Often called "White-Box" testing. SAST analyzes the raw source code, byte code, or binaries _without_ running the application.
    - **The Goal:** It looks from the inside out. It is used very early in the development lifecycle (shifting left) to find fundamental coding errors, hardcoded credentials, and unsafe library calls before the software is ever compiled.    
    - **Pros & Cons:** Excellent at pointing a developer to the exact line of vulnerable code, but it is notorious for high false-positive rates because it lacks runtime context.

- **DAST (Dynamic Application Security Testing)** — /dæst/ or /ˌdiː ˌeɪ ˌɛs ˈtiː/:

	* **The Approach:** Often called "Black-Box" testing. DAST interacts with the fully compiled, running application from the outside, exactly as a threat actor would.    
    - **The Goal:** It looks from the outside in. It crawls the live application (usually in a staging environment) and automatically fires payloads at input fields to uncover runtime vulnerabilities like SQL Injection, Cross-Site Scripting, and server misconfigurations.
    - **Pros & Cons:** Highly accurate for testing real-world exploitability with fewer false positives, but when it finds a flaw, it cannot tell the developer which line of source code needs to be fixed.
  
- **IAST (Interactive Application Security Testing)** — /iːˈæst/ or /ˌaɪ ˌeɪ ˌɛs ˈtiː/:

	* **The Approach:** A modern "Gray-Box" approach combining the best of both SAST and DAST.
    - **The Goal:** It places a software agent directly inside the running application server. As the app is dynamically tested (either by a DAST scanner or normal QA testers), the agent monitors how the code and memory react in real-time, providing highly accurate vulnerability reports that include the exact line of vulnerable code.
#### Managing the Output

Because scanners operate blindly at scale, they generate massive amounts of data. The effectiveness of a vulnerability scanning program depends entirely on how the security team handles this output:

- **False-Positive Handling:** Scanners are notoriously noisy and often flag issues that don't actually exist (e.g., flagging a software version as vulnerable based on its banner, without realizing the Linux vendor securely backported the patch). Security teams must continuously tune the scanner's logic and filter out these false alarms to prevent alert fatigue.
- **Finding Validation:** The critical manual step that bridges scanning and remediation. Before a developer is asked to fix a flaw, a security analyst manually verifies the scanner's claim, proving that the vulnerability actually exists, confirming it is realistically exploitable in the current environment, and determining its true business impact.
  
### Penetration Testing

While vulnerability scanning relies on automated tools to broadly _identify_ potential open doors, **Penetration Testing (Pen Testing)** is the manual, active, and authorized attempt to physically break through those doors. It is the ultimate validation of an organization's security posture, simulating the exact tactics, techniques, and procedures (TTPs) of a real-world threat actor.

- **Reconnaissance:** The intelligence-gathering phase that occurs before any active attacks are launched. This involves passive techniques (like leveraging Open-Source Intelligence, or OSINT, to find leaked employee credentials or public GitHub repositories) and active techniques (like network mapping and port scanning) to deeply map out the target's attack surface.
- **Exploitation Validation:** Moving beyond the theoretical "maybe" of an automated scanner. If a scanner flags a potential vulnerability, the penetration tester actively crafts and executes a custom payload to prove definitively whether the system is truly vulnerable, entirely eliminating false positives.
- **Chaining Weaknesses:** The hallmark of manual security testing. Automated tools view vulnerabilities in isolation, but human attackers do not. A skilled penetration tester will take three distinct, low-severity bugs (e.g., an outdated server plugin, weak password requirements, and a slightly misconfigured file permission) and chain them together sequentially to achieve a critical, system-wide compromise.
- **Impact Demonstration:** Translating a highly technical flaw into a tangible business risk. Instead of simply stating "the database is vulnerable," the tester demonstrates the real-world impact by securely exfiltrating a dummy table, escalating their account to a Domain Administrator, or showing exactly how they could disrupt the business's core operations.
- **Documentation:** Meticulous, step-by-step record-keeping throughout the entire engagement. Testers must log every IP address targeted, every payload sent, screenshots of successful breaches, and the exact timestamps of the attacks. This is crucial for verifying the attack path and allowing the client's internal Blue Team to correlate the penetration test against their own security alerts.
- **Responsible Reporting:** The final and most critical deliverable. The testing team securely transmits a comprehensive report detailing the narrative of the attack, the business risk of the findings, and, most importantly, providing actionable, prioritized remediation guidance so the organization can close the holes before a real adversary exploits them.

### Security Testing Techniques

- **Red Team and Blue Team Engagements:** An advanced adversarial simulation. The Red Team acts as the offensive unit, mimicking a real-world attacker to exploit the infrastructure, while the internal Blue Team actively defends, detects, and executes [Incident Response and Recovery](Incident%20Response%20and%20Recovery) procedures to stop the intrusion.

- **Physical Tests and Social Engineering:** Simulations focused on the human and physical perimeters. This involves face-to-face or digital simulations where an actor attempts to bypass physical access controls or extract confidential credentials using psychological manipulation and [Common Threats and Attacks](03%20Common%20Threats%20and%20Attacks.md) like phishing or pretexting.

### Security Regression Testing

Even after a vulnerability has been identified and patched, the security lifecycle is not complete. **Security Regression Testing** is the ongoing practice of ensuring that software updates, bug fixes, and new feature deployments do not inadvertently break existing security controls or resurrect old vulnerabilities.

- **Retesting Fixed Vulnerabilities:** The immediate, targeted action taken after a developer applies a patch. The security team (or an automated script) fires the exact same malicious payloads that originally triggered the vulnerability to prove that the specific attack vector is now definitively blocked.
- **Validating Remediation:** Moving beyond just verifying the fix, this ensures the patch was implemented correctly at the root cause level. It also confirms that the applied security fix did not cause collateral damage, such as accidentally breaking a legitimate business workflow or blocking authorized users.
- **Preventing Reintroduction (The "Zombie Bug"):** In collaborative software development, it is incredibly common for an old, vulnerable piece of code to be accidentally merged back into the main branch by a developer working on an outdated local copy. Regression testing acts as a continuous safety net to catch these resurrected flaws before they are re-deployed.
- **CI/CD Security Gates:** To scale regression testing, organizations embed automated security tools ([like SAST and DAST scanners](#Application%20Scanning%20(SAST,%20DAST,%20and%20IAST))) directly into their Continuous Integration and Continuous Deployment (CI/CD) pipelines. These act as automated checkpoints. If a developer's new code commit fails a security test or reintroduces a known flaw, the security gate automatically halts the build process, preventing the vulnerable code from ever reaching the production environment.