# More OS Concepts

This note collects operating-system topics that matter in practice but do not fit cleanly into a single earlier section of the course sequence.

## User space vs kernel space

- **User space:** The unprivileged region where application code runs.
- **Kernel space:** The privileged region where the operating system, device drivers, and core subsystems execute.
- **System calls:** The controlled boundary-crossing mechanism that allows user-space code to request kernel work safely.

## Boot chain

- **Firmware:** Initializes hardware after power-on.
- **Bootloader:** Locates the kernel image and places it into memory.
- **Kernel initialization:** Sets up memory management, core drivers, and the first user-space processes.

## Device drivers

- **Drivers translate hardware-specific behavior into OS-managed interfaces.**
- **Interrupts, polling, and DMA** are the main strategies for coordinating with physical devices efficiently.

