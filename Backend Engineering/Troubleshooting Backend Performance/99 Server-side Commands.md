# Server-side Commands

## Command ss

The `ss` command in Linux is a utility used to display detailed information about sockets. It is often considered a faster and more modern replacement for the older `netstat` command.

It provides statistics and information about different types of network connections: TCP, UDP, RAW sockets, Unix domain sockets, etc.

```
ss -ltn
```

Where

*   `ss -l`: show only listening sockets.
*   `ss -t`: show TCP sockets.
*   `ss -n`: show numerical addresses instead of resolving hostnames/ports.

You will get something like (I capped to only one line)

```
State   Recv-Q   Send-Q   Local Address:Port   Peer Address:Port
LISTEN  0        4096     0.0.0.0:8080         0.0.0.0:*
```

Where:

*   For `LISTEN` sockets:
    *   `Recv-Q` : accept queue - the current number of pending connections sitting in the accept queue.
    *   `Send-Q`: listen backlog - the upper bound of how many can sit in the accept queue.

*   For `ESTABLISHED` sockets:
    *   `Recv-Q`: how much data is sitting in the kernel buffer, not yet read by the application.
    *   `Send-Q`: how much data is buffered for sending, not yet acknowledged by the peer.