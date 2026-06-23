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

Here is a rewritten, highly polished version of your documentation. It improves the structural flow, enhances scannability with clearer formatting, and adds brief contextual explanations to make the technical steps more intuitive for the reader.

## Tier 2: MITM (Man-in-the-Middle) Proxy

A debugging proxy intercepts and inspects network traffic flowing between a client and a server.

### Why use a MITM proxy?

- **No DevTools:** Essential for mobile apps, desktop applications, or IoT devices where standard browser developer tools are unavailable.
- **Backend Inspection:** Ideal for analyzing service-to-service (microservice) communication.

> 💡 *Note: The examples below utilize the open-source **[mitmproxy](https://www.mitmproxy.org/)** suite.*

### Regular Proxy Modes

In standard proxy mode, the client explicitly routes its traffic through the proxy.

#### 1. Interactive Terminal (`mitmproxy`)

Starts an interactive, keyboard-driven terminal UI.

```bash
mitmproxy -p 8181
```

- **Tip:** If a local client bypasses the proxy due to native `NO_PROXY` environment defaults, force compliance by explicitly resetting the parameter:

  ```bash
  curl --proxy http://127.0.0.1:8181 --noproxy "" http://127.0.0.1:80/
  ```

#### 2. Command-Line Stream (`mitmdump`)

Prints all intercepted traffic directly to the standard output (similar to `tcpdump`).

```bash
mitmdump -p 8181
```

- **Verbose Logging:** Use `--verbose` and `--flow-detail 4` to capture full headers and bodies.

#### 3. Web Interface (`mitmweb`)

Launches a browser-based graphical user interface for a cleaner, DevTools-like experience.

```bash
mitmweb -p 8181
```

### Intercepting TLS/HTTPS Traffic

To inspect encrypted HTTPS traffic, the proxy must perform a **TLS termination handshake** with the client and establish a new secure connection with the destination server. This requires the client to trust the proxy's custom certificate authority (CA).

#### The Local CA Certificate

The first time you run `mitmproxy`, it automatically generates a unique, self-signed CA certificate on your machine to prevent unauthorized interception by other users.

- **Location:** `~/.mitmproxy/mitmproxy-ca-cert.pem`

#### Installation Workflows:

- **For GUI Clients (Browsers, OS-level apps):**

  1. Route your client's traffic through the proxy.
  2. Navigate to **`http://mitm.it/`** in a browser on the client device.
  3. Download the specific `.pem` or certificate file matching the client OS and add it to the system root store.

- **For Programmatic Runtimes (NodeJS, Python, Go):**

  Many application runtimes completely ignore the operating system's root certificate store. If your code throws errors like `UNABLE_TO_VERIFY_LEAF_SIGNATURE` or `certificate signed by unknown authority`, you must explicitly pass the `~/.mitmproxy/mitmproxy-ca-cert.pem` certificate into their environments.

- **Certificate Pinning:** Apps enforcing strict certificate pinning (common in high-security mobile apps) will reject the proxy's signed certificate entirely and break the connection, regardless of these environment adjustments.

#### Runtime-Specific CA Configuration

Instead of changing system-wide security settings, isolate the scope to your development runtime using environment variables.

#### Node.js

Node.js uses a hardcoded list of built-in standard CAs. You can inject the mitmproxy certificate by passing the `NODE_EXTRA_CA_CERTS` variable:

```bash
NODE_EXTRA_CA_CERTS="$HOME/.mitmproxy/mitmproxy-ca-cert.pem" \
node app.js
```

#### Python

Most Python HTTP clients (like `requests` and `httpx`) rely on the `certifi` package for validation rather than the OS. They look for the `REQUESTS_CA_BUNDLE` or `SSL_CERT_FILE` variables:

```bash
# For requests / httpx
REQUESTS_CA_BUNDLE="$HOME/.mitmproxy/mitmproxy-ca-cert.pem" \
python script.py

# Alternative / generic fallback
SSL_CERT_FILE="$HOME/.mitmproxy/mitmproxy-ca-cert.pem" \
python script.py
```

#### Go (Golang)

Go binaries are statically compiled and typically read from standard system paths (like `/etc/ssl/certs/ca-certificates.crt` on Linux) to build their root trust store.

While you can override this globally in your terminal using `SSL_CERT_FILE="$HOME/.mitmproxy/mitmproxy-ca-cert.pem"`, the most robust and idiomatic way inside a Go program is to explicitly load the proxy's certificate, append it to a custom `x509.CertPool`, and inject it into your custom `http.Client`.

```go
package main

import (
	"crypto/tls"
	"crypto/x509"
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
)

func main() {
	// 1. Locate and read the mitmproxy CA certificate file
	homeDir, err := os.UserHomeDir()
	if err != nil {
		log.Fatalf("Failed to get home directory: %v", err)
	}
	certPath := filepath.Join(homeDir, ".mitmproxy", "mitmproxy-ca-cert.pem")

	pemCerts, err := os.ReadFile(certPath)
	if err != nil {
		log.Fatalf("Failed to read mitmproxy CA cert: %v", err)
	}

	// 2. Create a new x509 CertPool and append the proxy cert
	certPool := x509.NewCertPool()
	if ok := certPool.AppendCertsFromPEM(pemCerts); !ok {
		log.Fatalf("Failed to append mitmproxy CA to cert pool")
	}

	// 3. Pass the cert pool to your custom http.Client via TLSClientConfig
	client := &http.Client{
		Transport: &http.Transport{
			TLSClientConfig: &tls.Config{
				RootCAs: certPool,
			},
		},
	}

	// Now you can safely make requests through your mitmproxy setup
	resp, err := client.Get("https://example.com")
	if err != nil {
		log.Fatalf("Request failed: %v", err)
	}
	defer resp.Body.Close()

	fmt.Printf("Success! Status code: %d\n", resp.StatusCode)
}
```

**Why this is preferred:** This method limits the scope of your proxy trust strictly to this specific `http.Client` instance inside your code, ensuring your system-wide security configurations remain untouched and secure.

### Target-Specific Proxying (Linux)

Instead of routing global system traffic through the proxy, isolate the scope to a single terminal command or application by prefixing it with inline environment variables:

```bash
http_proxy="http://127.0.0.1:8181" \
https_proxy="http://127.0.0.1:8181" \
no_proxy="localhost,127.0.0.1" \
program-name
```

### Reverse Proxy Mode

When you cannot easily modify a client's proxy settings, you can deploy the proxy *in front* of the target backend service as a reverse proxy.

Bash

```bash
mitmweb --mode reverse:http://localhost:9002 -p 9000
```

- **How it works:** The client is configured to send requests directly to port `9000`. The proxy intercepts, logs the traffic, and transparently forwards the request to the actual backend service running on port `9002`.

### Docker Container Proxying

When containerizing applications, routing traffic through `mitmproxy` requires configuring both the container's network routing and its internal security trust store.

#### 1. Network Routing (`localhost` vs. Host)

Inside a container, `localhost` refers to the container itself, not your development machine. To route traffic out to a proxy running on your host machine, use the internal host gateway string:

- **Proxy Address:** `http://host.docker.internal:8181`

#### 2. Injecting the CA Certificate

Because containers do not inherit your host machine's root trust store, your containerized application will throw TLS/SSL verification errors unless it is explicitly told to trust the proxy.

#### Option A: Quick Runtime Injection (Volume Mounting)

For a quick test without rebuilding your Docker image, you can bind-mount your local `mitmproxy` certificate directly over the container's default CA bundle.

```bash
docker run -it \
  -e http_proxy="http://host.docker.internal:8181" \
  -e https_proxy="http://host.docker.internal:8181" \
  -v "$HOME/.mitmproxy/mitmproxy-ca-cert.pem:/etc/ssl/certs/ca-certificates.crt:ro" \
  my-app-image
```

**Caution:** This completely overwrites the container's built-in root certificates. If your application needs to talk to both `mitmproxy` and public internet APIs simultaneously, use Option B instead.

#### Option B: Updating the OS Cert Store (Dockerfile)

The robust approach is to copy your proxy certificate into the image during the build phase and append it to the system bundle using the OS-native certificate manager.

**For Debian / Ubuntu Images:**

```bash
FROM node:20-slim

# Install system certificates utility
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*

# Copy local proxy cert into the OS trust folder (Must use the .crt extension)
COPY ./mitmproxy-ca-cert.pem /usr/local/share/ca-certificates/mitmproxy-ca.crt

# Rebuild /etc/ssl/certs/ca-certificates.crt safely
RUN update-ca-certificates

CMD ["node", "app.js"]
```

**For Alpine Linux Images:**

```bash
FROM alpine:3.20

RUN apk add --no-cache ca-certificates

# Alpine also reads from /usr/local/share/ca-certificates/
COPY ./mitmproxy-ca-cert.pem /usr/local/share/ca-certificates/mitmproxy-ca.crt

RUN update-ca-certificates

CMD ["./my-binary"]
```

**Tip:** Tools like `update-ca-certificates` are strict about file extensions. Even though the underlying encoding is identical, you must rename or copy your `.pem` file to use a `.crt` extension inside the container destination path.

### Mocking and Testing with Server Replay

The `--server-replay` option allows you to take a previously recorded file of HTTP/HTTPS traffic and use it to **mock the remote server entirely**.

When a client makes a request, `mitmproxy` intercepts it, searches the saved session file for a matching historical request, and immediately replays the corresponding saved response back to the client—without ever touching the live internet.

#### The Workflow

1. **Record the Traffic:** Run `mitmdump` with the `-w` (write) flag while interacting with your application to capture real server interactions.

   ```bash
   mitmdump -p 8181 -w recorded_session.mitm
   ```

2. **Replay the Traffic (Mock Mode):** Start your proxy pointing to the saved file. You can now safely shut down your live backend or disconnect from the internet.

   ```bash
   mitmweb -p 8181 --server-replay recorded_session.mitm
   ```

#### Tweaking Request Matching Behavior

By default, `mitmproxy` is highly strict when matching incoming requests against the replay file. It verifies the HTTP method, host, path, and *every single header*. If a dynamic header (like a timestamp or token) differs by even one character, `mitmproxy` won't find a match and will pass the request through to the live web.

You can modify this behavior using these critical settings:

##### Replay Behavior Flags

- `--server-replay-nopop`: **Crucial for testing.** By default, `mitmproxy` deletes a response from its memory queue once it is replayed. Use this flag to allow the same recorded endpoint to be requested multiple times.
- `--server-replay-kill-extra`: Instantly returns a `404` to the client if a request does not exist in the replay file. This enforces strict isolation from the public internet.
- `--server-replay-refresh`: Adjusts response header dates (like `Date`, `Expires`, and `Last-Modified`) to match the current time, keeping time-sensitive clients happy.

##### Overriding Match Criteria

If your client sends dynamic query parameters or headers that change each run, use the `--set` option to tell the replay engine to ignore them during the matching phase:

```bash
mitmproxy --server-replay recorded_session.mitm \
  --set server_replay_ignore_headers=User-Agent,Cookie,Authorization,X-Request-ID \
  --set server_replay_ignore_params=timestamp,nonce
```

### " Command for General Testing

When you need to spin up `mitmproxy` quickly to diagnose an issue, you usually want three things: a clean graphical interface, the ability to replay mock data repeatedly without it vanishing from memory, and isolated testing that doesn't leak out to the real internet.

Instead of juggling multiple configurations, you can use this comprehensive out-of-the-box command optimized for local development, API mocking, and traffic analysis:

```bash
mitmweb -p 8181 \
  --server-replay recorded_session.mitm \
  --server-replay-nopop \
  --server-replay-kill-extra \
  --set server_replay_ignore_headers=User-Agent,Cookie,Authorization,X-Request-ID,Date \
  --set server_replay_ignore_params=timestamp,nonce,cb
```

#### Core Use Cases

- **Flake-Free CI/CD Pipelines:** Run front-end or integration tests against a completely predictable, static snapshot of backend data.
- **Offline Sandbox:** Work on API-dependent desktop or mobile applications during network outages or flights by replaying previous sessions.
- **Bypassing Rate Limits:** Test how your application scales under rapid-fire requests without burning through third-party paid API quotas.

## Tier 3: Wireshark

For foundational concepts on protocol analyzers, packet decoding, and how these tools capture data, refer to [Network Management](../Networking/05%20Network%20Management.md).

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

Terminal-oriented packet capture, [see more](../Networking/05%20Network%20Management.md).

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
