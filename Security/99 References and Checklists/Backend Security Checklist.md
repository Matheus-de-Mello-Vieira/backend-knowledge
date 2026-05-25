# Backend Security Checklist

## Overall Check

* [ ] **Input validation**: Validate all user-supplied data before processing to maintain data integrity and protect system security.
  * Test the application with invalid, unexpected, and boundary input to confirm that validation logic behaves correctly.
  * Example tools and libraries:
    - **Node.js:** [Joi](https://joi.dev/), [Yup](https://github.com/jquense/yup), [express-validator](https://express-validator.github.io/), [Zod](https://zod.dev/), [validator.js](https://github.com/validatorjs/validator.js)
    - **Python:** [Pydantic](https://docs.pydantic.dev/), [Marshmallow](https://marshmallow.readthedocs.io/), [Cerberus](https://docs.python-cerberus.org/), [Voluptuous](https://github.com/alecthomas/voluptuous), [Django forms/validators](https://docs.djangoproject.com/en/stable/ref/forms/validation/)
    - **Go:** [go-playground/validator](https://github.com/go-playground/validator), [ozzo-validation](https://github.com/go-ozzo/ozzo-validation), [govalidator](https://github.com/asaskevich/govalidator), [gojsonschema](https://github.com/xeipuuv/gojsonschema)
* [ ] **Authentication and authorization**: Implement strong authentication and authorization mechanisms to control access to sensitive information.
  * Use well-known patterns such as JWT and OAuth 2.0.
* [ ] **Protection against SQL injection attacks**: Use secure database libraries and parameterized queries to prevent SQL injection attacks.
  * Validate and sanitize all user-supplied data before including it in SQL statements.
  * Example tools and libraries:
    - **Node.js:** [Sequelize](https://sequelize.org/), [Knex.js](https://knexjs.org/), [Prisma](https://www.prisma.io/), [TypeORM](https://typeorm.io/)
    - **Python:** [SQLAlchemy](https://www.sqlalchemy.org/), [Django ORM](https://docs.djangoproject.com/en/stable/topics/db/queries/), [psycopg2](https://www.psycopg.org/docs/) (with parameterized queries)
    - **Go:** [GORM](https://gorm.io/), [sqlx](https://github.com/jmoiron/sqlx), [database/sql](https://pkg.go.dev/database/sql) (with prepared statements)
* [ ] **Protect the system against brute-force attacks**: Implement rate limiting and temporary account/IP lockouts; monitor and alert on suspicious authentication activity.
  * Set a threshold for consecutive failed login attempts and temporarily block the account or originating IP when the threshold is exceeded.
  * Add a delay (progressive backoff) between failed login attempts to hinder automated tools.
  * Example tools and services for brute-force protection:
  * Rate limiting libraries / middleware  
    - **Node.js:** [express-rate-limit](https://www.npmjs.com/package/express-rate-limit), [rate-limiter-flexible](https://www.npmjs.com/package/rate-limiter-flexible) (supports Redis), [fastify-rate-limit](https://github.com/fastify/fastify-rate-limit)  
    - **Python:** [flask-limiter](https://flask-limiter.readthedocs.io/), [django-ratelimit](https://github.com/jsocol/django-ratelimit)  
    - **Go:** [tollbooth](https://github.com/didip/tollbooth), [go-rate](https://github.com/beefsack/go-rate), [ulule/limiter](https://github.com/ulule/limiter)  

  * Monitoring & alerting  
    - [SIEM](Incident%20Response,%20Forensics,%20and%20Disaster%20Recovery.md#SIEM) / logs: [Datadog](https://www.datadoghq.com/), [Splunk](https://www.splunk.com/), [ELK Stack](https://www.elastic.co/what-is/elk-stack) — alert on spikes of failed logins  

  * CAPTCHA and bot challenges  
    - [Google reCAPTCHA](https://www.google.com/recaptcha/), [hCaptcha](https://www.hcaptcha.com/), [Friendly Captcha](https://friendlycaptcha.com/)
* [ ] **Sensitive data encryption**: Encrypt all sensitive data before storing it to ensure confidentiality and integrity
  * Use strong, industry-standard encryption algorithms and manage encryption keys securely.  
  * Recommended options include [bcrypt](https://www.npmjs.com/package/bcrypt), [scrypt](https://howtodoinjava.com/java/java-security/how-to-generate-secure-password-hash-md5-sha-pbkdf2-bcrypt-examples/), [PBKDF2](https://medium.com/@kasunpdh/how-to-store-passwords-securely-with-pbkdf2-204487f14e84), [Argon2](https://mkyong.com/java/java-password-hashing-with-argon2/), and [SHA-3](https://mkyong.com/java/java-sha-hashing-example/).
* [ ] **Protection against session attacks**: Implement mechanisms to prevent session hijacking and fixation by enforcing strong authentication and secure session handling.
  * Store sensitive session data in an encrypted and signed cookie or token on the client side.
  * Verify the origin and integrity of each session request (e.g., IP address, User-Agent, CSRF tokens).
  * Set a session timeout and automatically invalidate expired sessions.
  * Implement multi-factor authentication (MFA) and stronger auth methods:
    - **Node.js:** [speakeasy](https://www.npmjs.com/package/speakeasy) (TOTP), [passport.js](https://www.passportjs.org/), [express-session](https://www.npmjs.com/package/express-session)
    - **Python:** [pyotp](https://pypi.org/project/pyotp/), [Flask-Login](https://flask-login.readthedocs.io/), [Django sessions & CSRF middleware](https://docs.djangoproject.com/en/stable/ref/csrf/)
    - **Go:** [gorilla/sessions](https://github.com/gorilla/sessions), [gorilla/csrf](https://github.com/gorilla/csrf), [go-webauthn](https://github.com/go-webauthn/webauthn), [go-otp](https://github.com/xlzd/gotp)
* [ ] **Protection against Cross-Site Request Forgery (CSRF) attacks**: Implement mechanisms to prevent CSRF attacks.
  * Include an `X-CSRF-TOKEN` HTTP header in every request that modifies server state: [see more](../04%20Application%20and%20API%20Security/CSRF%20Tokens.md).
  * Allow state-changing operations only through POST, PUT, PATCH, or DELETE routes (avoid using GET for them).
  * Example tools and libraries:
    - **Node.js:** [csurf](https://www.npmjs.com/package/csurf), [@fastify/csrf-protection](https://github.com/fastify/csrf-protection)
    - **Python:** [Django CSRF Middleware](https://docs.djangoproject.com/en/stable/ref/csrf/), [Flask-WTF CSRF](https://flask-wtf.readthedocs.io/en/stable/csrf.html)
    - **Go:** [gorilla/csrf](https://github.com/gorilla/csrf)
* [ ] **Library update**: All libraries must be updated with the latest security patch.
  * Alternatively, you can use a security and stable version, without well-now security breaches.
  * The  [OWASP Dependency Check](https://owasp.org/www-project-dependency-check/) should
* [ ] **Security monitoring**: The application is continuously monitored to detect any suspect activity.
  * [ ] **Access auditing and logging:** Processes are in place to log and monitor access in order to detect any suspicious activity.
    * Define and standardize the data fields to be logged, such as timestamp, user, email address, IP address, request type, API endpoint, and response.
    * Choose a tool suitable for your API, such as:
      * **Java:** [Logback](https://logback.qos.ch/), [Log4j](https://logging.apache.org/log4j/2.x/), [SLF4J](https://www.slf4j.org/)
      * **Node.js:** [Winston](https://github.com/winstonjs/winston), [Pino](https://github.com/pinojs/pino)
      * **Python:** [logging (built-in)](https://docs.python.org/3/library/logging.html), [Loguru](https://github.com/Delgan/loguru)
      * **Go:** [Zap](https://github.com/uber-go/zap), [Logrus](https://github.com/sirupsen/logrus)

* [ ] Do not redirect to URLs provided by the user, or at least verify that the target domain is trustworthy.

* [ ] **Vulnerability check:** Use tools to identify potential vulnerabilities.
  * Tools such as [Qualys Community Edition](http://qualys.com/community-edition/), [OWASP Dependency Check](https://www.owasp.org/index.php/OWASP_Dependency_Check) e [Mozilla Observatory](https://observatory.mozilla.org/).
  * Be careful when sending code to platforms that are not approved by the client’s or project’s policies. Always follow these policies.
* [ ] **Threats Modeling**: Address any risks and vulnerabilities identified during the threat modeling process.
  - At minimum, make sure these findings are recorded in the project backlog.
  - All projects should go through a threat modeling process, and development teams must have access to the results. If your project doesn’t follow this, inform your manager or supervisor.
  - Learn more here: [Microsoft Threat Modeling Introduction](https://learn.microsoft.com/en-us/training/modules/tm-introduction-to-threat-modeling/).
* [ ] **Approved tools only:** All dependencies and tools used in the project must be approved according to the client’s or project’s policies.

## HTTP Headers

* **Do not expose server name/version:** prevent the server from returning its name or version in response headers or cookies — that info helps attackers find known vulnerabilities.
  - Check both response headers (e.g. `Server`, `X-Powered-By`) and any cookie values/attributes to ensure they don’t contain product names or versions.
  - Also avoid exposing this information in error pages, banners, or HTML comments.
  - For example, in Nginx you can do this by adding the `server_tokens off;` directive.
* **Turn on [Content Security Policy (CSP)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP):**
  * Content Security Policy (CSP) protects web applications by restricting which content sources the browser can load, helping prevent XSS and data injection attacks.
* **Turn on [Strict-Transport-Security (HSTS)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security)**
  * HSTS ensures that browsers always use HTTPS to connect to your site after the first visit, preventing attackers from forcing insecure HTTP connections.
  * For example, in Nginx you can do this by adding the `*add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;*` directive.
* Set a [Referrer Policy](https://scotthelme.co.uk/a-new-security-header-referrer-policy/).
* Set a [Permissions Policy](https://scotthelme.co.uk/goodbye-feature-policy-and-hello-permissions-policy/).

## Cookies

* Must be created with `HttpOnly=true` and `Secure=true` so they can’t be accessed by JavaScript or intercepted during transmission.
  - Limit cookies to a specific domain and set a reasonable expiration time.
  - Always set the `SameSite` attribute; `Lax` is a good default pattern for most use cases.
* **Be careful with CNAME Cloaking:**: An advertising company might ask you to add a CNAME record pointing a subdomain of your site to their servers. This can cause your site to send authentication cookies to them, potentially giving them access to user data.
  * You should deny such requests whenever possible. If that’s not feasible, mitigate the risk by limiting cookie domains or by changing the authentication method (for example, using tokens instead of cookies).

## **JWT (JSON WEB TOKEN)**

* [ ] Use a random and complex security key (`JWT Secret`) to make brute-force attacks less efficient.
* [ ] Do not use the encryption algorithm specified in the payload header. Enforce the use of a specific algorithm on the backend (`HS256` or `RS256`).
* [ ]  Set the token’s lifetime (`TTL`, `RTTL`) to the shortest possible duration.
* [ ] Do not store confidential information in the JWT, since it can be [easily decoded](https://jwt.io/#debugger-io).
* [ ] Avoid storing too much data. JWTs are usually shared in headers, which have a size limit.

## OAUTH

* [ ] Always validate the `redirect_uri` on your server against a list of known (pre-registered) URLs.
* [ ] Always try to return authorization codes, not access tokens (do not allow `response_type=token`).
* [ ] Use the `state` parameter with a random hash to prevent CSRF attacks during the OAuth authentication process.
* [ ] Define data scopes, and validate the `scope` parameter for each application.

## Access

* [ ] Limit the number of requests (Throttling) to prevent DDoS and brute-force attacks.
* [ ] Use HTTPS on your server to prevent MITM (Man-In-The-Middle) attacks.
* [ ] Use the `HSTS` header with SSL to prevent SSL Strip attacks.
* [ ] Disable directory listings in SourceMap resources.
* [ ] For private APIs, allow access only from whitelisted IPs/hosts.

## Request

* [ ] Use the appropriate HTTP method for each operation — `GET` (retrieve), `POST` (create), `PUT/PATCH` (replace/update), and `DELETE` (remove).
* [ ] Validate the content type declared in the `Accept` header (Content Negotiation) to allow only supported formats (e.g., `application/xml`, `application/json`, etc.), responding with `406 Not Acceptable` if it’s not supported.
* [ ] Validate the `Content-Type` header of incoming requests to allow only supported formats (e.g., `application/x-www-form-urlencoded`, `multipart/form-data`, `application/json`, etc.).
* [ ] Validate the request content to prevent common vulnerabilities (e.g., `XSS`, `SQL Injection`, `Remote Code Execution`, etc.).
* [ ] Do not use sensitive information (credentials, passwords, authentication tokens) in URLs. Use the request’s `Authorization` header instead.
* [ ] Use only server-side encryption.
* [ ] Use an API gateway service to enable caching, limit successive accesses (e.g., by maximum allowed quota, by spike arrest during traffic surges, or by concurrent rate limiting), and to simplify deploying new features.

## Processing

* [ ] Continuously verify endpoints protected by authentication to avoid access protection failures.
* [ ] Do not use user IDs directly. Use `/me/orders` instead of `/user/654321/orders`.
* [ ] Do not use incremental IDs. Use UUIDs.
* [ ] If you are processing XML files, make sure that entity parsing is disabled to prevent XXE attacks (XML External Entity).
* [ ] If you are processing XML files, ensure that entity expansion is disabled to prevent *Billion Laughs/XML bomb* attacks caused by exponential XML expansion.
* [ ] Use a CDN for file uploads.
* [ ] If you are working with a large amount of data, use workers and queues (processing queues) to return responses quickly and avoid blocking HTTP requests.
* [ ] Do not forget to disable debug mode (`DEBUG mode OFF`).
* [ ] Use non-executable stacks when available.

## Responses

* [ ] Send the header `X-Content-Type-Options: nosniff`.
  * It prevents browsers from guessing a file’s MIME type and forces them to use the declared `Content-Type`.
* [ ] Send the header `X-Frame-Options: deny`.
  * It prevents the webpage from being displayed in a frame or iframe, blocking clickjacking entirely.
* [ ] Send the header `Content-Security-Policy: default-src 'none'`.
  * Blocks all content sources by default—no scripts, images, or other resources can load unless explicitly allowed.
* [ ]  Remove server software identification headers — `X-Powered-By`, `Server`, `X-AspNet-Version`.
* [ ] Send a `Content-Type` header in your response with the appropriate value (e.g., if returning JSON, send `Content-Type: application/json`).
* [ ] Do not return sensitive data such as passwords, credentials, or authentication tokens.
* [ ] Use the appropriate response status code for each operation. For example:
  * `200 OK` (successfully responded),
  *  `201 Created` (new resource created),
  *  `400 Bad Request` (invalid request),
  * `401 Unauthorized` (not authenticated),
  * `405 Method Not Allowed` (HTTP method not permitted), etc.

## CI & CD

* [ ] Monitor your API’s specification and implementation through unit and integration tests.
* [ ] Use a code review process — avoid self-approvals.
* [ ] Ensure all service components are validated by AV software (antivirus, anti-malware) before deploying to production, including third-party dependencies.
* [ ] Continuously run security tests (static and dynamic analysis) on your code.
* [ ] Check your dependencies (software and OS) for known vulnerabilities.
* [ ] Implement a rollback feature for deployments.
