# Linux Endpoint Security

Linux provides a comprehensive security model through multiple layers of protection, leveraging the operating system's inherent architecture and specialized security tools to create robust endpoint defense.

### **The Linux Security Model: SELinux**

- **Definition:** SELinux (Security-Enhanced Linux) is a mandatory access control (MAC) system that provides fine-grained security policies at the operating system level.
- **Core Concept:** Uses the principle of **least privilege** by defining domains and access policies that restrict what processes can do, regardless of user permissions.
- **Distribution Availability:**
  - **Default Installation:** Red Hat Enterprise Linux (RHEL), CentOS, Fedora, and Rocky Linux
  - **Available but Not Default:** Ubuntu, Debian, SUSE Linux Enterprise
  - **Installation Command:** `apt install selinux-utils selinux-basics` (Debian/Ubuntu) or `yum install selinux-policy-targeted` (RHEL-based)
- **Configuration Locations:**
  - **Main Config:** `/etc/selinux/config` - controls SELinux mode and policy type
  - **Policy Files:** `/etc/selinux/targeted/` - contains the actual security policies
  - **Runtime Status:** `/sys/fs/selinux/enforce` - current enforcement status (0=permissive, 1=enforcing)
- **Operation Modes:**
  - **Enforcing Mode:** Actively blocks policy violations and logs security events
  - **Permissive Mode:** Logs policy violations but doesn't block them (useful for testing and debugging)
  - **Disabled Mode:** SELinux is completely turned off
- **Security Benefits:**
  - Prevents privilege escalation attacks by confining processes to their designated domains
  - Mitigates zero-day exploits by limiting what compromised processes can access
  - Provides defense-in-depth even when traditional Unix permissions are bypassed

### **Virus and Malware Protection**

Linux endpoint protection relies on multiple complementary approaches:

#### **Architectural Defenses**
- **Kernel Design:** Linux kernel architecture inherently limits malware propagation through strict process isolation and memory protection
- **Permission System:** Traditional Unix file permissions (read/write/execute) create barriers for unauthorized file modification
- **Package Integrity:** Most software is installed through trusted package managers with cryptographic signature verification

#### **Active Protection Tools**
- **ClamAV:** Open-source antivirus engine commonly used for mail servers and file scanning
- **ESET NOD32:** Commercial antivirus solution with real-time protection
- **Sophos:** Enterprise-grade endpoint protection for Linux servers and workstations
- **Firewall Integration:** Host-based firewalls block suspicious network connections and malicious downloads

#### **Preventive Measures**
- **Regular Updates:** Automatic security patches through package managers (`apt`, `yum`, `dnf`, `pacman`)
- **File Integrity Monitoring:** Tools like `AIDE` and `Tripwire` detect unauthorized file modifications
- **Secure Boot:** UEFI Secure Boot prevents loading of unauthorized kernel modules and bootloaders

### **Encryption and Access Control**

#### **SSH (Secure Shell) Protection**
SSH provides cryptographic protection for remote access. For detailed information about SSH's encryption mechanisms, see [Cryptography and Data Protection](../03%20Cryptography%20and%20Data%20Protection/01%20Cryptography.md#5.%20Applications%20of%20Asymmetric%20Cryptography).

**Linux SSH Security Configuration:**
- **Key-Based Authentication:** Ed25519 keys preferred for stronger security
- **Host Key Verification:** Fingerprint validation to prevent MITM attacks
- **Configuration Hardening:**
  - Disable root login: `PermitRootLogin no`
  - Use non-standard ports: `Port 2222`
  - Require key-based authentication: `PasswordAuthentication no`
- **Access Control Integration:** Integrate with PAM and system user management

#### **ACL (Access Control Lists)**
Linux ACLs provide extended access control beyond traditional UNIX permissions. For comprehensive information about access control models, see [Authorization and Access Control](../02%20Identity%20and%20Access/02%20Authorization%20and%20Access%20Control.md).

**Linux ACL Implementation:**
- **Extended Permissions:** Fine-grained control using `setfacl` and `getfacl` commands
- **Use Cases:** Shared directories, database file permissions, system resource access control
- **Integration:** Works with SELinux and AppArmor for comprehensive access control

### **Firewall: iptables and netfilter**

#### **Architecture Overview**
- **netfilter:** Kernel-space framework that provides packet filtering hooks in the Linux network stack
- **iptables:** User-space utility that configures netfilter rules and policies
- **Modern Alternative:** `nftables` is the newer framework replacing iptables in recent distributions

#### **iptables Rule Processing**
- **Tables and Chains:** Rules are organized in tables (`filter`, `nat`, `mangle`) with predefined chains (`INPUT`, `OUTPUT`, `FORWARD`)
- **Sequential Processing:** iptables evaluates rules in order from top to bottom within each chain
- **Rule Matching:** Packets are evaluated against rules based on criteria like source IP, destination port, and protocol
- **Actions:** Matched packets can be `ACCEPT`ed, `DROP`ped, `REJECT`ed, or `LOG`ged

**Execution Flow for Rule Processing:**

1. **Terminal vs Non-Terminal Targets:**
   - **Terminal Targets** (`ACCEPT`, `DROP`, `REJECT`): Stop rule processing immediately when matched
   - **Non-Terminal Targets** (`LOG`, `MARK`): Continue to next rule after executing the action

2. **Rate Limiting Execution Route:**
   Using the SSH brute force example, here's how packets are processed:

   - **Within Rate Limit:** Packet matches first rule's limit condition → `ACCEPT` (terminal) → processing stops
   - **Exceeds Rate Limit:** Packet fails first rule's limit condition → continues to second rule → `LOG` (non-terminal) → continues to third rule → `DROP` (terminal)

3. **Module Matching Behavior:**
   - The `limit` module only matches packets that are *within* the specified rate
   - Packets exceeding the rate do not match the limit rule, allowing them to fall through to subsequent rules
   - This creates an automatic "overflow" mechanism for handling excess traffic

4. **Policy vs Rules:**
   - If no rules match, the chain's default policy takes effect (usually `ACCEPT` or `DROP`)
   - It's best practice to set restrictive policies and explicitly allow desired traffic

#### **Common Firewall Configurations**

**Basic SSH-Only Access Control:**
The most fundamental firewall configuration allows only SSH connections while blocking all other incoming traffic. This creates a secure baseline for server administration.

```bash
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -j DROP
```

- `-A INPUT`: Appends rules to the INPUT chain (handles incoming packets)
- `-p tcp`: Specifies the TCP protocol
- `--dport 22`: Matches packets destined for port 22 (SSH default port)
- `-j ACCEPT`: Jumps to ACCEPT target, allowing the packet through
- `-j DROP`: Silently discards packets without sending rejection responses

**Stateful Connection Tracking:**
Modern firewalls should allow established connections to continue functioning. This rule permits return traffic for connections that were initiated from the local machine, enabling normal internet browsing and outbound communications.

```bash
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
```

- `-m state`: Loads the connection tracking module
- `--state ESTABLISHED`: Matches packets belonging to existing connections
- `--state RELATED`: Matches packets related to established connections (like FTP data channels)
- The comma separates multiple connection states in a single rule

**SSH Brute Force Protection:**
Rate limiting prevents automated password attacks by restricting the number of SSH connection attempts. This configuration allows only 3 SSH connection attempts per minute from any single source, with logging for anomaly detection.

```bash
iptables -A INPUT -p tcp --dport 22 -m limit --limit 3/min -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j LOG --log-prefix "SSH_BRUTE_FORCE: "
iptables -A INPUT -p tcp --dport 22 -j DROP
```

- `-m limit`: Loads the limit module for rate limiting functionality
- `--limit 3/min`: Sets maximum rate to 3 matches per minute per source IP
- The limit module uses a token bucket algorithm to track connection rates
- `-j LOG`: Logs packets that exceed the rate limit to system logs (`/var/log/messages` or `/var/log/syslog`)
- `--log-prefix "SSH_BRUTE_FORCE: "`: Adds a custom prefix to log entries for easy filtering and alerting
- The three-rule sequence: ACCEPT (rate-limited) → LOG (excess packets) → DROP (excess packets)

### **Application and Service Control**

#### **Mandatory Access Control Systems**
- **SELinux:** Comprehensive MAC system with complex policies (Red Hat/CentOS/Fedora default)
- **AppArmor:** Profile-based MAC system that's easier to configure (Ubuntu/SUSE default)
- **grsecurity:** Kernel hardening patchset with additional security features (third-party)

#### **Package Management Security**
- **Package Verification:** All major package managers verify cryptographic signatures before installation
- **Dependency Resolution:** Automatic handling of software dependencies reduces manual installation risks
- **Common Package Managers:**
  - `apt` (Debian/Ubuntu): `apt update && apt upgrade`
  - `yum`/`dnf` (Red Hat/CentOS/Fedora): `dnf update`
  - `pacman` (Arch Linux): `pacman -Syu`
  - `zypper` (openSUSE): `zypper update`

#### **Service Management with systemd**
- **Service Control:** `systemctl start/stop/restart/enable/disable service-name`
- **Security Features:**
  - Process sandboxing with `SystemCallFilter` and `CapabilityBoundingSet`
  - Network isolation with `PrivateNetwork`
  - Filesystem restrictions with `ReadOnlyPaths` and `InaccessiblePaths`
- **Monitoring:** `journalctl` provides centralized logging for security analysis

### **User and Group Management**

#### **User Account Control**
- **Account Creation:** `useradd -m -s /bin/bash username`
- **Password Policy:** `passwd` command with complexity requirements via PAM
- **Account Modification:** `usermod -aG sudo username` (add to sudo group)
- **Account Removal:** `userdel -r username` (remove home directory)

#### **Group-Based Permissions**
- **Group Creation:** `groupadd groupname`
- **Group Assignment:** `usermod -aG groupname username`
- **Permission Management:** Use groups to control access to shared resources and system functions

#### **Security Configuration Files**
- `/etc/passwd` - User account information
- `/etc/shadow` - Encrypted password storage (restricted access)
- `/etc/group` - Group definitions
- `/etc/sudoers` - Sudo access control (edit with `visudo`)

### **Advanced Security Hardening**

#### **Network Security**
- **SSH Key Management:** Use `ssh-keygen -t ed25519` for strong key generation
- **VPN Integration:** WireGuard or OpenVPN for secure remote access
- **Network Monitoring:** `netstat`, `ss`, and `lsof` for connection analysis

#### **System Monitoring and Logging**
- **Log Analysis:** `rsyslog` or `systemd-journald` for centralized logging
- **Security Monitoring:** `auditd` for system call auditing and compliance
- **Intrusion Detection:** `OSSEC` or `Samhain` for host-based intrusion detection

#### **Disk and Data Protection**
- **Full Disk Encryption:** LUKS (Linux Unified Key Setup) for transparent disk encryption
- **File-Level Encryption:** `gpg` for individual file encryption
- **Secure File Deletion:** `shred` command for secure file wiping
