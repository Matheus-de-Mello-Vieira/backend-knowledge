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