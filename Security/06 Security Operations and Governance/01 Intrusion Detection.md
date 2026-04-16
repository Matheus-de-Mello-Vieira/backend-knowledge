# Intrusion Detection

Even when perimeter defenses like firewalls and authentication are successful, a threat actor may still manage to operate within the system using legitimate credentials. An **Intrusion Detection System (IDS - /ˌaɪ.diːˈɛs/)** acts as a surveillance layer that monitors system activity for malicious behavior or policy violations.

**Behavioral and Anomaly Detection**: Instead of just checking "keys," an IDS analyzes behavior. It establishes a baseline of "normal" activity and flags deviations that could indicate an intruder impersonating a legitimate user. Key indicators include:

- **Access Patterns**: Identifying logins at unusual times or from unexpected sequences of internal systems.

- **Unusual Web Traffic**: Monitoring access to suspicious or non-standard websites that could indicate a "Command and Control" (C2) connection.

- **Frequency Anomalies**: Detecting access rates (e.g., API calls or login attempts) that far exceed standard user behavior.

- **File Integrity and Activity**: Flagging the **unusual access, modification, or deletion** of files—actions often associated with data exfiltration or ransomware.

**Detecting the "Insider" Threat**:  The primary strength of an IDS is its ability to detect an attacker even when they possess correct credentials. By identifying that a specific user's behavior has become highly irregular, the system can trigger alerts or automated responses to mitigate the impact of a potential breach.

> **Analogy:** If a Firewall is the locked front door, and Authentication is the ID check, an **IDS** is the security camera and motion sensor inside the building that notices someone walking through the halls at 3 AM opening drawers they shouldn't.

**Remark**

> **Device Profiling and IoT Baselines**: Unlike human users, IoT devices typically have highly predictable and "narrow" communication patterns (e.g., a smart light bulb only communicates with a specific controller at fixed intervals). An IDS is essential for identifying compromised IoT devices by flagging any deviation from this baseline—such as a thermostat suddenly performing an internal network scan or attempting to access a laptop's file system. This behavioral detection allows for the immediate isolation of the device, preventing an initial foothold from turning into a full-scale breach.
