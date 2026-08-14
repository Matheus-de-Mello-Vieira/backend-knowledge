
# Process Management

Process management is the heartbeat of the operating system. It is the complex machinery responsible for creating, scheduling, isolating, and terminating programs. It is the exact system that creates the illusion that a computer with only 8 physical CPU cores can flawlessly run 400 applications simultaneously.

- **The Kernel as Orchestrator:** The kernel acts as the secure gatekeeper and traffic controller. It ensures no single process monopolizes the CPU, corrupts another program's memory, or touches the physical hardware directly.
- **The Illusion of Concurrency:** To achieve multitasking, the kernel rapidly swaps processes on and off the CPU cores. This happens in milliseconds, requiring incredibly precise coordination between software (the OS scheduler) and hardware (the CPU registers and interrupts).
- **Scheduling & Fairness:** Determining exactly which runnable process gets CPU time next, on which specific hardware core, and for exactly how long (timeslicing).

## Core Mechanics

- **The Process Lifecycle:** The transition of a program through distinct states: `Created` -> `Ready` (waiting in line for a CPU) -> `Running` (actively executing on a core) -> `Blocked` (waiting for an external event) -> `Terminated`.
- **Context Switching:** The physical act of evicting a process from the CPU. The kernel must pause execution, save the exact state of the CPU's registers (Instruction Pointer, Stack Pointer, Flags) into the PCB, and load the saved registers of the next process. This heavy computational overhead is why thread-thrashing destroys application performance.
- **Blocking vs. Runnable:** If a process needs to wait for a network packet or a slow disk read, the OS moves it to a `Blocked` state. It is immediately evicted from the CPU core so another program can use the hardware, consuming zero CPU cycles until a hardware interrupt wakes it back up.
- **System Calls:** When user-space code needs a privileged action (like `read()`, `fork()`, or `exec()`), it triggers a hardware trap. The CPU pauses the application, elevates its privilege level (Ring 0), and hands control to the kernel to safely execute the requested work.

## Processes vs. Threads

To understand how the kernel manages work, you must separate the concept of _resources_ from the concept of _execution_.

- **The Process (The Container)**: A process is the ultimate resource container.
       - By itself, a process doesn't actually "do" anything; it is simply the bounded, isolated environment in which code runs.
              - It holds the isolated virtual memory space—which is strictly divided into its own dedicated **code, data, heap, and stack sections**—along with the Per-Process File Descriptor Table and the [Process Control Block](#The%20Process%20Control%20Block%20(PCB)).  
- **The Thread (The Execution)** A thread is the actual active unit of execution.
       - Every process starts with exactly one main thread, but it can spawn dozens of child threads.
       - The OS scheduler does not actually schedule processes; it schedules _threads_ onto physical CPU cores.
       - All threads within a single process share [exact same memory](#Multi-Threaded%20Memory%20Layout) and open files, but each thread is given its own isolated Stack and CPU Registers (like the Program Counter).
### The Process Control Block (PCB)

The Process Control Block (in Linux, known as the `task_struct`) is the definitive data structure representing a process inside the operating system. It is the kernel's internal ledger tracking every single detail about a process's state, memory boundaries, and security permissions.

When a Context Switch occurs, this is exactly where the kernel saves the CPU registers.

**What the PCB Contains:**

- **Identification & Security:** Process ID (PID), Parent Process ID (PPID), and the User/Group IDs that dictate what the process is allowed to touch.
- **Execution State:** The current state of the process (Runnable, Blocked, Stopped, Zombie), the saved Program Counter (PC), and the saved CPU registers from the last time it was evicted from the CPU.
- **Scheduling & Accounting:** CPU priority levels, total CPU time consumed, and memory usage limits.
- **Memory Management:** Pointers defining the boundaries of the process's specific Code, Data, Heap, and Stack sections. Crucially, it holds the pointer to the process's **Page Table**, which the MMU uses to translate its virtual memory into physical RAM.
- **I/O and Resources:** The Per-Process [File Descriptors (FDs)](02%20The%20Anatomy%20of%20a%20Process.md#File%20Descriptors%20(FDs)) table, tracking all open files, network sockets, and pipes.
- **Inter-Process Communication (IPC):** Metadata tracking any semaphores, mutexes, shared memory segments, or message queues the process is currently using to talk to other processes.

### The Kernel Process Table

Because a system might have thousands of active processes, the kernel cannot search through them one by one. It organizes them using the **Kernel Process Table**.

- **The Mapping:** It is a highly optimized kernel-space data structure (functioning like a hash map) that maps a numeric **PID to its specific PCB**.
- **O(1) Lookups:** This allows the OS scheduler and system calls to find a process instantly.
- **Real-World Example:** If you type `kill -9 4052` in your terminal, the kernel immediately checks the Process Table for PID `4052`, retrieves its PCB, checks if your user has the security permissions to modify it, and then forcefully changes its execution state to Terminated.

## Threads

### Why We Use Threads

If a process is perfectly isolated, why do we spawn threads inside it instead of just spinning up entirely separate processes?

- **Multi-Core Parallelism:** If a single-threaded process runs on an 8-core CPU, 7 cores sit completely idle. By spawning 8 threads, the OS can assign one thread to each physical CPU core, allowing the application to execute machine instructions simultaneously and divide heavy mathematical workloads.
- **Hiding I/O Latency:** If a single-threaded application requests a file from the disk, the entire process is moved to a `Blocked` state and execution halts. With multiple threads, Thread A can sit blocked waiting for the database to respond, while Thread B continues executing code on the CPU to serve the UI or process a different user's request.
- **Instant Data Sharing:** Because threads live inside the exact same Process container, they share the same physical RAM. Thread A can calculate a result, save it to a variable, and Thread B can read that exact same variable on the next clock cycle. If you used two separate _processes_, their memory would be strictly isolated, forcing you to use complex and slow Inter-Process Communication (IPC) pipes.
- **Cheaper Context Switches:** Switching the CPU from Thread A to Thread B (if they belong to the same process) is physically faster than switching between two entirely different processes. Because the threads share the same virtual memory, the kernel does not have to flush the CPU's MMU or swap out the Page Tables, dodging a massive performance penalty.
- **Shared Sockets for High-Throughput Connection Acceptance:** Because threads exist within the exact same process container, they inherently share system resources, including the Per-Process File Descriptor Table. This means all threads have access to the exact same array of open files and network sockets. This shared access enables backend architectures to utilize the [Multiple Threads, Single Shared Socket](02%20Execution%20Patterns.md#3.%20Multiple%20Threads,%20Single%20Shared%20Socket)" pattern, where multiple worker threads can actively compete to call `accept()` on one shared listening socket. Leveraging threads in this way is highly effective for increasing throughput when an application needs to process a large volume of small tasks, such as accepting massive numbers of incoming network connections.

### Multi-Threaded Memory Layout

- **The Single-Thread Illusion:** The classic memory layout—where the Stack starts at the absolute maximum address and grows downwards toward the Heap—technically represents a purely single-threaded process.
- **The Collision Problem:** Because threads within the same process share the exact same virtual memory space, they cannot all share the Main Thread's top-level Stack. If they did, their independent Last-In, First-Out (LIFO) function frames would instantly collide and corrupt one another.
- **Parachuting Stacks via `mmap`:** To provide each newly spawned thread with its own isolated execution state, the kernel utilizes the `mmap` system call. It allocates new, fixed-size blocks of memory and parachutes them directly into the massive gulf of empty virtual addresses residing in the "middle space" between the upward-growing Heap and the Main Thread's Stack.
- **Guard Pages (Preventing Silent Corruption):** While any `mmap` allocation can suffer from a software [buffer overflows](02%20The%20Anatomy%20of%20a%20Process.md#Buffer%20Overflow), stacks are uniquely dangerous because their growth is implicit. The CPU hardware blindly decrements the Stack Pointer (`sp`) as functions are called, never checking if memory limits have been reached. Because these mapped thread stacks float dangerously close to one another in virtual memory, the OS places a Read/Write-protected [**Guard Page**](02%20The%20Anatomy%20of%20a%20Process.md#Stack%20Overflow) at the absolute bottom of each thread's block. Just like the Main Thread's boundary, if a runaway thread's `sp` hits this hardware tripwire, the MMU triggers an instant Segmentation Fault, killing the process before it can silently overwrite an adjacent thread's function frames.
- **Resource Sharing:** Because threads exist _within_ the same parent process, they inherently share almost all system resources, completely bypassing the need for complex Inter-Process Communication (IPC) like pipes or shared `mmap` files.
    - **Shared:** All threads within a process read from the exact same Text/Code segment, the Data/BSS segments (global variables), the Heap (dynamic memory), and the File Descriptor array.
    - **Isolated:** Each thread must maintain its own independent execution state. Therefore, the OS allocates every thread its own private **Stack** memory (to track its own function calls and local variables) and saves its own dedicated copy of the CPU registers (including its own Instruction Pointer, Base Pointer, and Stack Pointer).

### User-Space Threads (Green Threads & Coroutines)

Besides **OS threads**, also commonly called **native threads**, **kernel threads**, or **system threads**, applications and language runtimes can maintain their own **user-space execution units** and multiplex them over a smaller number of OS threads. Depending on the runtime and programming model, these may be called **Green Threads**, **Fibers**, **Coroutines**, or **Virtual Threads**. These terms are related but not completely interchangeable—for example, a coroutine does not necessarily behave like a thread.

- **Multiplexing Over OS Threads:** The operating system only schedules the underlying native threads. A runtime may internally manage thousands of user-space tasks and decide which one executes whenever one of its OS threads receives CPU time.

- **User-Space Scheduling:** Because the runtime controls these execution units, switching between them can often happen without invoking the kernel scheduler. The runtime saves whatever execution state its abstraction requires and resumes another task on the same OS thread. The exact state depends on the implementation: some abstractions have their own stacks and resumable execution state, while others, such as stackless coroutines, are represented differently.

- **Lower Per-Task Memory Cost:** Every native thread requires its own stack and kernel bookkeeping. Native thread stacks commonly reserve a relatively large **virtual address range**, but this does not mean the entire reservation is immediately backed by physical RAM—the MMU allows the stack to appear contiguous while its physical pages are allocated and mapped as needed. User-space runtimes can still be more memory-efficient because their execution units can start with much smaller stacks, use dynamically growing stacks, or avoid dedicated stacks entirely depending on the model.

- **Lower Scheduling Overhead:** Native threads are managed by the kernel scheduler, so switching between them involves kernel-maintained scheduling and execution state. Switching between user-space tasks can often be handled entirely by the runtime, avoiding a kernel scheduling operation. This makes very large numbers of concurrent tasks more practical than creating the same number of native OS threads.

- **Blocking Depends on the Runtime Model:** If many user-space tasks are multiplexed onto a single OS thread, a synchronous blocking system call can block that OS thread and prevent the other tasks assigned to it from executing. Event-loop systems therefore rely heavily on non-blocking I/O. More sophisticated runtimes can multiplex tasks across multiple OS threads and compensate when one underlying thread blocks, although some operations can still temporarily pin or occupy an OS thread.

### The Thread Control Block (TCB)

Just as the kernel uses a PCB to track an entire process, it uses a **Thread Control Block (TCB)** to track the individual threads executing inside that process. Because the OS scheduler actually dispatches _threads_ to the CPU cores, the TCB holds the precise metadata needed to pause, resume, and prioritize that specific thread.

**What the TCB Contains:**

- **Identification:** The Thread ID (TID) and a direct pointer back to the parent's Process Control Block (PCB).
- **Execution State:** The current state of the thread (Runnable, Blocked, Stopped), the saved Program Counter (PC), and the specific CPU registers last used by this thread.
- **Scheduling & Accounting:** The thread's individual priority level and its specifically consumed CPU time.
- **Parent PCB Pointer:** A direct link back to the parent's Process Control Block. Because the TCB is intentionally lightweight, it uses this pointer whenever the thread needs to access shared resources owned by the process—such as allocating memory on the Heap, looking up a memory address in the Page Table, or writing to an open File Descriptor.
- **Memory Management:** A pointer to the thread's isolated, dedicated **stack**.

### The Kernel Thread Table

Because a single operating system might be running 5,000 threads distributed across 500 processes, the OS scheduler needs a way to manage them all efficiently.

- **The Mapping:** Similar to the [process table](#The%20Kernel%20Process%20Table), this is a highly optimized kernel-space data structure that maps a numeric **TID to its specific TCB**.
- **Quick Lookup:** It provides an O(1) lookup mechanism. When a hardware interrupt wakes up a blocked thread, or the scheduler needs to pick the next task to run, it uses the Thread Table to instantly find the TCB, check its priority, and load its saved registers onto the CPU core.

## Context Switching

A CPU core does not understand a **process** as a hardware concept. It simply executes instructions using whatever execution state is currently loaded into its registers. The operating system creates the abstraction around that execution: a **process** owns resources and a virtual address space, while a **thread** represents the execution state that can actually be scheduled onto a CPU core.

A thread's **context** is the information required to pause it and later resume it exactly where it stopped. This primarily includes CPU registers such as the Program Counter / Instruction Pointer (`pc` / `ip`), Stack Pointer (`sp`), Base/Frame Pointer (`bp`), general-purpose registers, and status/flags registers. The process also provides the address-space context, especially the page-table root used by the MMU to translate virtual addresses into physical memory.

During a context switch, the kernel saves the outgoing thread's execution state, chooses another runnable thread, restores that thread's saved state, and resumes execution from its saved Instruction Pointer. If the new thread belongs to a different process, the kernel must also activate that process's virtual address space.

### Context Switching Overhead

- **Thread Switch Within the Same Process (Usually Cheaper):** Threads in the same process share the same virtual address space and page tables. The kernel mainly needs to save and restore thread-specific state such as registers and the Stack Pointer, while the MMU can continue using the same address-space mapping.
- **Switch Between Different Processes (Usually More Expensive):** In addition to restoring the new thread's registers, the kernel must switch to the destination process's page-table context. This can reduce the effectiveness of cached address translations in the **TLB**, because translations belonging to the previous process may no longer be useful.
- **CPU Caches Are Not Explicitly Flushed:** A context switch does not normally clear the L1, L2, or L3 caches. However, the incoming thread may use a completely different set of instructions and data. As it runs, its working set can replace the previous thread's cache lines, causing additional cache misses. This loss of **cache locality** contributes significantly to context-switch overhead.

Therefore, the distinction between a "process switch" and a "thread switch" is mainly about whether the virtual address space also changes. The scheduler fundamentally switches **execution contexts**, but switching between threads that share the same process is usually cheaper because less memory-management state needs to change.

#### TLB Behavior

Historically, switching from one process to another often required flushing the **Translation Lookaside Buffer (TLB)**. The TLB caches recent virtual-to-physical address translations, but without additional metadata the CPU cannot distinguish which process a cached translation belongs to. Since two processes can use the same virtual address while mapping it to completely different physical pages, retaining the previous process's TLB entries would be unsafe.

Modern CPUs reduce this overhead by tagging TLB entries with an **address-space identifier**. Different architectures use different names for this mechanism: ARM commonly uses **ASID (Address Space Identifier)**, while x86 uses **PCID (Process-Context Identifier)**.

Instead of the TLB effectively storing only `virtual address → physical address`, it stores something conceptually closer to `address-space identifier + virtual address → physical address`

When the OS switches to another process, it changes the active address-space identifier together with the page-table context. The MMU then only considers TLB entries associated with the currently active address space. This allows translations from multiple processes to coexist in the TLB and avoids many full TLB flushes during context switches.

These identifiers must remain relatively small because they are stored alongside TLB entries, and increasing their width increases hardware area, power usage, and lookup complexity. As a result, the number of available identifiers is finite.

When the identifier space is exhausted, the operating system eventually has to **reuse** an identifier. Before assigning it to a different address space, the OS must ensure that stale TLB entries carrying the same identifier cannot be mistaken for translations belonging to the new process. This may require invalidating those entries or using a generation/versioning mechanism. Therefore, address-space tagging significantly reduces the frequency of TLB flushes, but it does not eliminate TLB invalidation entirely.

### When Context Switches Happen

A context switch happens whenever the currently running thread stops using the CPU and the scheduler decides that another runnable thread should execute instead. This can happen for several reasons:

- **Scheduling Decisions:** The scheduler may choose another runnable thread according to the operating system's scheduling policy, such as priority, fairness, CPU affinity, or accumulated CPU time.
- **Preemptive Multitasking:** In a preemptive operating system, a running thread does not control the CPU indefinitely. A periodic timer interrupt gives control back to the kernel, which may decide that the thread's time slice has expired and preempt it in favor of another runnable thread.
- **I/O Wait:** If a thread performs a blocking operation, such as waiting for disk, network, or user input, it cannot make progress on the CPU. The kernel moves it into a blocked/waiting state and schedules another runnable thread. When the I/O operation completes, an interrupt or kernel event wakes the blocked thread and makes it runnable again.

A context switch can therefore be triggered either because the **scheduler takes the CPU away from a thread** or because the **thread voluntarily stops being runnable**, for example by blocking on I/O or waiting for synchronization.
#### Scheduling Algorithms

The scheduler decides **which runnable thread executes on which CPU core and for how long**. Designing a good scheduling policy is difficult because the operating system must balance competing goals such as fairness, responsiveness, throughput, latency, and efficient CPU utilization.

Modern operating systems normally schedule **threads**, rather than processes directly. The scheduler may also consider where a thread previously executed. Running a thread again on the same core can preserve **cache and TLB locality**, because some of its instructions, data, and address translations may still be available close to that core. This tendency is known as **CPU affinity**.

However, locality is only one objective. If several threads from the same process can execute independently, spreading them across different cores may provide true parallelism. The scheduler therefore balances locality against load distribution and parallel execution.

Some classic scheduling algorithms include:

- **First-Come, First-Served (FCFS):** Runnable tasks execute in the order they arrive. It is simple, but a long-running task can delay every task behind it.
- **Shortest Job First (SJF):** The task expected to require the least CPU time runs first. This can minimize average waiting time, but the operating system usually cannot know a task's future execution time precisely.
- **Round Robin (RR):** Each runnable task receives a fixed **time slice**. When its slice expires, the scheduler preempts it and gives another task a turn. This improves fairness and responsiveness but introduces additional context-switch overhead.

Real operating systems usually use more sophisticated scheduling policies that combine ideas such as priorities, time slicing, CPU affinity, fairness, and workload history rather than relying on a single simple algorithm.
#### Cooperative vs. Preemptive Multitasking

- **Cooperative multitasking** relies on the running thread voluntarily giving control of the CPU back to the operating system, usually by yielding, blocking, or reaching some point where the program allows another task to run. If a program fails to yield—for example, because it enters an infinite loop or performs a long computation—other tasks may receive little or no CPU time.
- **Preemptive multitasking** gives the operating system control over how long a thread can execute. A timer interrupt periodically returns control to the kernel, allowing the scheduler to preempt the running thread, save its context, and execute another runnable thread. Because the operating system does not depend on applications voluntarily yielding, one CPU-bound program cannot normally monopolize a CPU core indefinitely.

Modern general-purpose operating systems primarily use preemptive multitasking, although threads can still voluntarily yield or block when they do not need the CPU.

> [!example] Windows 3.1  
> Windows 3.1 used cooperative multitasking between 16-bit Windows applications. Applications were expected to periodically yield control, commonly while processing their message loop. If an application entered an infinite loop or performed a long-running computation without yielding, other applications could stop receiving CPU time and the graphical environment could appear frozen.
### Thread Prioritization

When multiple threads are **runnable** at the same time, the scheduler must decide which one should receive CPU time. One of the inputs to that decision is **priority**.

A higher-priority thread is generally favored over a lower-priority one, although the exact meaning of "priority" depends on the operating system and scheduling policy. Priority does not reserve a CPU core or guarantee continuous execution. If a high-priority thread blocks on I/O, a mutex, or another event, it stops being runnable and the scheduler can execute another thread.

Priority is closely related to **preemption**. Under priority-based scheduling policies, when a sufficiently higher-priority thread becomes runnable, the scheduler may preempt the currently executing thread, save its context, and switch the CPU to the higher-priority thread.

#### Windows

Windows gives each process a **priority class**, such as `IDLE`, `NORMAL`, `ABOVE_NORMAL`, `HIGH`, or `REALTIME`. Each thread also has its own priority level. Windows combines these values to determine the thread's base scheduling priority.

For example, selecting **High** for a process in Task Manager changes the process's priority class. The scheduler still schedules individual threads, but the threads belonging to that process generally receive higher base priorities and are therefore favored when competing with lower-priority runnable threads.

This should be used carefully: a CPU-bound high-priority process can reduce the CPU time available to ordinary applications, while real-time priorities can interfere with important system work.

#### Linux

Linux exposes a similar idea differently. For ordinary time-sharing workloads, a thread has a **nice value** ranging from `-20` to `+19`:

- `-20` → higher scheduling preference
- `0` → default
- `+19` → lower scheduling preference

Despite the name, a "higher" nice value actually means the task is being **nicer to other tasks**, so the scheduler gives it a smaller share of CPU time when there is contention.

For example:

`nice -n 10 ./program`

starts a program with a lower scheduling preference than the default. Conversely, decreasing the nice value gives the task a greater share of CPU time, although increasing priority is normally restricted by permissions.

Linux also provides separate **real-time scheduling policies**, such as `SCHED_FIFO` and `SCHED_RR`, whose threads take precedence over ordinary time-sharing tasks. These policies are conceptually closer to strict priority scheduling and must be used carefully because a CPU-bound real-time thread can starve ordinary work.

## Concurrency and Parallelism

Parallelism is executing multiple tasks simultaneously across separate cores. Concurrency is managing multiple tasks by interleaving their execution to create the illusion of parallelism. However, both demands the art/science of split your program into processes or threads.

### 