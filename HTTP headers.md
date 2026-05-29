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
