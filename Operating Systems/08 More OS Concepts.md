# More OS Concepts

This note collects operating-system topics that matter in practice but do not fit cleanly into a single earlier section of the course sequence.

## User space vs kernel space

- **User space:** The unprivileged region where application code runs.
- **Kernel space:** The privileged region where the operating system, device drivers, and core subsystems execute.
- **System calls:** The controlled boundary-crossing mechanism that allows user-space code to request kernel work safely.

## Containers

A **container** is an isolated environment for running one or more processes. Unlike a virtual machine, a container does not normally emulate an entire computer or run its own kernel. The processes inside the container ultimately execute as ordinary processes on the host operating system and share the host's kernel.

The isolation comes from operating-system mechanisms that restrict what those processes can see and use. On Linux, containers are built primarily from **namespaces** and **cgroups**. Namespaces give processes isolated views of resources such as process IDs, filesystems, network interfaces, hostnames, and users, while cgroups control and account for resources such as CPU time and memory.

As a result, a process inside a container may believe it is PID 1, see its own filesystem tree, and observe only its container's network interfaces and processes. From the host's perspective, however, it is still a normal [processes](05%20Process%20Management.md#Processes%20vs.%20Threads) with a host PID that the same kernel schedules onto the CPU.

Containers therefore provide **OS-level isolation rather than hardware virtualization**. Because they reuse the host kernel instead of running a separate guest kernel for every environment, they generally require fewer resources and can start much faster than virtual machines.

A container is also not itself a process. It is better understood as a collection of isolation and resource-control boundaries applied to one or more processes. If every process belonging to a container terminates, there is effectively no running workload left inside that container.

Container runtimes such as Docker coordinate these mechanisms for applications. They prepare the container's namespaces, resource limits, filesystem, networking, and other configuration, then start the application's processes inside that environment.

## Boot chain

- **Firmware:** Initializes hardware after power-on.
- **Bootloader:** Locates the kernel image and places it into memory.
- **Kernel initialization:** Sets up memory management, core drivers, and the first user-space processes.

## Device drivers

- **Drivers translate hardware-specific behavior into OS-managed interfaces.**
- **Interrupts, polling, and DMA** are the main strategies for coordinating with physical devices efficiently.
