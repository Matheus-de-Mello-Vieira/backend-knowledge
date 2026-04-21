<!-- markdownlint-disable MD043 -->

# Authorization and Access Control

Authorization is the process of granting or denying specific permissions to an
authenticated entity. It is governed by the **Principle of Least Privilege
(PoLP)**, which states that a user or system should only have the minimum levels
of access—or permissions—necessary to perform its intended function.

## Access Control Models

To implement authorization effectively, different models can be used depending
on the complexity of the architecture:

- **ACL (Access Control List):** /ˌeɪ.siːˈɛl/
  - **Definition:** A simple list attached to a specific object, like a file or
    a network folder, that specifies which users or system processes are granted
    access and what operations are allowed: Read, Write, or Execute.
  - **Use Case:** Ideal for simple, object-level security. In our architecture,
    a cloud folder might have an ACL allowing only Alice's UID to "Write" data.
- **RBAC (Role-Based Access Control):** /ˌɑːr.biːˈeɪ.siː/
  - **Definition:** Permissions are assigned to specific **roles**, such as
    "Manager," "Editor," or "Administrator," rather than individual users.
    Users are then assigned to one or more roles.
  - **Benefit:** Highly scalable and easier to manage in large organizations. If
    Bob is promoted to an "Administrator" role, his permissions update
    automatically across the entire system.
- **ABAC (Attribute-Based Access Control):** /ˌeɪ.biːˈeɪ.siː/
  - **Definition:** The most flexible and complex model. Access is granted based
    on a combination of **attributes**:
    - **User attributes** such as job title or department.
    - **Resource attributes** such as file sensitivity level.
    - **Environmental attributes** such as time of day or current location.
  - **Connection to Adaptive Auth:** ABAC is often used in the "Adaptive
    Authentication" scenarios we discussed. For example: *"Allow Bob to access
    sensitive files only if he is in the office during business hours."*

## Credential Lifecycle Management

Managing credentials, such as passwords, API keys, and digital certificates, is
a continuous process. A failure at any stage of the lifecycle can compromise the
entire architecture, regardless of how strong the individual authentication
factors are.

1. **Provisioning (Birth):** The first stage involves creating the identity and
   assigning the necessary permissions based on **RBAC** or **ABAC**.
   - **Secure Delivery:** Temporary credentials must be sent through secure
     channels and forced to change upon first use.
   - **Verification:** The identity must be thoroughly vetted before a
     credential is issued to ensure **Authenticity**.
2. **Maintenance and Rotation (Life):** Credentials should not be static. The
   longer a credential remains unchanged, the higher the risk of it being
   compromised through slow-burning attacks like brute force or credential
   stuffing.
   - **Rotation Policies:** Regularly changing passwords or rotating API keys
     reduces the "window of opportunity" for a threat actor.
   - **Complexity Requirements:** Enforcing strong entropy, through length and
     variety of characters, mitigates the risk of automated cracking.
3. **Monitoring and Auditing:** As discussed in the **IDS** section, credentials
   must be monitored for anomalous behavior.
   - **Audit Logs:** Keeping a record of when and where a credential was used
     provides the necessary diagnostics for **Incident Response**.
   - **Privilege Creep:** Regular reviews are necessary to ensure users have not
     accumulated more permissions than they need over time.
4. **Revocation and Deprovisioning (Death):** This is often the most overlooked
   stage. When a user leaves an organization or a project through offboarding,
   their access must be terminated immediately.
   - **Zombie Accounts:** Accounts that remain active after a user has left are
     prime targets for attackers, as their activity is rarely monitored.
   - **Centralized Management:** Using a Single Sign-On (SSO) system allows for
     "one-click" revocation across all integrated applications, ensuring
     **Availability** is not compromised by unauthorized former users.

Examples:

- **Insider Threat:** If Bob is fired and his credentials are not immediately
  revoked, he may become an insider threat, using his lingering access to
  compromise the system's Integrity or Confidentiality.
- **Password Rotation:** If Alice has been using the same password for years,
  the likelihood that Charlie will eventually crack it increases. Implementing a
  password rotation policy, such as every 90 days, significantly reduces this
  risk by limiting the attacker's "window of opportunity".

Based on the provided materials, here is the section "Proper Procedures for Data
Availability and Confidentiality" in English for your documentation.

## Access Control

- **Definition:** Systems or equipment designed to restrict unauthorized access
  to specific locations, assets, or data.
- **Purpose:** To safeguard valuable assets, ensure data integrity, and provide
  personal safety.
- **Architecture:** Implemented in layers, ranging from broad/collective areas
  to highly restrictive/private zones.
  - **Collective:** Residential buildings, common areas, and commercial
    complexes.
  - **Private:** Individual offices, apartments, or specific rooms within a
    department.
  - **Equipment:** Individual workstations, smartphones, and vehicles.
  - **Software:** Corporate systems, such as finance and HR, and personal
    applications, such as email and banking.

### Primary Access Control Modalities

Access control is categorized into two distinct but complementary branches.
While one addresses tangible boundaries, the other secures digital environments;
both are essential for a comprehensive security posture.

#### Physical Access Control

The use of physical barriers and technology to prevent unauthorized entry to
tangible environments and assets.

- **Boom Gates (Cancelas):** Manage vehicle flow; triggered by TAGs or payment.
- **Turnstiles (Catracas):** Individual passage control; enables precise data
  tracking but requires human supervision.
- **Doors and Locks:** The fundamental boundary and restriction mechanism.
- **Padlocks:** Targeted security for specific assets, such as lockers and
  cabinets.

#### Logical Access Control

Protocols implemented via hardware or software to manage identification,
authentication, and monitoring without physical barriers.

- **Surveillance Systems:** Monitoring and deterrence; can be integrated with
  License Plate Recognition (LPR) to automate physical barriers.
- **Passwords:** Primary method for data confidentiality; requires complexity
  and secrecy policies to mitigate human error.
- **Access Cards:**
  - *Proximity (125 kHz):* Contactless, limited storage for basic
    identification.
  - *MIFARE (13.56 MHz):* Smart cards with memory for digital certificates and
    cryptographic keys.
- **Biometrics:** Unique physiological authentication, such as fingerprint or
  iris; provides non-transferable identification.

## 4. Best Practices

To ensure a robust security posture, the following standards should be applied:

- **Individual Credentials:** Establish unique accounts for every user to ensure
  accountability.
- **Password Complexity:** Enforce strong, non-predictable password
  requirements.
- **Multi-Factor Authentication (MFA):** Require two or more independent
  credentials, such as a password plus a biometric or hardware token.
- **Periodic Reviews:** Regularly audit user permissions and revoke access for
  inactive or transferred personnel.
- **Centralized Management:** Utilize specialized management tools to monitor
  logs and system health in real-time.
