# Reading and sending data

* Once the connection is established, how to read and send data?

## Receiving buffer

* Once a connection is established, the OS creates two buffers: send and receive.
* the receive buffer will be filled with client data, and the send buffer with server data.
* reviving data:
  1) the client sends data on a connection
  2) the Kernel puts data in receive buffer
     * The Kernel receive data without backend asking for it.
  3) The ACKs and update window
     *  The ACKs may delay and update the window.
       * The ACKs usually are trigged by time or by amount of data received, otherwise every bit would cause a ACK.
     * The kernel ACKs according to the remain space in the receiving buffer, in order to don't overflow it.
  4) App calls read to copy data
     * copy is expensive
     * The process can use `read()` or `recv()` to do it
       * `read()` is a general-purpose system call for reading from any file descriptor (including sockets).
       * `recv()`  is specifically for sockets and offers extra options.
       * by default, sockets are blocking
         * it means that `read()` or `recv()` will block the process until data arrives
         * else, both will return immediately; error if no data (`EAGAIN`/`EWOULDBLOCK`)
     * there is a function `epoll_wait()` that allows the process wait until data is available in one of the connections of interest.
  5) The kernel discards the copied data from the buffer
  6) Now the backend can decrypt, parse and process the data

## Send buffers

1. the process calls `send()`
   * It will copy the data from the process into the send buffer
2. The kernel will wait enough information to dispatch to the client.
   * For example, the Nagle's algorithm usually waits for the maximum segment size, for efficiency purpose.
     * most process disable  Nagle, for latency sake.
3. As long the client ACK the data, the kernel sends the data from the buffer to it. 

## Problems with reading and sending

* backend doesn't read fast enough
* receive queue is full
* clients slows down'