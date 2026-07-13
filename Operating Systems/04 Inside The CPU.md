# Inside The CPU

The CPU is where instructions actually execute. To understand performance, context switching, and low-level code behavior, it helps to treat the CPU as a small hierarchy of execution hardware rather than a single black box.

## Core execution pieces

- **Registers:** The fastest storage in the machine. They hold the values the current instruction is actively using.
- **Instruction Pointer (`IP` / `PC`):** Tracks the virtual address of the next instruction to execute. For process-level context, see [The Anatomy of a Process](02%20The%20Anatomy%20of%20a%20Process.md#Process%20Execution%20and%20State).
- **ALU:** Executes arithmetic and logical operations on register values.
- **Control Unit:** Decodes instructions and orchestrates how data moves between registers, caches, memory, and execution units.
- **MMU:** Translates virtual addresses into physical addresses using page-table metadata managed by the operating system.

## Cache hierarchy

- **L1 Cache:** Smallest and fastest cache, typically private to a single core.
- **L2 Cache:** Larger and slightly slower, still commonly private to a core.
- **L3 Cache:** Larger shared cache used to reduce expensive trips to DRAM.
- **Cache coherency:** Because multiple cores may cache the same memory line at once, the hardware must coordinate updates and invalidate stale copies.

## Why this matters

- **Instruction cost is not uniform:** Different instructions consume different numbers of cycles.
- **Data locality dominates performance:** Keeping frequently used data in registers and caches is dramatically cheaper than pulling it from DRAM.
- **Low-level execution leaks upward:** Compiler behavior, context switches, lock contention, and memory layout all eventually show up as CPU work.

For the broader hardware overview, cache diagram, and boot-chain context, see [System Architecture Overview](00%20System%20Architecture%20Overview.md#CPU).
