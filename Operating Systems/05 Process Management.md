# Process Management

Process management is the part of the operating system responsible for creating, scheduling, pausing, resuming, and terminating running programs.

## Responsibilities

- **Scheduling:** Decide which runnable process or thread gets CPU time next.
- **State tracking:** Keep per-process metadata such as PID, memory limits, open resources, and execution state.
- **Isolation:** Prevent one process from directly corrupting another process's memory or hardware state.
- **Resource mediation:** Coordinate access to CPU time, memory, storage, and I/O devices through kernel-controlled interfaces.

## Core mechanics

- **Process lifecycle:** A process is created, becomes runnable, may block waiting for I/O, resumes when the event arrives, and eventually exits.
- **Context switching:** When the kernel swaps one running task for another, it must save CPU register state and restore a different one. This is why excessive switching is expensive.
- **Blocking vs runnable:** A process waiting on disk, network, or another kernel event is not actively using a CPU core, even though it still exists.
- **System calls:** User-space code crosses into kernel space to request privileged work such as `read()`, `write()`, `fork()`, `exec()`, or `wait()`.

## Related notes

- For memory layout, the PCB, the stack, and execution state, see [The Anatomy of a Process](02%20The%20Anatomy%20of%20a%20Process.md).
- For backend scheduling tradeoffs at the application level, see [Execution Patterns](../Backend%20Engineering/02%20Execution%20Patterns.md).
- For kernel-space coordination and device access, see [System Architecture Overview](00%20System%20Architecture%20Overview.md#Process%20Management).
