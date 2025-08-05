# Rest

* Stands for Representational State Transfer
  * It means that REST API enables transfer of representation of a resource’s state
    * state is:
      * the current resource properties
      * result of an action on the resource
* REST isn't restricted on HTTP, because any API that follows the REST Architecture Constrains is considered RESTful.

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

## RRM

You can measure the RESTfulness using Richardson Maturity Model (RMM) of your HTTP API

* There is 4 levels, that begins with 0 (lowest level of REST compliance) and ends with 3 (highest level of REST compliance)

* the levels are:

  * **level 0**

    * RPC (Remote Procedure Cal)

      * The API are using XML as the data format
        * usually SOAP standard is commonly used

      * Uses HTTP as the transport
        * typically uses HTTP GET and POST

    * API endpoints look like verbs
      * e.g.: `http://.../getCustomerData`

  * **level 1**

    * Resources: Representation of real-world object

  * **level 2**

    * HTTP Verb: `GET`, `POST`, `DELETE`, `PUT`, etc
    * Manipulation must be made with right HTTP verb.
    * CRUD: 
      * Create - POST
      * read - GET
      * update - PUT
      * delete - DELETE

  * **level 3**

    * [HATEAOS](08 Advanced Topics.md#HateOAS)

## WebApp versus REST API

* WebAPP architecture forms the bases for REST API
  * both uses cleint - server
  * layered
  * caching
  * [HATEAOS](08 Advanced Topics.md#HateOAS)
* but there is differences
  * webAPP have no hard rules on interface, the REST have (Contract, Resources identity )
  * webAPP can be stateful. The REST is always stateless.
  * 
