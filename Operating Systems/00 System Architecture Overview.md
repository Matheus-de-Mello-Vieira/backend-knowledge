# System Architecture

## CPU

The CPU is where actual execution **happens**, making it one of the most valuable resources in a computer system.

To maximize performance, data that is accessed frequently must reside as close to the execution cores as possible. This storage exists inside the CPU itself rather than at the system memory (RAM) level.

This internal storage is structured as a hierarchy of caches:

- **L1 Cache:** The fastest and closest to the core.
- **L2 Cache:** Slightly larger and slower than L1. Like L1, it is usually dedicated to a single core.
- **L3 Cache:** The largest and slowest of the on-chip caches, typically shared across all cores on the CPU.

```mermaid
block-beta
columns 7

block:core2:2
  columns 1
  c2title["CPU Core #2"]
  c2alu["ALU"]
  c2cu["CU"]
  c2reg["Registers"]
  space
  c2mmu["MMU"]
  c2l1["L1 Cache"]
end

space:3

block:core1:2
  columns 1
  c1title["CPU Core #1"]
  c1alu["ALU"]
  c1cu["CU"]
  c1reg["Registers"]
  space
  c1mmu["MMU"]
  c1l1["L1 Cache"]
end

c2l2["L2 Cache"]:2
space:3
c1l2["L2 Cache"]:2

l3["Shared L3 Cache"]:7

c2reg --> c2mmu
c2mmu --> c2reg
c1reg --> c1mmu
c1mmu --> c1reg

c2l1 --> c2l2
c1l1 --> c1l2
c2l2 --> l3
c1l2 --> l3  

classDef core fill:#f9f9f9,stroke:#333,stroke-width:2px;
classDef compute fill:#e1f5fe,stroke:#0288d1;
classDef register fill:#fff9c4,stroke:#fbc02d;
classDef mmu fill:#e8f5e9,stroke:#388e3c;
classDef cache fill:#ffe0b2,stroke:#f57c00;
classDef title font-weight:bold,fill:#eee;

class core1,core2 core
class c1alu,c1cu,c2alu,c2cu compute
class c1reg,c2reg register
class c1mmu,c2mmu mmu
class c1l1,c2l1,c1l2,c2l2,l3 cache
class c1title,c2title title
```

Because the L1 and L2 caches are private to each individual core, they introduce complex **cache coherency** challenges. To write highly optimized software and prevent the CPU from constantly invalidating and discarding cached data, developers must understand how this underlying hardware operates.

Each core operates at a specific clock speed, which dictates how many **cycles per second** it can execute.
- Depending on the CPU architecture and the specific type of instruction, a single operation may take less than, exactly, or more than one clock cycle to complete.

Every CPU family has its own unique set of machine-level instructions.
- Because your source code must ultimately be translated into these specific machine instructions, the **compilation process is highly dependent on the target CPU architecture** (e.g., x86 vs. ARM).

## Storage

- **Persistent Storage:** Unlike volatile RAM, storage retains data permanently, even when the system loses power.
- **Mainly HDD and SSD:** The two primary architectures used for non-volatile storage.
- **Hard Disk Drives (HDD):**
	- *Sector-Level Access:** HDDs are block devices that operate in fixed-size chunks called **sectors** (typically 4KB). To change a single piece of data, the OS must read the entire sector, update it in memory, and rewrite the entire sector back to the disk.
    - **Sequential Dependency:** HDDs rely on a physical spinning magnetic platter and a mechanical arm. Because the arm must physically move to locate data (seek time), random access is extremely slow. They perform significantly better when reading and writing data **sequentially**.
- **Slower than Memory:** Both HDDs and SSDs are significantly slower than RAM.
- **Solid State Drives (SSD):**
    - **Random Access:** Built with electronic flash memory and no moving parts, SSDs execute fast, **random** reads and writes.
    - **Pages vs. Blocks:** SSDs read and write data in small units called **pages** (usually 4KB to 16KB). However, flash memory can only _erase_ data in much larger chunks called **blocks** (which contain dozens or hundreds of pages).
    - **The Update Overhead:** SSDs cannot overwrite a page in place. To update a value, the drive marks the existing page as "stale", finds a brand new empty page, and writes the updated data there.
    - **Garbage Collection:** As the drive fills up with invalid pages, the controller must occasionally read all the valid pages in a block, copy them to a new block, and erase the entire original block to free up space. This background cleanup process is called **Garbage Collection** and introduces performance overhead and hardware wear.
    - **The Shift to Integrated Controllers:** Early HDDs lacked built-in "brains," forcing the OS to manually manage physical disk geometry (CHS - Cylinder / Head / Sector), bad sectors, and mechanical timing. The industry solved this by moving the controller directly onto the drive (IDE), which abstracted physical complexities into simple Logical Block Addressing (LBA) and provided the necessary architectural foundation for modern, controller-dependent SSDs to exist.
	    - **Hardware-OS Coupling:** Under the old model, the Operating System was tightly coupled to the specific hardware it was running on. Because the OS had to be explicitly aware of the drive's physical characteristics, simply swapping or upgrading a drive was extremely difficult; it required manually reconfiguring the OS or BIOS with the new drive's exact physical geometry, making hardware changes rigid, tedious, and highly prone to data corruption.

## Network

- [See more](Networking/01%20Introduction.md)
## Kernel

- **Every system has a limited set of resources.** Because these hardware resources are scarce, they must be carefully managed to keep the system running smoothly.
- **The kernel is the core component of an Operating System.** It acts as the foundational layer of software; everything else in the system is built directly on top of it.
- **The primary job of the kernel is resource management.** It directly handles how hardware like the CPU, memory, and storage are allocated to different tasks.
- **The OS includes additional tools on top of the kernel for usability.** While the kernel handles the low-level hardware communication, the rest of the OS provides user interfaces, libraries, and application management tools to make the computer user-friendly.

### Where the Kernel Comes From: The Boot Chain

The kernel does not simply exist in memory when a machine powers on; it must be fetched from persistent storage and initialized through a strict, cooperative multi-layered boot process.

1. **Firmware Initialization (BIOS/UEFI):** When the system powers up, the CPU is completely blank and executes its first hardcoded instructions out of non-volatile flash memory on the motherboard. This low-level code is the **firmware**. It runs a Power-On Self-Test (POST) to inventory and test the physical hardware (RAM, CPU cores, storage controllers).
2. **The Bootloader:** Once the firmware ensures the hardware is stable, it searches the persistent storage drives for a small, specialized program called a **bootloader** (e.g., GRUB, systemd-boot). The firmware loads this bootloader into RAM and hands over execution control.
3. **Loading the Kernel:** The bootloader's sole job is to locate the compiled kernel binary on the storage drive, load it into physical memory, and jump execution to the kernel's initialization entry point.
4. **Kernel Takeover & OS Initialization:** The kernel wakes up, takes full control of the CPU, initializes its internal memory management systems (like Page Tables), loads essential device drivers, and finally spawns the very first user-space process (e.g., `init` or `systemd`), which boots the rest of the **Operating System**.

### Differentiating Firmware, Kernel, and the Operating System

To understand how physical hardware transitions into a usable software environment, it helps to view the system as a cooperative stack:

|**Component**|**Where It Resides**|**Primary Responsibility**|**Privilege Level**|
|---|---|---|---|
|**Firmware** (BIOS/UEFI)|Non-volatile flash memory soldered onto the motherboard.|Initializes and tests physical hardware components at power-on; handles low-level hardware configurations before any OS boots.|Highest (Runs beneath/before the kernel).|
|**Kernel**|Stored on persistent media; loaded into privileged RAM during the boot sequence.|Managing active hardware resources (CPU scheduling, memory management, I/O coordination) and providing secure isolation via System Calls.|Privileged (Kernel Space / Mode 0).|
|**Operating System (OS)**|Stored on persistent media; loaded into user RAM as needed.|The complete software suite built around the kernel, providing user interfaces (GUI/CLI), system utilities, package managers, and runtime libraries.|Unprivileged (User Space).|

## File System
[06 Storage Management](06%20Storage%20Management.md)

## Program vs Process
[Program vs Process](02%20The%20Anatomy%20of%20a%20Process.md#Program%20vs%20Process)
## Process Management

- **The Kernel's Role:** Because the kernel is the core component of an Operating System, its primary job is resource management. This includes maintaining the state, tracking the memory space, and overseeing the entire lifecycle of every active process.
- **CPU Scheduling:** The CPU is where actual execution happens, making it a highly valuable and scarce resource. The kernel acts as a traffic controller (the scheduler), determining exactly which process gets to run on which CPU core, in what order, and for how long.
- **Context Switching:** To create the illusion that dozens of programs are running at the exact same time, the kernel rapidly swaps processes on and off the CPU cores. During this switch, it must save the current state of the active process (like the data in the CPU registers) and load the saved state of the next process before execution can resume.
- **Resource Allocation and Access:** Processes are strictly isolated and cannot directly interact with physical hardware. The kernel acts as the secure gatekeeper, granting and mediating access to resources like physical RAM (via the MMU and Page Tables), storage drives, and network interfaces.

## User Space vs Kernel Space

- **The Virtual Memory Split:** Every process's private virtual address space is divided into two strict regions: User Space and Kernel Space.
- **User Space:** The unprivileged region where the application's actual code, libraries, and standard data reside.
- **Kernel Space:** A reserved, privileged mapping present in the memory layout of every process. It stores the core kernel code, hardware device drivers, and background subsystems like the TCP/IP network stack.
    - **Virtual, Not Physical:** Addresses in Kernel Space are still **virtual addresses**, mapped to physical RAM via the Page Table. However, the CPU hardware strictly blocks any user-mode code from accessing these specific virtual addresses.
- **Mode Switching (System Calls):** An application cannot directly read data sitting in kernel memory (such as a [network receiving buffer](02%20Reading%20and%20Sending%20Data.md#Receiving%20data)). It must ask the kernel to perform the action on its behalf via a **system call**.
    - **The Shared Mapping:** The actual executable machine code for these system calls resides inside Kernel Space. Because every process has Kernel Space mapped into its own virtual memory layout, the kernel's code is technically "present" within the process's own memory boundaries—it is just strictly walled off by CPU privilege levels.
	- **The Hardware Trapdoor (`syscall`):** Because the CPU blocks direct execution of that walled-off memory, the application cannot just jump to the function. Instead, it places a specific ID number into a CPU register and executes a special hardware instruction (like `syscall` on x86-64 or `svc` on ARM).
	- **The System Call Table:** Executing this instruction triggers a secure trapdoor. The CPU instantly elevates its hardware state from User Mode to Kernel Mode, catches the request, and looks up the ID in a secure kernel directory called the **System Call Table**.
	- **Execution & Return:** The kernel uses its privileged access to safely execute the requested code, places the result back into a CPU register (usually `r0` or `rax`), lowers the CPU privilege back to User Mode, and hands control back to the application.
	- **The Cost:** While faster than a full process context switch, this mode switch is still computationally expensive due to the required security checks, CPU register swapping, and physical boundary crossings.
- **Bypassing the Boundary (`io_uring`):** To avoid the high overhead of constant mode switching during heavy I/O workloads, modern Linux introduced `io_uring`. It establishes a shared memory ring buffer that is mapped and visible to _both_ User Space and Kernel Space. This allows the application and the kernel to pass data back and forth asynchronously without requiring expensive system calls or redundant data copying.

## Device Drivers

- **Kernel-Level Software:** Drivers are specialized software components that typically reside within the privileged Kernel Space. Because the primary job of the kernel is resource management, drivers act as the essential translators between the OS and the physical hardware.
- **Hardware Management:** They manage external devices—such as NVMe storage drives, Keyboards, and Network Interface Cards (NICs)—abstracting their proprietary electrical signals into standard, uniform interfaces that the OS and user applications can interact with.
- **Interrupt Service Routines (ISR):** To handle immediate, unpredictable hardware events, drivers utilize hardware interrupts.
    - **The Keyboard Example:** When you press a key, the keyboard hardware sends an electrical signal that instantly interrupts the CPU. The CPU pauses its current execution, saves its state, and jumps to a specific function in Kernel Space called the ISR. The kernel quickly reads the keystroke from the hardware buffer, clears the interrupt, and routes the input to the active user application.
- **Polling and DMA (Direct Memory Access):** Relying strictly on ISRs for high-speed devices (like a 10Gbps NIC or an NVMe drive) would cripple system performance by interrupting the CPU millions of times per second.
    - **Polling:** Instead of waiting to be interrupted, the driver instructs the CPU to actively check (poll) the device's hardware queues for new data at highly optimized, scheduled intervals.
    - **DMA:** To further reduce CPU strain, high-speed devices utilize Direct Memory Access. The driver configures the hardware (like the NIC) to write incoming data payloads directly into physical system memory (RAM) entirely on its own. The hardware only sends a single CPU interrupt _after_ a massive batch of data has already been safely delivered to memory.
