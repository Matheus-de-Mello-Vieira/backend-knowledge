# HTTP Verbs

* It is part HTTP standard, not necessarily REST 

* Set the action to be performed

  * Retrieve a resource

  * Add a resource

  * Update a resource

  * Delete a resource

* Always use the correct verb

  * Improves readability

| **Verb**   | **Role**             | **Body?** | **Params In...** | **Idempotent?** |
| ---------- | -------------------- | --------- | ---------------- | --------------- |
| **GET**    | Retrieve resource(s) | No        | URL              | Yes             |
| **POST**   | Add resource(s)      | Yes       | Body             | No              |
| **PUT**    | Modify resource(s)   | Yes       | Body             | Yes             |
| **DELETE** | Delete resource(s)   | No        | URL              | Yes             |

## GET

* Used to retrieve resource(s)
* Never use it to add / update / delete resources
* The default verb of the browser's address bar
* Usually combined with parameters
* Should not include body
* Sometimes GET cannot be used for retrieval. For example if there is too may parameters. In these cases, is OK using POST.
* GET is idempotent.

## POST

* Used to add resource
* Could contain a message body that specifies the resource to be added
* Should not contain query string parameters
* Used to modify resource(s)
* POST isn't idempotent, because duplicated requests will cause duplicated resources.

## PUT

* Used to modify resource(s)
* Should contain a message body that specifies the resource to be modified
* Should not container query string parameter
* A new resource should be created if is requested to modify one that doesn't exists
  * But you can use your own discretion, for example response 404.
* PUT is idempotent.

## DELETE

* Used to delete resources
* never use it to add / update / retrieve resources
* Almost always combined with parameters.
* Should not include body.
* DELETE is idempotent.

### Rarely Used Verbs

* **PATCH**: Similar to put, but with partial updates

* **HEAD**: Same as GET, but without the body in the response

* **OPTIONS**: Describes the available verbs for the URL
  
  ```bash
  $ curl -X OPTIONS http://example.org -i
  HTTP/1.1 204 No Content
  Allow: OPTIONS, GET, HEAD, POST
  ```
  
  