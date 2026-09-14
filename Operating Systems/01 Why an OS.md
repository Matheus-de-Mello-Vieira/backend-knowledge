# Why an OS?

Strictly speaking, you don’t actually need an operating system; we use them to make interacting with hardware much simpler. An OS abstracts away technical complexities, providing a uniform interface that works across a vast range of hardware.

You could build software that communicates with the hardware directly—which would be highly specialized and significantly faster—but the code would be far more complex and error-prone. A middle ground is to extend the kernel to fit your specific purpose. However, you will still face limitations stemming from architectural decisions originally designed to make the kernel general-purpose.

## Kernel and Operating System

The **kernel** is the privileged core of an operating system. It manages scarce hardware resources such as CPU time, memory, storage, and I/O devices, and it exposes controlled abstractions through which programs use them.

An **operating system** is broader than its kernel. It combines that core with user-space software such as libraries, command-line or graphical interfaces, system utilities, and application-management tools. The kernel enforces the boundary between programs and hardware; the surrounding software makes the machine usable.

## Software, Hardware, and POSIX

An operating system and POSIX solve related but different portability problems.

- **Hardware Abstraction:** An operating system serves as an intermediary between software applications and hardware. The kernel hides device- and architecture-specific details behind operating-system abstractions such as processes, virtual memory, files, sockets, and synchronization primitives.
- **Standardized Interface:** **POSIX (Portable Operating System Interface)** standardizes a user-space programming interface to many of those operating-system abstractions. It defines APIs and behavioral contracts for concepts such as processes, file descriptors, files, signals, threads, and sockets.
- **OS Portability:** Unix-like operating systems implement large portions of this interface, so software written against POSIX APIs can often remain portable across different operating-system implementations even when their kernels and underlying hardware differ.
- **Portability Boundary:** The **operating system abstracts the hardware**, while **POSIX standardizes how applications interact with the operating system**. POSIX is therefore primarily an OS-interface portability layer rather than the mechanism that makes applications directly hardware-independent.
- **Implementation Freedom:** POSIX constrains the externally visible interface and behavior rather than prescribing one internal kernel architecture. Different operating systems can implement compatible interfaces using different schedulers, filesystems, networking stacks, memory managers, and device drivers.

Most OSs are designed for general-purpose use, which inherently involves trade-offs; optimizing for one use case often requires deprecating support elsewhere. A classic example is the industry shift from 32-bit to 64-bit architectures. In specialized environments, developers may even modify the kernel to solve specific bottlenecks. For instance, ByteDance addressed significant shutdown delays by re-engineering the OS to flush SSD caches in parallel and asynchronously, rather than sequentially.

## Scheduling

A process is a running instance of a program. Once multiple processes are spawned, they begin competing for system resources. Left unchecked, a single process could monopolize the CPU indefinitely—a common issue in early computing where a single hung program could freeze the entire UI, including the mouse cursor. Because of this, modern operating systems employ various scheduling algorithms. There is no single 'best' algorithm; the ideal choice always depends on the specific workload.

## Understand the OS

While many developers treat the operating system as a black box, peak performance requires looking under the hood. Understanding OS fundamentals allows you to make more informed architectural decisions—such as optimizing context switching during I/O operations—to build more efficient software.
