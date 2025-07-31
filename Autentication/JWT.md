# JWT

* Stands for JSON Web Token
* Contains the data the servers needs in order to authenticate the user

## Anatomy

Is a the following three parts, concatenated with and Base64 encoded.

* **Header**: type of token (JWT) and signing algorithm

  ```json
  {
    "alg": "HS256",
    "typ": "JWT"
  }
  ```

* **Payload**: Data on the user
  ```json
  {
    "sub": "1234567890",
    "name": "John Doe",
    "admin": true,
    "iat": 1516239022
  }
  ```
  
  * * You can include custom fields, but there is registered claims (optional standard ones) like:
    * `iss` (issuer) Identifies who created and signed the token. It helps verify the token came from a trusted source.
    * `sub` (subject) Identifies the subject of the token — usually a user ID or username. It tells *who* the token is about.
    * `aud` (audience) Specifies the intended recipient(s) of the token. The app or service using the token should check this.
    * `exp` (expiration time) Defines when the token will expire. After this time, it should no longer be accepted.
    * `iat` (issued at) Indicates when the token was created. Useful for determining token age.
    * `nbf`  (not before) Sets a time before which the token is not valid. The token becomes valid only after this time.
  
* **Signature**: Used to verify the token wasn’t altered. It's created by encoding the header and payload and signing it using a secret or private key.

  ```scss
  HMACSHA256(
    base64UrlEncode(header) + "." +
    base64UrlEncode(payload),
    secret
  )
  ```


## Workflow

1) User requests a log-in
   * Sends credentials (e.g., username/password)
2) Server checks the credentials
   * If valid, generates a JWT token
   * Sends the JWT back to the client
3) Client stores the token (e.g., in localStorage or cookie)
   * The client starts to send the header `Authorization` with `Bearer <JWT token>` on the following requests
     * The client can also send it on the body or request parameter, put it
4) Server receives the request
   * Extracts and verifies the JWT:
     * Signature
     * Expiration (`exp`)
   * If valid: process request
   * If invalid: respond with 401 Unauthorized

```mermaid
flowchart TB
    subgraph Server
        J[Hidden Node]
        class J hidden;
        B{Are credentials valid?}
        C[Generate JWT token]
        D[Send JWT token to client]
        G["Verify JWT (signature & expiration)"]
        H{Is JWT valid?}
        I[Allow access to protected resource]
        X["Respond with 401 Unauthorized"]
    end

    subgraph Client
        A[User sends login request with credentials]
        E["Store JWT (e.g., localStorage or cookie)"]
        F[Send request with JWT in Authorization header]
    end

    A --> B
    J ~~~ B
    B -- No --> X
    B -- Yes --> C --> D --> E
    E --> F --> G --> H
    H -- Yes --> I
    H -- No --> X
```

