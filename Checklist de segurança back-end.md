# Back-end security checklist

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
    - SIEM / logs: [Datadog](https://www.datadoghq.com/), [Splunk](https://www.splunk.com/), [ELK Stack](https://www.elastic.co/what-is/elk-stack) — alert on spikes of failed logins  

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
  * Include an `X-CSRF-TOKEN` HTTP header in every request that modifies server state, and verify it against the token stored on the server side.
  * Allow state-changing operations only through POST, PUT, PATCH, or DELETE routes (avoid using GET for them).
  * Example tools and libraries:
    - **Node.js:** [csurf](https://www.npmjs.com/package/csurf), [@fastify/csrf-protection](https://github.com/fastify/csrf-protection)
    - **Python:** [Django CSRF Middleware](https://docs.djangoproject.com/en/stable/ref/csrf/), [Flask-WTF CSRF](https://flask-wtf.readthedocs.io/en/stable/csrf.html)
    - **Go:** [gorilla/csrf](https://github.com/gorilla/csrf)
