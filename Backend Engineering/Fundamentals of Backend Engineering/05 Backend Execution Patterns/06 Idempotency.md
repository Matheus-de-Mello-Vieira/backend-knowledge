# Idempotency

* The client can repeat a request and it won't affect the state of backend
* Useful when the client timeout a request, because the server receives the request, but due a problem the client doesn't receives the response.
  * the client could retry it, and it should not be problematic to server.
  * any proxy can also retry
* In HTTP
  * GET is idempotent
    * browsers and proxies treat GET as idempotent
      * so never uses GET to write something on the server, maybe only logs.
  * POST isn't, but we can make it. 
    * You can't simply append them the table because retries could lead to duplication.
      * Very bad for financial systems.
    * You can make it with `requestID`:
      * If `requestID` has been processed return
      * it is expensive because you have to lookup on the table.
      * also know as idempotency token.
    * You can make it with upsert
      * "create, but update if already exists."