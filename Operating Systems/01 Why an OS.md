# Why an OS?

Strictly speaking, you don’t actually need an operating system; we use them to make interacting with hardware much simpler. An OS abstracts away technical complexities, providing a uniform interface that works across a vast range of hardware.

You could build software that communicates with the hardware directly—which would be highly specialized and significantly faster—but the code would be far more complex and error-prone. A middle ground is to extend the kernel to fit your specific purpose. However, you will still face limitations stemming from architectural decisions originally designed to make the kernel general-purpose.

## Software, Hardware, and POSIX

An operating system (OS) serves as an intermediary between software applications and hardware. While different hardware components have unique interfaces, the OS abstracts them into a uniform standard like POSIX (Portable Operating System Interface), allowing applications to remain hardware-agnostic.

Most OSs are designed for general-purpose use, which inherently involves trade-offs; optimizing for one use case often requires deprecating support elsewhere. A classic example is the industry shift from 32-bit to 64-bit architectures. In specialized environments, developers may even modify the kernel to solve specific bottlenecks. For instance, ByteDance addressed significant shutdown delays by re-engineering the OS to flush SSD caches in parallel and asynchronously, rather than sequentially.

## Scheduling

A process is a running instance of a program. Once multiple processes are spawned, they begin competing for system resources. Left unchecked, a single process could monopolize the CPU indefinitely—a common issue in early computing where a single hung program could freeze the entire UI, including the mouse cursor. Because of this, modern operating systems employ various scheduling algorithms. There is no single 'best' algorithm; the ideal choice always depends on the specific workload.

## Understand the OS

While many developers treat the operating system as a black box, peak performance requires looking under the hood. Understanding OS fundamentals allows you to make more informed architectural decisions—such as optimizing context switching during I/O operations—to build more efficient software.
