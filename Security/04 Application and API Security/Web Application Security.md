# Web Application Security

**Definition:** Web Application Security is the discipline of protecting websites, web applications, and web services (like APIs) from malicious attacks, unauthorized access, and data exploitation. Because web applications are inherently designed to be publicly accessible and routinely interact with sensitive backend databases, they represent one of the most prominent and heavily targeted attack surfaces in modern IT infrastructure.

## The Paradigm Shift in Defense

Traditional [network security](01%20Network%20Security.md) tools (like the [IPsec](16%20IPsec.md) tunnels or standard [firewalls](Firewall%20Technologies.md)) are largely designed to block unauthorized traffic at the perimeter. However, web applications fundamentally change this dynamic:

- **The "Port 443" Problem:** Web applications operate on standard web ports (HTTP port 80 and HTTPS port 443) that _must_ remain open to the public. Traditional network firewalls cannot blindly block this traffic without taking the application offline. This means attackers can send malicious payloads directly through the front door, bypassing traditional Layer 3 and Layer 4 defenses.
- **Complexity and Custom Code:** Unlike standardized network protocols, web applications are built using massive amounts of custom code, third-party libraries, and complex business logic. This bespoke nature drastically increases the likelihood of human error, logic flaws, and hidden vulnerabilities.
  
### Core Pillars of Web Defense

To secure a web application, security teams must focus on defending the application layer (Layer 7) itself through several key disciplines:

- **Input Validation and Sanitization:** Enforcing the golden rule of web security: _Never trust user input_. Every piece of data sent by a client (search bars, login forms, URLs, headers, cookies) must be strictly validated and neutralized to prevent injection attacks.
- **Authentication and Session Management:** Securely proving a user's identity and protecting their session token (usually a cookie) so that an attacker cannot hijack an active, authorized session over the inherently stateless HTTP protocol.
- **Access Control (Authorization):** Ensuring that an authenticated user can only access the specific data and functions they are explicitly permitted to use, preventing both horizontal and vertical privilege escalation.
- **Secure Configuration:** Hardening the web servers, application frameworks, and underlying dependencies, while ensuring that modern browser security headers (like Content Security Policy or HSTS) are properly implemented to protect the end-user.

## Web Application Firewalls (WAF)
A **Web Application Firewall (WAF - `/ˌdʌbəl.juː eɪ/`)** is a specialized Layer 7 firewall designed specifically to protect web applications and APIs. While a traditional firewall focuses on network-level access control—such as IP addresses, ports, and connection states—a WAF understands **HTTP and HTTPS traffic** and inspects the actual web requests being sent to an application.

A WAF typically sits in front of a web server as a **reverse proxy**. When a client sends a request to a website, the request reaches the WAF first. The WAF analyzes the request, compares it against security rules, and then decides whether to allow, block, log, or challenge the request before it reaches the application.

WAFs are mainly used to defend against application-layer attacks such as:

- **SQL Injection:** Attempts to manipulate database queries through malicious input.
- **Cross-Site Scripting (XSS):** Attempts to inject malicious scripts into web pages.
- **Command Injection:** Attempts to execute unauthorized system commands through the application.
- **Path Traversal:** Attempts to access files outside the intended web directory.
- **Malicious Bots:** Automated traffic used for scraping, credential stuffing, or abuse.

A WAF can also enforce application-specific policies. For example, it may block requests with suspicious payloads, limit repeated login attempts, restrict access by geography, or require additional verification when traffic appears abnormal.

However, a WAF is not a replacement for secure application development. It acts as a protective layer in front of the application, but vulnerabilities should still be fixed in the code itself. In a Defense in Depth strategy, the WAF protects the exposed web application while other firewall technologies continue to protect the broader network.

## CORS

CORS (Cross-Origin Resource Sharing) is a security mechanism implemented by web browsers to control how web pages can make requests to resources on a different origin (domain, protocol, or port) than their.

A **same-origin** request happens when a web page and the resource it accesses share the **same domain, protocol, and port**. For example, a page from `https://example.com` requesting data from `https://example.com/api/data`.

A **cross-origin** request occurs when any of those three parts differ. For example:

- **different protocol**`https://example.com` → `http://example.com/api/data`
- **different domain** `https://example.com` →`https://another-site.com/data`
- **different subdomain**: `https://example.com` → `https://api.example.com/data`

Browsers treat these cases differently for security reasons, using **CORS (Cross-Origin Resource Sharing)** to control which cross-origin requests are allowed.

Modern browsers isolate websites by origin (domain + protocol + port).

- This is part of the **Same-Origin Policy (SOP)**, one of the web's core security models.

CORS is a controlled relaxation of that policy, allowing safe and intentional sharing of data across origins.

### How CORS Works

When a web page makes a cross-origin request, such as through `fetch()` or `XMLHttpRequest`, the browser checks the server's response headers to determine whether access is allowed.

| Header | Description | Example Value |
| --- | --- | --- |
| `Access-Control-Allow-Origin` | Specifies which origin(s) are allowed to access the resource. | `Access-Control-Allow-Origin: https://example.com` or `Access-Control-Allow-Origin: *` |
| `Access-Control-Allow-Methods` | Lists the HTTP methods allowed when accessing the resource. | `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS` |
| `Access-Control-Allow-Headers` | Specifies which custom headers can be sent by the browser. | `Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With` |
| `Access-Control-Allow-Credentials` | Indicates whether cookies or other credentials can be included in requests. | `Access-Control-Allow-Credentials: true` |
| `Access-Control-Expose-Headers` | Lists which response headers can be accessed by JavaScript in the browser. | `Access-Control-Expose-Headers: Content-Length, X-Custom-Header` |

The **browser** uses the CORS headers to decide whether it is safe and allowed to share the response with the page's JavaScript code.

1. The server responds with a subset of the headers above.
2. The browser checks whether the request fits those response headers.
3. If they match, the browser lets the page access the response.
4. If they do not match, the browser blocks the response, even though the request still reached the server.
### Simple vs. Preflight Requests

- **Simple requests:** If the request is simple, such as `GET` or `POST` with standard headers, the browser sends it directly and then checks the response for CORS headers.
- **Preflight requests:** If the request uses custom headers, non-simple methods like `PUT` or `DELETE`, or credentials, the browser sends an `OPTIONS` request first. This preflight request asks whether the actual request is allowed. The server must approve it with the right headers or the browser cancels the actual request.

### Access-Control-Allow-Credentials

`Access-Control-Allow-Credentials` means it is acceptable to include and expose credentials, such as cookies, `Authorization` headers, or TLS client certificates, in cross-origin requests.

If a page wants to send cookies or authentication headers, the browser includes them only if:

- The request sets `fetch(..., { credentials: 'include' })`
- The server responds with `Access-Control-Allow-Credentials: true`
- `Access-Control-Allow-Origin` is not `*`; it must be a specific origin

Otherwise, the browser strips credentials for security.

### Why CORS Exists

CORS exists to protect users from malicious websites that try to read or manipulate private data from other sites where the user is logged in.

Imagine you are logged into `https://mybank.com` and your browser stores a session cookie for that site. Now you visit the malicious website `https://evil.com` . If browsers did not enforce the same-origin policy, or CORS, that site could attempt:

```javascript
fetch("https://mybank.com/account", {
  credentials: "include"
})
  .then((response) => response.text())
  .then((data) => sendToHackerServer(data));
```

Your browser would automatically include your cookies, and the attacker could read your account information even though you never directly interacted with your bank site.

**Attacks CORS Helps Prevent**

1. [Cross-Site Request Forgery (CSRF)](03%20Common%20Threats%20and%20Attacks.md#Cross-Site%20Request%20Forgery%20(CSRF)): CORS blinds the attacker, but it doesn't prevent them from making an action. So additional protections as [**`SameSite` cookie attributes**](#`SameSite`%20Policies) and [Anti-CSRF Tokens](#Anti-CSRF%20Tokens) are necessary. 
2. [Cross-Site Data Theft](03%20Common%20Threats%20and%20Attacks.md#Cross-Site%20Data%20Theft): This is exactly what CORS prevents. Browsers block access to the response unless the target site explicitly allows it with `Access-Control-Allow-Origin`.
## Anti-CSRF Tokens

`X-CSRF-TOKEN` is a custom HTTP header used to protect against [Cross-Site Request Forgery (CSRF)](03%20Common%20Threats%20and%20Attacks.md#Cross-Site%20Request%20Forgery%20(CSRF)). It is a token, usually a random unique string, that helps ensure a request to a server actually comes from a legitimate authenticated user rather than a malicious site.

Here is the general flow:

1. **Server generates a token**
   When a user loads a form or page, the server generates a **unique CSRF token** tied to that user's session.

   Example:

   ```json
   { "csrf_token": "12345abcd6789" }
   ```

2. **Client includes the token**
   The frontend includes that token in all state-changing requests, such as `POST`, `PUT`, or `DELETE`, usually via:

   - A hidden form field
   - A request header such as `X-CSRF-TOKEN`

   Example:

   ```javascript
   fetch("/api/user/update", {
     method: "POST",
     headers: {
       "Content-Type": "application/json",
       "X-CSRF-TOKEN": csrfToken
     },
     body: JSON.stringify({ name: "Alice" })
   });
   ```

3. **Server validates the token**
   When the request arrives, the server compares the incoming token with the one stored in the user's session, or a signed JWT-based equivalent.

   - If they match, the request is legitimate.
   - If not, reject the request as a possible CSRF attack.

## Cookie Security and Session Management

Cookies are small text-based data payloads generated by a web server and stored by the client's browser. While originally designed to maintain state over the inherently stateless HTTP protocol, cookies frequently serve as **session tokens** (the "keys to the castle"). Because possessing a valid session cookie allows an attacker to completely bypass authentication mechanisms (including Multi-Factor Authentication), securing cookies is a critical component of application-layer defense.

### Cookie Security Attributes

When a server issues a cookie via the `Set-Cookie` HTTP response header, it can append specific security attributes. These attributes instruct the browser to restrict how and when the cookie is transmitted or accessed.

| **Attribute** | **Security Purpose**                                                                                                             | **Operational Impact**                                                                                                                                                                                               |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Secure`      | Prevents interception via eavesdropping.                                                                                         | Forces the browser to _only_ transmit the cookie over encrypted `https://` connections, protecting it from network sniffing.                                                                                         |
| `HttpOnly`    | Mitigates Cross-Site Scripting (XSS) data theft.                                                                                 | Blocks client-side scripts (like JavaScript's `document.cookie`) from accessing the cookie. Even if an application suffers from an XSS vulnerability, the attacker cannot programmatically scrape the session token. |
| `SameSite`    | Mitigates [Cross-Site Request Forgery (CSRF)](03%20Common%20Threats%20and%20Attacks.md#Cross-Site%20Request%20Forgery%20(CSRF)). | Controls whether cookies are sent along with cross-site requests, preventing malicious third-party sites from abusing an active session.                                                                             |

### `SameSite` Policies

The `SameSite` attribute is a primary defense against CSRF attacks, dictating browser behavior when a user navigates from an external origin to the target application:
- **`SameSite=Strict`:** The cookie is restricted exclusively to first-party contexts. It will never be sent on cross-site requests. For example, if a user clicks a link to their bank from an external email or search engine, the browser will not attach the session cookie, requiring the user to re-authenticate or refresh the destination page.
- **`SameSite=Lax`:** The modern browser default. The cookie is withheld on cross-site sub-requests (such as an external site trying to load images or `<iframe>` elements from the application), but it _is_ sent when the user performs top-level navigation (e.g., clicking a link to follow a URL).
- **`SameSite=None`:** The cookie is sent on all cross-site requests, both top-level and sub-requests. This is required for third-party tracking or embedded cross-origin widgets.
	- **Note:** Browsers strictly require that `SameSite=None` must be paired with the `Secure` attribute, or the cookie will be rejected.

### Key Threats to Cookie Security

- **Session Hijacking (Cookie Replay):** If an attacker steals a valid session cookie—whether via a compromised network, an XSS exploit, or physical access—they can inject it directly into their own browser profile. The server cannot distinguish the attacker's request from the legitimate user's request.
- **Infostealer Malware:** Modern cybercriminals heavily rely on client-side malware (e.g., RedLine, Lumma) designed to bypass browser sandbox protections. These tools scrape the local database storage files where web browsers store active cookies, exfiltrating valid session states directly to the dark web.
- **Session Fixation:** An attack where a malicious actor forces a known, static session identifier onto a victim's browser (often via URL manipulation). If the application fails to rotate or invalidate the session identifier upon successful user login, the attacker can use the predetermined cookie to access the authenticated session.

### Implementation Best Practices

1. **Enforce the Triple Threat:** Always issue sensitive session tokens with `Secure; HttpOnly; SameSite=Lax` (or `Strict`) attributes enabled.
2. **Session Lifecycle Management:** Implement strict absolute timeouts (forcing a full re-login after a set period) and idle timeouts (terminating inactive sessions).
3. **Cryptographic Invalidation on Logout:** Ensure that clicking "Log Out" explicitly destroys the session state on the backend server database, rendering any leaked or residual client-side cookies useless.
4. **Token Rotation:** Always generate a completely new, cryptographically secure random session ID immediately after a user successfully authenticates to neutralize session fixation vectors.