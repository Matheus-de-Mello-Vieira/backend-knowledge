# Virtualization and Containerization

Virtualization and containerization both isolate workloads, but they place the isolation boundary at different layers. A **virtual machine** presents a virtual computer to a guest operating system, whereas a **container** applies operating-system isolation and resource-control boundaries to processes that share the host kernel.

## Virtual Machines

A virtual machine runs a guest operating system, including its own kernel, on virtualized hardware. A hypervisor provides the virtual-machine environment and mediates the guest's access to the physical machine. The guest therefore has an operating-system boundary distinct from the host's kernel.

This model supports workloads that need a different guest kernel or a separately administered operating-system environment. That stronger separation also means each virtual machine needs its guest OS and kernel in addition to its applications.

## Containers

A container is an isolated environment for one or more processes. It does not normally emulate an entire computer or run a separate kernel: its processes execute as ordinary processes on the host operating system and share the host kernel.

On Linux, the principal mechanisms are **namespaces** and **cgroups**:

- **Namespaces:** Give processes isolated views of resources such as process IDs, filesystems, network interfaces, hostnames, and users.
- **Cgroups:** Control and account for resources such as CPU time and memory.

As a result, a process inside a container can believe that it is PID 1, see its own [filesystem tree](06%20Storage%20Management.md#Mount%20Namespaces), and observe only its container's processes and network interfaces. From the host's perspective, it remains a normal [process](05%20Process%20Management.md#Processes%20vs.%20Threads) with a host PID that the same kernel schedules onto the CPU.

## Isolation Boundary and Consequences

Containers provide **OS-level isolation**, while virtual machines provide a guest operating system on virtualized hardware. Because containers reuse the host kernel rather than starting a guest kernel for every environment, they generally require fewer resources and start faster than virtual machines.

A container is not itself a process. It is a collection of isolation and resource-control boundaries applied to one or more processes; when those processes terminate, no workload remains in that container.

Container runtimes such as Docker coordinate these operating-system mechanisms for an application. They configure namespaces, resource limits, filesystems, networking, and related settings, then start the application's processes within those boundaries.
