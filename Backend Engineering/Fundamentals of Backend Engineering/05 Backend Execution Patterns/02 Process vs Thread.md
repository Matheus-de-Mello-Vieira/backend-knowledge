# Process vs Thread

## Process

* From CPU pespective, it is nothing but a set of instructions
* Has an isolated memory
  * A reserved space in memory, that only the process can read (or cheaters)
  * You can assign multiple process to the same memory memory, so they share memory.
* Every process has a PID, that identify
* Scheduled in the CPU
  * CPU is a scarce resource, and many processes compete for it.
  * once your process make request that makes it idle (as read from disk), the kernel remove it from CPU immediataly.
    * been kicking out from CPU is something that you want to avoid

## Thread

* Also called Light Weight Process (LWP)
* A set of instructions
* Shares memory with parent process
* Has a ID
* Scheduled in the CPU

## Singles Threaded Process

* One process with a single thread
* Simple
* Example NodeJS

## Multi-processes

* App has multiple processes
* Each has it own Memory
* Examples Nginx and Postgres
* Take advantage of multi-cores
* More memory but isolated
* Redis backup routine (COW)
  * it gets whatevery is in cache and flushes into the disk. It sounds simple, but is really hard to implement:
    * if someone change on the meanwhile 
      * it can't
        * write anyway: it will cause inconsistency
        * lock the writing: it will reduce the throughput, cancels the redis proposes out
        * copy at memory first, because it will double the memory usage
  * COW stands for Copy on Write.
  * When a backup process is reading main Redis' memory and writing it into disk, if a page is about to be changed, the system copy it into the memory of a process.

## Multi-Threaded

* One Process, multiple threads
* Shared Memory (compete)
* Take advantage of multi-cores
* Require less memory
* Race conditions, if you don't properly lock stuffs.
* Lock and Latches (SQL Server)
  * Lock can cause multi-threaded applications slower than the same instructions running sequentially.
* Apache, Envoy

## How many is too many?

* CPU context switch is costly. More processes threads means more CPU context switches.
* Rule of thumb -> # Cores = # Processes