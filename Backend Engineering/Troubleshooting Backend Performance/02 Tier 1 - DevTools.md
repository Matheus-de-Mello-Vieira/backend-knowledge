# Tier 1 - DevTools

You see if a request is slugging, but not why it is slugging.

## Interface

We will use the tab "network" of Google Chome.

*   Turn on "preserve log", so the network tab won't be cleaned everytime the page the reloaded or changed.
*    disable cache, to avoid caching while DevTools is open.

### Request/Response Columns

Click with mouse right button, on the collumn headers, that will open a menu to choose which columns to show.

*   hover the mouse on "size" column to get the uncompressed size
    *   bigger the difference, more is the CPU usage to compression and decompression.
    *   Compare the size with the MTU (Maximum Transmission Unit) of your network, so you can have a tip about slowness.
*   You can see the brower Priorities
*   see the Connection IDs on requests
    *   it is important to know if you a openning new connections or reusing the existent ones.

*   You can click on a row to see the details

### Waterfall

Here we can see how much time each part took.

*   Resource Scheduling
    *   Queuering: The brownser have a limit of simulataneos connections, so the requests that surpass it get enqueued.
*   Connection Start
    *   Stalled: There are no other requests ahead in the queue, but there aren’t enough resources to fulfill this one.
    *   DNS Lookup
    *   Initial connection: the handshakes between the server and client
        *   SSL: the SSL/TLS handshakes
            *   The Initial connection time minus the SSL times is the TCP handshake time
            *   if HTTP3, the "Initial connection" and "SSL" are always equal.
*   Request/Response
    *   Request sent
    *   Wainting for server response: time for first response byte. (TTFB)
        *   it isn't literally the first byte, because the browser read a buffer from a socket.
    *   Content Download: time for last response byte (TTLB)

## Identifying the slowness

*   If the "Wainting for server response" is high, the server is delaying to process the request
*   If the "Content Download" is  high, the server is delaying to deliver the bytes after the first one
*   If "Initial connection" is high, the server is delaying to accept new connections, probability is getting filled
*   If all "DNS Lookup", "Initial Connection", "Waiting for server" are high, you have network issues on the client
    *   for example, the client is using a VPN
    *   The ‘Content Download’ phase is not necessarily affected, because while the first byte may be delayed, the rate at which subsequent bytes arrive remains the same unless the network itself becomes a bottleneck.
