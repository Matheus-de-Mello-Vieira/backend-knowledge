# Backup and Restore

A backup is a recoverable copy of data kept separately from the primary system. A restore is the process of taking that stored copy and using it to rebuild or recover the original data after loss, corruption, deletion, hardware failure, or attack.

Backups matter because availability failures are unavoidable. Disks fail, users delete the wrong files, ransomware encrypts production data, and whole sites can become unavailable. A secure system therefore needs not only prevention, but also a way back.

Backups are not the same as live redundancy. A backup is a stored recovery point; it usually takes time to restore. Replication keeps another active copy closer to real time, but it can also replicate mistakes or malicious changes if the source is already compromised.

## Backup Basics

A backup process copies data from its primary location to a secondary location such as external storage, a dedicated backup server, or a cloud environment.

Important properties of a useful backup include:

- **Separation from the original:** The copy must survive when the primary environment fails.
- **Regular execution:** Manual backups are easy to forget; automation reduces that operational gap.
- **Recoverability:** A backup is only valuable if it can be restored successfully.
- **Physical and logical protection:** Backup media must be protected against theft, tampering, and accidental destruction.

## Backup Strategies

Different strategies trade storage cost, backup time, and restore complexity.

- **Full backup:** Copies all data at a point in time. Recovery is straightforward, but each run is expensive.
- **Incremental backup:** Copies only what changed since the most recent backup of any kind. This reduces routine backup cost but makes restore chains longer.
- **Differential backup:** Copies what changed since the last full backup. This sits between full and incremental approaches in both backup cost and restore complexity.

## Restore Workflow

Restore is the operational proof that the backup strategy actually works.

1. Identify what was lost, corrupted, or destroyed.
2. Choose the correct backup set.
3. Recover the data to the original system or to a replacement environment.
4. Verify that the restored data is complete and usable.
5. Return the service or workflow to normal operation.

Modern tooling often allows granular restore of specific files or datasets, but the core dependency remains the same: the earlier backup must have been correct and intact.

## Backup Security Controls

Backup copies protect availability, but they can also become a confidentiality risk if handled poorly.

- **Off-site storage:** Geographic separation helps the organization survive fires, theft, floods, and other localized disasters.
- **Access control:** Backup repositories should not be readable or mutable by everyone who can use the primary system.
- **Encryption:** Sensitive backups should be protected at rest because backup media are attractive theft targets.
- **Regular testing:** Restoration drills confirm that the data, tooling, permissions, and recovery steps still work.

## Backups vs. Replication

Backups and replication both improve resilience, but they solve different problems.

- **Backups:** Preserve older recoverable copies and are essential for recovery after corruption, deletion, or ransomware.
- **Replication:** Keeps data or services available across multiple nodes with much lower recovery delay.

Replication is usually better for fast failover. Backups are usually better for recovering from destructive history, because they preserve earlier states instead of only mirroring the latest one.

## Relationship to Incident Response and Disaster Recovery

Restore operations usually happen inside a broader recovery process. After a major incident, the organization still needs to verify the root cause, contain the attacker, and avoid reintroducing compromised data or systems.

The larger [incident-response and disaster-recovery lifecycle](../06%20Security%20Operations%20and%20Governance/Incident%20Response,%20Forensics,%20and%20Disaster%20Recovery.md) and the [controls that protect stored data before recovery is needed](File%20and%20Filesystem%20Security.md) both shape restore decisions.
