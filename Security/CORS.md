## CORS

CORS (Cross-Origin Resource Sharing) is a security mechanism implemented by web browsers to control how web pages can make requests to resources on a different origin (domain, protocol, or port) than their.

A **same-origin** request happens when a web page and the resource it accesses share the **same domain, protocol, and port** — for example, a page from `https://example.com` requesting data from `https://example.com/api/data`.

A **cross-origin** request occurs when any of those three parts (domain, protocol, or port) differ. For example:

-   `https://example.com` → `https://api.example.com/data` (**different subdomain**)
-   `https://example.com` → `http://example.com/api/data` (**different protocol**)
-   `https://example.com` → `https://another-site.com/data` (**different domain**)

Browsers treat these cases differently for security reasons, using a mechanism called **CORS (Cross-Origin Resource Sharing)** to control which cross-origin requests are allowed.

Modern browsers isolate websites by “origin” (domain + protocol + port).

*   This is part of the **Same-Origin Policy (SOP)** — one of the web’s core security models.

CORS is a *controlled relaxation* of that policy, allowing *safe and intentional* sharing of data across origins.

### How CORS Works

When a web page makes a cross-origin request (like using `fetch()` or `XMLHttpRequest`), the browser first checks the server’s response headers to see if the resource allows such requests.

| **Header**                         | **Description**                                              | **Example Value**                                            |
| ---------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| `Access-Control-Allow-Origin`      | Specifies which origin(s) are allowed to access the resource. | `Access-Control-Allow-Origin: https://example.com``Access-Control-Allow-Origin: *` |
| `Access-Control-Allow-Methods`     | Lists the HTTP methods allowed when accessing the resource.  | `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS` |
| `Access-Control-Allow-Headers`     | Specifies which custom headers can be sent by the browser.   | `Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With` |
| `Access-Control-Allow-Credentials` | Indicates whether cookies or other credentials can be included in requests. | `Access-Control-Allow-Credentials: true`                     |
| `Access-Control-Expose-Headers`    | Lists which response headers can be accessed by JavaScript in the browser. | `Access-Control-Expose-Headers: Content-Length, X-Custom-Header` |

The **browser** uses the CORS headers to **decide whether it’s safe and allowed** to share the response with the page’s JavaScript code.

1)   The server responds with a subset of the aforementioned headers

2)   The browser checks if the requests fits on those response headers.

     *   In case of `Access-Control-Allow-Origin`, the request header `Origin` must fit on it.

3)   If they match, the browser **lets the page access the response** (e.g., `fetch()` or `XMLHttpRequest` can read it).

4)   If they **don’t match**, the browser **blocks the response**, even though the request technically reached the server.

     >   The data is fetched but **not made available** to JavaScript for security reasons.

#### Simple vs. Preflight Requests

*   **Simple Requests**
     If the request is “simple” (like `GET` or `POST` with standard headers), the browser just sends it directly, but still checks the response for CORS headers.

*   **Preflight Requests**
     If the request uses custom headers, non-simple methods (`PUT`, `DELETE`, etc.), or credentials, the browser sends an **OPTIONS** request first.
     This is called a **preflight request**, asking:

	>   “Hey server, can I send this request?”

	The server must respond with headers that approve it; otherwise, the browser cancels the actual request.

#### Access-Control-Allow-Credentials

>   “It’s okay to include and expose **credentials** (like cookies, Authorization headers, or TLS client certificates) in cross-origin requests.”

If the page wants to send cookies or authentication headers, the browser only includes them if:

-   The request sets `fetch(..., { credentials: 'include' })`, **and**
-   The server responds with `Access-Control-Allow-Credentials: true`, **and**
-   `Access-Control-Allow-Origin` is **not `\*`** (it must be a specific origin).

Otherwise, cookies are stripped for security.

## Why CORS Exists

CORS (Cross-Origin Resource Sharing) exists to protect users from malicious websites that try to read or manipulate private data from other sites where the user is logged in.

### Generic scenario

Let’s imagine you’re logged into:

```url
https://mybank.com
```

and your browser stores your session cookie for that site.

Now, you visit a **malicious website**:

```url
https://evil.com
```

If browsers didn’t enforce the same-origin policy (or CORS), this evil site could do:

```javascript
fetch('https://mybank.com/account', {
  credentials: 'include'
})
  .then(response => response.text())
  .then(data => sendToHackerServer(data));
```

Your browser would **automatically include your cookies** (since you’re logged in), and the hacker could read your **account info** — even though you never interacted with your bank site directly.

### Attacks CORS Helps Prevent

#### 1. **Cross-Site Request Forgery (CSRF)**

“Make the user’s browser do something on another site.”

-   **Definition:** An attacker tricks a user’s browser into making authenticated requests to another site where the user is logged in.
-   **Goal:** Perform actions (like transferring money or changing passwords) without the user’s consent.
-   **Limitation:** The attacker *cannot see the response* — they just cause actions to happen.
-   **CORS relevance:** CORS doesn’t stop the *request*, but it stops the attacker from *reading* the response.
-   **Example**: Transfer money, change password

#### 2. **Cross-Site Data Theft / Cross-Site Scripted Request**

 “Make the user’s browser *read something* from another site.”

-   **Definition:** An attacker tries to **read private data** from another site via a cross-origin request.
-   **Goal:** Extract sensitive information (e.g., account balances, emails).
-   **CORS relevance:** This is **exactly what CORS prevents** — browsers block access to the response unless the target site explicitly allows it with `Access-Control-Allow-Origin`.
-   **Example**: Read account balance, download user data

## Common Misconceptions

*   CORS is **not a server-side security feature** — it’s enforced by browsers only.
*   Setting `Access-Control-Allow-Origin: *` doesn’t make your API secure — it just removes CORS restrictions for browsers.
*   CORS errors do **not** mean the server is broken; they mean the **browser** is blocking access.

