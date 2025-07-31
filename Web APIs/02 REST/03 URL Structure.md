# URL Structure

* Defines the structure of the API
* The most important part of the API
  * developers will decide if they use your APIs or not based on URL structure

* Should be
  * Self explanatory
  * Consistent across the API
  * Predictable

## Domain name

* The first part of the URL
* Usually contains FQDN (Fully Qualified Domain Name) or server name
  * Protocol should be HTTPS
  * For FQDN - should have `api` in its name
    * for example:
      * `https://api.myapp.com`
      * `https://language.googleapis.com/v1/documents:analyzeEntities`
    * if not, you can put on the url, as `https://www.myapp.com/api`

## Version

* Assumes that your API will be updated

* Versioning is specially important when we don't control our clients

  * you can't force version upgrade

* Set version support policy (for example, minimum three years from the data of first realease).

* Only natural number (positive integer)

* could be prefixed with `v`

* It can be many strategies

  * URI Path Version: `http://www.myapp.com/api/v1`.

    * Default choose for public developers
      * Simple
      * Familiar to most developers
      * Easy to manage with minimal infrastructure support
    * Pros
      * Easy to understand and use.
      * Clear separation between versions.
      * Caches well and works with most proxies and CDNs.
    * Cons
      * Violates RESTful principle of resource uniformity.
      * Forces clients to change base URLs when upgrading.

  * Query Parameter: `https://api.example.com/resource?version=1`

    * Not recommended

    * Pros

      * Easy to implement and test.
      * Keeps the URI path clean.

    * Cons

      - Less visible in logs and documentation.

      - Can be problematic with caching proxies.

      - Not considered RESTful by some purists.

  * Header Parameter:

    ```
    GET /resource
    Accept: application/vnd.example.v1+json
    ```

    * Good when:
      * You need fine-grained control over representations.
      * Your clients are sophisticated or under your control (e.g., internal apps).
    * Pros
      * Clean and REST-compliant.
      * Allows content negotiation and flexible representation.
    * Cons
      * Harder to test/debug in browsers and CLI tools like curl.
      * Not always supported or handled well by intermediate systems (e.g., proxies, CDNs).

  * Subdomain Versioning: `https://v1.api.example.com/resource`
    * Pros:
      * Clear separation, useful for large organizations.
      * Can support independent infrastructure for each version.
    * Cons:
      * More complex DNS and routing configuration.
      * Uncommon; may confuse clients.

* Use URI Path Versioning for most public APIs

## Entity

* REST deals with resources, or entities
* Should be one word, no more
* Always use nouns to name entities
* Examples:
  * `/orders`: entity orders
  * `employees`: entity employees
  * `travels`: entity travels

* When dealing with a specific entity, use entity ID
  * The ID is part of the URL
  * Example: `/order/17`
  * Relevant for GET, PUT and DELETE
    * not for PST because the client can't know the ID of a to-be-entity
* When dealing with a entities that are dependent on other entities, use sub entities
  * Example: Get all items of order 17 `GET /order/17/items`
  * Same goes for sub-sub-entity, etc
*  you should generally use plural nouns for resource names. This is a widely accepted convention.
  * `GET /books` Get all books
  * `POST /books` Create a new book
  * `GET /books/1` Get book with ID 1
  * `PUT /books/1` Update book with ID 1
  * `DELETE /books/1` Delete book with ID 1

## Query Parameters

* Used to query the entities in GET method
* Come at the end of the URL, after `?`, and are concatenates with `&`
  * `/api/v1/orders?fromDate=12/12/2018&toDate=2/2/2019`
* Good to query a list of entities, instead of query exactly one entity (as on id parameter)
  * It no entities is found, it response a empty list.
    * on the other error, if you query using id, it should response a 404.
  * 