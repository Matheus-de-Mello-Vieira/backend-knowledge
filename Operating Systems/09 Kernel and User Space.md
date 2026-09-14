# Kernel and User Space

An operating system separates ordinary application execution from privileged control of hardware and system-wide state. **User space** is where application code and its libraries run; **kernel space** holds the kernel code and data that implement resource management, device access, and core subsystems.

This separation combines CPU privilege modes with virtual-memory permissions. A process receives an isolated virtual address space, while the kernel retains authority over the mappings and resources that the process uses. [Virtual memory](03%20Memory%20Management.md#Virtual%20Memory) provides the address-translation and protection mechanisms underlying that isolation.

## Privilege Boundary

- **User mode:** Application code executes without permission to directly control devices or access privileged kernel mappings. Its code, libraries, and ordinary data occupy user-space mappings.
- **Kernel mode:** The kernel executes with the privilege required to manage CPU scheduling, memory, storage, networking, and devices. Kernel code, device drivers, and subsystems such as the network stack use kernel-space mappings.
- **Virtual mappings:** Kernel-space addresses are virtual addresses translated through page tables, not raw physical-RAM addresses. The processor blocks user-mode accesses to mappings without user permission.
- **Per-process layout:** Operating systems commonly arrange each process's address-space layout so that user mappings and kernel mappings occupy distinct regions. The exact mapping strategy depends on the architecture and operating system.

The boundary is a security and isolation mechanism, not merely an address-range convention. A program cannot read a kernel receive buffer or execute privileged kernel code by jumping to an address. It must request that work through a controlled entry point.

## System Calls

A **system call** is the controlled transition through which user-space code asks the kernel to perform a privileged operation, such as reading from a file descriptor, creating a process, or communicating through a socket.

1. The application prepares the system-call identifier and arguments according to the platform's calling convention, then executes a dedicated trap instruction, such as `syscall` on x86-64 or `svc` on ARM.
2. The CPU transfers execution from user mode to kernel mode at a protected entry point. The kernel dispatches the identifier through its system-call table, then validates the request before using privileged state or hardware.
3. The kernel performs the operation, makes its result available according to the calling convention, restores user-mode execution state, and returns control to the application.

This transition is cheaper than switching to a different process, but it still requires controlled state handling and privilege checks. It is therefore more expensive than an ordinary function call.

## Shared I/O Queues

Some interfaces reduce how often an application must cross the system-call boundary for individual I/O operations. Linux `io_uring`, for example, uses shared submission and completion rings between user space and the kernel. An application submits operations and later observes their results through those rings, reducing per-operation transition overhead for workloads that fit its model. The [completion-based socket-I/O model](07%20Socket%20Management.md#Completion-Based%20I/O) applies the same submission-and-result pattern to sockets.
