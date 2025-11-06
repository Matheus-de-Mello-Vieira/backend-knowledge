# Web API

An API exposed by a web component, allowing other components to interact with it;

* Platform Agnostic
* Standard Protocols, usually over HTTP
* Usually Request/Response based

Some types of Web APIs are:

* **SOAP**

  * stands for Simple Object Access Protocol

  * Designed in 1998 for Microsoft

  * XML-based

  * RPC Style

    * the clients call for a procedure (subroutine) to execute in the server
    * RPC stands for Remote Procedure Call

  * Outdated

  * Do not use, unless have to

  * Structure
    
    ```xml
    <?xml version="1.0"?>
    <soap:Envelope 
        xmlns:soap="http://www.w3.org/2001/12/soap-envelope" 
        soap:encodingStyle="http://www.w3.org/2001/12/soap-encoding">
        <soap:Body xmlns:m="http://www.stock.org/stock">
            <m:GetStockPrice>
                <m:StockName>IBM</m:StockName>
            </m:GetStockPrice>
        </soap:Body>
    </soap:Envelope>
    ```

* **REST**

  * stands for Representational State Transfer
  * Designed in 2000 by Roy Fielding
  * URL + JSON Based
  * Message Style
  * De factor Standard for APIs

* **GraphQL**

  * Developed internally in 2012 by Facebook

  * Released publicly in 2015

  * Enables very flexible querying, updating and subscribing to data changes

    * allows the client specify exactly which fields to get

  * JSON based

  * Very flexible

  * Requires some upfront dev effort

  * Requires performance optimization

  * Example

    * Request

      ```apl
      query {
        posts {
          id
          title
          body
          published
          author {
            name
          }
        }
      }
      ```

    * Response

      ```json
      {
        "data": {
          "posts": [
            {
              "id": "1",
              "title": "Post Title",
              "body": "Post content here...",
              "published": true,
              "author": {
                "name": "Author Name"
              }
            },
            {
              "id": "2",
              "title": "Another Title",
              "body": "Another post content...",
              "published": false,
              "author": {
                "name": "Another Author"
              }
            }
          ]
        }
      }
      ```

* **gRPC**

  * [Fundamentals of Backend Engineering](../../Backend Engineering/Fundamentals of Backend Engineering/03 Protocols/11 gRPC.md)
  * Quite performant
  * Not widely used yet
    * Uses HTTP2 that isn't quite popular
  * Requires specialized libraries at both ends
