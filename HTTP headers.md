# HTTP headers

## Caching Headers

Caching-related headers control freshness, validation, and cache key variance across clients and intermediaries. Core pieces are:

- `Cache-Control`: Directives for freshness and caching policy (request/response).
- `Expires`: Absolute expiration date for a response.
- `Last-Modified`: Timestamp of last change; used with `If-Modified-Since`/`If-Unmodified-Since`.
- `ETag`: Validator token for conditional requests.
- `Vary`: Which request headers differentiate cached variants.
- Conditional requests: `If-Match` and `If-None-Match` for concurrency/validation.

For the full caching guide (policies, validators, examples), see: [Cache/Caching Headers.md](Cache/Caching%20Headers.md)

## CORS

CORS-related headers let servers declare which cross-origin requests browsers may share with page scripts. Common response headers include:

- `Access-Control-Allow-Origin`: Allowed origin for the response. Use a specific origin when sending credentials; not `*`.
- `Access-Control-Allow-Methods`: Methods permitted for cross-origin access.
- `Access-Control-Allow-Headers`: Request headers the browser may send.
- `Access-Control-Expose-Headers`: Response headers made readable by JavaScript.
- `Access-Control-Allow-Credentials`: Whether cookies/credentials may be included and exposed.

For the full CORS guide (how it works, preflight, credentials, threats), see: [CORS](Security/04%20Application%20and%20API%20Security/Web%20Application%20Security.md#CORS)

## Referer and Origin Headers

These headers provide servers with context about the source of a request, which is essential for analytics, logging, and security mechanisms like CSRF protection. Core pieces include:

- `Referer`: Contains the absolute or partial address of the previous web page from which a link was followed (note the historic misspelling of "referrer").
- `Referrer-Policy`: Controls how much referrer information (sent via the `Referer` header) should be included with requests. Common values include `no-referrer`, `same-origin`, and `strict-origin-when-cross-origin`.
- `Origin`: Indicates the origin (protocol, host, and port) that initiated the request. Unlike `Referer`, it does not include the path or query string, making it a more privacy-focused alternative used heavily in CORS and state-changing requests (like `POST`).
