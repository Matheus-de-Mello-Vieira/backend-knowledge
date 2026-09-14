# More OS Concepts

This note collects operating-system topics that matter in practice but do not fit cleanly into a single earlier section of the course sequence.

## Boot chain

The kernel must be loaded from persistent storage and initialized before it can manage the machine. Firmware, a bootloader, and the kernel cooperate in an ordered startup sequence.

1. **Firmware initialization:** At power-on, the processor begins executing firmware from the platform's non-volatile storage. The firmware initializes enough hardware to continue booting and commonly performs a power-on self-test or equivalent hardware checks.
2. **Bootloader startup:** The firmware locates and loads a bootloader from persistent storage, then transfers control to it. A bootloader such as GRUB or systemd-boot locates the kernel image.
3. **Kernel loading:** The bootloader places the kernel image in memory and transfers execution to the kernel's initialization entry point.
4. **Kernel takeover:** The kernel initializes its memory-management structures and essential drivers, then starts the first user-space process. That process begins the remaining operating-system startup work.

Each stage runs before the next one and therefore becomes part of the machine's trust boundary. A [bootkit](../Security/01%20Foundations%20and%20Risk/03%20Common%20Threats%20and%20Attacks.md#Bootkits) compromises firmware, boot-sector, or bootloader stages so that malicious code executes before ordinary operating-system security controls are active.

## Device drivers

A **device driver** translates hardware-specific behavior into an operating-system interface. It forms the hardware-facing part of the kernel's abstraction layer: higher-level subsystems use a driver's operations without needing to understand a particular controller's registers, queues, or protocol.

Drivers commonly execute in [privileged kernel context](09%20Kernel%20and%20User%20Space.md#Privilege%20Boundary) because they coordinate access to devices such as storage drives, keyboards, and network interface controllers. Applications do not normally invoke drivers directly. They request I/O through controlled kernel interfaces; for example, opening a [device node](06%20Storage%20Management.md#%60/dev%60%20%E2%80%94%20Device%20Nodes) produces a [file descriptor](02%20The%20Anatomy%20of%20a%20Process.md#File%20Descriptors%20%28FDs%29) whose operations the kernel routes to the relevant driver.

- **Interrupt service routines:** A device can interrupt the CPU to signal an event that requires prompt attention. The CPU saves enough execution state to run the corresponding interrupt handler; the handler reads or acknowledges the device state and makes the event available to the appropriate kernel subsystem or application.
    - A keyboard, for example, can signal an interrupt after a key press. Its driver reads the input from the device buffer, acknowledges the interrupt, and routes the input onward.
- **Polling:** For high-rate devices, an interrupt for every event can consume too much CPU time. A driver can instead check device queues at controlled intervals, trading prompt notification for predictable batching.
- **Direct memory access (DMA):** The driver configures a device to transfer payload data directly between the device and physical memory. The device can then interrupt the CPU after a batch completes rather than requiring CPU involvement in every transferred byte.

High-speed network interfaces and NVMe drives commonly combine queueing, polling, DMA, and batched interrupts to avoid overwhelming the CPU with interrupts.

Drivers therefore connect several OS abstractions to physical I/O. A storage driver supplies block operations beneath filesystem processing, a network-interface driver moves packets between the network stack and the NIC, and an input driver turns device events into input available to applications. The shared interface does not make the devices identical; it confines their hardware-specific behavior to the layer that controls them.
