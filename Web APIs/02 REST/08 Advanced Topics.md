# HateOAS

* Stands for Hypermedia As The Engine Of Application State
* Each REST request returns related resources
  * for example, if the API response a User entity, who has orders, you should put pointers to the order
* all the client needs up front is a single entry-point URL. Thereafter, the server’s responses include links (often via `rel` and `href` in JSON or XML) that describe what actions are valid next, depending on the current state of the resource
  * Client don't need have prior knowledge about other resources
  * it enables the client to navigate the API dynamically—without hardcoding every endpoint

```json
  {
    "account": {
      "account_number": 12345,
      "balance": 100.00,
      "links": {
        "deposit": "/accounts/12345/deposit",
        "withdraw": "/accounts/12345/withdraw",
        "transfer": "/accounts/12345/transfer",
        "close": "/accounts/12345/close"
      }
    }
  }
```

# API Discovery & Gateway

Image a scenario where I have `n` APIs and all of them are highly coupled. There is two solutions:

* **API Discovery**:  creates a information center, where each service asks to when they what to communicate with other services,
  * So you can change the URLs of the services and only update the center.
  * Easy to implement
  * External service
  * provides mainly URLs, and sometimes load balancing.

* **Gateway**: a proxy/reverse proxy for every service, each service communicates only with the gateway.
  * Difficult to implement (especially on-premise)
  * Man-in-the-middle
  * Can provide
    * Authentication and Authorization
    * Monitoring
    * Routing
    * Policies
    * Load Balancing

