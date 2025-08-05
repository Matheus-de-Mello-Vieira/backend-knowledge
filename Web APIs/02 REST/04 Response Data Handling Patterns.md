# Response Data Handling Patterns

When the API serves different clients, they could have different demands for data. For example, if an end-point for a list of entities always responds with the same number of entities, a client with a large screen size would need to make multiple requests to fill its screen. On the other hand, a client with a small screen size would make a single request and receive more entities than necessary, wasting bandwidth. This issue almost always occurs nowadays, as there is a wide variety of devices with different screen sizes.

To solve this problem, we can apply the following principle: The client controls response data

## Partial Responses

Client controls the granularity: the client can choose each attributes the server should send.

* GraphQL works better in this situation than REST, but there is some workarounds for REST

* On REST, there is many ways to implement it:

  * projections: holds expression that identifies the fields

    * Linked-In:

      * `/people/me?fields=firstname, lastname` to query the attributes `firstname` and `lastname`
      * `/sampleService/42?fields=id, parentFields:(childField1,childField2)` to query the attributes `id`, `parentFields.childField1` and `parentFields.childField2`
      * if you want to implement this kind of implementation, see the [Linked-In API documentation](https://learn.microsoft.com/en-us/linkedin/shared/api-guide/concepts/projections?context=linkedin%2Fconsumer%2Fcontext).

    * 

      Meetup API: supports two parameters: `only` and `ommit`

      * `?only=id,name`

  * filters: provides ways to filter the fields in response

## Pagination

Client controls the number of rows to me sent.

There are some approachs for the pagination:

1) Cursor

   * a cursor is a strucutre that enables traversal of records

     * a cursor is a token that points to a element in a list

   * Cursor based pagination is considered most efficient

   * [Facebook uses it](https://developers.facebook.com/docs/graph-api/overview#paging): it use the angular based cursor

     * The page 2 would be:

       ```json
       {
         "data": [
           // Endpoint data is here
         ],
         "paging": {
           "cursors": {
             "after": "MTAxNTExOTQ1MjAwNzISNDE=", // page 1
             "before": "NDMyNzQyODI3OTQw" // page 3
           },
           "previous": "https://graph.facebook.com/me/albums?limit=25&before=NDMyNzQyODI3OTQw",
           "next": "https://graph.facebook.com/me/albums?limit=25&after=MTAxNTExOTQ1MjAwNzISNDE="
         }
       }
       ```

2) Offset based

   * two parameters:
     * `offset` the initial element in the page
     * `limit` the max number of elements in the page 
   * Many companies uses this approach:
     * Linked-In: `/people/start=50&count=25`
     * Facebook: `/friends?offset=50&limit=25`
     * Twitter: `/search?page=3&rpp=25`
       * `rpp` stands for rows per page
   * most popular approach

3) Use HTTP link header

   * Use of Link header

     * it haves a url, and a relationship (`rel`)

   * Also known as web linking

   * Least popular approach. 

   * Github uses it

     ```
     Link: <https://api.github.com/user/repos?page=3&per_page=100>; rel="next", 
     <https://api.github.com/user/repos?page=50&per_page=100>; rel="last"
     ```

     