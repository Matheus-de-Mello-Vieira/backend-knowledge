# File and Filesystem Security

File security protects the data objects people actually use: documents, configuration files, databases, keys, logs, and executables. Filesystem security protects the storage layer that holds those objects: directories, permissions, mounts, removable media, and disk-level handling.

The distinction matters because a file can be sensitive even when the disk is healthy, and a filesystem can be dangerous even when the files themselves look ordinary. Security failures happen at both layers: a confidential file may be exposed through weak permissions, while a whole storage environment may be compromised through unsafe mounting, legacy formats, or poor recovery practices.

These controls sit close to the operating-system boundary where [storage mechanics behind file systems](../../Operating%20Systems/06%20Storage%20Management.md) start to matter.

## File Protection

File protection focuses on the individual object and who can do what to it.

- **Access control:** Permissions on files and directories form one of the first security boundaries on any endpoint.
- **Confidentiality:** Sensitive files may need encryption at rest so physical theft or offline disk access does not immediately expose their contents.
- **Integrity:** Executables, configuration files, and records must be protected against unauthorized modification.
- **Availability:** Important files need recoverable copies so corruption, deletion, or ransomware does not become permanent loss.

## Filesystem Security

Filesystem security focuses on the behavior and administration of the storage environment.

- **Permission inheritance and ownership:** Misconfigured directory structures can leak access far beyond the intended users.
- **Mounting and removable media:** External drives and mounted volumes introduce both malware risk and data-leak paths.
- **Operational actions:** Formatting disks, changing filesystem types, or using legacy filesystems can introduce reliability and security problems.
- **Recovery posture:** A filesystem is safer when backup and restore procedures exist before an outage or compromise occurs.

## Core Control Areas

### Permissions and access management

Least privilege matters at the storage layer. A service should not be able to modify files it only needs to read, and ordinary users should not be able to rewrite security-sensitive binaries or secrets.

### Encryption at rest

Encryption at rest protects data stored on disks, backups, and removable media. It raises the cost of physical theft and offline copying, but it does not fully protect a live compromised system that can already access the decrypted data through legitimate processes.

The [cryptographic mechanism](02%20Encryption.md#Encryption%20States) and the [lifecycle of the underlying keys](Key%20Management%20Lifecycle.md) both determine how much protection encryption at rest actually provides.

### Recovery and resilience

Backups reduce the impact of accidental deletion, corruption, hardware failure, and ransomware. They are part of file security because the value of the file includes the ability to recover it when the primary copy is gone.

The [operational recovery flow](Backup%20and%20Restore.md) determines whether those backups can be turned back into working files under pressure.

## Platform and Security Context

Storage protection rarely stands alone.

- [Endpoint Security](../05%20Architecture%20and%20Infrastructure%20Security/02%20Endpoint%20Security.md): endpoint hardening and device controls that surround the storage layer.
- [Windows Security](../05%20Architecture%20and%20Infrastructure%20Security/Windows%20Security.md#BitLocker%20Drive%20Encryption%20Integration): Windows-specific disk and file-encryption mechanisms.
- [Linux Endpoint Security](../05%20Architecture%20and%20Infrastructure%20Security/Linux%20Endpoint%20Security.md): Linux-oriented hardening practices and secure remote administration.
- [Incident Response, Forensics, and Disaster Recovery](../06%20Security%20Operations%20and%20Governance/Incident%20Response,%20Forensics,%20and%20Disaster%20Recovery.md): recovery, investigation, and restoration after storage-related incidents.

File and filesystem security is where abstract cryptographic and policy decisions become concrete operating-system behavior. If the permissions, keys, backup copies, or operational procedures fail here, higher-level security goals usually fail with them.
