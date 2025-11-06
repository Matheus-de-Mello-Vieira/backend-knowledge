# Real-world performance analysis

1)   Frontend performance
     *   If front-end does too many requests that there is no reason, and it is causing the slowness.
         *   you can use DevTools or MITM.
2)   Backend bottleneck
    *   Se DevTool to see the waterfall.
        *   if the  time for first response byte is high, you can use Wireshark to see the communication between the backend and database.
            *   it the slowness is due a huge response payload, probably it is because the backend is making a wider request than the necessary.
3)   One backend (out of two behind the load balancer) is the bottleneck.
     *   sometimes the request are fast, and sometimes they are slow: that is the giveaway.
     *   to investigate it, put one MITM reverse proxy in front of each backend, or put the reverse proxy on one backend per time.
         *   once you identify it, back to the case 2.
4)   Database performance
     *   The case is similar to 2, but in this case there is a time gap between two packages.

