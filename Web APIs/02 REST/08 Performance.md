# Performance

* Your API must be fast
* Performance is not related to the API, but to the underlying code
* techniques
  * **async operations**
    * Don’t wait for long operations to complete
    * Relevant mainly for IO operations (files, database access, networking, etc.)
    * Almost every platform supports this concept
  * **caching**
    * Store frequently accessed data close to the API
    * Usually in-Memory
    * Set expiration and invalidation
  * **rate limit**
    * Limit the maximum concurrent requests the API handles
    * Put a rate limiter on front of the API
  * **quotas**
    * Limits the number of requests a specific client can make
    * Minimizes risk of heavy load

