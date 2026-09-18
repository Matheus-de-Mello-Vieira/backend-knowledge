# GPU

A **GPU (Graphics Processing Unit)** is a throughput-oriented processor designed to apply the same mathematical operations across massive amounts of data in parallel. GPUs were originally developed to calculate geometry, lighting, and pixel colors for computer graphics, but the same architecture also maps naturally to scientific computing, video processing, and machine-learning workloads dominated by large amounts of vector and matrix math.

## CPU vs. GPU: Latency and Throughput

CPUs and GPUs optimize for different goals; neither is universally faster.

- **CPU:** Optimizes for **low-latency execution** of relatively small numbers of complicated instruction streams. It dedicates substantial silicon to [Branch Prediction](04%20Inside%20The%20CPU.md#Branch%20Prediction%20&%20Speculative%20Execution), [deep cache hierarchies](04%20Inside%20The%20CPU.md#The%20Cache%20Hierarchy), sophisticated [instruction pipelines](04%20Inside%20The%20CPU.md#The%20Instruction%20Life%20Cycle%20&%20Pipelining), and other control machinery.
- **GPU:** Optimizes for **high throughput**. It dedicates much more of the chip to mathematical execution units so enormous numbers of similar operations can proceed in parallel.

This trade-off makes a GPU highly specialized rather than inherently faster.

- Workloads with large amounts of independent, repetitive computation can keep thousands of execution units busy and benefit enormously from the architecture.
- Sequential dependencies, irregular memory access, and unpredictable branching leave much of the GPU's parallel hardware idle and may execute more efficiently on a CPU.

Both architectures use parallelism and concurrency to keep execution resources busy. CPUs invest more hardware in making a relatively small number of complex instruction streams progress quickly, whereas GPUs devote more resources to keeping a much larger number of similar operations in flight. Most of their architectural differences follow from this trade-off.

## GPU Hardware Architecture

A CPU core contains sophisticated machinery intended to keep a small number of instruction streams moving as quickly as possible. Replicating that entire structure thousands of times would consume enormous amounts of silicon with control logic rather than computation. GPU architecture instead simplifies much of the per-thread control machinery and uses the reclaimed chip area for a much larger number of mathematical execution units.

On NVIDIA GPUs, these units are organized into **Streaming Multiprocessors (SMs)**. Rather than treating every software thread as an independently scheduled hardware execution engine, each SM manages many threads collectively. It combines replicated execution units with Warp Schedulers, a large banked physical register file, Shared Memory / L1 Cache, and the control logic needed to coordinate them. ALUs and FPUs perform computation; the register file holds the private logical register state of many resident threads and supplies operands when Warp instructions execute.

```mermaid
flowchart TD
    subgraph SM["Streaming Multiprocessor (SM)"]
        WS["Warp Schedulers"]
        RF["Banked Physical Register File"]
        MEM["Shared Memory / L1 Cache"]

        subgraph EU["Execution Units"]
            direction LR
            A1["ALU"]
            A2["ALU"]
            A3["ALU"]
            A4["ALU"]
            F1["FPU"]
            F2["FPU"]
            F3["FPU"]
            F4["FPU"]
        end

        WS --> EU
        RF <--> EU
        MEM <--> EU
    end
```

- **Streaming Multiprocessor (SM):** NVIDIA's main computational building block. An SM contains Warp Schedulers, many mathematical execution units, a large banked physical register file, Shared Memory / L1 Cache, and the control logic needed to keep many Warps resident and coordinate their execution. A complete GPU contains many SMs operating in parallel.
- **Warp Scheduler:** Selects which Warp should execute. GPU threads are grouped into fixed-size Warps, so the scheduler issues instructions for groups rather than scheduling each thread as an independent hardware instruction stream.
- **Arithmetic Logic Units (ALUs):** Perform integer arithmetic and bitwise operations using the same basic principles as [CPU execution units](04%20Inside%20The%20CPU.md). GPUs contain large numbers of these units so similar calculations can occur across many elements simultaneously.
- **Floating-Point Units (FPUs):** Perform floating-point arithmetic. Graphics, scientific simulation, and machine learning rely heavily on this kind of math, so GPUs dedicate significant computational capacity to floating-point operations.
- **Registers:** An SM contains a large banked physical register file shared as a hardware resource among its resident threads. Each logical GPU thread has private register state, but its values physically occupy part of this SM-level capacity. Warp instructions read operands from the register file and write their results back to it.
- **Shared Memory / L1 Cache:** Low-latency SRAM close to the execution units. Besides normal caching behavior, software can explicitly manage Shared Memory so threads in the same cooperative group can rapidly exchange and reuse data; in CUDA, this cooperation is scoped to a **Thread Block**.
- **Global Memory (VRAM):** The GPU's primary large-capacity memory. It provides much more storage than on-chip memories but has substantially higher access latency, so efficient access patterns are critical to performance.

## GPU Execution Model

The **GPU execution model** describes the logical abstractions through which software expresses parallel work, whereas the hardware architecture describes the physical resources that perform it.

- **Hardware resources:** Streaming Multiprocessors, Warp Schedulers, execution units, registers, and caches.
- **Logical work:** Kernels, Grids, Thread Blocks, and GPU threads.

The runtime and GPU hardware map logical work onto physical resources during execution.

**CUDA terminology** provides a concrete representation of this hierarchy because CUDA exposes kernels, Grids, Thread Blocks, threads, and Warps explicitly. Other GPU programming systems use related abstractions and may give them different names, but the broad distinction between logical work and physical execution remains useful.

### Kernel and Kernel Launch

A **GPU kernel** is a function designed to execute across many GPU threads. The programmer writes the operation from one logical thread's perspective, then launches the kernel across a larger collection of threads so the same code operates on many pieces of data.

> [!note] GPU Kernel vs. OS Kernel
>
> In GPU programming, a **kernel** is computational code submitted to the GPU for parallel execution. This meaning is unrelated to the **operating-system kernel**, which is privileged system software responsible for managing processes, memory, devices, and other system resources.

CUDA marks a GPU kernel with `__global__`. This kernel doubles one array element for each logical thread:

```cpp
__global__ void double_values(float *values, int count) {
    int thread_id = blockIdx.x * blockDim.x + threadIdx.x;

    if (thread_id < count) {
        values[thread_id] = values[thread_id] * 2;
    }
}
```

A **kernel launch** creates the logical work that executes this function in parallel. CUDA expresses its launch configuration as:

```cpp
kernel<<<number_of_blocks, threads_per_block>>>(...);
```

The launch does not create one heavyweight hardware execution engine for every thread. Instead, it defines a logical hierarchy of parallel work that is later mapped onto available GPU hardware.

### Grid and Thread Blocks

A kernel launch creates a **Grid**: the complete collection of threads participating in that launch. The Grid is divided into **Thread Blocks**, each containing a fixed number of GPU threads chosen by the program.

For example:

```cpp
double_values<<<4, 256>>>(values, 1024);
```

This creates one Grid containing **4 Thread Blocks with 256 threads each**, for a total of `4 × 256 = 1024` logical GPU threads.

A **Thread Block** is more than an organizational unit. Threads in the same block can cooperate through Shared Memory and block-level synchronization. CUDA assigns each block to one SM for its lifetime, although an SM can keep multiple blocks resident simultaneously when registers, Shared Memory, thread slots, and other resources permit it.

The Grid and Thread Block hierarchy partitions a large parallel computation into groups that the GPU can distribute across its SMs.

### GPU Threads

A **GPU thread** is the smallest programmer-visible execution context in this hierarchy. Each thread represents one logical execution of the kernel and conceptually has its own identifiers, register values, local variables, and instruction state.

GPU threads are not operating-system threads. The OS does not independently schedule thousands of GPU threads onto CPU-like cores; GPU threads are much lighter logical contexts that GPU hardware later groups together for execution.

In `double_values()`, each thread computes its global index:

```cpp
int thread_id = blockIdx.x * blockDim.x + threadIdx.x;
```

- `threadIdx.x` identifies the thread within its Thread Block.
- `blockIdx.x` identifies the block within the Grid.
- `blockDim.x` gives the number of threads in each block.

Combining these values gives each logical thread a different array index. Every thread can therefore execute the same scalar kernel body while operating on a different element.

At the programming-model level, a **kernel launch creates a Grid, the Grid contains Thread Blocks, and each Thread Block contains GPU threads**. During execution, the hardware groups those logical threads into Warps.

### Warps and Their Lifecycle

When a Thread Block is assigned to an SM, the hardware allocates the resources needed by that block, including registers, Shared Memory, and execution-state slots. It then organizes the block's threads into fixed-size hardware execution groups called **Warps**. On NVIDIA CUDA hardware, each Warp contains 32 threads.

After allocation, the Warps are **resident** on the SM. Residency means the hardware has enough state available to keep a Warp on the SM; it does not mean that the Warp executes continuously or that its next instruction can execute immediately.

A resident Warp becomes **eligible** when its next instruction has no unresolved dependency preventing issue. The Warp Scheduler selects among eligible Warps, subject to the availability of the required execution pipeline, and issues instructions to the appropriate execution units. After issue, a Warp may remain eligible for another instruction or become temporarily unable to continue.

An unresolved data dependency commonly makes a Warp ineligible:

```cpp
float value = values[thread_id];
float result = value * 2;
```

The multiplication depends on the value loaded by the first instruction. If the load must reach Global Memory, the requested data may take many cycles to arrive. The Warp remains resident on the SM during that time, but cannot issue the dependent multiplication, so it is **stalled** or **ineligible**.

The hardware tracks dependencies and makes the Warp eligible again when the required result becomes available. Warps can similarly become ineligible while waiting for synchronization or other dependencies. Because their execution state remains resident throughout these stalls, changing to another eligible Warp does not require saving and restoring an operating-system-style thread context.

The main resident and schedulability conditions are:

- **Resident:** Hardware resources and execution state have been allocated to the Warp on the SM.
- **Eligible:** The Warp is resident and its next instruction has no blocking dependency.
- **Stalled / Ineligible:** The Warp remains resident but cannot currently issue its next instruction because a required dependency is unresolved.

A Warp reaches its terminal **completed** condition when it has finished execution.

A Warp can alternate between eligible and stalled states many times during its lifetime. Once all Warps in a Thread Block have completed, the block's resources can be released and the SM can admit additional work.

### Single Instruction, Multiple Threads (SIMT)

Warps are the hardware execution groups through which GPUs implement **SIMT — Single Instruction, Multiple Threads**. SIMT is closely related to [SIMD](04%20Inside%20The%20CPU.md#Single%20Instruction,%20Multiple%20Data%20(SIMD)), but the programming model exposes parallelism differently.

- **CPU SIMD:** Explicitly packs several values into a wide vector register and applies one vector instruction to those values.
- **GPU SIMT:** Presents many logical scalar threads to the programmer and lets hardware organize those threads into Warps.

When a Warp is eligible and selected, the Warp Scheduler issues an instruction for its active threads. Those threads execute the same instruction against their respective registers and data, allowing one instruction issue to drive parallel computation across many logical threads.

The programmer describes many independent thread executions, while the GPU groups them into Warps, keeps many Warps resident on each SM, and repeatedly selects eligible Warps for execution. Executing another Warp while one is stalled is one of the main mechanisms GPUs use to hide latency.

### GPU Occupancy

**Occupancy** describes how much of an SM's capacity for resident Warps is currently used. It is commonly expressed as the ratio of active resident Warps to the maximum number of Warps the SM can support.

Physical resources limit the number of resident Warps. Every Thread Block and Warp consumes registers, Shared Memory, thread slots, and other execution-state resources. A kernel that requires more resources per thread or block leaves less capacity for additional Warps.

For example, if an SM supports at most 64 resident Warps but a kernel's resource requirements allow only 32 Warps to be resident, its occupancy is `32 / 64 = 50%`.

A larger pool of resident Warps gives the Warp Scheduler more opportunities to find an **eligible** Warp while others are stalled. If only a few Warps are resident and all wait for memory or another dependency, the SM may have no useful instruction to issue even though its execution units are available.

Higher occupancy therefore helps with **latency hiding**, but maximum occupancy is not itself the goal. A kernel may perform better with lower occupancy if each thread uses more registers to avoid expensive memory accesses or if the workload already provides enough eligible Warps to keep execution units busy.

> [!note] Occupancy vs. Utilization
>
> **Occupancy** describes how much Warp execution state is resident on an SM, whereas **utilization** describes how busy the execution hardware actually is.
>
> High occupancy increases the amount of work available to the scheduler, but it does not guarantee high utilization or maximum performance.

### Branch Divergence

SIMT works most efficiently when all active threads in a Warp follow the same instruction path. Conditional logic becomes expensive when threads evaluate the same condition differently because a Warp cannot freely execute two unrelated instruction streams at the same time.

```c
if (value > 0) {
    do_a();
} else {
    do_b();
}
```

If some threads take the `True` branch and others take the `False` branch, the hardware uses **masking**:

1. It executes one branch while temporarily disabling threads that follow the other path.
2. It changes the mask and executes the other branch.
3. It reconverges the Warp.

For example, Threads 0–15 might take the `True` branch while Threads 16–31 take the `False` branch. The hardware runs the `True` threads with the `False` threads masked, then runs the `False` threads with the `True` threads masked before reconverging.

The result remains logically correct, but some execution lanes are idle while each branch runs. This is **Branch Divergence**. Highly irregular control flow can therefore dramatically reduce SIMT efficiency: when all threads take the same path, the hardware remains fully aligned; as paths diverge, execution becomes increasingly serialized.

> [!note] When a Conditional Is Cheap
>
> A conditional does not necessarily cause a meaningful performance penalty. Branch divergence occurs only when active threads within the same Warp take different paths. If all threads in a Warp make the same decision, they remain aligned and there is no divergence penalty.
>
> The `if (thread_id < count)` bounds check in `double_values()` is usually inexpensive because `thread_id` increases consecutively. Almost every Warp evaluates the condition uniformly; only the Warp that crosses the `count` boundary may contain both threads that execute the body and threads that do not. For `count = 1000` with 1024 launched threads, only the final Warp diverges: threads `992–999` execute the body while threads `1000–1023` do not.
>
> Data-dependent conditions such as `if (values[thread_id] > 0)` are more likely to make threads diverge across many Warps and therefore have a larger performance impact.

## GPU Memory Hierarchy

Massive arithmetic capacity is useful only when data can reach the execution units quickly enough. For many GPU workloads, performance is therefore constrained less by the raw speed of mathematical operations than by the cost of **moving data** through the memory hierarchy.

GPU memory follows the same capacity-versus-latency trade-off as [CPU memory hierarchies](03%20Memory%20Management.md): Registers and Shared Memory sit directly beside the execution hardware but have limited capacity, whereas Global Memory provides much more storage at substantially higher latency.

### Registers

**Registers** are the fastest storage available to GPU threads. They hold operands, addresses, intermediate results, and other values actively used during execution. Compiled GPU instructions ultimately read and write registers as operands, much like CPU machine instructions.

Each logical thread has private register values, while physical storage for those values comes from the SM's banked physical register file. Before a Thread Block can become resident, the SM must have enough register-file capacity for the registers required by all of that block's threads.

Two allocation details follow from this finite SM-level pool:

- **Capacity calculation:** A kernel requiring 32 registers per thread and a block containing 256 threads conceptually requires `32 × 256 = 8192` register values. Real hardware allocates registers with architecture-specific granularity, but every resident thread still consumes part of the finite pool.
- **Allocation and initialization:** Capacity is reserved before the block becomes resident, but registers do not all need useful values at that point. Values are produced and consumed incrementally as instructions execute. When a load receives data from memory, for example, it writes the result into storage already allocated to the thread; a later dependent instruction can read that register.

The compiler determines a thread's **register demand** largely from the values that must remain simultaneously available during execution. Higher per-thread demand consumes more of the SM's finite register file and can reduce the number of Thread Blocks and Warps that remain resident at the same time, lowering Occupancy.

If a thread's register demand cannot be satisfied by the available register allocation, some values may be **spilled into thread-private memory backed by slower levels of the GPU memory hierarchy**. These accesses may be served by caches, but can ultimately reach device memory and are therefore substantially more expensive than register accesses.

CUDA calls this thread-private address space **local memory**. Other GPU architectures and programming models expose the same general mechanism under different names, such as private or scratch memory.

### Shared Memory / L1 Cache

**Shared Memory** is a small, low-latency memory space located on the SM and explicitly accessible by threads within a Thread Block. Because a Thread Block remains assigned to one SM for its lifetime, its threads can use that SM's Shared Memory to exchange and reuse data.

Unlike an ordinary CPU or GPU cache, whose contents and eviction decisions are automatically managed by hardware, Shared Memory is managed by the program. Threads can cooperatively load data from VRAM into Shared Memory, synchronize, and then reuse or exchange those values without repeatedly accessing Global Memory.

On some GPU architectures, Shared Memory and the L1 cache use the same underlying on-chip SRAM, but they serve different logical roles: **L1 automatically caches memory accesses, while Shared Memory acts as a programmer-controlled scratchpad.**

### Global Memory / VRAM

**Global Memory**, commonly called **VRAM**, is the GPU's main high-capacity memory pool. Although it has much greater access latency than registers or Shared Memory, GPU memory systems compensate by providing very high **bandwidth**, allowing large amounts of data to move in parallel.

Technologies such as GDDR and HBM are designed around this need for bandwidth. However, a wide memory interface alone is insufficient: software must access memory in patterns the hardware can combine efficiently. The layout of data and the addresses requested by neighboring threads are therefore central to GPU performance.

### Memory Coalescing

Threads inside a Warp maintain independent logical contexts, so they are technically free to request unrelated addresses. When neighboring threads access neighboring data, the memory controller can combine those requests into a smaller number of large transfers. This optimization is **memory coalescing**.

A favorable pattern maps neighboring threads to neighboring elements:

| Thread | Requested element |
| --- | --- |
| 0 | `array[0]` |
| 1 | `array[1]` |
| 2 | `array[2]` |
| … | … |
| 31 | `array[31]` |

Because the requested addresses belong to a contiguous region, the memory hardware can service them efficiently. A Warp that accesses widely scattered addresses loses that opportunity and may require many separate memory transactions.

| Thread | Requested element |
| --- | --- |
| 0 | `array[10]` |
| 1 | `array[9000]` |
| 2 | `array[31]` |
| 3 | `array[700000]` |

The program remains correct in both cases, but the second pattern makes much poorer use of the available memory bandwidth. Coalescing is closely related to [Spatial Locality](03%20Memory%20Management.md#Spatial%20Locality): both reward software for organizing related accesses close together, although the GPU applies the principle across the simultaneous memory requests of a Warp.

## Host–Device Data Transfer

A discrete GPU and the CPU normally operate from different physical memory pools. The CPU primarily accesses system RAM, while the GPU primarily accesses its own VRAM. The devices communicate through an interconnect such as PCIe, so data stored in system RAM may need to cross that interconnect before a GPU kernel can operate on it.

This cost is separate from the GPU's internal memory hierarchy. Registers, Shared Memory, caches, and VRAM determine how efficiently a running kernel accesses data already available to the GPU. Host-to-device transfers determine how expensive it is to place that data there in the first place.

Integrated GPUs differ because the CPU and GPU may share the same physical memory rather than maintaining separate RAM and VRAM pools. They can therefore avoid some explicit copies, although synchronization, cache coherence, and memory-access costs still remain.

### DMA and Pinned Memory

Large transfers between system RAM and GPU memory normally use [Direct Memory Access (DMA)](03%20Memory%20Management.md#Direct%20Memory%20Access%20(DMA)). Instead of making the CPU execute instructions that copy every byte through its own registers, the transfer is configured and the GPU or a dedicated copy engine performs the bulk data movement.

DMA requires the device to have stable access to the physical memory backing the transfer. Ordinary pageable memory does not provide that guarantee indefinitely because the operating system remains free to reclaim, swap, or migrate its backing pages.

**Pinned (Page-Locked) Memory** keeps the required pages resident and stable while the device accesses them. The GPU can then perform DMA against those pages without requiring the CPU to copy every byte itself.

Transfers involving ordinary pageable memory may require additional preparation before DMA can proceed. The runtime or driver may temporarily pin the pages or copy data through an internal pinned staging buffer.

That preparation creates a trade-off for application-provided pinned memory:

- **Repeated transfer throughput:** Avoiding those extra operations can improve repeated high-throughput transfers.
- **Memory pressure:** Pinned pages cannot be reclaimed as freely as ordinary pageable memory, so pinning excessive amounts of RAM reduces the operating system's ability to respond to memory pressure.

### Device-Memory TCP Receive

Pinned memory enables the conventional DMA transfer from host memory to a discrete GPU, but it does not remove every host-memory hop. When an application receives TCP data for GPU processing, the NIC normally DMA-writes the packet into host memory, the kernel processes the TCP connection, and the application receives the payload into a host buffer before transferring it to GPU memory. For bulk accelerator traffic, that staging path consumes host-memory and PCIe bandwidth even when the host has no need to inspect the payload.

Linux **Device Memory TCP** (devmem TCP) removes that payload-staging step for a specialized receive path. The application exposes device memory as a DMA-BUF, binds it to a NIC receive queue, and opts in when receiving from the [TCP socket](07%20Socket%20Management.md#Receiving%20Data). A compatible NIC then splits each packet: its headers go to host memory for normal TCP/IP processing, while DMA writes the payload into the bound device buffer. The receive operation returns metadata identifying the buffer region, which the application returns after use so the NIC can reuse its finite buffer space.

This path changes where payload bytes land, not TCP's transport responsibilities:

- **Kernel processing remains necessary:** TCP still uses the host-resident headers to maintain connection state, sequence data, and perform its normal transport processing.
- **Hardware and queue setup are required:** The NIC must support header splitting, and the receiving flow must be steered to a queue bound to the DMA-BUF. Data can fall back to ordinary host-memory delivery when a packet cannot be split at its header boundary.
- **Payload inspection is constrained:** Because the payload remains in device memory, kernel components that need to read it, such as software checksumming, packet capture, or BPF payload inspection, cannot process that payload through the usual path.
- **The benefit is workload-dependent:** Avoiding the host-memory staging copy reduces pressure on host-memory bandwidth and on PCIe paths through the root complex. It matters most for large device-to-device transfers, such as distributed accelerator workloads, rather than for small transfers whose setup and synchronization costs dominate.

> [!note] Linux-Specific Interface
>
> Device Memory TCP is a Linux implementation for TCP sockets, not a general property of DMA or TCP. It requires driver, NIC, DMA-BUF, and application support; a regular TCP application continues to receive payload bytes through ordinary user-space buffers.

### The Transfer Penalty

GPU acceleration must be evaluated across the complete operation rather than by comparing kernel execution time alone. Suppose transferring the input takes `100 ms`, GPU computation takes `2 ms`, and transferring the result back takes `20 ms`. The complete operation takes `122 ms`, even though the kernel itself executes in only `2 ms`.

A GPU therefore provides the greatest benefit when enough computation is performed to amortize the cost of reaching the device. Large workloads that move data once and reuse it repeatedly in VRAM can benefit substantially, while small operations that continually transfer inputs and outputs across PCIe may spend more time moving data than computing.

Keeping reusable data on the GPU can consequently be as important as optimizing the kernel itself. Eliminating an unnecessary host/device transfer may save more time than reducing an already-small kernel execution time.

## GPU and the Operating System

A GPU is a shared hardware resource whose ownership and protection are controlled by the operating system. An application running in [user space](09%20Kernel%20and%20User%20Space.md#Privilege%20Boundary) cannot freely manipulate privileged GPU state or grant itself unrestricted access to device resources because doing so could interfere with other processes or the operating system.

GPU software therefore commonly includes:

- an application-facing runtime or API;
- user-space driver components; and
- a kernel-space [device driver](99%20More%20OS%20Concepts.md#Device%20Drivers).

The exact division depends on the operating system and GPU vendor. Operations that do not require privilege can remain in User Space, while the kernel driver controls operations that require authority over the physical device.

This division avoids placing every GPU operation behind a User Space / Kernel Space transition. Privileged software establishes a protected execution environment, after which user-space software and the GPU can perform large amounts of ordinary work without requiring the kernel to mediate every GPU instruction.

### GPU Contexts and Resource Ownership

When a process uses the GPU, the software stack creates a **GPU context** or equivalent execution state associated with that process. The context represents the process's use of GPU resources, including address mappings, execution state, and other device-specific resources.

Contexts allow multiple processes to use the same physical GPU while retaining separate logical environments. A process can therefore submit kernels and allocate GPU memory without being given unrestricted access to resources belonging to another process.

This resembles CPU process isolation, although the GPU maintains its own execution state rather than directly using the CPU's process context.

### GPU Virtual Memory

A CPU process operates within an isolated [virtual address space](03%20Memory%20Management.md#The%20Solution:%20Virtual%20Address%20Space%20%26%20MMU%20Isolation). Modern GPUs apply a similar principle to device-accessible memory.

GPU instructions generally use virtual addresses that GPU memory-management hardware translates into physical VRAM or other accessible memory. The driver establishes the mappings associated with each GPU context, allowing different processes to have independent GPU address spaces while sharing the same physical device.

Two processes may therefore use the same numerical GPU virtual address while having it resolve to different physical memory, just as the same CPU virtual address can refer to different physical RAM in different processes.

These mappings also enforce protection. A kernel executing within one context can access memory mapped into that context but should not be able to freely address VRAM or other resources belonging to another process.

### User Space and Kernel Space

The kernel driver remains responsible for operations requiring privileged control of the GPU, including:

- creating protected contexts;
- establishing memory mappings;
- coordinating ownership among processes;
- handling hardware faults and interrupts; and
- resetting or recovering the device when necessary.

Higher-frequency work can remain in User Space once those protected resources have been established. Runtime and user-space driver code can prepare kernels, descriptors, commands, and other execution state without repeatedly requiring privileged access.

The same operating-system principle therefore applies to the GPU as to other hardware: **Kernel Space establishes and protects access to the device, while User Space performs ordinary work within the boundaries that the kernel has created.**

## GPU Work Submission and Scheduling

Preparing a valid GPU execution environment does not itself execute a kernel. The CPU must submit work to the GPU, after which the device uses its own scheduling mechanisms to execute that work independently.

This creates multiple scheduling layers:

1. The operating system's CPU scheduler decides when the application's CPU threads execute.
2. Those threads prepare and submit GPU work.
3. The GPU schedules submitted work across its hardware, eventually assigning Thread Blocks to SMs and selecting eligible Warps for instruction issue.

CPU scheduling and Warp scheduling are therefore separate mechanisms operating at different levels.

### Command Queues and Streams

GPU work is submitted as commands describing operations such as kernel launches, memory transfers, and synchronization points. Rather than requiring the CPU to directly initiate every low-level GPU action, these commands are placed into queues that the device can consume independently.

- **Queue:** Represents submitted GPU operations waiting or ready to execute.
- **Stream:** In many GPU APIs, represents an ordered sequence of operations whose dependencies can be coordinated.

Ordering matters because some operations depend on previous results. A kernel that consumes data produced by an earlier memory transfer, for example, cannot safely execute before that transfer has completed. Independent operations, however, may be able to overlap when the hardware and programming model permit it.

Once a kernel reaches GPU execution, the scheduling hierarchy described earlier takes over: Thread Blocks are assigned to SMs, their Warps become resident, and Warp Schedulers repeatedly select eligible Warps for instruction issue.

### Asynchronous Execution

GPU submissions are commonly **asynchronous**. The CPU can enqueue work and continue executing without waiting for the GPU to finish immediately.

This independence allows CPU and GPU execution to overlap. While the GPU performs a long computation, the CPU may prepare another batch, process network requests, perform unrelated calculations, or submit additional GPU work.

Asynchronous submission does not remove dependencies. It merely delays the point at which the CPU must wait until a result is actually required.

### Synchronization

Suppose the CPU spends `20 ms` preparing and submitting GPU work. The GPU then requires `80 ms` to perform the computation, while the CPU has `50 ms` of unrelated work available.

```mermaid
gantt
    title Overlapping CPU and GPU Execution
    dateFormat x
    axisFormat %L ms
    tickInterval 20millisecond

    section CPU
    Prepare and submit     :cpu_prepare, 0, 20ms
    Independent CPU work   :cpu_work, 20, 50ms
    Synchronize / Wait     :crit, cpu_wait, 70, 30ms
    Consume GPU result     :cpu_result, 100, 20ms

    section GPU
    Waiting for submission :done, gpu_idle, 0, 20ms
    GPU computation        :gpu_work, 20, 80ms
```

The GPU begins computing at `20 ms`, while the CPU immediately proceeds with its independent work. Both processors therefore perform useful work simultaneously between `20 ms` and `70 ms`.

At `70 ms`, the CPU reaches an operation that requires the GPU's result. The GPU still has `30 ms` of computation remaining, so the CPU can no longer continue along that dependency and must **synchronize**.

Once the GPU completes at `100 ms`, the dependency is satisfied and the CPU can continue consuming the result.

The important distinction is between **submission and dependency**. Submission gives the GPU work to perform and allows the CPU to continue independently. Synchronization occurs only when one side reaches a dependency whose required work has not yet completed.

Efficient GPU programs therefore try to expose enough independent CPU and GPU work that execution can overlap, while postponing synchronization until the dependency actually requires it.

## GPU Programming APIs and Platforms

Applications do not normally target GPU execution units directly. They use a **programming API, runtime, or compute platform** to write kernels or shaders, manage memory, and submit work to the GPU. These interfaces sit above the driver and hardware mechanisms described earlier, but expose different abstractions and target different vendors and workloads.

Terms such as **CUDA**, **Vulkan**, and **Metal** name software interfaces rather than GPU architectures. They expose related underlying ideas—device memory, command queues, synchronization, kernels or shaders, and parallel execution—through different programming models.

### CUDA

**CUDA** is NVIDIA's GPU computing platform and programming model. It is designed primarily for general-purpose computation on NVIDIA GPUs and exposes kernels, Grids, Thread Blocks, threads, Warps, streams, Shared Memory, and explicit device-memory management.

CUDA extends languages such as C and C++ with GPU-specific syntax, including `__global__` kernel declarations and `<<<...>>>` launch configuration.

The CUDA runtime translates these high-level operations into commands understood by the NVIDIA driver, which then submits them to the GPU.

CUDA exposes NVIDIA's hardware model relatively directly. **Warps** and **Thread Blocks** are CUDA-specific terms and do not appear under those names in every GPU API.

### Vulkan

**Vulkan** is a cross-vendor, low-level graphics and compute API maintained by the Khronos Group. Unlike CUDA, it is not primarily a general-purpose numerical-computing platform; it was designed to give applications explicit control over modern GPU rendering and compute workloads.

- **Resources:** Command buffers, queues, memory allocations, synchronization primitives, and compute pipelines.
- **Compute work:** Usually expressed through **compute shaders**, compiled into an intermediate representation such as **SPIR-V**, then submitted through the general command infrastructure also used for graphics operations.
- **Explicit control:** Applications perform much of the resource management and synchronization that higher-level runtimes might otherwise hide. This can reduce driver overhead and give the programmer more control, but increases implementation complexity.

### Metal

**Metal** is Apple's graphics and compute API for Apple GPUs. It fills a role similar to Vulkan or Direct3D within the Apple ecosystem, exposing graphics pipelines, compute kernels, command queues, buffers, textures, and synchronization through a relatively low-level interface.

Because Apple controls the operating system, GPU architecture, driver stack, and API, Metal can be tightly integrated with Apple hardware. On systems with unified memory, CPU and GPU data may reside in the same physical memory rather than requiring the explicit RAM-to-VRAM copies typical of discrete GPUs.

Metal compute kernels use terminology that differs from CUDA, but the underlying execution concepts remain related: many logical threads execute the same kernel over different data and hardware groups them for parallel execution.

### Other GPU Compute Interfaces

Several other interfaces expose similar capabilities with different portability and abstraction goals:

- **OpenCL:** A Khronos standard for heterogeneous computation across GPUs, CPUs, and other accelerators. It provides a vendor-neutral kernel and memory model, although it generally exposes less vendor-specific hardware detail than CUDA.
- **ROCm and HIP:** ROCm is AMD's GPU computing software ecosystem. HIP provides a CUDA-like C++ programming model and can make it easier to write code targeting AMD and NVIDIA GPUs.
- **Direct3D / DirectCompute:** Provide graphics and general compute capabilities through Microsoft's DirectX ecosystem on Windows. Compute shaders use the same GPU-pipeline infrastructure as other Direct3D workloads.
- **SYCL:** Provides a higher-level C++ programming model for heterogeneous computing. SYCL implementations can map code onto backends such as CUDA, HIP, OpenCL, or other accelerator runtimes.

These systems differ in portability, supported hardware, language model, and degree of control, but all transform programmer-defined parallel work into memory operations and commands that a GPU driver can submit to the device.

CUDA therefore provides a useful concrete vocabulary for studying GPU execution. Kernels, groups of cooperating threads, device memory, asynchronous queues, and synchronization are broader GPU-computing ideas that appear across APIs under different names.

## Tensor Processing Units (TPUs)

A **TPU (Tensor Processing Unit)** is an application-specific integrated circuit (**ASIC**) developed by Google for machine-learning workloads. A CPU sacrifices computational density for general-purpose flexibility, while a GPU sacrifices some flexibility for much greater parallel throughput. A TPU specializes further around operations that dominate neural networks, especially **matrix multiplication and multiply-accumulate operations**.

This specialization lets a TPU dedicate a much larger fraction of its hardware to tensor computation instead of the more general execution machinery required by CPUs and GPUs.

### Matrix Multiplication Units

Each output value in matrix multiplication accumulates products of corresponding input values. Its innermost operation is:

```c
sum += a * b;
```

This is a **multiply-accumulate (MAC)** operation. Neural networks perform enormous numbers of MAC operations in matrix multiplications, convolutions, attention projections, and other tensor transformations.

- **CPU:** Executes these operations through general-purpose scalar or SIMD execution units.
- **GPU:** Provides many more execution units and concurrently executes large numbers of related operations.
- **TPU:** Uses specialized **Matrix Multiply Units (MXUs)**: large arrays of multiply-accumulate units physically connected to one another.

The important difference is not merely the number of multipliers. Their connections let intermediate values move directly between neighboring computational units rather than repeatedly returning to a general-purpose register file or memory hierarchy.

### Systolic Arrays

An MXU uses a **systolic array**: data enters an array of multiply-accumulate units, flows progressively through neighboring units, and each unit performs part of the matrix computation before forwarding values or partial results.

For matrix multiplication, values loaded into the array participate in many MAC operations as they move through the hardware. The data therefore receives substantial computational reuse without an independent memory access for every multiplication.

This addresses a central limitation of GPU execution: **moving operands can be as expensive as performing the arithmetic itself**. A GPU mitigates the problem with registers, caches, Shared Memory, coalescing, and high-bandwidth VRAM. A systolic array instead builds data reuse into the physical path through which computation executes.

The trade-off is flexibility. A systolic array is extremely efficient when a computation matches its matrix-oriented structure, but is not intended to efficiently execute arbitrary programs with complicated branches, pointer chasing, system calls, or unrelated scalar operations.

### Matrix, Vector, and Scalar Execution

A TPU is not composed exclusively of matrix units. Modern TPU architectures contain several kinds of execution hardware with different responsibilities:

- **MXU:** Performs the dense matrix multiplications that account for much of neural networks' computational cost.
- **Vector unit:** Handles operations applied independently across vectors of values, including activation functions, normalization, and other element-wise transformations.
- **Scalar unit:** Handles smaller scalar calculations, address generation, control flow, and supporting operations.
- **Specialized hardware:** Some TPU generations also contain hardware for workloads such as sparse embedding lookups.

This division resembles the broader CPU/GPU principle of assigning operations to different execution units, but the balance is much more heavily biased toward machine-learning tensor operations.

> [!note] TPU TensorCore vs. NVIDIA Tensor Core
>
> Google uses **TensorCore** for a major computational component inside a TPU containing MXUs, vector units, and scalar units.
>
> This differs from NVIDIA **Tensor Cores**, specialized matrix-multiplication execution units inside NVIDIA GPUs. The names are similar, but they identify components in different architectures.

### Reduced Precision

Machine-learning workloads frequently do not require every multiplication to use full 32-bit floating-point precision. TPUs exploit this by providing very high throughput for lower-precision numerical formats.

For example, TPU matrix units commonly use **bfloat16** for multiplication while accumulating results at higher precision such as FP32. Lower-precision operands require less storage, memory bandwidth, and physical circuitry per operation, allowing more arithmetic to proceed in parallel.

This is another form of specialization: the hardware is designed around precision characteristics that neural-network training and inference can tolerate rather than arbitrary numerical software.

### Memory and Data Reuse

TPUs still require a memory hierarchy because model weights, activations, and intermediate tensors cannot all remain inside the MXU. Cloud TPU systems use high-bandwidth memory (**HBM**) to hold large tensors close to the processor.

Performance depends on supplying computational units with enough data. A matrix operation that repeatedly waits for HBM cannot fully use the MXU's enormous arithmetic throughput.

The systolic architecture raises **arithmetic intensity** after data reaches the matrix unit. Rather than loading two operands, performing one multiplication, storing a result, and repeating the entire memory process, values flow through many multiply-accumulate units and participate in many operations before leaving the array.

The same principle behind GPU matrix tiling is therefore even more central to TPU design: **the more useful computation performed for each value fetched from memory, the better the hardware can exploit its arithmetic capacity.**

### Compiler-Driven Execution

TPUs are usually programmed at a higher level than CUDA-style GPU kernels. A machine-learning program may express an operation simply as:

```python
C = A @ B
```

Frameworks such as JAX or PyTorch can represent that operation as part of a larger computational graph. The **XLA compiler** then transforms the graph into operations suitable for the TPU.

XLA can perform operation fusion, memory-layout selection, and matrix tiling so computations fit the TPU's execution units efficiently. Rather than manually assigning individual TPU execution units, the programmer relies on the compiler to map high-level tensor operations onto MXUs, vector units, the memory system, and communication infrastructure.

TPU performance therefore depends strongly on the compiler seeing and optimizing sufficiently large regions of computation. Awkward tensor shapes, excessive reshaping, frequent host interaction, or computation dominated by non-matrix operations may fail to keep MXUs fully utilized.

### Scaling Across TPU Chips

Large machine-learning models can exceed one accelerator's computation and memory capacity. Cloud TPU systems therefore connect multiple TPU chips with high-bandwidth inter-chip interconnects.

- A collection of interconnected TPU chips forms a **TPU slice**.
- Much larger configurations can form part of a **TPU Pod**.
- Training can distribute tensors, model parameters, or batches across chips so one computation uses many accelerators simultaneously.

At this scale, performance depends on communication as well as matrix-computation throughput. If chips frequently need data produced by other chips, the interconnect becomes part of the critical path, just as memory bandwidth or PCIe transfers can constrain a single accelerator.

### CPU vs. GPU vs. TPU

The three architectures occupy progressively different positions in the flexibility-versus-throughput trade-off:

- **CPU:** Optimized to quickly execute a relatively small number of complicated and irregular instruction streams. It provides the greatest general-purpose flexibility.
- **GPU:** Optimized to execute enormous numbers of similar operations concurrently while remaining programmable for graphics, scientific computing, machine learning, and many other parallel workloads.
- **TPU:** Optimized much more specifically around tensor computation, particularly matrix multiplication and other operations common in machine-learning models.

A large neural-network matrix multiplication maps efficiently to all three architectures at different scales: a CPU uses multiple cores and SIMD, a GPU distributes work across many parallel execution units and specialized matrix hardware, and a TPU maps much of the computation directly onto large systolic matrix units.

Increasing specialization makes performance advantages conditional. A TPU can provide enormous throughput when a workload spends most of its time in large tensor operations, but it is poorly suited to general operating-system workloads, branch-heavy application logic, irregular pointer chasing, or small computations that do not meaningfully use its matrix units.

A TPU is therefore not universally faster. It is an example of **domain-specific architecture**: restricting the kinds of computation hardware executes efficiently allows more chip area and power to concentrate on the operations that matter most for that domain.

## Workload Alignment

Whether a GPU outperforms a CPU depends on whether the computation's structure matches the hardware. GPUs benefit most from large numbers of independent operations that follow similar instruction paths and access memory regularly. CPUs are generally stronger when execution has sequential dependencies, unpredictable branches, irregular memory access, or too little work to amortize GPU submission and data-transfer overhead.

The distinction becomes clearer through concrete workloads.

### Element-Wise Array Operations

Consider multiplying every element of an array by two:

```c
for (int i = 0; i < count; i++) {
    output[i] = input[i] * 2;
}
```

Every iteration is independent: calculating `output[500]` does not depend on `output[499]`. Each iteration also performs the same operation on neighboring memory locations.

A CPU can exploit this with [SIMD](04%20Inside%20The%20CPU.md#Single%20Instruction,%20Multiple%20Data%20(SIMD)), processing several values with one vector instruction. Conceptually, an optimized CPU loop may behave like:

```c
for (int i = 0; i < count; i += SIMD_WIDTH) {
    vector x = load(&input[i]);
    vector y = x * 2;
    store(&output[i], y);
}
```

A GPU exposes much more parallelism by assigning different elements to different logical threads:

```cpp
__global__ void double_values(float *input, float *output, int count) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;

    if (i < count) {
        output[i] = input[i] * 2;
    }
}
```

Thousands of these threads can be in flight simultaneously. Threads in each Warp also access neighboring array elements, producing favorable memory coalescing.

For a sufficiently large array already present in GPU memory, this maps extremely well to a GPU. For an array containing only a few hundred elements, a CPU may finish the loop before GPU-work submission becomes worthwhile.

### Matrix Multiplication

Matrix multiplication exposes much more computation per output value. For matrices `A`, `B`, and `C`, each element of `C` combines one row of `A` with one column of `B`.

A straightforward CPU implementation is:

```c
for (int row = 0; row < M; row++) {
    for (int col = 0; col < N; col++) {
        float sum = 0;

        for (int k = 0; k < K; k++) {
            sum += A[row][k] * B[k][col];
        }

        C[row][col] = sum;
    }
}
```

Each addition in the innermost loop contributes to the same `sum`, creating a dependency within that loop. Different output elements remain largely independent, however: `C[0][0]`, `C[0][1]`, `C[1][0]`, and thousands of other elements can be calculated concurrently.

A simple GPU mapping assigns one thread to each output element:

```cpp
__global__ void matmul(
    float *A,
    float *B,
    float *C,
    int M,
    int N,
    int K
) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;

    if (row < M && col < N) {
        float sum = 0;

        for (int k = 0; k < K; k++) {
            sum += A[row * K + k] * B[k * N + col];
        }

        C[row * N + col] = sum;
    }
}
```

If `C` contains millions of elements, this mapping creates millions of logical thread executions performing highly similar arithmetic.

Matrix multiplication also has high **arithmetic intensity**: each piece of data can participate in many arithmetic operations. Optimized implementations load tiles of the matrices into Shared Memory or caches and reuse them many times rather than repeatedly fetching the same values from VRAM.

This combination makes large matrix multiplication one of the strongest GPU workloads:

- Massive independent work
- Predictable control flow
- Regular memory access
- High data reuse

Modern GPUs also contain specialized matrix hardware, such as Tensor Cores, that can increase this advantage further.

CPUs still perform matrix multiplication efficiently with SIMD, caches, multiple cores, and optimized libraries such as BLAS. The GPU advantage becomes strongest when matrices are large enough to occupy substantial portions of the GPU and amortize host/device-transfer and submission costs.

### Reductions

A reduction combines many input values into a smaller result, such as a sum:

```c
float sum = 0;

for (int i = 0; i < count; i++) {
    sum += values[i];
}
```

This appears sequential because every iteration updates `sum`. Addition can instead be reorganized into independent partial sums: different workers sum different portions of the array, then combine those results.

A CPU can divide the array among cores:

```c
partial[0] = sum(values[0:250000]);
partial[1] = sum(values[250000:500000]);
partial[2] = sum(values[500000:750000]);
partial[3] = sum(values[750000:1000000]);

sum = partial[0] + partial[1] + partial[2] + partial[3];
```

A GPU can create a much larger number of partial reductions, combining values first within threads, then within Thread Blocks, and eventually across blocks.

The workload is parallel, but less trivially parallel than an element-wise operation because workers must eventually **synchronize and combine intermediate results**. GPUs can still perform large reductions extremely efficiently, but the synchronization and reduction stages prevent perfect independence.

For small reductions, CPU execution is often preferable because the available parallelism is insufficient to justify GPU overhead.

### Branch-Heavy Logic

Consider processing records whose behavior depends strongly on their contents:

```c
for (int i = 0; i < count; i++) {
    if (records[i].type == TYPE_A) {
        process_a(records[i]);
    } else if (records[i].type == TYPE_B) {
        process_b(records[i]);
    } else {
        process_other(records[i]);
    }
}
```

The iterations may be independent, but independence alone does not make a workload ideal for a GPU.

When neighboring GPU threads encounter different record types, threads in the same Warp follow different execution paths and cause Branch Divergence. Some execution lanes become inactive while the hardware processes paths required by other threads.

A CPU is built specifically for this kind of irregular execution. [Branch Prediction](04%20Inside%20The%20CPU.md#Branch%20Prediction%20&%20Speculative%20Execution), speculative execution, out-of-order execution, and large caches let a CPU core devote substantial hardware resources to advancing a complicated instruction stream quickly.

The GPU has traded much of this sophisticated per-thread machinery for a much larger number of arithmetic execution units. Highly unpredictable control flow therefore attacks the trade-off on which GPU throughput depends.

### Pointer Chasing

Linked structures create another difficult GPU workload:

```c
Node *node = head;

while (node != NULL) {
    process(node->value);
    node = node->next;
}
```

The address of the next load is unknown until the current node has been loaded. The processor must load the current node, obtain `node->next`, and only then issue the load for the next node. Future addresses cannot all be requested in advance.

This creates a sequential memory dependency: the processor cannot issue all node accesses simultaneously because future addresses have not yet been discovered.

If thousands of GPU threads independently traverse unrelated linked structures, their addresses are also likely to be scattered throughout memory. Warps then lose memory coalescing and generate many unrelated memory transactions.

CPUs are generally better suited to this latency-sensitive pointer chasing because they dedicate more hardware to cache hierarchies, speculative execution, out-of-order execution, and accelerating a relatively small number of irregular instruction streams.

The same problem appears in many tree traversals, graph algorithms, hash-table lookups, and object-heavy data structures.

### Large Batches and Single Requests

The amount of available parallel work can be as important as the operation itself.

Suppose a model evaluates one input through a sequence of matrix operations. The computation may be mathematically suitable for a GPU, but one small request may not expose enough work to use thousands of execution units efficiently.

Combining many inputs into a batch changes the size of the underlying operations:

```python
# One item
output = model(input)

# Many independent items
outputs = model(batch_of_inputs)
```

The underlying operations become larger matrix computations. Weights can be reused across many inputs, memory transfers can be amortized, and substantially more GPU execution units can remain occupied.

This is why GPU systems frequently rely on **batching**. The algorithm does not change; the amount of parallel work exposed to the hardware changes.

A latency-oriented CPU may therefore be preferable for isolated small requests, while the same computation becomes strongly GPU-oriented when requests accumulate into sufficiently large batches.

### Small Workloads and Fixed Overhead

Even a perfectly parallel operation can be slower on a GPU when the workload is too small.

Consider adding two numbers:

```c
result = a + b;
```

A GPU can perform the addition, but using it may require preparing a command, submitting work, scheduling a kernel, synchronizing, and potentially transferring data between host and device. The CPU can execute the addition directly with a few instructions.

The same effect applies to somewhat larger workloads. A computation may eventually become faster on the GPU, but only after enough work accumulates to overcome the GPU's fixed overhead.

There is therefore usually a **crossover point**, not a universal rule that one processor is faster.

### Practical CPU vs. GPU Comparison

The practical difference depends on the work presented to the processor:

- **Large matrix multiplication:** Usually strongly favors the GPU because it contains enormous amounts of regular, reusable arithmetic.
- **Large element-wise array operations:** Usually favor the GPU when data is already on the device, although CPUs also exploit SIMD effectively.
- **Large reductions:** Often favor the GPU, but require synchronization and hierarchical combination of partial results.
- **Large batches of similar independent requests:** Favor the GPU because batching exposes more parallel work and amortizes fixed costs.
- **Complex branch-heavy business logic:** Usually favors the CPU because execution paths are irregular and difficult to keep aligned across Warps.
- **Linked lists, trees, and irregular pointer chasing:** Usually favor the CPU because accesses are dependent and difficult to coalesce.
- **Small computations:** Usually favor the CPU because GPU submission and transfer costs can exceed the computation itself.
