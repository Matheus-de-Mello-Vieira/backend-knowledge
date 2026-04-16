# Endpoint Security

Endpoint security protects the devices, services, and logical endpoints that connect to a system. An endpoint can be a physical device such as a workstation, server, phone, or IoT device, but it can also be a software-facing communication point such as an API endpoint.

The goal is to reduce the risk that an endpoint becomes an entry point for unauthorized access, malware execution, data exposure, lateral movement, or service disruption.

## Core Areas

- [Workstation Security](Workstation%20Security.md): practical controls for user machines, including anti-malware, anti-ransomware, phishing prevention, sandboxing, virtualization, and monitoring.
- [Windows Endpoint Security](Windows%20Endpoint%20Security.md): Windows-specific protections such as Microsoft Defender, Credential Guard, SmartScreen, firewalls, and Windows-oriented Zero Trust controls.
- [Linux Endpoint Security](Linux%20Endpoint%20Security.md): Linux-specific protections such as SELinux, package security, service control, users/groups, iptables, SSH, and hardening practices.
- [Mobile Device Security](Mobile%20Device%20Security.md): mobile risks, MDM/MAM, BYOD, mobile authentication, app security, Wi-Fi safety, and data protection.
- [IoT Security](IoT%20Security.md): IoT device risks, insecure protocols, firmware vulnerabilities, data breaches, edge security, and supply-chain concerns.
- [Cloud Security](Cloud%20Security.md): cloud service protection, shared responsibility, cloud data security, provider selection, and cloud-native security controls.

## Related Foundations

- [File and Filesystem Security](../03%20Cryptography%20and%20Data%20Protection/File%20and%20Filesystem%20Security.md): protects stored data through permissions, encryption, access control, and safe storage practices.
- [Backup and Restore](../03%20Cryptography%20and%20Data%20Protection/Backup%20and%20Restore.md): supports resilience and recovery after data loss, corruption, ransomware, or device failure.
- [Zero Trust Architecture](../02%20Identity%20and%20Access/03%20Zero%20Trust%20Architecture.md): treats endpoint identity and posture as part of every access decision.
- [Authentication](../02%20Identity%20and%20Access/01%20Authentication.md): verifies users, services, and devices before allowing access.
- [Cryptography](../03%20Cryptography%20and%20Data%20Protection/01%20Cryptography.md): provides encryption, hashing, certificates, signatures, and key-management foundations.
- [Network Security and Firewalls](01%20Network%20Security%20and%20Firewalls.md): controls endpoint communication through filtering, segmentation, monitoring, and network access rules.
