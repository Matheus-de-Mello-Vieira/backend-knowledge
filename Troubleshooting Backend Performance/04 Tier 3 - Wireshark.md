# Wireshark

*   There are alternatives tools, as `tcpdump`
*   give low level details, also terminate TLS
*   You can listen the connection between client and reverse proxy, and reverse proxy and backend.
*   https://www.wireshark.org/

## How to use

You can capture from a network interface

*   If you don't see the interfaces, you should enter the wireshark with sudo.
*   you can understand what each interface means on the terminal of ubuntu `ip link show`

Once you a listerning:

*   You can filter by the destination or source, filtering using something like `ip.addr == 23.220.75.245`.
*   You can turn of the option "Reassemble HTTP headers spanning multiple TCP segments" or "Reassemble chunked transfer-coded bodies" on the preferences.

## Example

### HTTP

```bash
curl  -v http://example.com
```

| No | Time        | Source        | Destination   | Protocol | Length | Info                                                                                                         |
|----|-------------|---------------|---------------|----------|--------|--------------------------------------------------------------------------------------------------------------|
| 56 | 2.938918853 | 192.168.1.17  | 23.220.75.245 | TCP      | 74     | 38854 → 80 [SYN] Seq=0 Win=64240 Len=0 MSS=1460 SACK_PERM TSval=3195627682 TSecr=0 WS=128                    |
| 57 | 3.152556543 | 23.220.75.245 | 192.168.1.17  | TCP      | 74     | 80 → 38854 [SYN, ACK] Seq=0 Ack=1 Win=65160 Len=0 MSS=1460 SACK_PERM TSval=659283964 TSecr=3195627682 WS=128 |
| 59 | 3.152595907 | 192.168.1.17  | 23.220.75.245 | TCP      | 66     | 38854 → 80 [ACK] Seq=1 Ack=1 Win=64256 Len=0 TSval=3195627896 TSecr=659283964                                |
| 60 | 3.152691015 | 192.168.1.17  | 23.220.75.245 | HTTP     | 140    | GET / HTTP/1.1                                                                                               |
| 61 | 3.45939839  | 23.220.75.245 | 192.168.1.17  | TCP      | 66     | 80 → 38854 [ACK] Seq=1 Ack=75 Win=65152 Len=0 TSval=659284176 TSecr=3195627896                               |
| 62 | 3.459398575 | 23.220.75.245 | 192.168.1.17  | HTTP     | 1607   | HTTP/1.1 200 OK  (text/html)                                                                                 |
| 63 | 3.45942914  | 192.168.1.17  | 23.220.75.245 | TCP      | 66     | 38854 → 80 [ACK] Seq=75 Ack=1542 Win=62720 Len=0 TSval=3195628203 TSecr=659284181                            |
| 64 | 3.45973905  | 192.168.1.17  | 23.220.75.245 | TCP      | 66     | 38854 → 80 [FIN, ACK] Seq=75 Ack=1542 Win=62720 Len=0 TSval=3195628203 TSecr=659284181                       |
| 65 | 3.762686872 | 23.220.75.245 | 192.168.1.17  | TCP      | 66     | 80 → 38854 [FIN, ACK] Seq=1542 Ack=76 Win=65152 Len=0 TSval=659284489 TSecr=3195628203                       |
| 66 | 3.76270943  | 192.168.1.17  | 23.220.75.245 | TCP      | 66     | 38854 → 80 [ACK] Seq=76 Ack=1543 Win=62720 Len=0 TSval=3195628506 TSecr=659284489                            |

*   56, 57 and 59: TCP handshake
*   60: the client sends the request
    *   61 server acknowledges it
*   62: the server sends back the response
    *   63 client acknowledges it
*   64, 65 and 66: closure handshake

### HTTPS (TLS passthrough)

`curl  -v https://example.com`

| No | Time        | Source        | Destination   | Protocol | Length | Info                                                                                                         |
|-----|--------------|---------------|---------------|---------|------|---------------------------------------------------------------------------------------------------------------|
| 57  | 10.678876358 | 192.168.1.17  | 23.192.228.84 | TCP     | 74   | 54834 → 443 [SYN] Seq=0 Win=64240 Len=0 MSS=1460 SACK_PERM TSval=293004481 TSecr=0 WS=128                     |
| 59  | 10.952528199 | 23.192.228.84 | 192.168.1.17  | TCP     | 74   | 443 → 54834 [SYN, ACK] Seq=0 Ack=1 Win=65160 Len=0 MSS=1384 SACK_PERM TSval=3079788180 TSecr=293004481 WS=128 |
| 60  | 10.952561430 | 192.168.1.17  | 23.192.228.84 | TCP     | 66   | 54834 → 443 [ACK] Seq=1 Ack=1 Win=64256 Len=0 TSval=293004755 TSecr=3079788180                                |
| 62  | 10.963146901 | 192.168.1.17  | 23.192.228.84 | TLSv1.3 | 583  | Client Hello (SNI=example.com)                                                                                |
| 66  | 11.171749256 | 23.192.228.84 | 192.168.1.17  | TLSv1.3 | 2797 | Server Hello, Change Cipher Spec, Application Data, Application Data, Application Data, Application Data      |
| 67  | 11.171777699 | 192.168.1.17  | 23.192.228.84 | TCP     | 66   | 54834 → 443 [ACK] Seq=518 Ack=2732 Win=61568 Len=0 TSval=293004974 TSecr=3079788476                           |
| 69  | 11.184133642 | 192.168.1.17  | 23.192.228.84 | TLSv1.3 | 146  | Change Cipher Spec, Application Data                                                                          |
| 70  | 11.184292594 | 192.168.1.17  | 23.192.228.84 | TLSv1.3 | 152  | Application Data                                                                                              |
| 71  | 11.184529577 | 192.168.1.17  | 23.192.228.84 | TLSv1.3 | 125  | Application Data                                                                                              |
| 96  | 11.379314194 | 23.192.228.84 | 192.168.1.17  | TCP     | 66   | 443 → 54834 [ACK] Seq=2732 Ack=598 Win=64768 Len=0 TSval=3079788685 TSecr=293004987                           |
| 97  | 11.379314425 | 23.192.228.84 | 192.168.1.17  | TCP     | 66   | 443 → 54834 [ACK] Seq=2732 Ack=684 Win=64768 Len=0 TSval=3079788686 TSecr=293004987                           |
| 98  | 11.379314450 | 23.192.228.84 | 192.168.1.17  | TLSv1.3 | 353  | Application Data                                                                                              |
| 99  | 11.379314478 | 23.192.228.84 | 192.168.1.17  | TLSv1.3 | 353  | Application Data                                                                                              |
| 100 | 11.379314506 | 23.192.228.84 | 192.168.1.17  | TLSv1.3 | 127  | Application Data                                                                                              |
| 101 | 11.379314531 | 23.192.228.84 | 192.168.1.17  | TLSv1.3 | 97   | Application Data                                                                                              |
| 102 | 11.379623502 | 192.168.1.17  | 23.192.228.84 | TCP     | 66   | 54834 → 443 [ACK] Seq=743 Ack=3398 Win=60928 Len=0 TSval=293005182 TSecr=3079788687                           |
| 103 | 11.379656156 | 192.168.1.17  | 23.192.228.84 | TLSv1.3 | 97   | Application Data                                                                                              |
| 106 | 11.400516745 | 23.192.228.84 | 192.168.1.17  | TLSv1.3 | 252  | Application Data                                                                                              |
| 107 | 11.400516990 | 23.192.228.84 | 192.168.1.17  | TLSv1.3 | 1353 | Application Data                                                                                              |
| 108 | 11.400667462 | 192.168.1.17  | 23.192.228.84 | TCP     | 66   | 54834 → 443 [ACK] Seq=774 Ack=4871 Win=59520 Len=0 TSval=293005203 TSecr=3079788707                           |
| 109 | 11.400892932 | 192.168.1.17  | 23.192.228.84 | TLSv1.3 | 90   | Application Data                                                                                              |
| 110 | 11.401500617 | 192.168.1.17  | 23.192.228.84 | TCP     | 66   | 54834 → 443 [FIN, ACK] Seq=798 Ack=4871 Win=59520 Len=0 TSval=293005204 TSecr=3079788707                      |
| 116 | 11.602429409 | 23.192.228.84 | 192.168.1.17  | TCP     | 66   | 443 → 54834 [ACK] Seq=4871 Ack=799 Win=64768 Len=0 TSval=3079788908 TSecr=293005182                           |
| 117 | 11.602429692 | 23.192.228.84 | 192.168.1.17  | TLSv1.3 | 90   | Application Data                                                                                              |
| 118 | 11.602429727 | 23.192.228.84 | 192.168.1.17  | TCP     | 66   | 443 → 54834 [FIN, ACK] Seq=4895 Ack=799 Win=64768 Len=0 TSval=3079788909 TSecr=293005182                      |

*   Packets 57–60: TCP handshake
*   Packet 62: ClientHello
    *   That SNI is what many intermediates uses to block a domain.

*   Packet 66: ServerHello + (Encrypted) extensions, cert, Finished
*   Packet 69: Client Finished
*   Packet 70+: Encrypted HTTPS request/response
*   Packets 110–118: TCP teardown

### HTTPS (TLS termination)

You can ask the client write the symmetric key in a place that wireshark can see

*   For curl, it is the enviroment variable `SSLKEYLOGFILE`

```bash
export SSLKEYLOGFILE=~/Downloads/tlskey
curl  -v https://example.com
```

It will crate the file `tlskey` on `~/Downloads`

On wirshark, go to the TLS preferences and give the path of `tlskey` on the field `(PRE)-Master-Secret log filename`

| No | Time        | Source        | Destination   | Protocol | Length | Info                                                                                                         |
|-----|--------------|---------------|---------------|---------|------|---------------------------------------------------------------------------------------------------------------|
| 59 | 2.324242093 | 192.168.1.17 | 23.215.0.138 | TCP     | 74   | 58030 → 443 [SYN] Seq=0 Win=64240 Len=0 MSS=1460 SACK_PERM TSval=2149490412 TSecr=0 WS=128                    |
| 60 | 2.576021609 | 23.215.0.138 | 192.168.1.17 | TCP     | 74   | 443 → 58030 [SYN, ACK] Seq=0 Ack=1 Win=65160 Len=0 MSS=1384 SACK_PERM TSval=535909928 TSecr=2149490412 WS=128 |
| 61 | 2.576064162 | 192.168.1.17 | 23.215.0.138 | TCP     | 66   | 58030 → 443 [ACK] Seq=1 Ack=1 Win=64256 Len=0 TSval=2149490664 TSecr=535909928                                |
| 62 | 2.577636011 | 192.168.1.17 | 23.215.0.138 | TLSv1.3 | 583  | Client Hello (SNI=example.com)                                                                                |
| 63 | 2.782661358 | 23.215.0.138 | 192.168.1.17 | TLSv1.3 | 2797 | Server Hello, Change Cipher Spec, Encrypted Extensions, Certificate, Certificate Verify, Finished             |
| 64 | 2.782693833 | 192.168.1.17 | 23.215.0.138 | TCP     | 66   | 58030 → 443 [ACK] Seq=518 Ack=2732 Win=61568 Len=0 TSval=2149490870 TSecr=535910197                           |
| 65 | 2.784897835 | 192.168.1.17 | 23.215.0.138 | TLSv1.3 | 146  | Change Cipher Spec, Finished                                                                                  |
| 66 | 2.785041228 | 192.168.1.17 | 23.215.0.138 | HTTP2   | 152  | Magic, SETTINGS[0], WINDOW_UPDATE[0]                                                                          |
| 67 | 2.78532821  | 192.168.1.17 | 23.215.0.138 | HTTP2   | 125  | HEADERS[1]: GET /                                                                                             |
| 68 | 2.990346319 | 23.215.0.138 | 192.168.1.17 | TCP     | 66   | 443 → 58030 [ACK] Seq=2732 Ack=598 Win=64768 Len=0 TSval=535910390 TSecr=2149490872                           |
| 69 | 2.990346496 | 23.215.0.138 | 192.168.1.17 | TCP     | 66   | 443 → 58030 [ACK] Seq=2732 Ack=684 Win=64768 Len=0 TSval=535910390 TSecr=2149490873                           |
| 70 | 2.99034651  | 23.215.0.138 | 192.168.1.17 | TCP     | 66   | 443 → 58030 [ACK] Seq=2732 Ack=743 Win=64768 Len=0 TSval=535910390 TSecr=2149490873                           |
| 71 | 2.990346524 | 23.215.0.138 | 192.168.1.17 | TLSv1.3 | 353  | New Session Ticket                                                                                            |
| 72 | 2.99034654  | 23.215.0.138 | 192.168.1.17 | TLSv1.3 | 369  | New Session Ticket                                                                                            |
| 73 | 2.990346555 | 23.215.0.138 | 192.168.1.17 | HTTP2   | 127  | SETTINGS[0]                                                                                                   |
| 74 | 2.99034657  | 23.215.0.138 | 192.168.1.17 | HTTP2   | 97   | SETTINGS[0]                                                                                                   |
| 75 | 2.990599403 | 192.168.1.17 | 23.215.0.138 | TCP     | 66   | 58030 → 443 [ACK] Seq=743 Ack=3414 Win=60928 Len=0 TSval=2149491078 TSecr=535910401                           |
| 76 | 2.990637943 | 192.168.1.17 | 23.215.0.138 | HTTP2   | 97   | SETTINGS[0]                                                                                                   |
| 77 | 2.99144219  | 23.215.0.138 | 192.168.1.17 | HTTP2   | 252  | HEADERS[1]: 200 OK                                                                                            |
| 78 | 2.991442239 | 23.215.0.138 | 192.168.1.17 | HTTP2   | 1353 | DATA[1] (text/html)                                                                                           |
| 79 | 2.991538156 | 192.168.1.17 | 23.215.0.138 | TCP     | 66   | 58030 → 443 [ACK] Seq=774 Ack=4887 Win=59520 Len=0 TSval=2149491079 TSecr=535910441                           |
| 80 | 2.991800348 | 192.168.1.17 | 23.215.0.138 | TLSv1.3 | 90   | Alert (Level: Warning, Description: Close Notify)                                                             |
| 81 | 2.992607111 | 192.168.1.17 | 23.215.0.138 | TCP     | 66   | 58030 → 443 [FIN, ACK] Seq=798 Ack=4887 Win=59520 Len=0 TSval=2149491080 TSecr=535910441                      |
| 82 | 3.295189078 | 23.215.0.138 | 192.168.1.17 | TLSv1.3 | 90   | Alert (Level: Warning, Description: Close Notify)                                                             |
| 83 | 3.295189343 | 23.215.0.138 | 192.168.1.17 | TCP     | 66   | 443 → 58030 [ACK] Seq=4887 Ack=799 Win=64768 Len=0 TSval=535910600 TSecr=2149491078                           |
| 84 | 3.295189358 | 23.215.0.138 | 192.168.1.17 | TCP     | 66   | 443 → 58030 [FIN, ACK] Seq=4911 Ack=799 Win=64768 Len=0 TSval=535910600 TSecr=2149491078                      |

*   The 66 contains the informations about HTTP2
    *   inside it, there is a field `Stream: Settings`, that contains for example, Max current streams. 

## Investigating the slowness

*   If the download is slowing, there will be a huge time gap between one package of body and another,
*   If the connection is slowing, there will be a lot of TCP retransmission of the TCP handshake's `SYN` 
*   If the server isn't reading fast enough, so the receive buffer gets full, so the client can't send data, there will:
    *   a decreasing windows size and packages size, until the window size reach 0.
    *   a package from the client to the client with `[TCP Windown Full]`, following repeated probes if the widows still 0, until it gives up.

