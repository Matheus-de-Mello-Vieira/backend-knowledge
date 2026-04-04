# Troubleshooting Backend Performance

## Introduction

Performance troubleshooting can be done at several levels:

* Tier 1: client perspective only.
  * The backend is a black box, regardless of whether there is a CDN, API gateway, load balancer, or proxy in front of it.
  * Example: browser DevTools.
* Tier 2: intercepting proxy.
  * A debugging proxy sits between client and server.
  * Useful for mobile apps, desktop apps, and service-to-service debugging.
* Tier 3: packet capture.
  * Capture traffic at lower network layers for transport-level and protocol-level analysis.

## Tier 1: DevTools

DevTools shows that a request is slow, but not necessarily why.

### Interface

Use the browser Network tab.

* Turn on `Preserve log` so entries survive reloads and navigation.
* Disable cache while DevTools is open.

### Useful request and response columns

Right-click the header row to enable additional columns.

Important things to inspect:

* `Size`.
  * Hover to see the uncompressed size.
  * A large compressed-vs-uncompressed gap implies more compression and decompression CPU work.
  * Comparing size against MTU can also give hints about fragmentation or transfer cost.
* Browser priorities.
* Connection IDs.
  * Helps you see whether the browser is reusing connections or opening new ones.

### Waterfall

The waterfall shows how long each phase took.

#### Resource scheduling

* Queueing.
  * Browsers limit simultaneous connections, so extra requests wait.

#### Connection start

* Stalled.
  * No requests are ahead in line, but the browser still lacks resources to start this one.
* DNS lookup.
* Initial connection.
  * TCP or QUIC connection setup.
* SSL.
  * TLS handshake time.
  * For HTTP/3, `Initial connection` and `SSL` usually overlap entirely.

#### Request and response

* Request sent.
* Waiting for server response.
  * Roughly time to first byte, or at least time until the browser starts receiving the response.
* Content download.
  * Time to receive the rest of the response body.

### How to interpret slowness

* High `Waiting for server response`.
  * The server is slow to process or upstream dependencies are slow.
* High `Content download`.
  * The server is slow to deliver the body after starting the response, or the network throughput is poor.
* High `Initial connection`.
  * Connection establishment is slow.
  * This can point to slow accept handling, slow TLS, or client-side network issues.
* High `DNS lookup`, `Initial connection`, and `Waiting for server response` together.
  * Likely client-side network trouble, such as a VPN or unstable route.

## Tier 2: MITM Proxy

A debugging proxy intercepts traffic between client and server.

* Useful for mobile and desktop apps without DevTools.
* Useful for service-to-service traffic inspection.

This section uses [mitmproxy](https://www.mitmproxy.org/).

### As a proxy

#### `mitmproxy`

```bash
mitmproxy -p 8181
```

It starts listening and opens an interactive terminal UI.

Sometimes clients bypass proxies because of `NO_PROXY` settings. One example:

```bash
curl --proxy http://127.0.0.1:8181 --noproxy "" http://127.0.0.1:80/
```

You can inspect the request inside `mitmproxy` much like DevTools.

#### `mitmdump`

```bash
mitmdump -p 8181
```

* Terminal-only mode.
* Use `--verbose` and `--flow-detail 4` for more detail.

#### `mitmweb`

```bash
mitmweb -p 8181
```

* Web interface instead of terminal UI.

### Intercepting TLS

To inspect HTTPS, the MITM proxy has to terminate TLS.

That means installing the MITM root certificate in the client trust store:

1. Open `http://mitm.it/` while traffic is passing through the proxy.
2. Download the `.pem` for the client OS.
3. Add it to the certificate store.

Limitations:

* Some clients use their own certificate store.
* Some apps use certificate pinning and will reject the proxy certificate.

### Testing one specific program

Many Linux programs respect these environment variables:

```bash
http_proxy="http://127.0.0.1:8080" \
https_proxy="http://127.0.0.1:8080" \
ftp_proxy="http://127.0.0.1:8080" \
no_proxy="localhost,127.0.0.1" \
program-name
```

That way only the selected program uses the proxy.

### As a reverse proxy

To inspect traffic between two services, run MITM as a reverse proxy:

```bash
mitmweb --mode reverse:http://localhost:9002 -p 9000
```

Here `http://localhost:9002` is the real backend, and clients talk to port `9000`.

## Tier 3: Wireshark

Wireshark provides lower-level visibility than DevTools or MITM tools.

* `tcpdump` is a CLI alternative.
* Useful for packet-level timing, retransmissions, window sizes, and transport behavior.
* Can inspect both client-to-proxy and proxy-to-backend traffic.

### How to use it

Capture traffic from a network interface.

* If you do not see interfaces, you may need elevated privileges.
* On Linux, `ip link show` helps identify interfaces.

Once capturing:

* Filter by source or destination, for example:

```text
ip.addr == 23.220.75.245
```

You can also disable HTTP reassembly options if you want to see segment boundaries more directly.

### Example: HTTP

With:

```bash
curl -v http://example.com
```

Typical sequence:

* TCP handshake.
* HTTP request.
* TCP ACK for the request.
* HTTP response.
* TCP ACK for the response.
* Connection teardown.

### Example: HTTPS with TLS passthrough

With:

```bash
curl -v https://example.com
```

Typical sequence:

* TCP handshake.
* `ClientHello`.
* `ServerHello` and handshake flight.
* Client finished message.
* Encrypted application data.
* TCP teardown.

Interesting detail:

* The SNI in `ClientHello` is visible before encryption and is often enough for intermediaries to identify the target domain.

### Example: HTTPS with TLS decryption

You can export symmetric session secrets for some clients and let Wireshark decrypt the traffic.

For `curl`:

```bash
export SSLKEYLOGFILE=~/Downloads/tlskey
curl -v https://example.com
```

Then configure Wireshark TLS preferences with the key log file path.

Once configured, Wireshark can show decrypted HTTP/2 frames such as:

* `SETTINGS`
* `HEADERS`
* `DATA`

### How to interpret slowness in Wireshark

* Large gaps between response body packets.
  * Slow download or application pacing.
* Many retransmissions during connection setup.
  * Network issues or packet loss.
* Shrinking TCP window size until zero.
  * The receiver is not reading fast enough and its receive buffer is filling up.
* Zero-window probes.
  * Strong sign that the receiving side is the bottleneck.

## Real-World Performance Analysis

### 1. Frontend performance

The frontend may be the source of the slowness:

* Too many requests.
* Unnecessary requests.
* Poor client behavior.

Use DevTools or MITM tools to confirm.

### 2. Backend bottleneck

Use DevTools first:

* If time to first byte is high, the backend or one of its dependencies is slow.

Then use Wireshark or proxy-level tools:

* Inspect traffic between backend and database.
* If the slowness is due to a large payload, the backend may be asking for more data than necessary.

### 3. One backend behind a load balancer is slow

A common symptom:

* Some requests are fast.
* Some are consistently slow.

That often means one backend instance is unhealthy or overloaded.

How to isolate it:

* Put a reverse proxy in front of each backend separately.
* Or test one backend at a time behind the balancer.
* Once identified, inspect that backend as a normal backend bottleneck case.

### 4. Database performance

This can look similar to a backend bottleneck, but packet captures often show gaps specifically during backend-to-database exchanges.

## Other Tools

### `nc`

Establish a raw TCP connection:

```bash
nc example.com 80
```

### `curl`

Useful for HTTP and HTTPS:

* `-v` for verbose mode.
* `--trace <file>` for a detailed request/response dump.

### `tcpdump`

Terminal-oriented packet capture.

### `traceroute`

Shows the hops between client and server.

### `ss`

`ss` displays socket information and is a modern replacement for `netstat`.

```bash
ss -ltn
```

Meaning:

* `-l`: listening sockets only.
* `-t`: TCP sockets.
* `-n`: numeric addresses.

Example output:

```text
State   Recv-Q   Send-Q   Local Address:Port   Peer Address:Port
LISTEN  0        4096     0.0.0.0:8080         0.0.0.0:*
```

Interpretation:

* For `LISTEN` sockets:
  * `Recv-Q`: current accept queue occupancy.
  * `Send-Q`: configured listen backlog.
* For `ESTABLISHED` sockets:
  * `Recv-Q`: data sitting in the kernel receive buffer that the application has not read yet.
  * `Send-Q`: data buffered for sending that the peer has not yet acknowledged.
