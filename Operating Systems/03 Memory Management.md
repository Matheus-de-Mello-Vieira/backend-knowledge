# Memory Management

At its most basic level, memory is the volatile workspace where the operating system and applications store active, temporary data—information that is actively being processed but is completely wiped out during a power outage.

However, raw physical memory is chaotic. If every running program (your web browser, your code editor, and background system services) were allowed to write directly to the physical hardware, they would constantly overwrite each other's data, leading to instant crashes and massive security vulnerabilities.

This is where **Memory Management** comes in. The Operating System kernel acts as the supreme traffic controller, orchestrating a complex illusion to keep everything running safely and efficiently.

## RAM

**RAM** stands for **Random Access Memory**, which means the CPU can access any data location directly in a constant amount of time ($O(1)$ complexity), regardless of its physical position or the order in which it was stored. This contrasts with spinning mechanical hard drives, which rely on physical movement where a read/write head must traverse intermediate disk space to reach a specific target, resulting in significantly higher latency.

> [!note] **SSDs have diluted the literal meaning of the acronym "RAM"**
> Because SSDs also use flash memory circuits to access data electronically and non-sequentially, they are technically random-access devices too. However, the term "RAM" persists as a proper noun in the industry to specifically differentiate volatile, byte-addressable _system memory_ from non-volatile, block-addressable _storage_ like SSDs.

RAM are fast, but volatile and scarce.

### Static RAM (SRAM)

- **Speed & Cost:** Extremely fast, but highly expensive and physically large (which means low storage density).
- **The Hardware (6T Cell):** 1 bit of data is stored using a flip-flop circuit, which typically requires 6 transistors.
- **Power & State:** It is "static" because as long as the system has power, the flip-flops hold their state perfectly without any active maintenance.
- **Use Cases:** Used where lower latency than DRAM is required, primarily inside the CPU's internal L1/L2/L3 caches. It is also used for small internal buffers, such as mapping tables inside an SSD controller.

#### Banking for Concurrency

- **The Single-Access Bottleneck:** Although SRAM has lower access latency than DRAM, a single, unified block of memory can generally process only one read or write request at a time.
- **Superscalar Demands:** Modern CPUs are "superscalar," meaning they can execute multiple different machine code instructions during the exact same clock cycle. If three simultaneous instructions all need to read different variables from the L1 cache, a single memory block would force them to line up and wait, completely wasting the CPU's parallel processing power.
- **The Solution (Banking):** To solve this, engineers divide the SRAM into multiple independent physical segments called **Banks**.
- **Concurrent Access:** Because each bank has its own dedicated wiring and circuitry, the CPU can fetch a variable from Bank 0 and a variable from Bank 1 at the exact same physical millisecond.
- **Bank Conflicts:** This design is flawless unless two simultaneous CPU instructions attempt to read or write data that happens to be stored inside the _exact same_ bank. This is known as a **Bank Conflict**. When this happens, the hardware cannot process them in parallel; it forces one instruction to stall and wait for the next clock cycle, causing a slight performance dip.

### Dynamic RAM (DRAM)

- **Speed & Cost:** Slower than SRAM, but significantly cheaper and highly abundant. This is your main system memory (e.g., 16GB or 32GB of RAM).
- **The Hardware (1T1C Cell):** 1 bit of data requires only 1 capacitor (to hold the electrical charge) and 1 transistor (to act as a gate).
- **The Leakage Problem:** Capacitors naturally leak their electrical charge over time. Without intervention, the voltage drops to zero and data simply fades away.

#### Hardware Mechanics: Reading, Writing, and Refreshing

Because reading from a microscopic capacitor inherently drains its charge (a destructive read), and because they naturally leak over time, DRAM requires complex physical management:

- **Activation (RAS - Opening a Row):** The CPU cannot read a single bit; it must physically open an entire row. The memory controller issues a RAS (Row Access Strobe) command, sending voltage down a _Wordline_ to unlock thousands of transistors. The capacitors dump their weak charge down _Bitlines_ into **Sense Amplifiers** (the Row Buffer), which boost the signal to full strength and hold it.
- **Column Selection (CAS):** Once the massive row is sitting in the open Sense Amplifiers, the memory controller issues a CAS (Column Access Strobe) command. This extremely fast action selects only the specific 64-byte chunk the CPU actually asked for and fires it across the memory bus.
- **Precharging (Closing a Row):** Because the capacitors were drained during activation, the data would be lost if the controller just walked away. To close a row, the Sense Amplifiers forcefully push the electrical signals back into the empty capacitors to lock the data safely away. The lines are then cleared to prepare for the next RAS command.
- **The Refresh Cycle:** To combat natural capacitor leakage, the memory controller must routinely lock down the memory (typically every 64ms) to read and rewrite the cells, preventing data loss.
- **Banking & Interleaving (Hiding Latency):** Opening rows (RAS), closing rows (Precharge), and refreshing take massive amounts of physical time. To prevent the CPU from stalling, the memory is divided into independent **Banks** - each one with its own Row Buffer. The memory controller _interleaves_ commands—telling Bank 0 to start the slow RAS process, while instantly issuing a CAS command to an already-open row in Bank 1.
- **Row Buffer Hit vs. Miss:** A "hit" occurs when the requested data is in a row that is already open (requiring only a fast CAS). A "miss" means the controller must close the current row (Precharge) and open a new one (RAS) before finally reading the data (CAS), incurring a massive latency penalty.

> [!info] The Scale Difference: Rows vs. Cache Lines
> A **CPU Cache Line** is tiny (64 bytes). This is the maximum chunk of data the CPU pulls across the motherboard at one time. A **DRAM Row** is massive (4KB to 8KB). This is the minimum amount of data the RAM can physically open from its capacitors.
> When the CPU asks for a specific 64-byte cache line, the DRAM physically activates the entire 8KB row where it lives, dumping all of it into the Sense Amplifiers. It then selects only the requested 64 bytes to send back to the CPU. The remaining ~8,128 bytes sit idle in the open Row Buffer.
> To capitalize on those idle bytes, the system relies on a combination of **spatial and temporal locality**. If the software is reading memory sequentially (spatial locality), the next 64-byte chunk the CPU needs is already sitting in that open buffer. However, the CPU must request it quickly (temporal locality) before the memory controller decides to close the row. If the controller uses an **Open-Page policy**, it leaves the 8KB row open in the Sense Amplifiers, gambling that the CPU will ask for the next chunk immediately. When this bet pays off, the RAM delivers the next cache line instantly—a Row Buffer hit—completely bypassing the massive physical penalty of opening a new row of capacitors.

#### The Refresh Priority

While the memory controller tries to optimize for CPU performance (like holding a row open for fast sequential reads), it must constantly battle the physical reality of capacitor leakage. Every row must be recharged within a strict physical window (typically 64 milliseconds), or the voltage drops so low that the 1s and 0s are permanently corrupted.

In hardware architecture, the RAM's physical survival always outranks the CPU's immediate performance needs.

- **The Absolute Veto:** The CPU does not control the RAM directly; all requests pass through the Memory Controller. If a row's time is up, the controller literally freezes the CPU's memory queue. It locks the memory bank, forcefully opens and closes the dying row to recharge it, and only then allows the CPU to resume. This unavoidable hardware stall is known as the **Refresh Penalty**.
- **Distributed Refresh (The 7.8µs Rule):** If the memory controller waited until the 64ms mark to refresh all 8,192 rows at once (**Burst Refresh**), the massive system stutter would cripple performance and risk data death. Instead, it uses **Distributed Refresh**. By dividing the 64ms window by the number of rows, the controller paces itself—pausing the CPU for a tiny fraction of time every **7.8 microseconds** to refresh a single row. By the time it finishes the last row, 64ms have passed, and it instantly loops back to row zero.
- **The "Dumb" Hardware Counter:** Wiring an independent hardware timer for all 100 million rows on a RAM stick would require an impossible amount of physical silicon and cost thousands of dollars. Instead, engineers use a brilliant, cheap shortcut: **One Global Timer + One Counter**.
    - The global timer ticks every 7.8µs.
    - When it ticks, the RAM stick looks at its internal counter (e.g., "Row 45"), refreshes that row, and increments the counter to 46.
    - **The Power of 2 Overflow (Free Resets):** Because physical rows are selected via binary address pins, the total number of rows in a bank is mathematically locked to a strict power of 2 (e.g., 13 pins = 8,192 rows). Engineers size the internal refresh counter to match this exact bit width. When the counter reaches the final row (all `1`s in binary) and increments one more time, it triggers a natural **Integer Overflow**. The hardware drops the carried "1" and instantly snaps back to all `0`s. This provides an infinitely repeating loop for "free," completely eliminating the need for physical logic gates to check if the counter needs to reset.
- **The Metadata Problem (Simplicity over Efficiency):** This hardware counter is entirely blind. If the CPU happened to open and recharge Row 46 one nanosecond before the refresh timer ticked, the controller will still _redundantly_ refresh Row 46. To prevent this, the hardware would need to store a "last opened" timestamp for 100 million rows. Storing that metadata would require a massive, expensive SRAM chip just to track the DRAM, destroying the cost-efficiency of the motherboard. Engineers intentionally choose a "dumb" blind counter, accepting a tiny bit of wasted time to keep the physical memory cheap, dense, and easy to manufacture.

#### Internals Hierarchy and Address Mapping

The physical hardware is nested into distinct levels. When the CPU requests a physical memory address (a long binary number), the memory controller chops that binary number into specific slices to navigate this exact hardware hierarchy:

- **Channel / DIMM:** The highest level. Specific bits in the memory address tell the controller which physical stick of RAM (or which channel on that stick) holds the data.
- **Rank:** A single DIMM might have memory chips on both sides of the stick. A "Rank" is a specific group of chips that work together to output a full 64-bit data block. The address dictates which side of the stick to wake up.
- **Bank:** Inside those chips, the memory is divided into independent grids. The "Bank Bits" in the address tell the controller which independent grid to route the request to, enabling hardware interleaving.
- **Row:** The massive horizontal array of capacitors (e.g., 8KB). The "Row Bits" of the address are used to execute the slow **RAS** command, determining exactly which row of capacitors dumps its charge into the Sense Amplifiers.
- **Column:** The specific vertical intersection inside the open row. The "Column Bits" of the address are used to execute the fast **CAS** command, telling the Sense Amplifiers exactly which 64-byte chunk to select and fire back to the CPU.
- **Byte Offset:** Because the RAM always sends a full 64-byte Cache Line across the bus, it completely ignores the lowest 6 bits of the binary address. The CPU's internal L1 cache uses those remaining bits to pick the exact single byte or integer your software actually asked for.

#### Clock Synchronization

RAM communication is governed by the motherboard's **System Clock**—a quartz crystal oscillator generating a steady electrical pulse.

- **Asynchronous DRAM (Legacy):** Older RAM modules operated entirely independently of the system clock. Execution time was determined solely by analog physical delays. Because the CPU was "blind" to when the data would actually be ready, it relied on fixed, worst-case-scenario wait states (e.g., waiting exactly 60 nanoseconds) before attempting a read.
- **Synchronous DRAM (Modern SDRAM):** Modern memory eliminates blind wait states by synchronizing directly with the system clock, using a digital wrapper (Registers) around the unchanged, asynchronous analog core.
- **Input/Output Gating:** When a command arrives, the input register waits for the _immediate next_ clock edge to release the signal into the analog core. Once the analog physics finish, the output register catches the data and holds it patiently until a specific **target clock cycle** arrives before transmitting it back to the CPU.
- **CAS Latency (CL):** This target output cycle is determined by CAS Latency (e.g., CL14). It is a hard, mathematical guarantee based on worst-case physical operating conditions. If the analog physics finish early, the data simply waits in the buffer. If they finish late (due to extreme heat or manual overclocking), the register opens anyway, transmitting garbage data and causing an immediate system crash (Timing Violation).
- **SDR vs. DDR:** Single Data Rate (SDR) SDRAM transferred data exclusively on the rising edge of the clock signal. Double Data Rate (DDR) memory standard (like DDR4 or DDR5) executes transfers on both the rising _and_ falling edges, effectively doubling throughput without increasing the physical clock frequency.

#### The Evolution of DDR (DDR1 to DDR5)

While the digital interface of SDRAM has scaled to massive speeds over the last two decades, the physical analog core (the capacitors and sense amplifiers) has barely gotten faster. The absolute physical time it takes to open a row is almost the same today as it was in the late 1990s.

To achieve massive bandwidth increases without defying analog physics, hardware engineers rely on a technique called the **Prefetch Buffer**, alongside steady reductions in physical voltage.

**The Prefetch Buffer**: Because the internal analog core is too slow to feed the fast digital interface one bit at a time, it fetches data in wide, parallel chunks.

- **The Cache Line Target:** The CPU always requests memory in exactly 64-byte chunks (512 bits).
- **The Bus Width:** A standard stick of RAM communicates with the motherboard over a 64-bit wide data bus (64 physical data pins).
- **The 8n Prefetch (DDR3 and DDR4):** To fill those 64 pins, the slow analog core pulls 8 consecutive bits in parallel _for every single pin_.
- **The Perfect Match:** 64 pins × 8 bits per pin = 512 bits. This equals exactly 64 Bytes. The RAM grabs one perfect CPU cache line in a single internal sweep, places it in the buffer, and rapid-fires it across the bus.

| Generation | Year | Prefetch Buffer | Voltage | Key Architectural Leap |
| --- | --- | --- | --- | --- |
| **DDR** (DDR1) | 2000 | 2n | 2.5V | Baseline double data rate (transfers on rising and falling clock edges). |
| **DDR2** | 2003 | 4n | 1.8V | Doubled the internal clock multiplier, allowing the bus to run twice as fast as the internal memory cells. |
| **DDR3** | 2007 | 8n | 1.5V | Doubled the prefetch to 8n, perfectly aligning with the 64-byte cache line size over 64 pins. |
| **DDR4** | 2014 | 8n | 1.2V | Introduced **Bank Groups** to allow faster interleaving between different sections of the memory chip. |
| **DDR5** | 2020 | 16n | 1.1V | Introduced **Dual-Channel DIMMs** and **On-Die ECC**. |

Beyond simply lowering the voltage to reduce heat, modern memory relies on architectural redesigns to keep multi-core CPUs fed with data.

- **Bank Groups (Introduced in DDR4):** As speeds increased, the time required to switch between standard banks became a bottleneck. DDR4 grouped banks together. The memory controller can execute a command in Bank Group A, and immediately execute a command in Bank Group B on the very next clock cycle, vastly increasing interleaving efficiency.
- **On-Die ECC (Introduced in DDR5):** As microscopic capacitors become smaller and denser, they become highly vulnerable to cosmic rays and electrical noise randomly flipping a 1 to a 0. DDR5 incorporates Error Correction Code directly into the silicon chips to detect and repair single-bit errors internally.
- **Dual-Channel DIMMs (The DDR5 Breakthrough):** Historically, a single stick of RAM tied up all 64 of its data pins to serve a single CPU request. DDR5 physically splits the stick into **two independent 32-bit channels**, allowing one stick to serve two completely different CPU memory requests at the exact same time.
- **The 16n Synergy:** DDR5 could only split the stick into 32-pin channels because it successfully doubled the internal prefetch to **16n**. If it used 32 pins with the old 8n prefetch, it would only yield 256 bits (a useless half-cache line). By pushing the prefetch to 16 bits per pin, the math works out perfectly again: 32 pins × 16 bits per pin = 512 bits (64 Bytes). Each independent half of the RAM stick can now fetch its own full cache line simultaneously.

## Virtual Memory

### Limitations of physical memory

Before Virtual Memory existed, early computers operated purely on physical memory. The CPU would request a specific memory address, and that address mapped directly on a strict 1:1 scale to a physical transistor inside the RAM stick. While conceptually simple, this direct-access model suffers from catastrophic limitations in a modern, multi-tasking operating system:

- **Fragmentation (The Tetris Problem):** As programs continuously allocate and free memory, it becomes impossible to keep the remaining free space contiguous. This leads to two distinct types of wasted space:
    - **External Fragmentation:** Occurs with variable-size allocations. The total free memory might be large enough for a new program, but it is shattered into tiny, unusable gaps between active blocks.
    - **Internal Fragmentation:** Occurs with fixed-size allocations. If a program asks for 3KB but the system only hands out fixed 4KB blocks, that leftover 1KB is trapped inside the block and completely wasted.
- **Lack of Isolation (The Wild West):** Directly addressing physical memory slots causes immediate failure on a multi-program computer. If two applications are running at the same time, they will inevitably try to use the exact same physical RAM address. When this happens, they overwrite each other's data, causing random crashes, data corruption, and major security breaches where one program can freely spy on or manipulate another.
- **Shared Memory Nightmares:** If two processes _actually_ want to safely share memory for Inter-Process Communication, they have to manually coordinate and agree in advance on the exact physical addresses they will use. This makes writing software incredibly fragile and tightly coupled to whatever else happens to be running on the machine.
- **The Capacity Wall (Large Programs):** In a purely physical system, an entire program (and all its data) must fit into the available RAM. Programs often claim massive chunks of memory but leave them idle for long periods. Because physical addresses cannot be easily moved once assigned, this idle data holds highly valuable RAM hostage, preventing other active programs from using it.

### The Solution: Virtual Address Space & MMU Isolation

To surpass the catastrophic conflicts of raw hardware access, Operating Systems introduced **Virtual Memory**.

Instead of letting a program see the actual physical hardware, the OS provides every single program with its own completely isolated, private, and continuous layout of fake addresses called a **Virtual Address Space**.

- **The MMU Interception (Security & Isolation):** When a program attempts to execute a command at a specific virtual address, a hardware component inside the CPU core called the **Memory Management Unit (MMU)** intercepts the request. Because of this constant translation layer, every program operates under the illusion that it has the computer's memory entirely to itself. This completely prevents address conflicts and secures the data of individual applications from spying or corruption.

The process's virtual address space also distinguishes ordinary application mappings from privileged kernel mappings. Page-table permissions prevent user-mode code from accessing privileged mappings even when they are present in that address-space layout. [User and kernel space](09%20Kernel%20and%20User%20Space.md) explains how that memory-protection boundary combines with CPU privilege modes and system calls.

### Paging & Fragmentation Trade-offs

The OS manages this memory using fixed-size blocks called **Pages** (typically 4KB). While a program sees its virtual pages as a perfect, contiguous sequence, each virtual page is mapped to physical pages (often called _Frames_) that can be scattered chaotically across the RAM. By decoupling the addresses, the OS can piece together physical memory like a mosaic, filling in random gaps.

- **Eliminates External Fragmentation:** Because all blocks are exactly the same 4KB size, the OS can fit any page into any available physical frame. There are never any unusable "weirdly sized" gaps left between applications.
- **Accepts Internal Fragmentation:** The system intentionally sacrifices a tiny amount of memory to achieve this. If a program needs 5KB of memory, the OS must give it two 4KB pages (8KB total). The remaining 3KB inside that second page is permanently wasted (internal fragmentation), but engineers accept this minor loss to gain system-wide stability.
- **Breaking Spatial Locality:** While an array appears perfectly contiguous in virtual memory, crossing a 4KB page boundary often means jumping to a completely different physical location in RAM. If the array spans two physical pages that happen to live in two different physical DRAM rows, reading sequentially will suddenly cause a **Row Buffer Miss**. The memory controller must unexpectedly close the current row (Precharge) and open the new one (RAS), temporarily destroying the hardware's spatial locality optimizations.

### The Page Table & Hardware Translation

A **Page Table** describes how pages in a process's virtual address space correspond to physical memory. Conceptually, a mapping associates a **Virtual Page Number (VPN)** with a **Physical Frame Number (PFN)**.

Page tables are unusual because they sit directly at the boundary between software and hardware. The process generates virtual addresses, the operating-system kernel manages their mappings, and the CPU's Memory Management Unit performs the translation.

#### The Process, Kernel, and CPU

A process normally executes without knowing where its instructions and data physically reside in RAM. It issues virtual addresses as part of ordinary instruction fetches, loads, and stores.

The kernel owns the mappings. It creates page-table structures, maps and unmaps physical frames, assigns permissions, and handles faults when the current mappings cannot satisfy an access.

The CPU's **Memory Management Unit (MMU)** performs the normal translation path in hardware. The kernel does not execute software code for every memory reference; instead, it prepares page tables in a format that the MMU understands directly.

This design introduces two costs. Translation consumes CPU work because the physical destination must be discovered, while the page tables themselves consume physical RAM as metadata. Page-table design therefore needs to keep both translation work and metadata overhead small.

#### Why Multi-Level Paging Is Important

The simplest possible page table would be one enormous flat array containing an entry for every possible virtual page, allowing the Virtual Page Number to directly index that array. However, this conceptually simple approach creates a massive memory usage problem because the table must represent the entire virtual address space, regardless of how much memory a process actually uses. For instance, with a classic 48-bit virtual address space, 4 KiB pages, and 8-byte Page Table Entries, a single flat table would require a staggering 512 GiB of metadata. Even if a process only uses a few megabytes or gigabytes, the system would still have to reserve entries for tens of billions of possible pages.

While increasing the page size can reduce the total number of required entries—such as using 2 MiB pages instead of 4 KiB pages to shrink the hypothetical flat table from 512 GiB down to 1 GiB—this trade-off increases allocation granularity and internal fragmentation. Ultimately, the fundamental flaw with a flat array is how it handles sparsity: because the vast majority of an enormous virtual address space remains unmapped in practice, allocating contiguous metadata for every theoretical page is overwhelmingly inefficient.

> [!note]- Demonstration: Flat Page-Table Size  
> Let the base variables be:
> - $V$ = virtual-address width in bits
> - $P$ = page size in bytes
> - $E$ = PTE size in bytes
>
> The virtual address space contains $2^V$ bytes.
> The number of possible virtual pages is $\frac{2^V}{P}$, so a flat table requires:
> $$S_{\text{flat}} = \frac{2^V E}{P} \text{ bytes}$$
>
> Its space complexity is tightly:
> $$\boxed{\Theta\left(\frac{2^V E}{P}\right)}$$
> _This does not depend on how many pages are actually mapped._
>
> **Example 1: 4 KiB pages**
> - $V = 48$
> - $P = 4 \text{ KiB} = 2^{12} \text{ bytes}$
> - $E = 8 \text{ bytes} = 2^3$
>
> The number of possible virtual pages is $2^{48-12} = 2^{36}$.
> The table requires:
> $$2^{36} \times 2^3 = 2^{39} \text{ bytes} = 512 \text{ GiB}$$
>
> **Example 2: 2 MiB pages**
> - $P = 2 \text{ MiB} = 2^{21} \text{ bytes}$
>
> The table requires:
> $$2^{48-21} \times 2^3 = 2^{27} \times 2^3 = 2^{30} \text{ bytes} = 1 \text{ GiB}$$

#### Multi-Level Paging as a Sparse Radix Tree

Multi-level paging solves the sparsity problem by splitting the VPN into smaller indexes and organizing the mappings using the same mechanism as a [[../Data Structures#Radix Tree|Radix Tree]].

Each group of VPN bits selects an entry at one level of the hierarchy. That entry either points to the next page-table level or indicates that no mappings exist for the entire virtual-address range represented by that branch.

If a high-level entry is absent, all lower page-table structures underneath that region can remain completely unallocated.

This is the central advantage of multi-level paging: page-table memory follows the parts of the virtual address space that are actually populated rather than the maximum address space that could theoretically exist.

#### Deriving the Page-Table Shape

The shape of the hierarchy follows naturally from the page size and the size of each Page Table Entry.

With 4 KiB page-table pages and 8-byte PTEs, one page-table page holds **512 entries**. Because 512 possibilities require 9 bits to select among them, each level consumes 9 bits from the VPN.

A classic 48-bit virtual address using 4 KiB pages has 12 offset bits and therefore 36 VPN bits. Dividing those 36 bits into groups of 9 produces four page-table levels.

The familiar layout is therefore four 9-bit indexes followed by a 12-bit page offset.

> [!note]- Derivation: Page-Table Levels  
> Let:
> - (V) = virtual-address bits
> - (P) = page size in bytes
> - (E) = PTE size in bytes
> The number of entries in one page-table page is:
> $$
> B=\frac{P}{E}  
> $$
> The number of VPN bits consumed by one level is:
> $$
> r=\log_2B
> \log_2\left(\frac{P}{E}\right)  
> $$
> The page offset consumes:
> $$
> \log_2P  
> $$
> bits, leaving:
> $$
> V-\log_2P  
> $$
> VPN bits.
> Therefore the derived number of levels is:
> $$
> L=  
> \left\lceil  
> \frac{V-\log_2P}  
> {\log_2(P/E)}  
> \right\rceil  
> $$
> For 4 KiB pages and 8-byte entries:
> $$
> B=  
> \frac{4096}{8}
> 512
> 2^9  
> $$
> so:
> $$
> r=9  
> $$
> With a 48-bit virtual address:
> $$
> L=  
> \frac{48-12}{9}
> 4  
> $$
> producing:
> $$
> 9+9+9+9+12=48  
> $$
> > [!note] Architecture Variation  
> > Four levels and 48 virtual-address bits are a classic x86-64 configuration. Newer x86-64 hardware can support an additional paging level and a larger virtual address space. Other CPU architectures use different hierarchies.

#### Coverage at Each Level

Each level dramatically expands the range represented by one entry.

With 4 KiB pages and 512 entries per table, one lowest-level table describes **2 MiB** of virtual memory. The level above can describe **1 GiB**, the next **512 GiB**, and the root hierarchy covers the complete **256 TiB** represented by a 48-bit address space.

This exponential growth is what allows a small number of page-table pages to describe isolated mappings scattered across an enormous virtual address space.

> [!note]- Demonstration: Coverage by Level  
> One lowest-level table contains:
> $$
> 512  
> $$
> entries, each mapping:
> $$
> 4\text{ KiB}  
> $$
> so it covers:
> $$
> 512\times4\text{ KiB}
> 2\text{ MiB}  
> $$
> The next level covers:
> $$
> 512\times2\text{ MiB}
> 1\text{ GiB}  
> $$
> The next covers:
> $$
> 512\times1\text{ GiB}
> 512\text{ GiB}  
> $$
> and the root covers:
> $$
> 512\times512\text{ GiB}
> 256\text{ TiB}  
> $$
> In general, each level multiplies the represented range by:
> $$
> B=  
> \frac{P}{E}  
> $$

#### Mapping and Unmapping Pages

When the kernel maps a virtual page, it follows the page-table hierarchy corresponding to that VPN. Existing intermediate tables are reused. If part of the required path does not exist, the kernel creates the missing page-table pages.

Nearby mappings therefore tend to be cheap in metadata because they reuse most of the same hierarchy. A mapping in a distant virtual-address region can require additional intermediate structures.

Unmapping performs the reverse operation. The final mapping is removed, and intermediate page-table pages can be reclaimed when no mappings remain beneath them.

Changing a mapping also requires the kernel to ensure that the CPU no longer uses stale cached translations from the TLB.

> [!note]- Complexity: Mapping and Unmapping  
> Let:
> $$
> L=  
> \left\lceil  
> \frac{V-\log_2P}  
> {\log_2(P/E)}  
> \right\rceil  
> $$
> be the derived hierarchy depth.
> Processing one mapping requires at most one operation per level:
> $$
> \Theta(L)  
> $$
> Expanding the derived variable:
> $$
> \boxed{  
> \Theta(L)
> \Theta\left(  
> \left\lceil  
> \frac{V-\log_2P}  
> {\log_2(P/E)}  
> \right\rceil  
> \right)  
> }  
> $$
> The number of newly allocated page-table pages ranges from:
> $$
> 0  
> $$
> when the complete hierarchy already exists, to:
> $$
> O(L)  
> $$
> when most of the branch must be created.
> In bytes, the worst-case newly allocated page-table metadata for one mapping is:
> $$
> O(LP)  
> $$
> which expands to:
> $$
> \boxed{  
> O\left(  
> P  
> \left\lceil  
> \frac{V-\log_2P}  
> {\log_2(P/E)}  
> \right\rceil  
> \right)  
> }  
> $$
> The mean allocation cost depends on how closely mappings cluster in virtual memory.

#### Multi-Level Page-Table Memory

The amount of page-table metadata depends not only on how many pages are mapped, but also on **where those pages are located**.

Contiguous mappings share almost all of their upper hierarchy. Once an intermediate table exists, hundreds of nearby mappings can reuse it.

Highly scattered mappings share less structure and therefore require more intermediate page-table pages.

This is the same prefix-sharing behavior that makes a sparse radix tree efficient.

> [!note]- Complexity: Compact Mappings  
> Let:
> - (M) = number of mapped normal pages
> - (B=P/E) = entries per page-table page
> - (L) = page-table levels
> For a suitably aligned compact region, the number of required page-table nodes is approximately:
> $$
> N_{\text{compact}}
> \sum_{j=1}^{L}  
> \left\lceil  
> \frac{M}{B^j}  
> \right\rceil  
> $$
> Its tight asymptotic form is:
> $$
> \Theta\left(  
> L+\frac{M}{B}  
> \right)  
> $$
> Expanding the derived variables:
> $$
> \boxed{\Theta\left(\left\lceil \frac{V-\log_2 P}{\log_2(P/E)} \right\rceil + \frac{ME}{P}\right)}
> $$
> Since every page-table node occupies (P) bytes:
> $$
> \Theta\left(P\left(L+\frac{M}{B}\right)\right)
> $$
> becomes:
> $$
> \boxed{\Theta\left(P \left\lceil \frac{V-\log_2 P}{\log_2(P/E)} \right\rceil + ME\right)}
> $$
<!-- -->
> [!note]- Demonstration: One 4 KiB Mapping  
> In a four-level hierarchy, mapping one isolated 4 KiB page can require one page-table page at each level:
> $$
> 4\times4\text{ KiB} = 16\text{ KiB}
> $$
> of page-table metadata.
> This is large compared with one 4 KiB data page, but nearby mappings can reuse almost all of this initial structure.
<!-- -->
> [!note]- Demonstration: Mapping 2 MiB with 4 KiB Pages  
> A 2 MiB region contains:
> $$
> \frac{2\text{ MiB}}{4\text{ KiB}} = 512  
> $$
> normal pages.
> One lowest-level table contains exactly 512 entries, so those mappings fit into one leaf table.
> The complete four-level hierarchy therefore needs approximately:
> $$
> 4\times4\text{ KiB} = 16\text{ KiB}  
> $$
> of metadata.
> Mapping the 513th page requires another lowest-level table, increasing the total to approximately:
> $$
> 5\times4\text{ KiB} = 20\text{ KiB}  
> $$
<!-- -->
> [!note]- Demonstration: Mapping 1 GiB with 4 KiB Pages  
> A 1 GiB region contains:
> $$
> M = \frac{1\text{ GiB}}{4\text{ KiB}} = 262{,}144 = 512^2
> $$
> pages.
> The hierarchy requires:
> - 512 lowest-level tables
> - 1 table above them
> - 1 table above that
> - 1 root
> for:
> $$
> 515
> $$
> page-table pages.
> Their physical memory consumption is:
> $$
> 515\times4096 = 2{,}109{,}440\text{ bytes}
> $$
> or approximately:
> $$
> 2.01\text{ MiB}
> $$
> of metadata for a 1 GiB mapping.
> The metadata ratio is approximately:
> $$
> 0.196\%
> $$
<!-- -->
> [!note]- Complexity: Highly Scattered Mappings  
> Let:
> $$
> N_{\text{PT}}  
> $$
> be the number of allocated page-table nodes.
> At hierarchy depth (d), at most:
> $$
> B^d  
> $$
> nodes can exist, while (M) mappings can populate at most (M) different nodes there.
> A tight description of a maximally dispersed hierarchy is therefore:
> $$
> \boxed{  
> N_{\text{sparse}}
> \Theta\left(  
> \sum_{d=0}^{L-1}  
> \min(M,B^d)  
> \right)  
> }  
> $$
> Expanding (B=P/E):
> $$
> \boxed{  
> N_{\text{sparse}}
> \Theta\left(  
> \sum_{d=0}^{L-1}  
> \min\left(  
> M,  
> \left(\frac{P}{E}\right)^d  
> \right)  
> \right)  
> }  
> $$
> with:
> $$
> L=  
> \left\lceil  
> \frac{V-\log_2P}  
> {\log_2(P/E)}  
> \right\rceil  
> $$
> A simpler but looser upper bound is:
> $$
> N_{\text{sparse}}
> O(ML)  
> $$
> or:
> $$
> \boxed{  
> O\left(  
> M  
> \left\lceil  
> \frac{V-\log_2P}  
> {\log_2(P/E)}  
> \right\rceil  
> \right)  
> }  
> $$
> Since every table occupies (P) bytes:
> $$
> \boxed{  
> O\left(  
> MP  
> \left\lceil  
> \frac{V-\log_2P}  
> {\log_2(P/E)}  
> \right\rceil  
> \right)  
> }  
> $$
> is a safe memory upper bound.
> There is no universal mean memory cost without specifying how mappings are distributed across the virtual address space.

#### The Page Table Walk

The memory savings of multi-level paging come with additional translation work.

A flat table could conceptually use the VPN as one direct array index. A multi-level table instead requires the MMU to follow one entry after another until it reaches the final mapping.

For a classic four-level hierarchy, the MMU uses the first VPN group to select an entry in the root, obtains the physical address of the next table, uses the next VPN group there, and repeats until the final PTE identifies the physical frame.

The page offset is not translated. Once the physical frame is known, the original offset identifies the byte inside that frame.

Because each step depends on the result of the previous one, an uncached page-table walk involves several **dependent memory accesses**. This can be expensive even though the number of levels is small and bounded.

> [!note]- Complexity: Page-Table Walk  
> Let:
> $$
> L=  
> \left\lceil  
> \frac{V-\log_2P}  
> {\log_2(P/E)}  
> \right\rceil  
> $$
> A successful translation of a normal page on a TLB miss must process every level:
> $$
> \Theta(L)  
> $$
> or:
> $$
> \boxed{  
> \Theta(L)
> \Theta\left(  
> \left\lceil  
> \frac{V-\log_2P}  
> {\log_2(P/E)}  
> \right\rceil  
> \right)  
> }  
> $$
> Successful best, mean, and worst structural walks therefore have the same tight bound.
> An unsuccessful walk may discover an absent mapping earlier.
> Best case:
> $$
> \boxed{\Theta(1)}  
> $$
> Worst case:
> $$
> \boxed{  
> \Theta(L)
> \Theta\left(  
> \left\lceil  
> \frac{V-\log_2P}  
> {\log_2(P/E)}  
> \right\rceil  
> \right)  
> }  
> $$
> There is no universal mean fault depth without a distribution of unmapped addresses.
> On a fixed architecture, (L) is bounded, so the walk is technically constant with respect to the number of mapped pages. This does not imply that several dependent memory accesses have the same physical latency as one lookup.
> [!note]- x86-64: `CR3`  
> Hardware needs a way to locate the root of the currently active page-table hierarchy.
> On x86-64, the `CR3` control register provides the relevant page-table-root information. Switching address spaces changes which translation hierarchy the CPU should use.
> The CPU does not need to understand the operating-system abstraction of a process. It needs the translation state associated with the currently executing context.

#### Page-Table Entries and Protection

A Page Table Entry (PTE) does more than just point to a memory location—it tells the Memory Management Unit (MMU) exactly _how_ that memory can be used.

While an intermediate entry usually points to the next level of the page table, a **leaf entry** identifies the actual physical frame backing a virtual page. Alongside this physical address, the leaf entry contains control bits that the CPU checks during every single memory access.

Common control flags include:

- **Present:** Whether the page is currently mapped in physical memory.
- **Read/Write:** Whether the data on the page can be modified.
- **User/Supervisor:** Whether user-mode code is allowed to access it, or if it is restricted to the kernel.
- **Execute-Disable (NX/XD):** Whether the CPU is permitted to run instructions stored on this page.
- **Accessed:** Whether the CPU has recently read or written to the mapping.
- **Dirty:** Whether the page has been modified since it was loaded.

These control bits make page tables the foundation of the system's **memory-protection mechanism**, not just its address-translation tool.

Because of these flags, an operating system can assign distinct rules to different areas of memory. For example, a code page may be readable and executable but strictly read-only, preventing code injection. Conversely, a stack page may be readable and writable but marked non-executable to block buffer overflow attacks. The MMU enforces these permissions on the fly, as part of the exact same process that resolves the physical address.

When a program attempts an access that violates a PTE's state or permissions, the CPU halts the operation and raises a **page fault**.

Contrary to what the name implies, a page fault does not necessarily mean data must be loaded from a hard drive. It simply means the MMU cannot satisfy the memory request using the current page-table state. A fault can occur for several reasons:

- The page is completely unmapped.
- A lazily allocated page has not yet been assigned physical memory.
- A process is attempting to write to a Copy-on-Write (CoW) page.
- The access violates security permissions (e.g., trying to write to a read-only page or execute a data page).

When a fault occurs, the CPU hands control over to the operating system to determine if the error is recoverable. If the access is valid but unready (like demand paging or CoW), the kernel creates or modifies the mapping behind the scenes and resumes the process. If the access is genuinely invalid, the kernel terminates the process.

This separation of concerns is fundamental to modern computing: the **hardware (MMU)** blindly detects and enforces the current rules, while the **software (OS kernel)** dictates the policy and decides how to resolve violations.

#### Huge Pages

The page-table walk does not always need to reach the lowest level.

Some architectures allow an entry at a higher level to describe a larger physical page directly. On x86-64, common examples include 2 MiB and, when supported, 1 GiB pages.

A larger page needs fewer mappings to describe the same amount of memory. It can also terminate the page-table walk earlier and allows one TLB entry to represent a much larger region.

The trade-off is coarser allocation. Huge pages can increase internal fragmentation and can be more difficult for the operating system to allocate when physical memory is fragmented.

> [!note]- Derivation: 2 MiB Pages  
> A normal 4 KiB page uses:
> $$
> 12  
> $$
> offset bits because:
> $$
> 2^{12}=4\text{ KiB}  
> $$
> One page-table level consumes:
> $$
> 9  
> $$
> VPN bits.
> If a mapping terminates one level earlier, those 9 bits become part of the page offset:
> $$
> 12+9=21  
> $$
> so the resulting page size is:
> $$
> 2^{21}
> 2\text{ MiB}  
> $$
> On the classic four-level x86-64 hierarchy:
> - 4 KiB page → 4 levels
> - 2 MiB page → 3 levels
> - 1 GiB page → 2 levels
>
> [!note]- Complexity: Huge-Page Mapping Count  
> Let:
> - (D) = bytes of application memory to map
> - (X) = chosen page size
> - (E) = PTE size
> The number of required leaf mappings is:
> $$
> M_X=  
> \left\lceil  
> \frac{D}{X}  
> \right\rceil  
> $$
> Leaf-entry metadata therefore scales as:
> $$
> \Theta(M_XE)  
> $$
> Expanding (M_X):
> $$
> \boxed{  
> \Theta\left(  
> E  
> \left\lceil  
> \frac{D}{X}  
> \right\rceil  
> \right)  
> }  
> $$
> For large (D):
> $$
> \boxed{  
> \Theta\left(  
> \frac{DE}{X}  
> \right)  
> }  
> $$
> Moving from 4 KiB to 2 MiB pages increases (X) by:
> $$
> \frac{2\text{ MiB}}{4\text{ KiB}}
> 512  
> $$
> so approximately 512 times fewer leaf mappings are required for the same memory capacity.
> [!note]- Demonstration: Mapping 1 GiB with Huge Pages  
> Using 4 KiB pages, mapping 1 GiB required approximately:
> $$
> 515  
> $$
> page-table pages, or:
> $$
> 2.01\text{ MiB}  
> $$
> of metadata.
> With 2 MiB pages:
> $$
> \frac{1\text{ GiB}}{2\text{ MiB}}
> 512  
> $$
> mappings are required.
> They fit into one page-table node at that level, so the hierarchy needs approximately three page-table pages:
> $$
> 3\times4\text{ KiB}
> 12\text{ KiB}  
> $$
> With one supported 1 GiB page, the hierarchy can terminate another level earlier and requires approximately:
> $$
> 2\times4\text{ KiB}
> 8\text{ KiB}  
> $$
> of page-table structure.

#### Translation Lookaside Buffer (TLB)

While multi-level paging solves the memory overhead of large page tables by making them sparse, it introduces a serious performance penalty: a single memory access might now require multiple dependent memory reads just to walk the page-table hierarchy.

To solve this, CPUs use a **Translation Lookaside Buffer (TLB)**—a specialized, high-speed hardware cache that stores recently resolved virtual-to-physical page mappings and their associated permissions.

When a program requests a memory access, the MMU checks the TLB first:

- **On a TLB hit:** The MMU already has the physical frame address and permissions. It skips the expensive multi-level page-table walk entirely and proceeds with the access.
- **On a TLB miss:** The MMU must manually walk the page tables in main memory to resolve the physical address. Once found, it caches this mapping in the TLB to speed up future accesses to that page.

Because the TLB is a very small, fast cache, **spatial locality** is just as crucial for address translation as it is for data caching. A workload that repeatedly accesses a small cluster of pages will enjoy a high TLB hit rate. Conversely, a workload that jumps erratically across many disconnected pages will continuously evict old translations, suffering a severe performance drop due to constant page-table walks.

It is a common misconception that dynamically allocated memory (the heap) is inherently TLB-unfriendly. A large, contiguous array allocated on the heap will actually exhibit excellent translation locality. The real performance killer is **scattered or pointer-heavy memory** (like complex node-based graphs or fragmented linked lists). These structures force the CPU to touch data across dozens of unrelated pages, rapidly exhausting the TLB capacity.

> [!note]- Complexity: TLB Hit and Miss  
> Treating the hardware TLB lookup as fixed-latency, a hit is:
> $$
> \boxed{\Theta(1)}  
> $$
> A miss performs the TLB lookup plus an (L)-level walk:
> $$
> \Theta(1)+\Theta(L)
> \Theta(L)  
> $$
> Therefore:
> $$
> \boxed{  
> T_{\text{miss}}
> \Theta(L)
> \Theta\left(  
> \left\lceil  
> \frac{V-\log_2P}  
> {\log_2(P/E)}  
> \right\rceil  
> \right)  
> }  
> $$
> On a fixed architecture, both paths are technically bounded constants with respect to the number of mapped pages, but their physical costs can differ substantially.
> [!note]- Mean Translation Cost  
> Let:
> - (q) = probability of a TLB hit
> - (c_h) = physical TLB-hit cost
> - (c_w(L)) = physical cost of an (L)-level page-table walk
> Then the expected translation cost is approximately:
> $$
> \boxed{  
> E[T]
> q,c_h  
> +  
> (1-q)  
> \left(  
> c_h+c_w(L)  
> \right)  
> }  
> $$
> There is no useful universal mean translation cost without specifying the workload's TLB hit rate and hardware latency characteristics.

#### TLB Reach

The total amount of memory a CPU can access without suffering a page-table walk is known as its **TLB reach**.

Because the hardware limits the TLB to a fixed number of entries, the most effective way to increase its reach is to increase the page size. A workload whose active memory fits comfortably within the TLB's reach translates addresses efficiently, whereas a working set that drastically exceeds it will suffer from constant cache misses.  

This is the primary performance argument for using **huge pages** in memory-intensive applications. Because a 2 MiB page maps 512 times more memory than a standard 4 KiB page, a single TLB entry theoretically covers 512 times as much ground.

> **Demonstration: Calculating TLB Reach**
>
> Let $T$ represent the number of available TLB entries and $X$ represent the page size. The total TLB reach ($R$) is:
> $$R=T \times X$$
> With standard 4 KiB pages, the reach is:
> $$R_{4K}=T \times 4\text{ KiB}$$
> With 2 MiB huge pages, the reach becomes:
> $$R_{2M}=T \times 2\text{ MiB}$$
> Comparing the two reveals the exact scale of the efficiency gain. The same number of TLB entries can cover 512 times more memory:
> $$\frac{R_{2M}}{R_{4K}}=\frac{2\text{ MiB}}{4\text{ KiB}}=512$$
>
#### Context Switches and Address Spaces

Different processes can use the same virtual address while mapping it to different physical memory. A TLB translation belonging to one process therefore cannot be blindly reused as if it belonged to another.

A simple CPU could solve this by discarding process-specific translations whenever the active address space changes, but that would make context switches more expensive because the new process would need to rebuild its translation working set through TLB misses.

Threads belonging to the same process normally share the same virtual address space and page tables, so switching between those threads does not inherently require changing the page-table root.

Modern CPUs can also tag translations with an **address-space identifier**, allowing TLB entries from several processes to coexist. On x86, one such mechanism is the **Process-Context Identifier (PCID)**.

The more accurate model is therefore not that every process switch flushes the TLB, but that the CPU must ensure that translations from one address space are never incorrectly interpreted as belonging to another.

#### Shared Kernel Mappings

Although user-space mappings differ between processes, many kernel mappings can be identical.

There is only one running kernel, so the virtual addresses used for kernel code and kernel data can refer to the same physical memory regardless of which user process was executing before control entered the kernel.

Operating systems can exploit this by making the kernel portions of different address-space hierarchies refer to the same underlying kernel page-table structures. The process-specific branches remain different, while identical kernel branches can be shared.

This produces two separate benefits.

- **Sharing page-table structures** avoids storing independent copies of the same kernel mapping metadata for every process.
- **Reusing kernel TLB translations** avoids performing another page-table walk for a kernel address whose mapping did not change when the active user process changed.

Architectures such as x86 also support **global mappings**. Appropriate translations marked global can remain in the TLB across ordinary address-space switches because their meaning does not depend on the current process.

This differs from PCID. Global mappings are reusable because the mapping itself is shared, while PCID allows different process-specific translations to remain cached by tagging them with their owning address space.

> [!note]- Example: Process-Specific and Shared Translations  
> The same user virtual address can map differently:
> $$
> A:V\rightarrow P_1  
> $$
> $$
> B:V\rightarrow P_2  
> $$
> so that translation cannot be reused indiscriminately.
> A shared kernel virtual address can instead map identically:
> $$
> A:K\rightarrow P_K  
> $$
> $$
> B:K\rightarrow P_K  
> $$
> Because the translation is the same in both address spaces, it can potentially be represented by shared page-table structures and reusable global TLB state.
> **Note: Modern Linux and KPTI**
>
> Traditionally, operating systems mapped the entire kernel into every process's virtual address space, relying on **supervisor-mode permissions** in the page table to block unauthorized user access. However, speculative-execution vulnerabilities like **Meltdown** proved that relying solely on permission bits was no longer secure; the mere presence of those kernel mappings in user mode became an attack vector.
>
> In response, modern Linux relies on **Kernel Page-Table Isolation (KPTI)**. Under KPTI, when a process executes in user space, its active page table contains only the bare minimum kernel mappings required to trigger a system call or handle an interrupt. When the CPU actually enters the kernel, it must immediately swap to a completely different page table to access the full kernel view.
>
> Consequently, the classic model—where every process permanently shares a complete view of the kernel in its upper memory—remains vital for understanding fundamental operating system design, but it no longer accurately describes how modern, secure systems actually operate in the wild.

#### TLB Invalidation

A cached TLB entry can outlive the page-table entry from which it was originally created.

If the kernel unmaps a page, changes its physical frame, or modifies its permissions, the corresponding cached translation may become stale.

Updating the page table is therefore only one part of changing a mapping. The kernel must also ensure that obsolete TLB entries can no longer be used.

On a multicore system, the same address-space translation may be cached by several CPU cores. Invalidating a mapping can therefore require coordination with those cores, commonly called a **TLB shootdown**.

The page-table data-structure update itself is bounded by the hierarchy depth, but the complete system-wide invalidation cost also depends on which CPUs hold the translation and how the architecture coordinates invalidation. It should therefore not be treated as merely another page-table-tree traversal.

### Controlled Sharing & Concurrency

Because the OS controls the map, it can intentionally point multiple virtual pages from entirely different programs to the exact _same_ physical page. This solves the shared memory nightmare, enabling instant, secure Inter-Process Communication (IPC) without the programs ever needing to coordinate physical addresses.

- **Deduplicating Executables:** If you spin up ten instances of the exact same program, the OS does not copy the binary into RAM ten times. It loads the read-only code and fixed data sections into physical memory just once, and maps the virtual pages of all ten processes to those exact same physical frames.
- **Shared Libraries (`.so` / `.dll`):** This is even more critical for standard libraries (like C's `libc`). The OS loads the library code into physical RAM once, and every single program on your machine dynamically maps its virtual addresses to that shared physical space.
- **Threads vs. Processes:** This highlights the core difference in concurrency: while separate processes have independent Page Tables (isolated memory), multi-threading works by spawning execution threads that utilize the _exact same Page Table_, giving them native, shared access to the entire virtual address space.
- **Process Forking & Copy-on-Write (CoW):** When a program spawns a child process using the `fork()` system call, the OS does not waste time copying the gigabytes of physical RAM. Instead, it instantly duplicates the _Page Table_, pointing the child to the exact same physical pages as the parent, and temporarily marks them as Read-Only. The exact millisecond either process attempts to modify a variable, the MMU triggers a fault, and the OS creates a private, independent 4KB copy of _just that specific page_.
    - **Backend Architecture:** Modern infrastructure relies entirely on these OS tricks. Databases like PostgreSQL allocate massive shared memory buffers so all isolated worker processes can read the exact same database cache. Proxies like NGINX use `fork()` to spawn worker processes, relying entirely on Copy-on-Write to instantly boot new workers without duplicating the massive master configuration data in physical RAM.

> [!tip] Inspecting the Map in Linux
> You don't have to guess how the OS is routing your memory. You can physically look at the active virtual memory map for any running process in Linux by reading the file at [`/proc/[pid]/maps`](06%20Storage%20Management.md#%60/proc%60%20%E2%80%94%20Process%20and%20Kernel%20Information). It will show you the exact virtual address boundaries where your shared libraries, heap, and stack have been parachuted into your application!
> [!example] Python’s `None` and the Copy-on-Write Penalty
> An interesting case related to it is how Python’s reference-counting singletons (`None`, `True`, `False`) silently defeated Copy-on-Write in multi-process deployments: every assignment to `None` incremented its refcount, triggering CoW faults that forced the OS to duplicate memory pages across worker processes. Python fixed this with [[../Technologies/Python/Python Internals#The Fix: Immortal Objects|immortal objects]].
> [!example] Architecture Story: Redis & The Persistence
> Because Redis is fundamentally an in-memory database, it faces a massive existential threat: if the physical server loses power or crashes, every single piece of data is permanently wiped from RAM. To handle crashes, Redis engineers needed a way to periodically persist (save) this in-memory data to the physical hard drive.
> Because Redis is famously single-threaded, saving this data presented a massive architectural bottleneck:
> - **The Naive Approach (Blocking the Main Thread):** If the Redis process simply paused to copy 10GB of RAM onto a slow mechanical hard drive, the database would completely freeze for several seconds (or even minutes). This would cause massive latency spikes for every application connected to it, completely undermining Redis's core purpose of sub-millisecond speed.  
> - **The `fork()` Dilemma:** The logical solution is to spawn a background process to do the heavy lifting. However, if Redis had to duplicate 10GB of RAM into a new memory space for the child, creation would take longer and require roughly another 10GB of available physical memory, potentially causing an Out-Of-Memory (OOM) condition.
  >
To solve this, Redis relies entirely on the magic of the OS's Virtual Memory map and **Copy-on-Write (CoW)**.
>
> When Redis decides it is time to save to the disk (a background save, or `BGSAVE`), it executes the `fork()` system call.
> 1. **Instantaneous Snapshot:** Instead of copying the 10GB of physical data, the OS simply duplicates the master **Page Table**, which takes fractions of a millisecond. The child process instantly wakes up believing it has its own 10GB of memory, but it is actually pointing to the exact same physical RAM frames as the parent.
> 2. **Read-Only Lock:** The OS marks all of these shared physical pages as Read-Only.
> 3. **The Background Save:** The child process sequentially reads the memory and streams it to the physical hard drive. Because the child is purely reading and never modifying the data, it never triggers a memory conflict.
> 4. **The Parent Continues Serving:** Meanwhile, the parent process (the main Redis thread) continues serving live user traffic.
> 5. **Just-in-Time Duplication:** If a user sends a `SET` command to overwrite an existing key while the backup is running, the parent attempts to write to a Read-Only page. The hardware MMU intercepts this and triggers a Page Fault. The OS instantly steps in, creates a private 4KB copy of _just that specific page_ for the parent to modify, and leaves the original page intact for the child process to finish saving.
> By leveraging Copy-on-Write, Redis can avoid copying all pages at `fork()` time. The additional memory and latency are deferred until either process writes to a shared page, allowing the child to observe a point-in-time view while the parent continues to mutate its data.
>
### Swapping & Extending RAM to Disk

- **The RAM Bottleneck:** Virtual memory allows the OS to transparently offload inactive data to the storage drive whenever physical RAM hits its maximum capacity.
- **Targeting Stale Data:** The OS constantly monitors memory access. When it needs space, it identifies "stale" pages that haven't been used in a while (such as a background application you minimized hours ago).
- **Writing to Disk (The Swap):** The OS copies these inactive 4KB pages onto a dedicated space on the slower SSD or mechanical hard drive. This area is called the _Pagefile_ in Windows or _Swap Space_ in Linux.
- **Freeing Physical Memory:** Once safely written to the disk, the OS completely clears those physical RAM slots, making them instantly available for your active, demanding tasks.
- **The Seamless Illusion:** Because the OS and the hardware MMU handle all the underlying address translation, the evicted application is entirely unaware this happened. From the process's perspective, it still owns a continuous, uninterrupted chunk of RAM.
- **The Page Fault (Waking Up):** If you suddenly maximize that background application, the CPU tries to read the memory that is no longer there. Hitting this empty virtual address triggers a hardware trap known as a **Page Fault**.
- **The Rescue Operation:** The OS intercepts the Page Fault and instantly pauses the program. It reaches into the hard drive, fetches the missing data, and copies it back into an available physical RAM slot.
- **Resuming Execution:** Finally, the OS updates the application's Page Table to point to this new physical location and resumes the program. Later accesses can use RAM again, but the page-faulting access has already incurred storage and fault-handling latency.

### Limitations of Virtual Memory

While Virtual Memory solves massive architectural problems, maintaining this system-wide illusion introduces several unavoidable performance and hardware costs:

- **The Translation Penalty:** The CPU cannot read or execute virtual addresses directly. Every single memory request—from variable lookups to instruction fetches—must pass through an additional layer of translation, adding microscopic but constant latency to the system.
- **Page Table Memory Overhead:** The OS must maintain massive dictionaries (Page Tables) for _every single running process_. These tables are not free; they consume a significant amount of physical RAM just to manage the rest of the RAM.
- **The Page Fault Trap:** When a process accesses unmapped or swapped memory, it triggers a Page Fault. Handling it transfers control from User Mode to Kernel Mode and stalls the application while the OS allocates a page or waits for storage I/O, which has much higher latency than RAM.
- **Hardware Complexity:** Virtual memory requires dedicated hardware support. CPUs include an MMU, a TLB cache that is faster to consult than a page-table walk, and mapping registers such as the PTBR; these add hardware complexity.
- **Context Switching & TLB Misses:** A TLB reduces translation overhead by caching recent address translations. When the OS switches to a different process, some cached translations may no longer apply. Subsequent TLB misses require page-table walks, which have higher latency than TLB hits until useful translations are cached again.

## Memory Access & Caching

Accessing system memory (RAM) has higher latency than accessing data in CPU registers or caches. The gap comes from both the memory device's read/write timing and the distance signals travel between the CPU and RAM.

To understand why this matters, think of the CPU and RAM as a frontend and backend system web application:

- **Network Chattiness:** The more "chatty" the frontend and backend are—making thousands of tiny, individual requests back and forth—the more the latency builds up.
- **The Accumulated Cost:** A single RAM access may be acceptable, but the latency can become a bottleneck when it occurs across millions of operations.
- **The Hardware Solution:** CPUs use internal cache hierarchies (L1, L2, L3) to retain frequently used data closer to the core. A cache hit avoids a RAM access and therefore has lower latency.
- **The Cache Line:** To exploit nearby accesses, a memory request commonly fetches a contiguous block—often 64 bytes—called a Cache Line. The block is placed in a cache level; the exact level and path depend on the cache hierarchy and the access.

### Spatial Locality

- **The Concept:** If a program accesses a specific memory address, there is a very high probability it will access the immediately adjacent memory addresses next.
- **The Benefit:** Because CPUs fetch data in cache lines, sequential accesses can reuse a line that was fetched for a previous access. These cache hits have lower latency than fetching the same data from RAM.
- **Where it Applies:** Arrays (on the [Heap](02%20The%20Anatomy%20of%20a%20Process.md#The%20Heap) and [Data Section](02%20The%20Anatomy%20of%20a%20Process.md#The%20Data%20Section)) and sequential local variables (packed tightly on the [Stack](02%20The%20Anatomy%20of%20a%20Process.md#The%20Stack)) can be processed with fewer cache misses than scattered data.

> [!example] Sequential Reads
>
> ```asmarm
> ldr r0, [r2, #0]   
> ldr r1, [r2, #4]
> ```
>
> - **The First Read (`ldr r0`):** Assuming the register `r2` holds a base memory address, the CPU attempts to read it. If the data is not in any cache, the CPU must fetch an entire 64-byte Cache Line from system RAM. This has higher latency than a cache hit.
> - **The Cached Read (`ldr r1`):** The next instruction requests data exactly 4 bytes away from the first read (`#4`). If the surrounding 64-byte cache line remains in L1, this is a cache hit and has lower latency than another RAM access.
> [!example] Real-World Impact: Linux 6.8 TCP Optimization
> The sheer power of Spatial Locality and cache line optimization was demonstrated in the Linux 6.8 kernel update. Developers analyzed the core networking data structures and realized that frequently accessed variables were scattered at different memory offsets. By simply rearranging the declaration order of these variables in the source code—packing the "hot" variables tightly together—they ensured the data fit into a single CPU Cache Line. This drastically reduced L1 cache misses and boosted TCP performance for massive concurrent connections by ~40%, entirely through spatial locality.
>
### Temporal Locality

- **The Concept:** If a program accesses a specific memory address, there is a very high probability it will access that _exact same_ address again very soon.
- **The Benefit:** The CPU keeps recently accessed Cache Lines in the L1 cache for as long as possible before evicting them.
- **Where it Applies:** Local loop counters (e.g., `for(int i = 0; ...)`), frequently used global variables, and hot code paths can have lower average access latency when their data or instructions remain cached instead of requiring RAM accesses.

### Memory Alignment

Processors do not read memory one byte at a time; they fetch it in fixed-size hardware chunks (such as 4-byte words or 64-byte cache lines). If a variable is placed randomly and happens to cross the boundary between two of these chunks, the CPU is forced to perform two separate memory reads and artificially stitch the data together. To prevent this severe performance penalty and ensure every variable can be fetched in a single hardware cycle, compilers explicitly align variables in memory.

Variables are placed at memory addresses that are **divisible by their size**.

- `char` (1 byte): Any address.
- `short` (2 bytes): Even addresses (divisible by 2).
- `int` (4 bytes): Addresses divisible by 4.
- `double` (8 bytes): Addresses divisible by 8.

If the next available memory address does not satisfy a variable's alignment requirement, the compiler inserts empty, unused bytes (padding) until the requirement is met.

### Memory Optimization: The "Sort by Size" Rule

To minimize wasted memory due to padding, the standard best practice is to order struct members in descending order based on their data type size.

**Inefficient Layout (Wastes 8 bytes):**

```c
struct Inefficient {
    char c;
    double d;
    short s;
    int i;
};
```

uses a total of 24 bytes:

```mermaid
block-beta
  columns 8

  c["c (0)"]:1
  p1["padding (1–7)"]:7

  d["d double (8–15)"]:8

  s["s short (16–17)"]:2
  p2["padding (18–19)"]:2
  i["i int (20–23)"]:4

  classDef field fill:#1f2937,stroke:#9ca3af,color:#ffffff
  classDef padding fill:#7f1d1d,stroke:#fca5a5,color:#ffffff

  class c,d,s,i field
  class p1,p2 padding
```

**Optimized Layout (Zero wasted internal bytes):**

```c
struct Optimized {
    double d;
    int i; 
    short s;
    char c;
};
```

uses a total of 16 bytes:

```mermaid
block-beta
  columns 8

  d["d double (0–7)"]:8

  i["i int (8–11)"]:4
  s["s short (12–13)"]:2
  c["c char (14)"]:1
  p1["padding (15)"]:1

  classDef field fill:#1f2937,stroke:#9ca3af,color:#ffffff
  classDef padding fill:#7f1d1d,stroke:#fca5a5,color:#ffffff

  class d,i,s,c field
  class p1 padding
```

### Advanced Hardware Optimizations

While saving memory footprint is good, prioritizing CPU cache efficiency is often more important in high-performance computing.

> **Optimization 1: Spatial Locality (Ignoring the Size Rule)**
> If variables are frequently accessed together in the same loop (e.g., `x_velocity` and `y_velocity`), they should be placed next to each other in the struct—even if it means intentionally wasting a few bytes of padding. This guarantees one cache fetch brings all necessary data to the CPU, preventing expensive secondary memory reads.
> **Optimization 2: Preventing [False Sharing](04%20Inside%20The%20CPU.md#The%20Developer%20Trap:%20False%20Sharing) (Intentional Wasting)**
> In multithreaded environments, if Thread A modifies `Var1` and Thread B modifies `Var2`, placing them on the _same_ 64-byte cache line will cause the CPU cores to constantly invalidate each other's caches, severely degrading performance. Engineers will intentionally insert large blocks of padding (e.g., `char padding[64];`) between these variables to force them onto separate cache lines. Se more at

### Direct Memory Access (DMA)

As described in the physical [RAM](03%20Memory%20Management.md#RAM), memory access is highly complex. Normally, if the system needs to copy a large block of data from the hard drive into RAM (or send a file out to the Network Interface Card), the CPU has to act as the middleman. It reads the data from the disk into its own internal registers, and then writes it back out to the RAM.

For small transfers, CPU-mediated copying may be appropriate. For large transfers, using the CPU as an intermediary consumes cycles and memory bandwidth that could otherwise be used for computation.

To solve this, hardware engineers created the **DMA Controller**.

- **The Hardware Bridge:** The DMA controller is a specialized chip on the motherboard. Instead of the CPU doing the copying, it simply sends a command to the DMA controller: _"Copy 1GB from Disk X to RAM Location Y, and send me an interrupt when you are done."_ The CPU is then free to immediately return to executing program code while the DMA controller handles the heavy lifting in the background.
- **The Addressing Problem (No MMU):** Because the DMA controller sits completely outside the CPU, it does not have access to the CPU's Memory Management Unit (MMU). It does not know what a "virtual address" is. The software must translate the request and give the DMA controller raw, literal **Physical Addresses**.
- **The Swapping Danger (Pinned Memory):** This creates a massive danger with Virtual Memory. If the DMA is actively streaming a file into `Physical Frame 100`, the OS _cannot_ be allowed to swap that frame to the hard drive. If it did, the OS might assign that frame to another program, and the blind DMA controller would immediately overwrite and corrupt the new program's data. Therefore, any kernel memory allocated for a DMA transfer must be strictly **pinned** (locked), preventing the OS from ever swapping or paging it out until the transfer is complete.
- **The Modern Fix (IOMMU):** In modern hardware, managing contiguous physical addresses for massive peripherals (like a heavy GPU or high-speed Network Card) is incredibly difficult due to physical fragmentation. To fix this, modern motherboards include an **IOMMU (Input/Output Memory Management Unit)**.
    - Just like the CPU's MMU translates virtual memory for software, the IOMMU translates memory for hardware peripherals. It allows devices to safely use virtual addresses for DMA transfers, providing them with the exact same isolation, security, and fragmentation-solving benefits that standard programs enjoy!

#### Pros and Cons

**The Advantages:**

- **Massive Transfer Efficiency:** By creating a direct hardware bridge between peripherals (like an SSD or Network Card) and physical RAM, DMA allows gigabytes of data to stream at the maximum speed of the hardware bus, completely bypassing the CPU's internal buffer bottleneck.
- **Zero CPU Overhead:** Because the CPU delegates the copying task entirely to the DMA controller, it frees up billions of CPU cycles. The processor can continue executing application logic, rendering graphics, or handling network requests in parallel while the memory transfer happens in the background.
- **No Virtual Memory Overhead:** Traditional DMA operates strictly on raw physical addresses. This means it completely skips the latency of the MMU, Page Table Walks, and TLB lookups, resulting in raw hardware speed.

**The Trade-offs:**
- **The Setup Penalty (Initialization Cost):** Delegating a task to the DMA controller is not free. The CPU must assemble commands, translate addresses, and configure DMA registers. For sufficiently large transfers, this setup cost can be outweighed by reduced CPU involvement; for small copies, CPU copying can take less time.
- **Small, Frequent Events:** Because setup has a cost, DMA is generally not used for small, frequent, latency-sensitive events such as a keystroke or mouse movement. For a few bytes, direct CPU handling commonly has lower latency.
- **Security & Complexity Risks:** A traditional DMA controller is "blind." Because it bypasses the CPU's MMU isolation, a malicious or buggy hardware peripheral could accidentally overwrite kernel memory or corrupt the physical RAM of a completely different application. This immense security vulnerability is exactly why modern systems are forced to implement the highly complex IOMMU hardware to sandbox these peripherals.

#### DMA Attacks

Because traditional Direct Memory Access (DMA) operates purely on physical addresses and bypasses the CPU's MMU (Memory Management Unit), it implicitly trusts the hardware peripheral. A **DMA Attack** occurs when an attacker exploits this trust by plugging a malicious device into a high-speed external port to instantly read or overwrite the computer's physical RAM.

- **The Attack Vector (Thunderbolt & PCIe):** Ports like USB 2.0 or standard HDMI do not have direct access to system memory. However, high-bandwidth interfaces like **Thunderbolt, FireWire, and external PCIe** are essentially direct extensions of the motherboard's internal bus. If an attacker plugs a disguised, malicious device into one of these ports, the hardware is often automatically granted DMA privileges.
- **Bypassing the Operating System:** Because the malicious device talks directly to the physical RAM via the DMA controller, the Operating System is completely blind to the attack. The OS cannot log the event, antivirus software cannot scan it, and lock screens cannot block it.
- **The Impact (Total System Compromise):**
       - **Key Extraction:** The attacker can instruct the device to silently read the physical memory to find full-disk encryption keys (like BitLocker or FileVault) or plain-text passwords stored in RAM.
    - **Code Injection:** The device can overwrite kernel memory space to inject a malicious [[../Security/01 Foundations and Risk/03 Common Threats and Attacks#Rootkits|rootkits]] or instantly disable the operating system's lock screen password check.

To prevent someone from completely compromising a locked laptop just by plugging a rogue device into a Thunderbolt port, hardware and software engineers had to combine forces:
- **The Hardware Sandbox (IOMMU):** As mentioned earlier, the IOMMU (Input/Output Memory Management Unit) acts as a bouncer for hardware devices. Instead of letting a Thunderbolt device see raw physical RAM, the IOMMU forces the device to use virtual addresses. If the malicious device tries to read memory outside its strictly assigned sandbox, the IOMMU blocks the request at the hardware level.
- **Kernel DMA Protection:** Modern operating systems (like Windows 10/11 and macOS) utilize the IOMMU to implement strict DMA protection policies. By default, the OS will completely block DMA access for any newly plugged-in Thunderbolt or PCIe device until the user successfully unlocks the computer and authorizes the peripheral.

## Memory Pressure Stall Information (PSI)

Memory PSI ([`/proc/pressure/memory`](06%20Storage%20Management.md#%60/proc%60%20%E2%80%94%20Process%20and%20Kernel%20Information)) measures the time threads spend stalled waiting for the OS to organize RAM—such as waiting for page faults, page reclaims, or swapping to disk. It goes beyond simply asking "How much RAM is free?" by measuring actual performance degradation.

Unlike the [CPU](04%20Inside%20The%20CPU.md#CPU%20Pressure%20Stall%20Information), Memory PSI tracks two distinct metrics:

- **`some` (Partial Starvation):** At least one thread is stalled waiting for memory operations, but the CPU is still executing other threads. The system is "thrashing" slightly (swapping or clearing page cache), which hurts latency, but the app is surviving.
- **`full` (Total Lockup):** **ALL** runnable threads are stalled waiting for memory. The CPU has absolutely no work to do and is sitting idle.

**The OOM Danger Zone:** If the `full` metric spikes and stays high for more than a few seconds, it means the entire system has deadlocked waiting for RAM. The Linux kernel will panic and trigger the **OOM (Out of Memory) Killer**, terminating processes to forcefully reclaim memory pages and unfreeze the system.
