
# Process Management

Process management is the heartbeat of the operating system. It is the complex machinery responsible for creating, scheduling, isolating, and terminating programs. It is the exact system that creates the illusion that a computer with only 8 physical CPU cores can flawlessly run 400 applications simultaneously.

- **The Kernel as Orchestrator:** The kernel acts as the secure gatekeeper and traffic controller. It ensures no single process monopolizes the CPU, corrupts another program's memory, or touches the physical hardware directly.
- **The Illusion of Concurrency:** To achieve multitasking, the kernel rapidly swaps processes on and off the CPU cores. This happens in milliseconds, requiring incredibly precise coordination between software (the OS scheduler) and hardware (the CPU registers and interrupts).
- **Scheduling & Fairness:** Determining exactly which runnable process gets CPU time next, on which specific hardware core, and for exactly how long (timeslicing).

## Core Mechanics

### Process Lifecycle and Thread Execution States

A process provides resources and a virtual address space; its threads execute within that environment. The process lifecycle records process-wide events, while the scheduler tracks the execution state of each thread. Exact state names vary by operating system.

**Process lifecycle** includes these process-wide states:

- **Created:** The kernel has created the process and its initial execution context, but it has not yet begun execution.
- **Stopped:** The process has been suspended and its threads are not eligible for scheduling until it is continued.
- **Terminated:** The process no longer executes, either after its final thread exits or because a termination action ends it.

**Thread execution states** describe whether an individual thread is eligible to use a CPU:

- **Runnable:** The thread is ready to execute and waits for a CPU.
- **Running:** The thread is actively executing on a CPU.
- **Blocked:** The thread cannot proceed until an external event occurs, such as a network packet or disk I/O completion, so it does not consume CPU time while it waits.

Thread execution states are not a linear path. A newly created execution context becomes runnable; the scheduler moves a runnable thread to running; and a running thread can block and later become runnable again. Continuing a stopped process makes its threads eligible to run again. In a single-threaded process, the process and its sole thread move through these states together. A multithreaded process can have threads that are runnable, running, or blocked at the same time.

### Scheduling and System Calls

- **Context Switching:** The physical act of replacing one thread's execution context on a CPU. The kernel pauses the outgoing thread, saves CPU registers such as the Instruction Pointer, Stack Pointer, and flags in thread-specific kernel state, and restores the next thread's saved state. If the next thread belongs to another process, the kernel also changes the active address-space context. Frequent switches add overhead and can reduce application performance.
- **Blocking vs. Runnable:** If a thread needs to wait for a network packet or a slow disk read, the OS moves that thread to a blocked state and schedules another runnable thread. The blocked thread consumes no CPU time until an interrupt or kernel event makes it runnable again.
- [**System Calls**](09%20Kernel%20and%20User%20Space.md#System%20Calls): When user-space code needs a privileged action (like `read()`, `fork()`, or `exec()`), it executes a hardware trap. The CPU transfers control to the kernel at a protected entry point, where the kernel executes in kernel mode.

## CPU-Time Accounting

**CPU time** measures the time that a thread actually executes on a CPU. It differs from **elapsed time**, which also includes time spent waiting for a CPU or an external event. Operating systems normally account CPU time per thread and aggregate those values for the process.

The process's CPU time is the sum of user and system time:

$$
T_{\mathrm{CPU}} = T_{\mathrm{user}} + T_{\mathrm{system}}
$$

where $T_{\mathrm{CPU}}$ is total CPU time, $T_{\mathrm{user}}$ is time executing application code in user mode, and $T_{\mathrm{system}}$ is time executing kernel code on behalf of the thread.

- **User-mode execution:** Running application code increases user CPU time.
- **Kernel-mode execution:** System-call or fault handling performed for the thread increases system CPU time.
- **No execution:** A blocked thread and a runnable thread waiting for a CPU accrue neither user nor system CPU time.

If a system call blocks for I/O, the calling thread stops accruing CPU time while its elapsed time continues. The scheduler can run another thread during that interval, and that thread receives the CPU-time charge for its own execution.

> [!tip] Linux: Inspecting CPU Time with `top` and `htop`
>
> In `top`, `TIME+` reports cumulative CPU time used by a task since it started. It does not measure elapsed time. `%CPU` instead reports CPU use over the most recent display interval, so a blocked task does not add to `TIME+` while waiting and normally reports no CPU use in later intervals.
>
> `top`'s `us` and `sy` summary values describe system-wide user and kernel activity rather than the split for one selected process. A multithreaded process can report more than `100%` CPU on a multicore system, depending on `top`'s display mode. In `htop`, `TIME+` combines user and system CPU time; configurable `UTIME` and `STIME` columns expose the process-level split.

## POSIX Process-Control Interface

On POSIX systems, process control provides separate operations for creating a child, replacing a process's program, ending a process, and collecting child state. A program can compose them to let a parent retain control while a child becomes another program; it can also use a spawn operation for common create-and-execute cases.

### Process Lifecycle APIs

These APIs establish process identity, program replacement, termination, and direct-child state observation. Process groups and sessions later compose those process relationships into terminal-managed jobs.

- **Create a child — `fork()`:**
    - **Starting state:** `fork()` creates a child process as a copy of the calling process. The child initially executes the same program image at the instruction after `fork()`, but it has a separate address space.
    - **Return values:** The parent and child choose different paths because `fork()` returns the child's PID in the parent and `0` in the child.
    - **Memory:** The copy is a process-level starting state, not necessarily an immediate physical copy of every memory page. Many Unix-like systems use [copy-on-write](03%20Memory%20Management.md#Controlled%20Sharing%20%26%20Concurrency) so that both processes initially share physical pages and a write creates a private page for the writer.
    - **File descriptors:** The child receives [file descriptors](02%20The%20Anatomy%20of%20a%20Process.md#File%20Descriptors%20%28FDs%29) that refer to the same open resources as the parent's corresponding descriptors. It can change or close its own descriptor-table entries without changing the parent's entries, although the referenced open resource remains shared while either process retains a reference.
- **Create and execute — `posix_spawn()` and `posix_spawnp()`:**
    - **Operation:** These functions create a child to execute a specified program, combining the common creation-and-execution case without exposing a child-side interval in which application code runs before the new program begins.
    - **Configuration:** Spawn attributes and file actions configure properties such as signal state, process group, and file-descriptor changes.
    - **Availability:** They belong to POSIX's optional Spawn option, so an implementation need not provide them.
- **Replace the program image — `execve()`:**
    - **No new process:** `execve()` does not create a process; execution begins at the new program's entry point under the caller's existing process identity.
    - **New image:** The previous code, data, heap, and stack no longer define execution; the new program receives a new initial memory image.
    - **File descriptors:** File descriptors remain available unless they are marked close-on-exec.
- **End the current process — `exit()` and `_exit()`:**
    - **`exit()`:** Performs normal C-library termination work, including registered termination handlers and standard-I/O cleanup.
    - **`_exit()`:** Terminates the calling process directly, without returning.
    - **After `fork()`:** A child that cannot execute its intended program normally reports the error and uses `_exit()` so it does not repeat cleanup for runtime state inherited from the parent.
- **Collect child state — `wait()`, `waitpid()`, and `waitid()`:** These functions observe state transitions that a direct child has already reached; they do not cause the child to finish. A blocking call waits only when no selected child has a qualifying state to report. If the state is already available, it returns immediately.
    - **`wait()`:** Waits for the termination of an eligible child.
    - **`waitpid()`:** Selects a child, a process group, or any eligible child according to its process-ID argument. By default, it waits for termination; its options can also request reports for stopped or continued children.
        - **`WNOHANG`:** Requests a nonblocking check. If no selected child has a qualifying state change to report, `waitpid()` returns immediately instead of waiting.
    - **`waitid()`:** Supports selection by child identifier type, selects the reportable state through options, and returns structured status information.
    - **Reaping:** Collecting a terminated child's status normally releases the kernel state retained for that child. Without reaping, the terminated child remains a zombie until another process collects its status.

> [!example] Shell command execution
>
> A shell uses `fork()`-then-`execve()` to remain a shell in the parent while each child becomes a command. For command launches whose setup fits its defined attributes and file actions, a shell can instead use `posix_spawn()` or `posix_spawnp()`. A [shell pipeline](08%20Inter-Process%20Communication.md#Anonymous-Pipe%20Shell%20Pipeline%20Construction) creates its pipe before forking, prepares one child's standard output and another's standard input, then executes the commands in those children. The parent later collects the command statuses with `wait()`, `waitpid()`, or `waitid()`.

### Process Groups, Sessions, and Job Control

A parent/child tree identifies who created a process, but it does not describe which processes form one interactive job or which jobs share a terminal environment. POSIX process groups and sessions supply those independent relationships so that the kernel, terminal driver, and shell can manage a pipeline or command as a unit.

#### Identity hierarchy and job-control membership

A process participates in several relationships at once. They answer different questions and none follows directly from the others.

| Identifier | Relationship             | Meaning                                                                                                            |
| ---------- | ------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| PID        | Process identity         | Identifies one process. Threads execute within that process but have separate thread identities.                   |
| PPID       | Process ancestry         | Identifies the parent that created the process. It supports parent/child observation and reaping, not job control. |
| PGID       | Process-group membership | Identifies the job-control and group-signalling unit containing the process.                                       |
| SID        | Session membership       | Identifies the collection of process groups that share one job-control environment.                                |

Every POSIX process belongs to one **process group**, identified by a **process group ID (PGID)**. A group can contain one process or many unrelated processes; it is not a parent/child subtree. The kernel uses the group as a direct target for signalling and terminal job control.

A process whose PID equals its PGID is the **process-group leader**. Leadership supplies the group's identifying process and constrains some state changes; it does not make the leader a supervisor, the parent of every member, or a signal relay. Group-directed operations reach the members from the kernel. A process group persists while it still has members, even after its original leader exits.

A **session** is one or more process groups. Each group belongs to exactly one session, so all of its members share the same SID. A session leader initially has `PID == SID`, but session leadership likewise does not create a supervisory relationship. A session and a process group survive the exit of their original leaders while members remain.

A process group answers *which processes make up one job?* A session answers *which collection of jobs participates in one terminal/job-control environment?* A session is therefore neither a terminal, a login account, nor necessarily the shell process itself.

#### Controlling terminals and foreground jobs

A session may have one **controlling terminal**, and a terminal is the controlling terminal of at most one session. This is a session relationship, not a file-descriptor property: members can independently close or redirect descriptors while remaining in the same terminal-bearing session. Conversely, FD 0 referring to a TTY does not by itself establish a controlling-terminal relationship.

A session leader that has no controlling terminal can establish one under the platform's terminal rules. On Linux and many Unix-like systems, opening an eligible terminal establishes it unless `O_NOCTTY` suppresses that effect. `setsid()` therefore detaches a process from its former terminal domain but does not close or redirect inherited terminal descriptors.

The terminal records one **foreground process group ID**. At most one group in the terminal's session is foreground at a time; when one is designated, every other group in that session is background relative to that terminal.

To be **foreground** means that a process group is the terminal's designated interactive job. The terminal directs terminal-generated control signals to that group and permits it to read terminal input. This role is not a CPU-scheduling priority, nor does it merely mean that a process is producing visible output.

- **`tcgetpgrp(fd)`:** Returns the terminal's foreground PGID.
- **`tcsetpgrp(fd, pgid)`:** Sets the foreground PGID through the caller's controlling-terminal descriptor. The target group must belong to the caller's session, which prevents one session from foregrounding another session's job.

An interactive shell transfers the foreground role as a state transition:

1. It creates the command or pipeline, establishes its shared PGID, and configures its descriptors.
2. For a foreground job, it calls `tcsetpgrp()` to make that PGID the terminal foreground group, then waits for child state changes.
3. When the job exits or stops, the shell restores its own PGID with `tcsetpgrp()` before reading the next command.

#### Creating groups and sessions

`setpgid(pid, pgid)` controls process-group membership, but only within the caller's session:

- **New group:** `setpgid(0, 0)` makes the caller's PID its PGID, making it the leader of a new group.
- **Existing group:** The call joins an eligible process to an existing group in the same session.
- **Session and leadership constraints:** A process cannot move a group across sessions or change a session leader's process group.
- **Parent/child timing:** A parent changing a child's group must do so before the child has executed a new program image.

`posix_spawn()` can establish related job-control state at creation time. Unless `POSIX_SPAWN_SETPGROUP` or `POSIX_SPAWN_SETSID` is selected, the child inherits the parent's process group; `POSIX_SPAWN_SETPGROUP` selects its group. POSIX.1-2024's `POSIX_SPAWN_SETSID`, when supported, creates a new session and process group without a controlling terminal. Specifying both flags has unspecified behavior.

A job-controlling shell establishes group membership promptly after `fork()`. Parent and child may both participate in that setup so that a child cannot reach `execve()` or receive terminal control before the intended group exists. For `cat file | grep foo | sort`, the shell creates three children and places all three in one new group rather than making one group per command:

```text
shell PGID 1000

job PGID 1100
├── cat   PID 1100
├── grep  PID 1101
└── sort  PID 1102
```

The shared PGID lets stop, continue, foreground, and signal operations apply to the whole pipeline. The pipeline's pipes carry data; group membership supplies its control identity. The shell deliberately constructs both mechanisms.

`fork()` creates a new PID, but the child initially inherits the parent's PGID and SID. `execve()` replaces the program image without creating a process, so PID, PGID, SID, and controlling-terminal membership remain unchanged. The resulting `fork()` → `setpgid()` → `execve()` sequence lets a shell choose a job's control identity before the child begins its command.

`setsid()` creates a new session only when its caller is not already a process-group leader. On success, the caller becomes the sole initial member and leader of both a new process group and a new session:

```text
PID = PGID = SID = caller PID
```

The new session initially has no controlling terminal. A process-group leader cannot call `setsid()` because its PID already identifies an existing group; moving that leader into a new session while other members remained would break the rule that a group belongs to one session. The traditional `fork()` followed by parent exit gives the child a new PID, allowing it to call `setsid()`.

#### Terminal-mediated job control

The terminal driver delivers configured interrupt, quit, and suspend signals to every member of the foreground process group. Thus `Ctrl-C`, `Ctrl-\\`, and `Ctrl-Z` commonly generate `SIGINT`, `SIGQUIT`, and `SIGTSTP` for the job, not merely for whichever process is reading standard input. Signal dispositions and their default actions remain the subject of [POSIX signals](#POSIX%20Signals).

Foreground/background status is checked when a process accesses its controlling terminal, not merely because it uses `stdin`, `stdout`, or `stderr`. An interactive shell normally makes those standard streams terminal-backed, but each descriptor can instead refer to another I/O resource. The [file descriptor](02%20The%20Anatomy%20of%20a%20Process.md#File%20Descriptors%20%28FDs%29) identifies the resource; the process group relative to the terminal determines whether terminal job-control rules apply. Keystrokes are not assigned to one process simply because it holds `stdin`: a process receives terminal input only by reading a terminal-backed descriptor.

- **`stdin` (FD 0):** A read through a terminal-backed standard-input descriptor is a terminal read. A background group that tries to read its controlling terminal receives `SIGTTIN`; its default disposition stops the group. This is why an interactive background command commonly stops.
- **`stdout` and `stderr` (FDs 1 and 2):** Both descriptors can independently refer to the terminal. Background output is normally permitted. When the terminal's `TOSTOP` flag is set, a background group that writes to its controlling terminal receives `SIGTTOU`; terminal-control operations have related `SIGTTOU` rules.
- **Redirection:** Redirecting a standard stream to a file, pipe, or other resource bypasses the terminal driver for operations through that stream. It does not change the process's PID, PGID, SID, or foreground/background status; another terminal-backed descriptor remains subject to the same job-control rules.

Shell job builtins apply the same group and terminal relationships:

- **`jobs`:** Reports shell-maintained job state.
- **`bg`:** Sends `SIGCONT` to a stopped job while the shell remains foreground.
- **`fg`:** Moves the job's PGID to the foreground, continues it when needed, waits for it, and later restores the shell's foreground PGID.

#### Group and session lifecycle

A process group does not become **orphaned** merely because its leader exits or because one member loses its parent. It is orphaned only when none of its members has a parent in a *different* process group of the same session. At that point, no process in the session remains outside the group to perform shell-style job control over it.

When a group becomes orphaned while it has a stopped member, POSIX job-control behavior sends `SIGHUP` and then `SIGCONT` to every member of the newly orphaned group. The sequence resumes the stopped job so it cannot remain stranded after its shell or other controlling parent disappears.

Terminal hangup and session-leader exit are separate Linux-specific transitions:

- **Terminal hangup:** When terminal configuration permits it, a hangup sends `SIGHUP` to the controlling session leader.
- **Session-leader exit:** When a controlling session leader terminates, Linux sends `SIGHUP` to the controlling terminal's foreground process group and disassociates the terminal from the session.

Neither transition means that killing a process-group leader kills the rest of its group, and losing a parent does not by itself trigger the orphaned-group sequence.

#### Detachment and daemonization

Background execution, hangup handling, shell job tracking, session creation, and daemonization solve different lifecycle problems. Leaving a terminal's job-control domain and managing inherited terminal-backed descriptors are separate steps; running in the background or ignoring `SIGHUP` alone does not provide terminal detachment.

- **`command &`:** Starts the command as a shell background job.
    - **Changes:** The shell returns to its prompt instead of waiting for the job to finish.
    - **Does not change:** The job normally remains in the shell's session and retains that session's controlling-terminal relationship. It can still inherit terminal-backed standard descriptors, and terminal job-control rules still apply when it accesses the controlling terminal. Backgrounding does not create a new session or detach the job from the terminal.
- **`nohup command`:** Changes the invoked command's hangup-signal disposition.
    - **Changes:** The command ignores `SIGHUP`, so that signal does not use its default terminating action. Implementations typically redirect terminal-oriented standard streams when necessary.
    - **Does not change:** `nohup` does not create a new session or change the command's PGID. It addresses one signal-disposition concern; it does not remove the command from the terminal's job-control domain.
- **`disown`:** Changes a shell's tracking or hangup handling for one of its jobs.
    - **Changes:** It can prevent the shell from treating the job as a managed job when the shell exits, although the exact behavior depends on the shell.
    - **Does not change:** It changes shell policy rather than kernel session state, so it does not detach the process from its session or controlling terminal.
- **`setsid()`:** Creates a new session and a new process group whose caller is initially the only member and leader.
    - **Changes:** The new session initially has no controlling terminal, which removes the caller from the launching terminal's job-control domain.
    - **Does not change:** `setsid()` does not close, redirect, or otherwise clean up inherited descriptors. A terminal-backed descriptor remains usable until the process closes or replaces it.
    - **Precondition:** The caller must not already be a process-group leader, so traditional code commonly forks first.
- **Daemonization:** Applies a broader lifecycle pattern for a process intended to operate independently of an interactive session.
    - **Typical composition:** It commonly combines `setsid()` with deliberate cleanup of inherited descriptors, working directory, file-creation mask, and signal configuration.
    - **Optional second fork:** [Traditional daemonization](#Traditional%20Daemonization) optionally forks a second time so the final process is not a session leader, preventing accidental controlling-terminal acquisition on Unix-like systems with that behavior. The second fork is a historical portability precaution, not a universal POSIX requirement.
    - **Does not provide:** Daemonization does not itself provide service supervision.

#### Composition with process control and IPC

Job control composes independent control, observation, and data-flow mechanisms:

- **Job control and child status:** A process group is a collective control unit, not a collective child-status record. A shell uses a PGID to stop, continue, signal, foreground, and background a job, but it uses `wait()`, `waitpid()`, or `waitid()` to observe each direct child's stopped, continued, or exited state. A process group has no kernel-provided aggregate exit status.
- **Individual and group signals:** `kill()` can target either one process or a group: a positive argument selects a PID, `0` selects the caller's group, and a value less than `-1` selects the group whose PGID is the absolute value. `killpg()` is the named group-targeting interface; on Linux it is implemented through the negative-PGID form of `kill()`. Neither mechanism selects an entire session, and neither makes a signal inherently terminating.
- **Pipes and descriptors:** Pipes and [file descriptors](02%20The%20Anatomy%20of%20a%20Process.md#File%20Descriptors%20%28FDs%29) are independent of this hierarchy. A [shell pipeline](08%20Inter-Process%20Communication.md#Anonymous-Pipe%20Shell%20Pipeline%20Construction) uses descriptors and pipes for data flow, while its process group supplies job-control identity.

#### Observing and integrating the hierarchy

On Linux systems with a compatible `ps`, inspect the relationships with:

```sh
ps -o pid,ppid,pgid,sid,tpgid,tty,stat,cmd
```

- **PID / PPID:** Process identity and ancestry.
- **PGID / SID:** Job membership and job-control environment.
- **TPGID:** The foreground process group of the listed process's terminal.
- **TTY:** The terminal device, when one is associated with the process.
- **STAT:** The process state and status flags as reported by `ps`; their symbols vary by implementation.
- **CMD:** The command and arguments displayed by `ps`.

> [!note] `STAT` symbols on macOS and BSD `ps`
>
> `STAT` begins with one primary run-state symbol. Any later characters are modifiers, so the position of a symbol matters: the first `S` means *sleeping*, while a later `S` has a different meaning.
>
> | Initial symbol | Meaning |
> | --- | --- |
> | `I` | Idle: sleeping for longer than about 20 seconds. |
> | `R` | Runnable. |
> | `S` | Sleeping for less than about 20 seconds. |
> | `T` | Stopped. |
> | `U` | In an uninterruptible wait. |
> | `Z` | Dead but not yet reaped: a zombie. |
>
> The following modifiers add status information:
>
> | Modifier | Meaning |
> | --- | --- |
> | `+` | Member of its controlling terminal's foreground process group. |
> | `<` | Raised CPU scheduling priority. |
> | `>` | Exceeds its requested soft memory limit and is not swapped. |
> | `A` | Requested random page replacement. |
> | `E` | Trying to exit. |
> | `L` | Has pages locked in physical memory. |
> | `N` | Reduced CPU scheduling priority. |
> | `S` | Requested FIFO page replacement. |
> | `s` | Session leader. |
> | `V` | Suspended during `vfork()`. |
> | `W` | Swapped out. |
> | `X` | Being traced or debugged. |
>
> For example, `Ss` means *sleeping session leader*, `SN` means *sleeping with reduced CPU scheduling priority*, and `R+` means *runnable in the foreground process group*.

The following exercise applies these fields to background and foreground jobs.

> [!example] Inspecting background and foreground jobs
>
> An interactive shell assigns a **job number** separately from the kernel's PIDs and PGIDs. Start one background command and one background pipeline, then ask the shell for its jobs:
>
> ```sh
> sleep 200 &
> sleep 300 | cat &
> jobs
> ```
>
> A captured `zsh` run reported:
>
> ```text
> [1] 23722
> [2] 23723 23724
> [1]  - running    sleep 200
> [2]  + running    sleep 300 | cat
> ```
>
> The number in brackets is the shell job number: the pipeline is job `2`, so `%2` is its **job specification**. Its processes have PIDs `23723` and `23724`, but both belong to the process group whose PGID is `23723`. The standalone `sleep 200` process has its own PID and PGID, `23722`.
>
> Inspect the processes on the current terminal:
>
> ```sh
> # Linux systems with a compatible ps
> ps -t "$(tty | sed 's#^/dev/##')" -o pid,ppid,pgid,sid,tpgid,tty,stat,cmd
>
> # macOS and BSD ps
> ps -t "$(tty | sed 's#^/dev/##')" -o pid,ppid,pgid,sess,tpgid,tty,stat,command
> ```
>
> Before foregrounding either job, the shell owns the terminal's foreground PGID. The two background jobs have distinct PGIDs, while the pipeline members share one PGID; they normally share the shell's session and controlling terminal.
>
> ```sh
> fg %2
> # Press Ctrl-Z while the pipeline is foreground.
> ```
>
> `fg %2` tells the shell to select job `2`, not PID or PGID `2`. The shell gives the job's process group the terminal and waits instead of printing a prompt. If the selected job was stopped, `fg` also continues it; this already-running pipeline only changes from background to foreground. `Ctrl-Z` sends `SIGTSTP` to the foreground group, stopping both pipeline members. The shell then regains the terminal and reports that the job is suspended.
>
> After this interaction, one captured macOS/BSD `ps` output contained:
>
> ```text
> PID    PGID   TPGID  TTY      STAT
> 23722  23722  23741  ttys002  SN
> 23723  23723  23741  ttys002  TN
> 23724  23723  23741  ttys002  TN
> 23741  23741  23741  ttys002  R+
> ```
>
> The `TN` rows show that both pipeline members remain in PGID `23723` but are stopped (`T`); `N` reports their reduced CPU scheduling priority. PID `23741` is the `ps` command itself. Because the shell runs that command in its own foreground group, it temporarily becomes the terminal's `TPGID` and appears as `R+`. When `ps` exits, the shell regains the foreground role. To observe the pipeline's `TPGID` while `fg` blocks the first shell, run `ps -e -o pid,ppid,pgid,sid,tpgid,tty,stat,cmd` from a second terminal and locate the processes by PID or TTY.

## POSIX Signals

A POSIX signal is an asynchronous notification that the kernel delivers to a process or thread. An external actor can request delivery with `kill()`, and the kernel also generates signals for events such as a child changing state. A signal is a control notification, not a stream of structured application messages: its number identifies the event or requested action, while any associated work remains the receiver's responsibility.

> [!note] `kill()` sends signals
> Despite its name, the `kill()` function sends the signal specified by its `sig` argument to a process or process group; it does not inherently terminate the target. It can send `SIGTERM`, `SIGHUP`, `SIGUSR1`, or `SIGKILL`, subject to permission checks. `SIGKILL` is special because the receiving process cannot catch, ignore, or block it. The shell `kill` utility traditionally sends `SIGTERM` when no signal is specified.

For a signal whose disposition can be changed, the receiving process chooses a **disposition**, which determines the immediate response to delivery.

- **Default action:** The kernel applies the signal's defined action, such as terminating, stopping, or continuing the process.
- **Ignore:** The process discards the signal.
- **Handler:** A caught signal interrupts normal control flow to run the process's handler.

Because a handler interrupts normal control flow, it must limit itself to async-signal-safe work. It commonly records a small piece of state that the program's normal control loop examines later; substantial cleanup, I/O protocol work, and state transitions then occur outside the handler.

Each thread also has a **signal mask**: a set of signal identifiers whose delivery to that thread is temporarily blocked.

- **Pending delivery:** A blocked signal remains pending until it is unblocked.
- **Unblockable signals:** `SIGKILL` and `SIGSTOP` cannot be blocked.
- **Standard-signal coalescing:** Standard signals do not form a reliable event log. If an instance is already pending, further instances of that signal can merge rather than being delivered as distinct notifications.
- **Real-time signals:** Real-time signals have separate queued-delivery semantics.

Signal delivery therefore requests or reports a state change; it does not perform the receiving program's higher-level lifecycle policy. A process such as a supervisor decides how to translate the notification into shutdown, restart, reconfiguration, or cleanup work.

### Common Signals

The following signals are common in POSIX and Unix-like process control. Their **default action** applies only when the process has not installed a handler or changed the disposition. Signal names are portable identifiers; their numeric values vary by platform and must not be hard-coded.

| Signal                | Suffix after `SIG`        | Typical source or meaning                                         | Default action                                                     |
| --------------------- | ------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------ |
| `SIGHUP`              | Hang up                   | The controlling terminal disconnects                              | Terminate                                                          |
| `SIGINT`              | Interrupt                 | An interactive interrupt, commonly `Ctrl-C`                       | Terminate                                                          |
| `SIGQUIT`             | Quit                      | An interactive quit request                                       | Terminate and produce a core dump                                  |
| `SIGILL`              | Illegal instruction       | Execution reaches an invalid machine instruction                  | Terminate and produce a core dump                                  |
| `SIGABRT`             | Abort                     | A process deliberately aborts itself                              | Terminate and produce a core dump                                  |
| `SIGFPE`              | Floating-point exception  | An arithmetic exception, including integer division by zero       | Terminate and produce a core dump                                  |
| `SIGTERM`             | Terminate                 | A request to terminate                                            | Terminate                                                          |
| `SIGKILL`             | Kill                      | A request for immediate termination                               | Terminate; cannot be caught, blocked, or ignored                   |
| `SIGSTOP`             | Stop                      | A request to suspend execution                                    | Stop; cannot be caught, blocked, or ignored                        |
| `SIGTSTP`             | Terminal stop             | An interactive stop request, commonly `Ctrl-Z`                    | Stop                                                               |
| `SIGWINCH`            | Window change             | The controlling terminal reports a window-size change             | Ignore                                                             |
| `SIGCONT`             | Continue                  | A request to resume a stopped process                             | Continue if stopped                                                |
| `SIGCHLD`             | Child                     | An eligible child changes state                                   | Ignore; child status normally remains available to a wait function |
| `SIGPIPE`             | Pipe                      | A write targets a pipe or stream socket whose read side is closed | Terminate                                                          |
| `SIGALRM`             | Alarm                     | An alarm timer expires                                            | Terminate                                                          |
| `SIGUSR1` / `SIGUSR2` | User-defined signal 1 / 2 | Application-defined notification                                  | Terminate                                                          |
| `SIGSEGV`             | Segmentation violation    | Invalid memory reference                                          | Terminate and produce a core dump                                  |
| `SIGTTIN`             | Terminal input            | A background job attempts to read its controlling terminal        | Stop                                                               |
| `SIGTTOU`             | Terminal output           | Background write with `TOSTOP`, or terminal-control operation     | Stop                                                               |

`SIGTERM` is the normal signal for a cooperative shutdown: a process can catch it, stop accepting work, and release resources. `SIGKILL` gives the process no such opportunity because the kernel terminates it without running a handler. `SIGHUP`, `SIGUSR1`, and `SIGUSR2` have fixed signal identities but no universal application-level protocol; long-running programs often assign them roles such as configuration reload or log reopening by convention.

The terminal driver generates interactive signals from configured control characters: `Ctrl-C`, `Ctrl-\\`, and `Ctrl-Z` commonly produce `SIGINT`, `SIGQUIT`, and `SIGTSTP`. Those bindings are terminal configuration rather than inherent properties of the keys, so tools such as `stty` can change them.

`yes | head -n 1` illustrates `SIGPIPE`: after `head` reads one line and exits, a later write by `yes` targets a pipe with no reader.

### Alarm Timers

`alarm()` asks the kernel to arrange delivery of `SIGALRM` after a whole-second interval. Kernel timekeeping and its timer subsystem ultimately use hardware clocks or timers to maintain that countdown while the process sleeps, blocks in I/O, or is not scheduled; the process does not busy-wait by repeatedly checking the clock.

Timer expiration and handler execution are distinct events. If the timer expires while the process is not running, `SIGALRM` becomes pending. The handler runs only when delivery occurs, so an alarm does not guarantee execution at an exact wall-clock instant.

`alarm()` provides one simple process alarm: a later call replaces the previous one. POSIX also provides more capable timer APIs such as `timer_create()`, but an event loop commonly integrates deadlines through [timer sources in its readiness cycle](07%20Socket%20Management.md#Timer%20Sources%20for%20Event%20Loops) rather than by introducing `SIGALRM` as a separate control path.

### SIGCHLD, Child Status, and Reaping

`SIGCHLD` notifies the parent that a direct child reached an eligible lifecycle state; it does not itself contain the child's status. When the kernel retains a terminated child's status, the parent obtains it with `wait()`, `waitpid()`, or `waitid()`. Because standard signals can coalesce, one notification does not identify one child or one state transition.

Both `SIG_DFL` and `SIG_IGN` leave a delivered `SIGCHLD` without an immediate effect on the parent's control flow: neither runs a handler nor applies a terminating or stopping action. They differ in the kernel's child-termination bookkeeping, which determines whether the parent can later collect a child's status.

- **Default disposition — `SIG_DFL` (signal default):** `SIG_DFL` selects the signal's predefined behavior. For `SIGCHLD`, that behavior ignores the notification but retains a terminated child's status. The child normally remains a zombie until the parent collects its status with a wait function.
- **Explicit ignore — `SIG_IGN` (signal ignore):** `SIG_IGN` explicitly selects ignore behavior. For `SIGCHLD`, POSIX additionally prevents children that terminate under this disposition from becoming zombies, so the parent cannot later collect those termination statuses with a wait function.

Use `SIG_DFL` when the parent needs a child's termination status or plans to reap it. `SIG_IGN` suits children whose parent does not need their termination status.

### POSIX Signal Interface

These interfaces establish a handler and its signal-mask policy without losing a signal that arrives between setup and a blocking wait.

- **`sigaction()`:** Sets a signal's disposition. A `struct sigaction` specifies either a handler or another disposition, the signal mask used while that handler runs, and behavior flags.
- **Signal-set operations — `sigemptyset()`, `sigaddset()`, and `sigdelset()`:** Initialize a `sigset_t` as empty, add a signal to it, or remove a signal from it respectively.
- **`sigprocmask()` in a single-threaded program:** Examines or changes the calling thread's signal mask. With `SIG_BLOCK`, it adds signals to the mask and can save the old mask for later restoration. POSIX leaves its use unspecified in a multithreaded process.
- **`pthread_sigmask()` in a multithreaded program:** Examines or changes the calling thread's signal mask regardless of the process's thread count. It provides the same mask operations as `sigprocmask()`, but reports failures as error numbers instead of returning `-1` and setting `errno`.
- **`sigsuspend()`:** Atomically replaces the calling thread's signal mask and suspends the thread.
    - **Wake-up and return:** A signal unblocked by the temporary mask whose action invokes a handler ends the suspension. After the handler returns, the original mask is restored and `sigsuspend()` returns `-1` with `errno` set to `EINTR`. If the signal terminates the process, `sigsuspend()` does not return.
    - **Condition waits:** `sigsuspend()` does not report which signal woke it; any unblocked signal that invokes a handler produces the same return. Code that waits for an application condition rechecks its predicate after every return and suspends again when the condition remains false.
    - **Race avoidance:** A program blocks a signal while it tests its predicate, then passes `sigsuspend()` a mask that unblocks that signal. Replacing the mask and suspending as one operation leaves no gap between the test and the wait.

### Signals in Readiness-Based Event Loops

Signals are not descriptors, so a readiness loop cannot register a signal itself as though it were a socket. A program that needs one loop to react to I/O and signals must coordinate the two mechanisms explicitly.

- **Dedicated signal thread:** Block a selected signal with `pthread_sigmask()` before creating the other threads, which inherit the mask. One thread then calls `sigwait()` for that signal and writes a notification to a pipe that the event loop monitors. This avoids running an asynchronous handler for the signal; it is also necessary to avoid assuming that a process-directed `SIGALRM` will arrive in one particular thread.
- **Self-pipe:** A minimal signal handler writes a byte to a nonblocking pipe, whose read end wakes the readiness loop. `write()` is permitted in an async-signal context, but most handler work is not. If the write end is already full, treating `EAGAIN` as harmless is valid when one unread byte already means that the loop has notification work to process.
- **Linux descriptor interface:** `signalfd` represents selected blocked signals through a descriptor, allowing a Linux event loop to receive them through its normal readiness mechanism.

### Receiving `SIGTERM` in C

This single-threaded service converts `SIGTERM` delivery into a normal control-flow decision. Its handler runs on the program's existing thread, records that shutdown was requested, and leaves work and cleanup to the main control flow.

The handler communicates with normal control flow through one `volatile sig_atomic_t` object. It does not perform shutdown work itself.

```c
#define _POSIX_C_SOURCE 200809L

#include <signal.h>
#include <stdlib.h>

static volatile sig_atomic_t stop_requested = 0;

static void on_sigterm(int signal_number) {
    (void)signal_number;
    stop_requested = 1;
}
```

The service installs its handler before it begins processing work. The comments in `main()` stand in for operations that vary by service.

```c
int main(void) {
    struct sigaction action = {0};

    action.sa_handler = on_sigterm;
    sigemptyset(&action.sa_mask);

    if (sigaction(SIGTERM, &action, NULL) == -1) {
        return EXIT_FAILURE;
    }

    while (!stop_requested) {
        /*
         * Process one bounded unit of work. The service-specific operation
         * needs a separate wake-up or cancellation mechanism when it can
         * block indefinitely.
         */
    }

    /* Stop accepting new work. */
    /* Finish or cancel in-flight work according to the service's policy. */
    /* Release resources. */
    return EXIT_SUCCESS;
}
```

`SIGTERM` can interrupt a work unit, but the handler only records the request. Once normal control flow reaches the next loop test, it stops new work and applies the shutdown policy shown in the comments.

> [!warning] Signal-handler scope
> The handler only assigns `stop_requested`, a `volatile sig_atomic_t` object. Functions such as `printf()`, memory allocation, and most library operations are not async-signal-safe, so the handler must not use them. A multithreaded program needs an explicit signal-mask policy; it commonly uses `pthread_sigmask()` to block a selected signal before creating worker threads, which inherit the mask, and dedicates one thread to receiving it with `sigwait()`.

## Processes vs. Threads

To understand how the kernel manages work, separate *resources* from *execution*. A process establishes an isolated resource environment, while a thread executes instructions within that environment. A newly created process includes an initial thread, and that thread can create additional threads in the same process.

| Dimension                    | Process                                                                                                                                                                 | Thread                                                                                                                                                                                                 |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Primary role**             | Provides the resource and isolation context for execution.                                                                                                              | Provides an execution context that runs instructions.                                                                                                                                                  |
| **Memory and I/O resources** | Owns a virtual address space, whose mapped regions include code, data, heap, and stack memory, and a process-wide file-descriptor table.                                | Shares that address space and descriptor table with its sibling threads.                                                                                                                               |
| **Private execution state**  | Groups the threads that execute within its resource environment.                                                                                                        | Has its own stack and saved CPU register state, including the program counter.                                                                                                                         |
| **Scheduling**               | Is not the unit placed on a CPU by the scheduler.                                                                                                                       | Is the schedulable unit; the scheduler runs threads on CPU cores.                                                                                                                                      |
| **Kernel representation**    | Is represented by a [Process Control Block (PCB)](#The%20Process%20Control%20Block%20%28PCB%29) that records process-level identity, resource, and address-space state. | Is represented by a [Thread Control Block (TCB)](#The%20Thread%20Control%20Block%20%28TCB%29) that records thread-specific scheduling and execution state, including the context needed for switching. |

Consequently, while the descriptor table remains unchanged, FD `4` indexes the same table entry and reaches the same open file description for every thread in the process.

### The Process Control Block (PCB)

The Process Control Block (in Linux, known as the `task_struct`) is the definitive data structure representing a process inside the operating system. It is the kernel's internal ledger tracking every single detail about a process's state, memory boundaries, and security permissions.

When a Context Switch occurs, this is exactly where the kernel saves the CPU registers.

**What the PCB Contains:**

- **Identification & Security:** Process ID (PID), Parent Process ID (PPID), and the User/Group IDs that dictate what the process is allowed to touch.
- **Execution State:** The current state of the process (Runnable, Blocked, Stopped, Zombie), the saved Program Counter (PC), and the saved CPU registers from the last time it was evicted from the CPU.
- **Scheduling & Accounting:** CPU priority levels, total CPU time consumed, and memory usage limits.
- **Memory Management:** Pointers defining the boundaries of the process's specific Code, Data, Heap, and Stack sections. Crucially, it holds the pointer to the process's **Page Table**, which the MMU uses to translate its virtual memory into physical RAM.
- **I/O and Resources:** The Per-Process [File Descriptors (FDs)](02%20The%20Anatomy%20of%20a%20Process.md#File%20Descriptors%20%28FDs%29) table, tracking all open files, network sockets, and pipes.
- **Inter-Process Communication (IPC):** Metadata tracking any semaphores, mutexes, shared memory segments, or message queues the process is currently using to talk to other processes.

### The Kernel Process Table

Because a system might have thousands of active processes, the kernel cannot search through them one by one. It organizes them using the **Kernel Process Table**.

- **The Mapping:** It is a highly optimized kernel-space data structure (functioning like a hash map) that maps a numeric **PID to its specific PCB**.
- **O(1) Lookups:** This allows the OS scheduler and system calls to find a process instantly.
- **Real-World Example:** If you type `kill -9 4052` in your terminal, the kernel immediately checks the Process Table for PID `4052`, retrieves its PCB, checks if your user has the security permissions to modify it, and then forcefully changes its execution state to Terminated.

## Daemons

A **daemon is a role and lifecycle convention, not a kernel primitive**. From the kernel's perspective, a daemon is an ordinary process with the same PID, virtual address space, file descriptors, threads, scheduling state, and other resources as any other process.

What makes a process a daemon is how it is used: it is typically long-lived, operates independently of an interactive user session, and provides a persistent service or performs recurring system work. Examples include SSH servers, database servers, logging systems, schedulers, and network services.

> [!note] Where the name "daemon" comes from
>
> The word **daemon** comes from the Ancient Greek *daímōn*, which referred to a spirit or supernatural being. Unlike the modern word **demon**, a *daímōn* was not necessarily evil; it could simply represent an unseen force or agent acting in the world.
>
> Computing adopted **daemon** as a fitting name for programs that operate without direct user interaction, quietly performing work on behalf of the system. The term is also commonly associated with **Maxwell's demon**, the hypothetical agent from a physics thought experiment that continuously observes and acts on a system in the background.

Daemons commonly:

- remain alive for long periods, sometimes for the entire system uptime;
- wait for requests, events, timers, or other work rather than continuously consuming CPU;
- operate independently of an interactive terminal or login session;
- start automatically during system initialization or when their service is first needed;
- expose functionality to other processes through sockets, pipes, files, or other IPC mechanisms.

> [!info] Daemons and Services
>
> The terms **daemon** and **service** are closely related but describe slightly different perspectives. A daemon refers primarily to the **process performing the work**, while a service refers more broadly to the functionality being provided and managed.
>
> On Unix-like systems, services are commonly implemented by one or more daemon processes. On Windows, the corresponding operating-system concept is normally called a **Windows Service**.

### Common Use Cases

Daemons are useful whenever some functionality must remain available independently of a particular interactive user session. Their work is often event-driven or periodic: the process spends much of its lifetime waiting, then wakes when there is something to handle.

Common use cases include:

- **Network services:** SSH servers, web servers, DNS servers, proxies, and database servers wait for incoming connections or requests and respond as needed.
- **Logging:** logging daemons collect messages from applications and the kernel, then store, forward, filter, or rotate them.
- **Scheduled work:** schedulers such as `cron` remain available to start jobs at configured times.
- **Monitoring and observability:** monitoring agents collect metrics, logs, traces, health information, and other runtime data.
- **Networking infrastructure:** DHCP clients, VPN agents, routing daemons, and network managers maintain connectivity and react to network changes.
- **Background maintenance:** daemons can perform tasks such as cache refreshes, cleanup, log rotation, backups, certificate renewal, or periodic synchronization.
- **Queue and job processing:** worker processes can wait for messages or jobs and process them as they arrive.
- **System coordination:** some daemons provide shared functionality to other processes through sockets, files, pipes, or other IPC mechanisms.

The common pattern is not that the work is secondary, but that it must continue to exist **without requiring a user to keep an interactive program or terminal session open**. A web server, for example, may be the primary workload of an entire machine while still fitting the daemon role.

### Daemon vs. Background Process

A **background process** is a process executing without occupying the user's interactive shell. For example, a shell may start a command in the background using `&`.

A daemon is often associated with background execution, but the concepts are not equivalent. A short-lived command started with `&` may still belong to the user's session, inherit its terminal and standard streams, and terminate when that session ends. It is therefore a background process without necessarily being a daemon.

The defining property of a daemon is instead its independence from an interactive user session and its persistent operational role.

> [!example] Containers: a daemon does not have to "go into the background"
>
> Containers are a useful example of why defining a daemon simply as a **background process** is incomplete.
>
> A web server running inside a [container](10%20Virtualization%20and%20Containerization.md#Containers) is commonly the container's main process and may run as **PID 1** inside it. The server normally stays in the foreground rather than performing traditional daemonization. This allows the container runtime to directly observe its lifetime, collect its standard output and error, and detect when it terminates.
>
> Nevertheless, the server can still fulfill the role normally associated with a daemon: it is long-lived, operates independently of an interactive user session, waits for requests, and provides a persistent service.
>
> **Foreground and background describe how a process is attached to and managed by its execution environment; daemon describes its operational role and lifecycle.**

### Traditional Daemonization

Historically, Unix programs often had to make themselves independent of the interactive session that launched them. This procedure is commonly called **daemonization**.

Traditional daemonization commonly follows this sequence:

1. **Fork and exit the original parent:** The child inherits its parent's process group but receives a new PID, so it is not a process-group leader. The original parent exits, leaving the child able to call `setsid()`.
2. **Create a terminal-less session:** The child calls `setsid()`, becoming the leader of a new session and process group with no controlling terminal. This detaches the session from the launching terminal, but it does not close or redirect file descriptors that the process already inherited; a descriptor connected to that terminal remains usable until the process closes or replaces it.
3. **Optionally fork again:** The session leader forks and the intermediate parent exits, so the final daemon is not a session leader. On Unix semantics that allow a session leader without a controlling terminal to acquire one by opening a terminal device, this prevents the final daemon from doing so accidentally. POSIX does not require a particular mechanism for acquiring a controlling terminal, so the second fork is a portability-oriented historical precaution rather than a universal requirement.
4. **Clean up the inherited execution environment:** The final process chooses an appropriate working directory and file-creation mask, closes unneeded inherited [file descriptors](02%20The%20Anatomy%20of%20a%20Process.md#File%20Descriptors%20%28FDs%29), redirects standard input, output, and error to deliberate destinations, and establishes the signal dispositions and masks required by its lifecycle. Closing or redirecting standard streams is separate from the terminal detachment performed by `setsid()`.

These steps were conventions used to achieve the daemon's desired lifecycle rather than requirements imposed by the kernel.

### Lifecycle Control Before Service Managers

Terminal detachment made a daemon independent of its launcher, but it did not provide an interface for operating the service afterward. Before service managers centralized that work, an init script or other service-specific control tool commonly started the daemon, used a PID file to identify it, and requested lifecycle actions by sending it signals. The daemon and its control tool therefore had to agree on the PID-file location and on the meaning of the signals they used.

- **Stopping and restarting:** A control tool could send `SIGTERM` to request a graceful shutdown, then start a replacement process for a restart. Graceful shutdown depended on the daemon implementing the necessary cleanup behavior; signal delivery alone did not supply it.
- **Reloading configuration:** A daemon could treat `SIGHUP` as a reload request by convention. The signal has no universal reload semantics, so a tool could not assume that every daemon supported it.
- **Suspending and resuming:** An authorized operator could stop execution with `SIGSTOP` and resume it with `SIGCONT`. This changes the process's execution state but does not coordinate application-level work, so it is distinct from a graceful service operation.
- **Failure recovery and status:** Scripts could inspect a PID file or process state, but they had to handle stale files, PID reuse, logging, and restart policy themselves.

### PID Files

A **PID file** is an application-maintained file that publishes the numeric PID chosen to represent a service. A service-specific control tool can use its stable path to find that PID and then inspect or signal the process.

- **Kernel relationship:** Every running process has a kernel-assigned PID, but the kernel does not automatically create or maintain a PID file for it. A PID file is therefore external runtime metadata, historically used to control daemons rather than a part of the process itself.
- **Staleness and reuse:** Because the kernel does not keep the file synchronized with process lifetime, a PID file can become stale after a crash or unclean shutdown. A PID is also reusable after its original process exits, so reading a number from a PID file does not by itself prove that the process still belongs to the intended service.

Service managers can track the processes they start directly. Applications managed this way often do not need to create PID files themselves.

### Modern Service Managers

Modern Unix-like systems often delegate lifecycle management to a **service manager**. On many Linux distributions, for example, `systemd` starts and supervises services.

A service manager centralizes operations that previously depended on application-specific scripts and conventions: it can start and stop processes, track them, capture their output, manage dependencies, restart them after failures, configure privileges, and coordinate system startup and shutdown.

Because the service manager provides this surrounding lifecycle management, the application usually does not need to perform traditional daemonization. It can remain in the foreground from its own perspective while the service manager ensures that it operates independently as a long-lived service.

## Threads

### Why We Use Threads

Threads let a process create multiple independent execution paths while continuing to share the process's resources and [virtual address space](03%20Memory%20Management.md#The%20Solution:%20Virtual%20Address%20Space%20%26%20MMU%20Isolation). They are useful when an application benefits from **parallel CPU execution**, needs to continue making progress while some work is blocked, or has many independent tasks that should execute concurrently.

- **Multi-Core Parallelism:** A single thread can execute on only one CPU core at a time. If a workload can be divided into independent CPU-bound tasks, multiple runnable threads allow the operating-system scheduler to place those tasks on different cores so they execute simultaneously. This can increase throughput for workloads such as compression, parsing, numerical computation, or processing independent requests.
    - **Limit:** This benefit is limited by the available hardware parallelism. Once an application has more runnable CPU-bound threads than the machine can execute simultaneously, additional threads mostly compete for CPU time. The scheduler must switch between them, increasing scheduling and [context switching overhead](#Context%20Switching%20Overhead) rather than continuing to increase parallelism.
- **Hiding Blocking I/O Latency:** When a thread performs a blocking operation, such as waiting for disk, a database, or another external resource, that thread cannot perform useful application work until the operation completes. Other threads in the same process can continue executing during that time, allowing the application to remain productive while one execution path waits.
    - **Alternative:** Threads are not required for every form of I/O concurrency. With blocking APIs, moving slow operations to another thread can prevent the main execution path from stalling. [Readiness- and completion-based I/O](07%20Socket%20Management.md#Readiness%20and%20Completion%20Compared) lets a smaller number of threads coordinate many outstanding socket operations without dedicating one blocked thread to each operation.
- **Efficient Shared-Memory Communication:** Threads in the same process share the same virtual address space, including the Data/BSS segments and Heap. One thread can therefore produce data and another can consume it without copying the data through an [Inter-Process Communication](08%20Inter-Process%20Communication.md#Process%20Boundaries%20and%20Communication) mechanism.
    - **Trade-off:** Because multiple threads can access the same mutable memory, concurrent access can create [race conditions](../Backend%20Engineering/Concurrency/01%20Concurrency%20Fundamentals.md#Race%20Conditions); correct access requires appropriate [synchronization](../Backend%20Engineering/Concurrency/01%20Concurrency%20Fundamentals.md#Synchronization%20Mechanisms).
- **Lower Per-Worker Resource Cost:** Creating another thread usually requires fewer independent resources than creating another process because the new thread reuses the process's address space, [file descriptor table](02%20The%20Anatomy%20of%20a%20Process.md#File%20Descriptors%20%28FDs%29), and other process-level resources. Each thread still requires its own execution state, including registers, scheduling metadata, and [stack](02%20The%20Anatomy%20of%20a%20Process.md#The%20Stack), but much of the surrounding process state remains shared.
    - **Switching cost:** Switching between threads belonging to the same process is also usually cheaper than switching between threads belonging to different processes because the active virtual address space does not need to change.
- **Bounded Concurrency with Worker Pools:** Applications often receive large numbers of independent units of work, such as requests, jobs, or background tasks. Instead of creating a new OS thread for every task, an application can maintain a bounded **worker pool**. Incoming tasks are placed into a queue, and the existing worker threads repeatedly take tasks from that queue.
    - **Benefit:** A worker pool allows several tasks to execute concurrently while limiting the number of native threads, stacks, and schedulable execution contexts. The worker count can then be chosen according to the workload rather than growing without bound as new work arrives.

Threads therefore provide a useful middle ground between a single execution path and multiple isolated processes. They make parallel execution and inexpensive resource sharing possible, but those advantages come with additional synchronization and scheduling complexity.

### Multi-Threaded Memory Layout

Threads share one virtual address space, but each requires a private stack for its call frames and local variables. A conventional layout diagram with one stack growing down toward the heap depicts the initial thread; sibling threads cannot use that same stack without colliding frames.

Additional threads receive separate stack regions in the same address space. Their placement and reservation depend on the platform, runtime, and thread implementation; Unix-like implementations commonly create such mappings with `mmap`, often reserving fixed-size regions in otherwise unused parts of the address space. A [guard page](02%20The%20Anatomy%20of%20a%20Process.md#Stack%20Overflow) at a stack boundary turns an out-of-bounds stack access into a fault instead of allowing it to overwrite an adjacent mapping. It detects stack growth beyond that region, but it does not add bounds checking to arbitrary [buffers](02%20The%20Anatomy%20of%20a%20Process.md#Buffer%20Overflow).

- **Shared memory:** All threads access the same Text/Code segment, Data/BSS segments, and heap.
- **Private execution state:** Each thread has its own stack and saved CPU registers, including its Instruction Pointer, Base Pointer, and Stack Pointer.

### User-Space Threads (Green Threads & Coroutines)

Besides **OS threads**, also commonly called **native threads**, **kernel threads**, or **system threads**, applications and language runtimes can maintain their own **user-space execution units** and multiplex them over a smaller number of OS threads. Depending on the runtime and programming model, these may be called **Green Threads**, **Fibers**, **Coroutines**, or **Virtual Threads**. These terms are related but not completely interchangeable—for example, a coroutine does not necessarily behave like a thread.

- **Multiplexing Over OS Threads:** The operating system only schedules the underlying native threads. A runtime may internally manage thousands of user-space tasks and decide which one executes whenever one of its OS threads receives CPU time.
- **User-Space Scheduling:** Because the runtime controls these execution units, switching between them can often happen without invoking the kernel scheduler. The runtime saves whatever execution state its abstraction requires and resumes another task on the same OS thread. The exact state depends on the implementation: some abstractions have their own stacks and resumable execution state, while others, such as stackless coroutines, are represented differently.
- **Lower Per-Task Memory Cost:** Every native thread requires its own stack and kernel bookkeeping. Native thread stacks commonly reserve a relatively large **virtual address range**, but this does not mean the entire reservation is immediately backed by physical RAM—the MMU allows the stack to appear contiguous while its physical pages are allocated and mapped as needed. User-space runtimes can still be more memory-efficient because their execution units can start with much smaller stacks, use dynamically growing stacks, or avoid dedicated stacks entirely depending on the model.
- **Lower Scheduling Overhead:** Native threads are managed by the kernel scheduler, so switching between them involves kernel-maintained scheduling and execution state. Switching between user-space tasks can often be handled entirely by the runtime, avoiding a kernel scheduling operation. This makes very large numbers of concurrent tasks more practical than creating the same number of native OS threads.
- **Blocking Depends on the Runtime Model:** If many user-space tasks are multiplexed onto a single OS thread, a synchronous blocking system call can block that OS thread and prevent the other tasks assigned to it from executing. Event-loop systems therefore rely heavily on non-blocking I/O. More sophisticated runtimes can multiplex tasks across multiple OS threads and compensate when one underlying thread blocks, although some operations can still temporarily pin or occupy an OS thread.

### The Thread Control Block (TCB)

Just as the kernel uses a PCB to track an entire process, it uses a **Thread Control Block (TCB)** to track the individual threads executing inside that process. Because the OS scheduler actually dispatches *threads* to the CPU cores, the TCB holds the precise metadata needed to pause, resume, and prioritize that specific thread.

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

Historically, switching from one process to another often required flushing the **Translation Lookaside Buffer (TLB)**. The TLB caches recent virtual-to-physical address translations, but witgit lhout additional metadata the CPU cannot distinguish which process a cached translation belongs to. Since two processes can use the same virtual address while mapping it to completely different physical pages, retaining the previous process's TLB entries would be unsafe.

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
>
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

For example: `nice -n 10 ./program`.

starts a program with a lower scheduling preference than the default. Conversely, decreasing the nice value gives the task a greater share of CPU time, although increasing priority is normally restricted by permissions.

Linux also provides separate **real-time scheduling policies**, such as `SCHED_FIFO` and `SCHED_RR`, whose threads take precedence over ordinary time-sharing tasks. These policies are conceptually closer to strict priority scheduling and must be used carefully because a CPU-bound real-time thread can starve ordinary work.
