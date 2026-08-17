# Linux Endpoint Security

Linux provides a comprehensive security model through multiple layers of protection, leveraging the operating system's inherent architecture and specialized security tools to create robust endpoint defense.

## The Linux Security Model: SELinux

SELinux is a **Mandatory Access Control (MAC)** system. Unlike standard Linux permissions (DAC), which rely on user ownership, SELinux applies security labels to every process and object on the system.

### Core Concept: Least Privilege

SELinux operates on the **principle of least privilege**. It confines processes into "domains" and files into "types."

- **Isolation:** Even if a web server (like Apache) is compromised by a root-level exploit, SELinux prevents that process from accessing the `/home` directory or other sensitive files it doesn't explicitly need.
- **Policy-Driven:** Access is denied by default unless a specific policy rule allows it.

### Operation Modes

You can check your current status using the `sestatus` command.

| **Mode**       | **Description**                       | **Result of Policy Violation**                             |
| -------------- | ------------------------------------- | ---------------------------------------------------------- |
| **Enforcing**  | The default and recommended state.    | Action is **blocked** and logged.                          |
| **Permissive** | Useful for troubleshooting/debugging. | Action is **allowed** but still logged.                    |
| **Disabled**   | SELinux is completely turned off.     | Nothing is blocked or logged; requires a reboot to change. |

### 3. Distribution Support & Installation

While SELinux is baked into the kernel, its implementation varies by "flavor":

- **Native (Default):** Red Hat Enterprise Linux (RHEL), CentOS Stream, Fedora, Rocky Linux, and AlmaLinux.
- **Optional:** Ubuntu, Debian, and SUSE (where AppArmor is typically the default).

**Common Installation Commands:**

- **RHEL/Clone:** `sudo yum install selinux-policy-targeted selinux-utils`
- **Debian/Ubuntu:** `sudo apt install selinux-utils selinux-basics`

### 4. Key Configuration Paths

To manage SELinux effectively, you’ll spend most of your time in these locations:

- **Main Configuration:** `/etc/selinux/config`
    - _Note: This is where you switch between `enforcing` and `permissive` permanently._
- **Policy Directory:** `/etc/selinux/targeted/`
    - Contains the binary policies that define how the system behaves.
- **Runtime Status:** `/sys/fs/selinux/enforce`
    - _A virtual file where `1` means enforcing and `0` means permissive._

### 5. Why Keep It Enabled?

Many admins' first instinct is to disable SELinux when a service breaks. However, keeping it active provides:

- **Zero-Day Mitigation:** It can stop an attacker from using a brand-new exploit to hop from a service to the rest of your data.
- **Privilege Escalation Defense:** It prevents "root" in a process from becoming "root" over the entire OS.
- **Audit Trails:** Detailed logging in `/var/log/audit/audit.log` provides a forensic trail of exactly what a process tried to do.

> [!tip]
> If you think SELinux is breaking your app, don't disable it! Switch to **Permissive** mode first. If the app starts working, you'll see exactly which policy you need to fix in the audit logs without leaving your system wide open.

## Virus and Malware Protection

Linux endpoint protection relies on multiple complementary approaches:

### Architectural Defenses

- **Kernel Design:** Linux kernel architecture inherently limits malware propagation through strict process isolation and memory protection
- **Permission System:** Traditional Unix file permissions (read/write/execute) create barriers for unauthorized file modification
- **Package Integrity:** Most software is installed through trusted package managers with cryptographic signature verification

### Active Protection Tools

- **ClamAV:** Open-source antivirus engine commonly used for mail servers and file scanning
- **ESET NOD32:** Commercial antivirus solution with real-time protection
- **Sophos:** Enterprise-grade endpoint protection for Linux servers and workstations
- **Firewall Integration:** Host-based firewalls block suspicious network connections and malicious downloads

### Preventive Measures

- **Regular Updates:** Automatic security patches through package managers (`apt`, `yum`, `dnf`, `pacman`)
- **File Integrity Monitoring:** Tools like `AIDE` and `Tripwire` detect unauthorized file modifications
- **Secure Boot:** UEFI Secure Boot prevents loading of unauthorized kernel modules and bootloaders

## Encryption and Access Control

### SSH (Secure Shell) Protection

SSH provides [cryptographic protection for remote access](../03%20Cryptography%20and%20Data%20Protection/02%20Encryption.md#Asymmetric%20encryption).

**Linux SSH Security Configuration:**
- **Key-Based Authentication:** Ed25519 keys preferred for stronger security
- **Host Key Verification:** Fingerprint validation to prevent MITM attacks
- **Configuration Hardening:**
    - Disable root login: `PermitRootLogin no`
    - Use non-standard ports: `Port 2222`
    - Require key-based authentication: `PasswordAuthentication no`
- **Access Control Integration:** Integrate with PAM and system user management

### Pluggable Authentication Modules (PAM)

Pluggable Authentication Modules (PAM) provide a modular framework for authentication, account validation, session controls, and password policy enforcement across Linux services such as `sshd`, `sudo`, `su`, and local console logins.

**Why PAM Matters**

- **Centralized Authentication Logic:** Multiple services can share consistent authentication and account policies
- **Defense in Depth:** PAM adds controls beyond basic passwords, including MFA, login restrictions, and account lockout behavior
- **Operational Flexibility:** Administrators can change authentication behavior by updating module stacks without rewriting the service itself

**Core PAM Function Groups**

- **`auth`:** Verifies identity, for example by checking passwords, smart cards, or MFA factors
- **`account`:** Applies account restrictions such as allowed login times, expired accounts, or access rules
- **`password`:** Handles password changes, complexity requirements, and password history
- **`session`:** Runs actions when sessions start or end, such as logging, environment setup, and mount handling

**Common Configuration Paths**

- **Service-Specific Policies:** `/etc/pam.d/`
- **Legacy or Centralized Configuration:** `/etc/pam.conf`
- **Access Rules Often Used with PAM:** `/etc/security/`

**Common Hardening Use Cases**

- **Restrict Administrative Access:** Apply tighter controls to `sudo`, `su`, and remote logins
- **Enforce Password Policy:** Use PAM modules to require strong passwords and rotation rules
- **Limit Login Scope:** Allow or deny access based on groups, terminals, or source conditions
- **Add Multifactor Authentication:** Integrate TOTP, hardware tokens, or external identity providers where supported

**Example Modules**

- **`pam_unix.so`:** Standard local password authentication
- **`pam_faillock.so`:** Tracks failed logins and can temporarily lock accounts
- **`pam_access.so`:** Applies allow or deny rules from access control files
- **`pam_securetty.so`:** Restricts direct root logins to approved terminals on systems that still use it

> [!warning]
> PAM misconfiguration can lock administrators out of `ssh`, `sudo`, or console access. Validate changes carefully and keep an active root-capable session open while testing.

### ACL (Access Control Lists)

Linux ACLs provide extended [access control](../02%20Identity%20and%20Access/02%20Authorization%20and%20Access%20Control.md) beyond traditional UNIX permissions.

**Linux ACL Implementation:**
- **Extended Permissions:** Fine-grained control using `setfacl` and `getfacl` commands
- **Use Cases:** Shared directories, database file permissions, system resource access control
- **Integration:** Works with SELinux and AppArmor for comprehensive access control

## Firewall: iptables and netfilter

### Architecture Overview

- **netfilter:** Kernel-space framework that provides packet filtering hooks in the Linux network stack
- **iptables:** User-space utility that configures netfilter rules and policies
- **Modern Alternative:** `nftables` is the newer framework replacing iptables in recent distributions

### iptables Rule Processing

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
   - The `limit` module only matches packets that are _within_ the specified rate
   - Packets exceeding the rate do not match the limit rule, allowing them to fall through to subsequent rules
   - This creates an automatic "overflow" mechanism for handling excess traffic
4. **Policy vs Rules:**
   - If no rules match, the chain's default policy takes effect (usually `ACCEPT` or `DROP`)
   - It's best practice to set restrictive policies and explicitly allow desired traffic

### Common Firewall Configurations

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

## Application and Service Control

### Mandatory Access Control Systems

- **SELinux:** Comprehensive MAC system with complex policies (Red Hat/CentOS/Fedora default)
- **AppArmor:** Profile-based MAC system that's easier to configure (Ubuntu/SUSE default)
- **grsecurity:** Kernel hardening patchset with additional security features (third-party)

### Package Management Security

- **Package Verification:** All major package managers verify cryptographic signatures before installation
- **Dependency Resolution:** Automatic handling of software dependencies reduces manual installation risks
- **Common Package Managers:**
    - `apt` (Debian/Ubuntu): `apt update && apt upgrade`
    - `yum`/`dnf` (Red Hat/CentOS/Fedora): `dnf update`
    - `pacman` (Arch Linux): `pacman -Syu`
    - `zypper` (openSUSE): `zypper update`

### Service Management with systemd

- **Service Control:** `systemctl start/stop/restart/enable/disable service-name`
- **Security Features:**
    - Process sandboxing with `SystemCallFilter` and `CapabilityBoundingSet`
    - Network isolation with `PrivateNetwork`
    - Filesystem restrictions with `ReadOnlyPaths` and `InaccessiblePaths`
- **Monitoring:** `journalctl` provides centralized logging for security analysis

This is a great foundation for a Linux security cheat sheet. I’ve refined the commands for better practice, added a section on the "Primary vs. Secondary" group distinction, and broken down the file structures so you actually know what you're looking at when you `cat` them.

## User and Group Management

Managing users isn't just about giving people logins; it’s about defining the boundaries of your system's "blast radius."

### Identity Basics: UID and GID

Every Linux user is identified internally by a **UID** (User ID), and every group is identified by a **GID** (Group ID).

- **UID:** Numeric identifier for a user account.
- **GID:** Numeric identifier for a group.
- The system enforces ownership and permissions using these numeric IDs, not just the visible account or group names.
- Each user has one **primary GID** and can also belong to multiple supplemental groups.

### User Account Control

In the Linux world, there are two main ways to add users. `useradd` is the low-level binary, while `adduser` (on Debian/Ubuntu) is a friendlier interactive script. Stick to these standard practices:

- **Account Creation:** `sudo useradd -m -s /bin/bash -c "Full Name" username`
    - `-m`: Creates the home directory (essential, or they'll land in `/`).
    - `-s`: Sets the default shell.
    - `-c`: Adds a comment (useful for identifying who owns the account).
- **Password Policy:** Use `passwd username` to set a password. For enterprise environments, password aging is handled via `chage -M 90 username` (forces a change every 90 days).
- **Account Modification:** `usermod -aG sudo username`
    - **Warning:** Always use the `-a` (append) flag with `-G`. If you forget it, you’ll remove the user from every other group they belong to.
- **Account Removal:** `userdel -r username`
    - The `-r` is the "scorched earth" flag—it deletes the user's home directory and mail spool along with the account.

### Group-Based Permissions

Groups are the scalable way to manage permissions. Instead of giving 50 people access to a folder individually, you give the group access and just drop users into it.

- **Primary Group:** Every user has exactly one. Usually named after the user. Defined in `/etc/passwd`.
- **Secondary (Supplemental) Groups:** A user can belong to many of these (like `sudo`, `docker`, or `developers`).
- **Management Commands:**
    - `groupadd project_alpha`: Creates a new security boundary.
    - `gpasswd -d username groupname`: The cleanest way to remove a user from a specific group.
    - `groups username`: Quickly check which "clubs" a user belongs to.

### Security Configuration Files

Understanding the anatomy of these files is key to troubleshooting.

| **File**             | **Purpose**        | **Key Detail**                                                                                  |
| -------------------- | ------------------ | ----------------------------------------------------------------------------------------------- |
| **`/etc/passwd`**    | User metadata      | Publicly readable. Contains UID, GID, and Home Path.                                            |
| **`/etc/shadow`**    | Secure credentials | Only readable by root. Contains hashed passwords and expiry info.                               |
| **`/etc/group`**     | Group registry     | Maps group names to GIDs and lists supplemental members.                                        |
| **`/etc/sudoers`**   | Privilege rules    | Controls who can "become" root.                                                                 |
| **`/etc/securetty`** | Console access     | Lists terminals authorized for root; an empty file blocks direct root logins via local console. |

> [!warning] Always edit `/etc/sudoers` using `visudo`.
>
> `visudo` checks your syntax before saving. If you make a typo in the sudoers file with a standard text editor like `nano` or `vi` you can accidentally lock everyone (including yourself) out of root access. `visudo` prevents that nightmare.

### Extended Security: Permissions Integration

User management is essentially the "who," while the filesystem is the "what" and "how." Without mastering **chown** and **chmod**, you're either leaving the front door wide open or locking yourself out of your own house.

### Ownership: Defining the "Who"

The `chown` command dictates which user and which group "own" a specific resource. This is your first line of defense.

- **Recursive Control:** When dealing with web directories or large projects, you rarely want to change just one folder. Adding the `-R` flag applies the change to every file and subdirectory within. E.g.: `chown -R www-data:www-data /var/www/html`
- **Safety First:** Only the superuser (root) can change the ownership of a file to another user. If you aren't logged in as root, you'll need to prepend `sudo`.

### Permissions: Defining the "How"

While `chown` sets the owner, `chmod` sets the rules. You can use the **Octal (numeric) method** or the **Symbolic method**.

#### The Octal Breakdown

The numeric system is a simple addition of bits. Think of it as a scoreboard:

| **Permission**    | **Octal Value** | **Binary Value** | **Bit Position** | **Symbol** |
| ----------------- | --------------- | ---------------- | ---------------- | ---------- |
| **Read**          | **4**           | `100`            | $2^2$            | `r`        |
| **Write**         | **2**           | `010`            | $2^1$            | `w`        |
| **Execute**       | **1**           | `001`            | $2^0$            | `x`        |
| **No Permission** | **0**           | `000`            | —                | `-`        |

If you want a user to have "Read" and "Write" but not "Execute," you add $4 + 2 = 6$.

| Value | Permissions | Symbolic |
| --- | --- | --- |
| **7** | Read + Write + Execute | `rwx` |
| **6** | Read + Write | `rw-` |
| **5** | Read + Execute | `r-x` |
| **4** | Read Only | `r--` |
| **0** | No Access | `---` |

#### The Hierarchy

Each **digit** in a chmod code (as `750`) represents one of three distinct **permission classes** assigned to the owner, the group, and others

- **First Digit (User/Owner):** This represents the person who created the file or was assigned ownership via `chown`. In `750`, the **7** gives the owner total control.
- **Second Digit (Group):** This represents a collection of users. In `750`, the **5** lets all members of the group to read and enter the folder, but not change its contents.
- **Third Digit (Others/World):** This is everyone else on the system. It’s the "public" setting. A **0** here is the standard for security, ensuring that unless you are the owner or in the approved group, you can't even acknowledge the file exists.

#### The Symbolic Method

Sometimes you just want to tweak one specific setting without recalculating the whole string.

- **Add execution for everyone:** `chmod +x script.sh`
- **Remove write access for the group:** `chmod g-w file.txt`
- **Make a file private to the owner:** `chmod go-rwx private.key` (Removes Read/Write/Execute from **G**roup and **O**thers).

#### The "Execute" Bit Secret

It is a common "gotcha" for beginners: the **Execute (x)** bit behaves differently depending on what it’s attached to:

- **On a File:** It allows you to run the file as a program or script.
- **On a Directory:** It allows you to "enter" the directory (e.g., `cd` into it) and access the metadata of files inside.

> [!tip]
> If a directory has `r` (read) permissions but lacks `x` (execute), you can see the filenames inside, but you can't open them, read their contents, or see their sizes. It’s like looking through a locked window.

## Security Hardening

### System Accounts

#### Disable interactive logins for specific users

To minimize your system's attack surface, service accounts (such as `www-data`, `mysql`, or `bin`) should never be allowed to log in interactively. These accounts exist solely to run background processes, not for human use.

By switching the user's shell in `/etc/passwd` to `/sbin/nologin`, you effectively "lock the front door" while allowing the underlying services to function normally.

**Implementation**

To change a user's shell to a non-interactive state, use the `usermod` command:

```bash
sudo usermod -s /sbin/nologin <username>
```

**How to Verify**

Confirm the change by checking the user's entry in the password file:

```bash
grep "<username>" /etc/passwd
# Expected output: <username>:x:1001:1001::/home/<username>:/sbin/nologin
```

**`/sbin/nologin` vs `/bin/false`?**

- **`/sbin/nologin` (Recommended):** Politely refuses the login and displays a message stating "This account is currently not available." It’s cleaner for auditing.
- **`/bin/false`:** Simply exits immediately with a failure status. It provides no feedback to the user, which can be useful if you want to be as "stealthy" as possible, but it's less helpful for troubleshooting.
#### Restricting Direct Root Logins

Emptying the `/etc/securetty` file is a security practice designed to block the `root` user from logging in directly via any local terminal or console device (TTY).

Run the following commands to safely empty the file:

```bash
# Create a backup of the original file
sudo cp /etc/securetty /etc/securetty.bak

# Clear the contents of the file
sudo truncate -s 0 /etc/securetty
```

**Why This Matters**

- **Accountability & Audit Trails:** It forces system administrators to log in using their personal user accounts first, then elevate privileges using `sudo` or `su`. This ensures every root action is tied to a specific person in the system logs.
- **Mitigates Physical Access Risks:** If an attacker gains physical access to a server's crash cart or serial console, they cannot log straight into the root account—even if they know the root password—without first compromising a standard user account.

> [!NOTE] Modern Distro Compatibility Many modern Linux distributions (such as recent versions of RHEL, CentOS, and Ubuntu) have deprecated `/etc/securetty` or disabled the `pam_securetty.so` module by default. They now handle console restrictions through `systemd` or specific PAM configurations. Always verify your OS-specific security baselines.

#### Disabling direct root access over SSH

By default, many Linux systems allow the `root` user to log in via SSH. This is a significant security risk as it gives attackers a known username to target with brute-force attacks. Disabling this forces users to log in with a standard account and use `sudo` for administrative tasks.

**Why This Matters**

- **Eliminates the "Known User" Vector:** Attackers no longer have a guaranteed username (`root`) to attack; they must now guess or discover a valid non-root username first.
- **Accountability:** All administrative actions are logged to a specific user account before privilege escalation, creating a clear audit trail of who did what.

**Implementation**

1. Open the SSH daemon configuration file:
    ```bash
    sudo nano /etc/ssh/sshd_config
    ```
2. Find the line `PermitRootLogin`. Change it to:
    ```
    PermitRootLogin no
    ```
    _(Note: If the line is commented out with a `#`, remove the `#` to enable the setting.)_
3. Save the file and restart the SSH service to apply changes:
    ```bash
    sudo systemctl restart sshd
    ```
    
**Verification**

Open a **new** terminal window (do not close your current session yet!) and try to log in as root:

```bash
ssh root@your-server-ip
# Expected result: "Permission denied" or "Connection closed"
```

> [!warning]
> **Do not log out of your current session until you have verified you can log in with a standard user and successfully run `sudo`.** If you disable root login without a working alternative user, you may be permanently locked out of your remote server.

> [!TIP] The Middle Ground
> `prohibit-password` If you absolutely must log in as root for specific automated tasks (like off-site backups), use `PermitRootLogin prohibit-password`. This disables password-based logins for root but allows access via **SSH Keys**, which are significantly more secure.
### Network Security

- **SSH Key Management:** Use `ssh-keygen -t ed25519` for strong key generation
- **VPN Integration:** WireGuard or OpenVPN for secure remote access
- **Network Monitoring:** `netstat`, `ss`, and `lsof` for connection analysis

### System Monitoring and Logging

- **Log Analysis:** `rsyslog` or `systemd-journald` for centralized logging
- **Security Monitoring:** `auditd` for system call auditing and compliance
- **Intrusion Detection:** `OSSEC` or `Samhain` for host-based intrusion detection

### Disk and Data Protection

- **Full Disk Encryption:** LUKS (Linux Unified Key Setup) for transparent disk encryption
- **File-Level Encryption:** `gpg` for individual file encryption
- **Secure File Deletion:** `shred` command for secure file wiping
