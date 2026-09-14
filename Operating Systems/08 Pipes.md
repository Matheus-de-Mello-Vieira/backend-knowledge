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

## Shell Pipeline Construction

Shell pipelines combine pipe endpoint configuration with the [POSIX process-control interface](05%20Process%20Management.md#POSIX%20Process-Control%20Interface). For `cat file | grep foo`, the pipe-specific result is that `cat` receives the write end as FD `1` and `grep` receives the read end as FD `0`.

The following fragments show the pipe-specific descriptor setup. They omit argument construction and error handling so that each fragment exposes one change to endpoint references.

1. **Create the pipe:** The shell starts with FDs `0`, `1`, and `2` connected to terminal input, output, and error. It must create the kernel communication resource before either child exists:

    ```c
    int p[2];
    pipe(p);
    ```

    `p[0]` now refers to the read end and `p[1]` to the write end. Assume they are FDs `3` and `4`; the actual numbers depend on which descriptors are available. The shell holds both endpoint references, so each later `fork()` gives its child access to the same kernel pipe state.

2. **Connect `cat` to the write end:** The first child inherits references to both pipe endpoints. Its setup path makes the write-end construction handle become standard output and discards every pipe reference it will not use:

    ```c
    dup2(p[1], 1);
    close(p[0]);
    close(p[1]);
    ```

    FD `1` retains the write-end reference after `p[1]` is closed; the child no longer retains a read-end reference. When that child executes `cat`, its prepared FD `1` determines where `cat` writes.

3. **Connect `grep` to the read end:** The parent still holds both construction handles when it creates the second child, so this child also receives both endpoints. Its setup path makes the read-end handle become standard input and discards the write-end reference:

    ```c
    dup2(p[0], 0);
    close(p[0]);
    close(p[1]);
    ```

    FD `0` retains the read-end reference after `p[0]` is closed; the child no longer retains a write-end reference. When that child executes `grep`, its prepared FD `0` determines where `grep` reads.

4. **Release the shell's construction handles:** Once both children have inherited the endpoints, the shell no longer needs either reference:

    ```c
    close(p[0]);
    close(p[1]);
    ```

    Closing the shell's write-end reference allows `grep` to observe EOF once `cat` closes its write end and the pipe's buffered bytes are consumed.

Temporary descriptors are construction handles, not final stream assignments. Closing them prevents a process that does not need an endpoint from extending that endpoint's lifetime. The resulting stream connection is `cat` FD `1` → pipe → `grep` FD `0`.

After the children execute their commands, `cat` opens `file` and transfers its bytes approximately as follows:

```c
read(file_fd, buffer, n);
write(1, buffer, n);
```

FD `1` refers to the pipe write end, so that `write()` supplies bytes to the pipe. `grep` reads from FD `0`, which refers to the pipe read end, and writes matching output to its unchanged FD `1`, the terminal:

```c
read(0, buffer, n);
```

When `cat` reaches file EOF and exits, its write descriptor closes. After `grep` consumes the remaining pipe bytes and no write-end references remain, a later `read(0, ...)` returns `0` to signal EOF.
