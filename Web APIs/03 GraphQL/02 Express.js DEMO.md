# Express.JS + GraphQL

## Basic setup

```bash
npm install express graphql-http graphql
```

*   For demo proposes only: `npm install --save-dev expect`

`app.js`

```javascript
import express from "express";
import { GraphQLSchema, GraphQLObjectType, GraphQLString } from "graphql";
import { createHandler } from "graphql-http/lib/use/express";

const schema = new GraphQLSchema({
  query: new GraphQLObjectType({
    name: "Query",
    fields: {
      hello: {
        type: GraphQLString,
        resolve: () => "world",
      },
    },
  }),
});

const app = express();

app.all("/graphql", createHandler({ schema }));

app.listen({ port: 4000 });
console.log("Listening to port 4000");

```

and on `client.js`

```javascript
import { createClient } from "graphql-http";
import expect from 'expect';

const client = createClient({
  url: "http://localhost:4000/graphql",
});

(async () => {
  let cancel = () => {
    /* abort the request if it is in-flight */
  };

  const result = await new Promise((resolve, reject) => {
    let result;
    cancel = client.subscribe(
      {
        query: "{ hello }",
      },
      {
        next: (data) => (result = data),
        error: reject,
        complete: () => resolve(result),
      }
    );
  });

  expect(result).toEqual({data: { hello: "world" }});
})();
```

Or, but [ruru](https://github.com/graphile/crystal/tree/main/grafast/ruru) :

*   `npm install ruru --save-dev`
*   `npx ruru -SP -p 4001 -e http://localhost:4000/graphql`
*   Now I can access `http://127.0.0.1:4001/` for a fancy web site to test my graphql

## Books

I added it on `app.js`

```javascript
const authors = [
  { id: 1, name: 'J. K. Rowling' },
  { id: 2, name: 'J. R. R. Tolkien' },
  { id: 3, name: 'Brent Weeks' }
]

const books = [
  { id: 1, name: 'Harry Potter and the Chamber of Secrets', authorId: 1 },
  { id: 2, name: 'Harry Potter and the Prisoner of Azkaban', authorId: 1 },
  { id: 3, name: 'Harry Potter and the Goblet of Fire', authorId: 1 },
  { id: 4, name: 'The Fellowship of the Ring', authorId: 2 },
  { id: 5, name: 'The Two Towers', authorId: 2 },
  { id: 6, name: 'The Return of the King', authorId: 2 },
  { id: 7, name: 'The Way of Shadows', authorId: 3 },
  { id: 8, name: 'Beyond the Shadows', authorId: 3 }
]
```

Created the schema:

```javascript
const BookType = new GraphQLObjectType({
  name: "Book",
  description: "This represents a book",
  fields: {
    id: {
      type: new GraphQLNonNull(GraphQLInt),
    },
    name: {
      type: new GraphQLNonNull(GraphQLString),
    },
    authorId: {
      type: new GraphQLNonNull(GraphQLInt),
    },
  },
});

const RootQueryType = new GraphQLObjectType({
  name: "Query",
  description: "Root Query",
  fields: {
    books: {
      type: new GraphQLList(BookType),
      description: "List of All Books",
      resolve: () => books,
    },
  },
});

const schema = new GraphQLSchema({
  query: RootQueryType,
});
```

And now I can query the books:

```apl
{
  books {
    name
  }
}
```

Results in:

```javascript
{"data":{"books":[
    {"name":"Harry Potter and the Chamber of Secrets"},
    {"name":"Harry Potter and the Prisoner of Azkaban"},
    {"name":"Harry Potter and the Goblet of Fire"},
    {"name":"The Fellowship of the Ring"},
    {"name":"The Two Towers"},
    {"name":"The Return of the King"},
    {"name":"The Way of Shadows"},
    {"name":"Beyond the Shadows"}
]}}
```

### Books > Author

Given

```javascript
const AuthorType = new GraphQLObjectType({
  name: "Author",
  description: "This represents a author",
  fields: {
    id: {
      type: new GraphQLNonNull(GraphQLInt),
    },
    name: {
      type: new GraphQLNonNull(GraphQLString),
    },
  },
});
```

Lets add the possibility of search about the author inside the books.

```javascript
const BookType = new GraphQLObjectType({
  ...
  fields: {
    ....
    author: {
      type: AuthorType,
      resolve: (book) => {
        return authors.find((author) => author.id === book.authorId);
      },
    },
  },
});
```

And now the query:

```javascript
{
  books {
    name
    author {
      name
    }
  }
}
```

Gives me:

```json
{"data":{"books":[
    {"name":"Harry Potter and the Chamber of Secrets","author":{"name":"J. K. Rowling"}},
    {"name":"Harry Potter and the Prisoner of Azkaban","author":{"name":"J. K. Rowling"}},
    {"name":"Harry Potter and the Goblet of Fire","author":{"name":"J. K. Rowling"}},
    {"name":"The Fellowship of the Ring","author":{"name":"J. R. R. Tolkien"}},
    {"name":"The Two Towers","author":{"name":"J. R. R. Tolkien"}},
    {"name":"The Return of the King","author":{"name":"J. R. R. Tolkien"}},
    {"name":"The Way of Shadows","author":{"name":"Brent Weeks"}},
    {"name":"Beyond the Shadows","author":{"name":"Brent Weeks"}}
]}}
```

### Author > Books

You could try to add
```javascript
const AuthorType = new GraphQLObjectType({
  ....
  fields: {
    ...
    books: {
      type: new GraphQLList(BookType),
      resolve: (author) => {
        return authors.filter((book) => book.authorId === author.id);
      },
    },
  },
});
```

But the `BookType` wasn't declared yet, so it won't work. Instead you need to declare the `fields` as  a method, so it is executed afterwards the declaration.

*   It is a good practice to always declare the fields this way

```javascript
const AuthorType = new GraphQLObjectType({
  name: "Author",
  description: "This represents a author",
  fields: () => ({
    id: {
      type: new GraphQLNonNull(GraphQLInt),
    },
    name: {
      type: new GraphQLNonNull(GraphQLString),
    },
    books: {
      type: new GraphQLList(BookType),
      resolve: (author) => {
        return books.filter((book) => book.authorId === author.id);
      },
    },
  }),
});
```

So the query

```apl
{
  authors {
    name
    books {
      name
    }
  }
}
```

gives

```json
{"data":{"authors":[
      {"name":"J. K. Rowling","books":[
            {"name":"Harry Potter and the Chamber of Secrets"},
            {"name":"Harry Potter and the Prisoner of Azkaban"},
            {"name":"Harry Potter and the Goblet of Fire"}
      ]},
      {"name":"J. R. R. Tolkien","books":[
            {"name":"The Fellowship of the Ring"},
            {"name":"The Two Towers"},
            {"name":"The Return of the King"}
      ]},
      {"name":"Brent Weeks","books":[
            {"name":"The Way of Shadows"},
            {"name":"Beyond the Shadows"}
      ]}
]}}
```

## Single Book

```json
const RootQueryType = new GraphQLObjectType({
  name: "Query",
  description: "Root Query",
  fields: () => ({
    book: {
      type: BookType,
      description: "A single book",
      args: {
        id: {
          type: GraphQLInt,
        },
      },
      resolve: (parent, args) => books.find((book) => book.id === args.id),
    },
    ....
  }),
});
```

Now the query

```apl
{
  book(id: 1) {
    name
  }
}
```

Gives me

```json
{
  "data": {
    "book": {
      "name": "Harry Potter and the Chamber of Secrets"
    }
  }
}
```

## Mutations

Mutations are the GraphQL version of POST, PUT and DELETE

```javascript
const RootMutationType = new GraphQLObjectType({
  name: "Mutation",
  description: "Root Mutation",
  fields: () => ({
    addBook: {
      type: BookType,
      description: "Add a book",
      args: {
        name: {
          type: new GraphQLNonNull(GraphQLString),
        },
        authorId: {
          type: new GraphQLNonNull(GraphQLInt),
        },
      },
      resolve: (parent, { name, authorId }) => {
        const book = {
          id: books.length + 1,
          name,
          authorId,
        };

        books.push(book);

        return book;
      },
    },
  }),
});

const schema = new GraphQLSchema({
  query: RootQueryType,
  mutation: RootMutationType,
});
```

Then the query:

```apl
mutation {
  addBook(authorId: 1, name: "Order of the Phoenix ") {
    name
    id
  }
}
```

Will return

````apl
{
  "data": {
    "addBook": {
      "name": "Order of the Phoenix ",
      "id": 9
    }
  }
}
````

And add the book on the list

## Wrap up

`app.js`

```javascript
import express from "express";
import {
  GraphQLSchema,
  GraphQLObjectType,
  GraphQLNonNull,
  GraphQLList,
  GraphQLInt,
  GraphQLBoolean,
  GraphQLString,
  GraphQLError,
} from "graphql";
import { createHandler } from "graphql-http/lib/use/express";

const authors = [
  { id: 1, name: "J. K. Rowling" },
  { id: 2, name: "J. R. R. Tolkien" },
  { id: 3, name: "Brent Weeks" },
];

const books = [
  { id: 1, name: "Harry Potter and the Chamber of Secrets", authorId: 1 },
  { id: 2, name: "Harry Potter and the Prisoner of Azkaban", authorId: 1 },
  { id: 3, name: "Harry Potter and the Goblet of Fire", authorId: 1 },
  { id: 4, name: "The Fellowship of the Ring", authorId: 2 },
  { id: 5, name: "The Two Towers", authorId: 2 },
  { id: 6, name: "The Return of the King", authorId: 2 },
  { id: 7, name: "The Way of Shadows", authorId: 3 },
  { id: 8, name: "Beyond the Shadows", authorId: 3 },
];

const AuthorType = new GraphQLObjectType({
  name: "Author",
  description: "This represents a author",
  fields: () => ({
    id: {
      type: new GraphQLNonNull(GraphQLInt),
    },
    name: {
      type: new GraphQLNonNull(GraphQLString),
    },
    books: {
      type: new GraphQLList(BookType),
      resolve: (author) => {
        return books.filter((book) => book.authorId === author.id);
      },
    },
  }),
});

const BookType = new GraphQLObjectType({
  name: "Book",
  description: "This represents a book",
  fields: () => ({
    id: {
      type: new GraphQLNonNull(GraphQLInt),
    },
    name: {
      type: new GraphQLNonNull(GraphQLString),
    },
    authorId: {
      type: new GraphQLNonNull(GraphQLInt),
    },
    author: {
      type: AuthorType,
      resolve: (book) => {
        return authors.find((author) => author.id === book.authorId);
      },
    },
  }),
});

const RootQueryType = new GraphQLObjectType({
  name: "Query",
  description: "Root Query",
  fields: () => ({
    book: {
      type: BookType,
      description: "A single book",
      args: {
        id: {
          type: GraphQLInt,
        },
      },
      resolve: (parent, args) => books.find((book) => book.id === args.id),
    },
    books: {
      type: new GraphQLList(BookType),
      description: "List of All Books",
      resolve: () => books,
    },
    author: {
      type: AuthorType,
      description: "A single Author",
      args: {
        id: {
          type: GraphQLInt,
        },
      },
      resolve: (parent, args) =>
        authors.find((author) => author.id === args.id),
    },
    authors: {
      type: new GraphQLList(AuthorType),
      description: "List of All Authors",
      resolve: () => authors,
    },
  }),
});

const schema = new GraphQLSchema({
  query: RootQueryType,
});

const app = express();

app.all("/graphql", createHandler({ schema }));

app.listen({ port: 4000 });
console.log("Listening to port 4000");
```

The query

*  The query 
   ```apl
    {
      authors {
        name
        books {
          name
        }
      }
      books {
        name
        author {
          name
        }
      }
    }
   ```

   gives me

   ```json
   {"data":{
     "authors":[
       {"name":"J. K. Rowling","books":[
         {"name":"Harry Potter and the Chamber of Secrets"},
         {"name":"Harry Potter and the Prisoner of Azkaban"},
         {"name":"Harry Potter and the Goblet of Fire"}
       ]},
       {"name":"J. R. R. Tolkien","books":[
         {"name":"The Fellowship of the Ring"},
         {"name":"The Two Towers"},
         {"name":"The Return of the King"}
       ]},
       {"name":"Brent Weeks","books":[
         {"name":"The Way of Shadows"},
         {"name":"Beyond the Shadows"}
       ]}
     ],
     "books":[
       {"name":"Harry Potter and the Chamber of Secrets","author":{"name":"J. K. Rowling"}},
       {"name":"Harry Potter and the Prisoner of Azkaban","author":{"name":"J. K. Rowling"}},
       {"name":"Harry Potter and the Goblet of Fire","author":{"name":"J. K. Rowling"}},
       {"name":"The Fellowship of the Ring","author":{"name":"J. R. R. Tolkien"}},
       {"name":"The Two Towers","author":{"name":"J. R. R. Tolkien"}},
       {"name":"The Return of the King","author":{"name":"J. R. R. Tolkien"}},
       {"name":"The Way of Shadows","author":{"name":"Brent Weeks"}},
       {"name":"Beyond the Shadows","author":{"name":"Brent Weeks"}}
     ]
   }}
   ```
   
*   The query

    ```apl
    {
      author(id: 1) {
        name
      }
    }
    ```

    Gives me

    ```json
    {
      "data": {
        "author": {
          "name": "J. K. Rowling"
        }
      }
    }
    ```

    

