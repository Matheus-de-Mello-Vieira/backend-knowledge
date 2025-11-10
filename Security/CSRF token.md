# CSRF Token

`X-CSRF-TOKEN` is a custom HTTP header used to protect against Cross-Site Request Forgery (CSRF) attacks. It’s a token (a random, unique string) that ensures a request to a server actually comes from a legitimate, authenticated user rather than a malicious site.

* Prevents **unauthorized commands** being sent by an authenticated user’s browser

 ## How the `X-CSRF-TOKEN` Works

Here’s the general flow:

1. **Server generates a token**
    When a user loads a form or a page, the server generates a **unique CSRF token** tied to that user’s session.

   Example:

   ```json
   { "csrf_token": "12345abcd6789" }
   ```

2. **Client includes the token**
    The frontend includes that token in all state-changing requests (like POST, PUT, DELETE) — usually via:

   - a hidden form field, or
   - a request header such as `X-CSRF-TOKEN`.

   Example (AJAX request):

   ```javascript
   fetch('/api/user/update', {
     method: 'POST',
     headers: {
       'Content-Type': 'application/json',
       'X-CSRF-TOKEN': csrfToken
     },
     body: JSON.stringify({ name: 'Alice' })
   });
   ```

3. **Server validates the token**
    When the request arrives, the server compares the incoming token with the one stored in the user’s session (or signed JWT).

   - If they match → request is legitimate.
   - If not → reject the request (possible CSRF attack).