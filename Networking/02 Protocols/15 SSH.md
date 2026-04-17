# SSH

SSH stands for Secure Shell.

* It is an application-layer protocol for secure remote access to another machine.
* It is commonly used to open an interactive shell, execute remote commands, transfer files, and create encrypted tunnels.
* The standard port is `22`.

## What SSH Provides

SSH is designed to protect remote administration traffic:

* **Confidentiality:** Traffic is encrypted.
* **Integrity:** Messages are protected against tampering.
* **Authentication:** The client verifies the server, and the server verifies the user.

## Common Uses

### Remote Shell Access

* Log into Linux and Unix systems securely.
* Run administrative commands from another machine.

### Remote Command Execution

* Execute one command or script without opening a full interactive session.
* This is useful for automation and operational tooling.

### Tunneling and Port Forwarding

* SSH can forward local or remote ports through an encrypted channel.
* This is often used to reach internal services safely.

### File Transfer

* Tools such as `scp` and `sftp` build on SSH for secure file movement.

## Authentication Models

SSH usually authenticates users with one of these methods:

* **Password authentication**
* **Public key authentication**

Public key authentication is usually preferred for automation and stronger operational security.

## Operational Notes

* SSH is widely available, which makes it a practical fallback when a device does not expose richer management telemetry.
* Because SSH gives command execution access, it should be tightly controlled, logged, and protected with strong authentication.
