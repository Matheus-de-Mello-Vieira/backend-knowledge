# Pipes

A POSIX pipe is a kernel-managed inter-process communication (IPC) resource that carries a bounded, unidirectional byte stream. A producer writes bytes at one end and a consumer reads them at the other. The kernel buffer absorbs temporary differences in their execution rates, but its finite capacity eventually makes each side's progress depend on the other.

## Endpoints and Kernel State

Calling `pipe(p)` creates a pipe and stores two process-local [file descriptors](02%20The%20Anatomy%20of%20a%20Process.md#File%20Descriptors%20%28FDs%29) in `p`: `p[0]` is the read end, and `p[1]` is the write end.

- **Descriptor handles:** The descriptors refer to the pipe; they are not the pipe buffer itself.
- **Kernel pipe state:** The kernel maintains the buffered byte stream and the references to its read and write ends.
- **Anonymous pipe:** An anonymous pipe has no filesystem pathname. Related processes commonly share its endpoints when descriptors created before `fork()` are inherited.

## Stream and File Semantics

A pipe exposes an ordered byte stream rather than discrete messages. A `read()` consumes whichever bytes are currently available, so one read result does not reveal application-message or `write()` boundaries.

Pipes are non-seekable: consuming bytes advances through the stream, but `lseek()` does not supply the position semantics of a regular file. This is one example of how [resource-specific operations](02%20The%20Anatomy%20of%20a%20Process.md#Resource-Specific%20Operations) remain different beneath the common descriptor interface.

> [!note] Pipes and Go Channels
> Go channels transfer typed values and preserve value boundaries; pipes transfer untyped stream bytes. Both can use bounded buffering and impose blocking or backpressure when producer and consumer rates differ.

## Blocking and Backpressure

A pipe buffer decouples producer and consumer only while it holds unread bytes or has usable capacity. Once the buffer is empty or full, a blocking operation waits for the other side to change that state.

- **Empty pipe:** A `read()` blocks while the pipe is empty and at least one write-end reference remains open. When a writer adds bytes, the reader can resume and consume them.
- **Full pipe:** A `write()` blocks when the pipe lacks enough capacity for the operation to make progress. Reading frees capacity and allows the writer to resume.
- **Backpressure:** A consumer that reads too slowly eventually fills the bounded pipe buffer and constrains producer progress instead of allowing queued data to grow without bound.

While an operation waits, its calling thread is in the operating system's [blocked state](05%20Process%20Management.md#Core%20Mechanics), allowing another runnable thread to use the CPU.

## EOF and Pipe Lifetime

A reader observes EOF only after the pipe has no more buffered data and no process retains a write-end reference:

1. The reader consumes every buffered byte.
2. Every write end is closed.

An open write end means the kernel must still allow for a future write. An empty pipe with any write-end reference is therefore a waitable stream rather than EOF. Processes that inherit endpoints must close every unused end; otherwise, a process that only reads can keep its own later read waiting by retaining its write end. These rules follow the same [descriptor lifetime](02%20The%20Anatomy%20of%20a%20Process.md#Descriptor%20Operations%20and%20Lifetime) model as other FD-backed resources.

## Anonymous Pipes and FIFOs

An anonymous pipe is reached through descriptors that a process already holds. It is commonly created before `fork()` so related processes inherit references to the same kernel pipe state; descriptor-passing mechanisms can also transfer an endpoint to another process.

A **FIFO** (named pipe) adds a filesystem pathname that independent processes can use as a rendezvous point. Once opened, a FIFO still carries a bounded byte stream through kernel-managed state. Its pathname does not make the transferred bytes persistent regular-file content.
