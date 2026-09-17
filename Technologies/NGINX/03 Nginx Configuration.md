# NGINX Configuration

NGINX configuration is organized into contexts. Each context limits where its directives apply and which protocol layer NGINX processes.

```nginx
events {
    # Connection-processing configuration.
}

http {
    # HTTP servers, routes, and upstream groups.
}

stream {
    # TCP and UDP servers and upstream groups.
}
```

- **`events`:** Configures connection processing for [worker processes](02%20NGINX%20Internals.md#Process%20Roles). The context is required even when it is empty.
- **`http`:** Configures application-layer HTTP handling, including static files, virtual servers, routing, reverse proxying, TLS termination, and HTTP/2.
- **`stream`:** Configures transport-layer TCP or UDP proxying without requiring NGINX to interpret the application protocol.

Within `events`, commonly used directives include:

- **`worker_connections`:** Sets the maximum simultaneous connections opened by each worker. The count includes client connections, upstream connections, and other connections rather than clients alone.
- **`multi_accept`:** Controls whether a worker accepts multiple [pending connections](../../Operating%20Systems/07%20Socket%20Management.md#Pending%20and%20Established%20Connection%20Queues) after receiving an acceptance event.
- **`use`:** Selects the operating system's [readiness-based event method](../../Operating%20Systems/07%20Socket%20Management.md#Readiness-Based%20I/O), such as `epoll` or `kqueue`. NGINX normally selects the most efficient available method automatically.

## HTTP Request Handling

### Static Files and Location Selection

An HTTP `server` listens on one or more addresses and ports. Its `root` directive maps request URIs to the filesystem by appending the normalized URI to the configured path.

```nginx
http {
    server {
        listen 8080;
        root /srv/site;

        location /images/ {
            root /srv/assets;
        }

        location ~ \.jpg$ {
            return 403;
        }
    }
}

events {}
```

With this configuration, `/index.html` maps to `/srv/site/index.html`, while `/images/logo.png` maps to `/srv/assets/images/logo.png`. The `root` inside the `/images/` location replaces the inherited value, but NGINX still appends the entire request URI. Use `alias` instead when the location prefix must be replaced rather than appended.

Several locations may match one URI, so NGINX selects one in a defined order:

1. An exact location such as `location = /health` terminates the search immediately.
2. Otherwise, NGINX finds and remembers the longest matching prefix location.
3. Unless that prefix uses `^~`, NGINX evaluates regular-expression locations in configuration order. The first matching regular expression wins.
4. If no regular expression matches, NGINX uses the remembered prefix location.

The `~` modifier makes a regular expression case-sensitive, while `~*` makes it case-insensitive. In the example, the regular-expression location rejects a request ending in `.jpg`, even if `/images/` was the longest prefix match.

## HTTP Reverse Proxying

NGINX acts as a [reverse proxy and load balancer](../../Networking/99%20Proxying%20and%20Load%20Balancing.md) when `proxy_pass` forwards an HTTP request to an upstream server or server group. Because routing occurs in the `http` context, a `location` can select an upstream from application-layer information such as the request URI.

### Upstream Groups and Load Balancing

An `upstream` block gives a server group a name that `proxy_pass` can reference.

```nginx
http {
    upstream node_backend {
        ip_hash;

        server node_app_1:8080;
        server node_app_2:8080;
        server node_app_3:8080;
    }

    server {
        listen 8080;

        location / {
            proxy_pass http://node_backend;
        }
    }
}

events {}
```

- **Round robin:** Without another load-balancing directive, NGINX distributes requests across available upstream servers in a repeating sequence.
- **`ip_hash`:** NGINX hashes the first three octets of an IPv4 client address or the complete IPv6 address. Requests from the same address therefore select the same available server; if that server is unavailable, NGINX selects another server.

### URI-Based Routing

Separate locations can route HTTP requests to different upstream groups or handle a path directly.

```nginx
http {
    upstream app_1_backend {
        server node_app_1:8080;
        server node_app_2:8080;
    }

    upstream app_2_backend {
        server node_app_3:8080;
        server node_app_4:8080;
    }

    server {
        listen 8080;

        location /api1/ {
            proxy_pass http://app_1_backend;
        }

        location /api2/ {
            proxy_pass http://app_2_backend;
        }

        location /admin {
            return 403;
        }
    }
}

events {}
```

### URI Replacement and the Trailing Slash

The trailing slash in `proxy_pass` is not only formatting: it determines whether the directive contains a URI component. That changes how NGINX constructs the URI sent upstream.

Without a trailing slash, `proxy_pass` contains only the upstream address. NGINX preserves the request URI:

```nginx
location /api/ {
    proxy_pass http://app_1_backend;
}
```

A request for `/api/users` reaches the upstream as `/api/users`.

With a trailing slash, `proxy_pass` contains the URI `/`. NGINX replaces the part of the normalized request URI that matched the location:

```nginx
location /api/ {
    proxy_pass http://app_1_backend/;
}
```

A request for `/api/users` reaches the upstream as `/users` because the matching `/api/` prefix is replaced by `/`. The replacement URI can contain a different prefix: with `proxy_pass http://app_1_backend/v1/;`, the same request reaches the upstream as `/v1/users`.

- **No URI in `proxy_pass`:** Preserve the complete request URI when forwarding it.
- **URI in `proxy_pass`:** Replace the prefix matched by the `location` with the URI written after the upstream address.

This prefix-replacement form should not be used in regular-expression or named locations because NGINX cannot determine a stable location prefix to replace. In those locations, specify `proxy_pass` without a URI.

## TCP and UDP Stream Proxying

The `stream` context proxies TCP or UDP sessions at Layer 4. It selects an upstream without parsing HTTP paths, headers, or methods.

```nginx
stream {
    upstream node_backend {
        server node_app_1:8080;
        server node_app_2:8080;
        server node_app_3:8080;
    }

    server {
        listen 8080;
        proxy_pass node_backend;
    }
}

events {}
```

For TCP, one accepted client connection forms one stream-proxy session. NGINX selects an upstream for that session and forwards the connection's [byte stream](../../Operating%20Systems/07%20Socket%20Management.md#Stream%20Sockets) through the corresponding upstream connection. Load balancing therefore occurs per connection rather than per application message carried inside it.

## TLS and HTTP/2

The `ssl` parameter on `listen` enables TLS for the server. The [certificate and private-key directives](../../Security/03%20Cryptography%20and%20Data%20Protection/04%20Digital%20Certificates%20and%20PKI.md#What%20a%20Certificate%20Does) identify the credentials presented during the [TLS handshake](../../Networking/02%20Protocols/06%20TLS.md).

```nginx
server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate /etc/nginx/tls/fullchain.pem;
    ssl_certificate_key /etc/nginx/tls/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    http2 on;
}
```

- **Protocol versions:** Enabling TLS 1.2 and TLS 1.3 retains compatibility with clients that do not support TLS 1.3. The accepted versions should match the compatibility and security requirements of the deployment.
- **Cipher configuration:** `ssl_ciphers` configures ciphers for TLS 1.2 and earlier. TLS 1.3 cipher-suite configuration follows the underlying TLS library's configuration interface.
- **HTTP/2:** In NGINX 1.25.1 and later, `http2 on;` enables the [HTTP/2 protocol](../../Networking/02%20Protocols/09%20HTTP2.md#How%20an%20HTTP%2F2%20Connection%20is%20Established). Older versions used the now-deprecated `http2` parameter on `listen`, as in `listen 443 ssl http2;`.

HTTP/2 over TLS also depends on Application-Layer Protocol Negotiation support in the TLS library so the client and server can select the protocol during the handshake.

## Timeout Boundaries

Timeouts limit how long a connection or request may occupy resources without making the expected progress. Most data-transfer timeouts below measure the gap between successive I/O operations rather than imposing a deadline on the whole request or response. Values that are too high retain stalled connections for longer; values that are too low terminate legitimate slow traffic.

### Client-Side Timeouts

- **`client_header_timeout` (`60s` by default):** Limits the time available to receive the complete client request header. NGINX terminates an incomplete header with a `408 Request Timeout` response.
- **`client_body_timeout` (`60s` by default):** Limits the interval between successive reads of the client request body. If the client sends no body data during that interval, NGINX terminates the request with `408 Request Timeout`.
- **`send_timeout` (`60s` by default):** Limits the interval between successive writes of the response to the client. It does not limit the duration of the complete response transfer.
- **`keepalive_timeout` (`75s` by default):** Controls how long an [idle client keep-alive connection](../../Networking/02%20Protocols/07%20HTTP1.1.md#The%20Standard:%20HTTP%2F1.1) remains open while waiting for another request. A value of `0` disables client-side keep-alive. An optional second value populates the `Keep-Alive: timeout=` response-header parameter and may differ from the server-side timeout.

> [!security] Slow clients
> Header and body timeouts limit how long slow clients can hold connections while making insufficient progress, which reduces exposure to [Slowloris-style resource exhaustion](../../Networking/02%20Protocols/07%20HTTP1.1.md#The%20Slowloris%20Attack). They complement rather than replace connection limits, request-size limits, and capacity controls.

### Lingering Connection Closure

NGINX may finish processing a request before the client finishes transmitting it. For example, NGINX can reject a request from its headers, send a final error response, and decide to close the connection while request-body bytes are still in transit. Those bytes should not be passed to an upstream because the request has already reached a terminal result and an upstream request may never have been created.

Closing the client socket immediately while input remains unread can cause an abrupt TCP reset and interfere with the client receiving the response that NGINX already sent. Lingering connection closure exists to avoid that outcome: after request processing ends, NGINX enters a bounded cleanup phase in which it drains and discards additional client data before closing the connection. The discarded bytes are no longer application input; reading them only makes connection termination more reliable.

When `lingering_close` is active, the cleanup proceeds as follows:

1. `lingering_timeout` limits each wait for additional data. Its default is `5s`.
2. If data arrives, NGINX reads and discards it, then waits again.
3. `lingering_time` limits the complete drain cycle. Its default is `30s`.
4. NGINX closes the connection when one wait expires without data or the total lingering time is exhausted.

### DNS Resolution Timeout

- **`resolver_timeout` (`30s` by default):** Limits the time NGINX spends resolving a name through resolvers configured by the `resolver` directive.

### Upstream Connection and Transfer Timeouts

HTTP proxy timeouts divide upstream communication into separate phases:

- **`proxy_connect_timeout` (`60s` by default):** Limits establishment of the connection to the proxied server. In practice, this timeout cannot usually exceed `75s`. A high value delays failure detection for an unreachable upstream, while a low value can reject connections during transient network or backend pressure.
- **`proxy_send_timeout` (`60s` by default):** Limits the interval between successive writes while NGINX sends the request to the upstream. It is not a deadline for the entire request transfer.
- **`proxy_read_timeout` (`60s` by default):** Limits the interval between successive reads while NGINX receives the upstream response. It is not a deadline for the entire response transfer.

These timers are independent. For example, `proxy_read_timeout` may close an upstream connection while the client-facing `send_timeout` has not expired, or the [client may stop receiving data first](../../Networking/03%20Connections/02%20Reading%20and%20Sending%20Data.md#Slow%20or%20Stalled%20Receivers).

### Retry Budget Across Upstreams

`proxy_next_upstream` defines which failed attempts permit NGINX to try another server. `proxy_next_upstream_timeout` bounds the time available across that sequence of attempts, while `proxy_next_upstream_tries` can impose a separate attempt-count limit.

```nginx
proxy_next_upstream error timeout;
proxy_next_upstream_timeout 10s;
proxy_next_upstream_tries 3;
```

A `proxy_next_upstream_timeout` value of `0`, the default, disables the time limit rather than disabling retries. Retrying is possible only while NGINX has not sent any part of the response to the client; after response transmission begins, NGINX cannot replace that partial response with one from another upstream.

### Upstream Keep-Alive Timeout

When upstream connection caching is enabled, `keepalive_timeout` inside an `upstream` block controls how long an idle connection remains available for reuse.

```nginx
upstream node_backend {
    server node_app_1:8080;
    server node_app_2:8080;

    keepalive 32;
    keepalive_timeout 60s;
}
```

The timeout applies only while a cached upstream connection is idle. The `keepalive` value limits idle cached connections per worker; it does not cap the total number of connections that the worker may open to upstream servers.
