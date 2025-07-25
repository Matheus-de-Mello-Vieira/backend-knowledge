# MongoDB

## MongoDB native driver

The official MongoDB driver for Node.js.

* NPM package: https://www.npmjs.com/package/mongodb

* Documentation: https://mongodb-node.netlify.app/docs/drivers/node/current/

* Install command

  ```bash
  npm install mongodb
  ```

### Overview

It is a straight map of the MongoDB features 

```javascript
const { MongoClient } = require("mongodb");

// Replace the uri string with your connection string
const uri = "<connection string uri>";

const client = new MongoClient(uri);

async function run() {
  try {
    const database = client.db('sample_mflix');
    const movies = database.collection('movies');

    // Queries for a movie that has a title value of 'Back to the Future'
    const query = { title: 'Back to the Future' };
    const movie = await movies.findOne(query);

    console.log(movie);
  } finally {
    await client.close();
  }
}
run().catch(console.dir);
```

### Cursor

```javascript
async function run() {
  ...
  const cursor = myColl.find();

  while (await cursor.hasNext()) {
    console.log(await cursor.next());
  }
}
```

## Mongoose

* Mongoose is a higher-level abstraction built on top of the MongoDB native driver.
* It adds features like schemas, validation, population, middleware, and models on top of the lower-level driver.