## Basic Authentication

* Easier way to implement
* Client sends User and Passwords on Headers
  * it is the `authorization` header with value `Basic [encoded]`, where:
    * `[encoded]` is `[User]:[Password]` is encoded in Base64
    * `[User]` and `[Password]` are the user and password respectively.
  * If OK, the server sends `200 OK`, otherwise it sends `401 Unauthorized`
* weakness:
  * it is sent in plain text, everyone that can read the connection can read the access.
    * so it is OK with HTTPs, but not with HTTP
  * User have to send the credentials on every request
    * if the server store session data, it isn't more REST

When the user don't send the credentials, the server respond with a `401` along with the `www-authenticate` header with value `Basic realm="title"`, where `title` is a string provided by the server that identifies it to the user.

* For example, for nginx

  ```nginx
  auth_basic "Prometheus Login";
  auth_basic_user_file /etc/nginx/.htpasswd;
  ```

  If the user don't provide the header, it will respond `401` with  `www-authenticate: Basic realm="Prometheus Login"`

* For example, the browser will open a pop-up asking the user and password