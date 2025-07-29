# Rest

* Stands for Representational State Transfer
  * It means that REST API enables transfer of representation of a resource’s state
    * state is:
      * the current resource properties
      * result of an action on the resource

## Structure

### Request

* **Method**: HTTP Verb (GET, POST, PUT, DELETE, ...)
* **URL**: Location of the resource + parameters
* **Header**: Meta-data of the request (User Agent, ...)
* **Body**: contents of the request (optional)

### Response

* **Status code**: 200 (Success), 404 (Not Found), etc
* **Headers**: Meta-data of the request (Content Type, ...)
* **Body**: Contents of the response (optional)
  * Usually it is a JSON, but rarely can be also XML or HTML
