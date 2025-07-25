# PostgreSQL

We will use https://www.npmjs.com/package/pg, that have a quite thorough documentation https://node-postgres.com/

```bash
npm install pg
```

## Use

### Connection

`Pool` and `Client`  receives the same authorization arguments

* Enviroment variable

  ```javascript
  PGUSER=process.env.USER
  PGPASSWORD=null
  PGHOST=localhost
  PGPORT=5432
  PGDATABASE=process.env.USER
  ```

* Programmatic

  ```javascript
  const pool = new Pool({
    user: 'dbuser',
    password: 'secretpassword',
    host: 'database.server.com',
    port: 3211,
    database: 'mydb',
  })
  ```

* Connection URI

  ```javascript
  const connectionString = 'postgresql://dbuser:secretpassword@database.server.com:3211/mydb'
   
  const pool = new Pool({
    connectionString,
  })
   
  ```

### Reading

```javascript
import { Client } from 'pg'
const client = new Client()
await client.connect()
 
const res = await client.query('SELECT $1::text as message', ['Hello world!'])
console.log(res.rows[0].message) // Hello world!
await client.end()
```

#### Error Handling

```javascript
import { Client } from 'pg'
const client = new Client()
await client.connect()
 
try {
   const res = await client.query('SELECT $1::text as message', ['Hello world!'])
   console.log(res.rows[0].message) // Hello world!
} catch (err) {
   console.error(err);
} finally {
   await client.end()
}
```

#### Pooling

Connection pool

* you can set `max` and `min` number of connections.
  * `min`  is the number of connections not affected by `idleTimeoutMillis`
  * `allowExitOnIdle` allow the node event loop to exit as soon as all clients in the pool are idle, even if their socket is still open to the postgres server
    * if false (the default), pool will keep clients open & connected to the backend until `idleTimeoutMillis` expire for each client and node will maintain a ref to the socket on the client, keeping the event loop alive until all clients are closed  after being idle or the pool is manually shutdown with `pool.end()`.
  * timeouts
    * `connectionTimeoutMillis`: number of milliseconds to wait before timing out when connecting a new client
      * by default this is 0 which means no timeout
    * `idleTimeoutMillis`: number of milliseconds a client must sit idle in the pool and not be checked out before it is disconnected from the backend and discarded
      * default is 10000 (10 seconds)
      * set to 0 to disable auto-disconnection of idle clients
    * `maxLifetimeSeconds`: Sets a max overall life for the connection.
      *  A value of 60 would evict connections that have been around for over 60 seconds, regardless of whether they are idle.
      * It's useful to force rotation of connection pools through middleware so that you can rotate the underlying servers.
      * The default is disabled (value of zero)

```javascript
import pg from 'pg'
const { Pool } = pg
const pool = new Pool({
    max: 10, 
    min: 0,
    allowExitOnIdle: false,
    connectionTimeoutMillis: 0,
    idleTimeoutMillis: 10000,
    maxLifetimeSeconds: 0,
}) //default values
 
console.log('starting async query')
const result = await pool.query('SELECT NOW()')
console.log('async query finished')
 
console.log('starting callback query')
pool.query('SELECT NOW()', (err, res) => {
  console.log('callback query finished')
})
 
console.log('calling end')
await pool.end()
console.log('pool has drained')
```

##### Centralize Pool Connection

Create a javascript file in your project, to centralize the `Pool` object

* on `./db.js`

  ```javascript
  const { Pool } = require('pg');
  
  const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
  });
  
  const query = (text, params) => pool.query(text, params);
  
  module.exports = {
    query,
  };
  ```

* on `anyFile.js`

  ```javascript
  const db = require('./db');
  
  async function getUsers() {
    const res = await db.query('SELECT * FROM users');
    return res.rows;
  }
  ```

#### Cursor

A cursor can be used to efficiently read through large result sets without loading the entire result-set into memory ahead of time. It's useful to simulate a 'streaming' style read of data, or exit early from a large result set. The cursor is passed to `client.query` and is dispatched internally in a way very similar to how normal queries are sent, but the API it presents for consuming the result set is different.

```bash
npm install pg pg-cursor
```

```javascript
import { Pool } from 'pg'
import Cursor from 'pg-cursor'
 
const pool = new Pool()
const client = await pool.connect()
const text = 'SELECT * FROM my_large_table WHERE something > $1'
 
const cursor = client.query(new Cursor(text, [10]))
 
const { rows } = await cursor.read(100)
console.log(rows.length) // 100 (unless the table has fewer than 100 rows)
cursor.close(() => client.release())
```

If `rows.length==0`, there is no more data

```javascript
while (true) {
  const { rows } = await cursor.read(100)
  if (rows.length === 0) {
    break  // no more data
  }
  console.log(`Fetched ${rows.length} rows`)
  // process rows here
}
```

### Transactions

```javascript
import { Pool } from 'pg'
const pool = new Pool()
 
const client = await pool.connect()
 
try {
  await client.query('BEGIN')
  const queryText = 'INSERT INTO users(name) VALUES($1) RETURNING id'
  const res = await client.query(queryText, ['brianc'])
 
  const insertPhotoText = 'INSERT INTO photos(user_id, photo_url) VALUES ($1, $2)'
  const insertPhotoValues = [res.rows[0].id, 's3.bucket.foo']
  await client.query(insertPhotoText, insertPhotoValues)
  await client.query('COMMIT')
} catch (e) {
  await client.query('ROLLBACK')
  throw e
} finally {
  client.release()
}
```

### Data Type

`pg` will convert json, jsonb, and datatime automatically according their data types on the database schema

* There is no data type in JavaScript for a uuid/guid so node-postgres converts a uuid to a string. JavaScript has great support for JSON and node-postgres converts json/jsonb objects directly into their JavaScript object via [`JSON.parse`](https://github.com/brianc/node-pg-types/blob/master/lib/textParsers.js#L193). Likewise sending an object to the PostgreSQL server via a query from node-postgres, node-postgres will call [`JSON.stringify`](https://github.com/brianc/node-postgres/blob/e5f0e5d36a91a72dda93c74388ac890fa42b3be0/lib/utils.js#L47) on your outbound value, automatically converting it to json for the server.

  ```javascript
  const createTableText = `
  CREATE EXTENSION IF NOT EXISTS "pgcrypto";
   
  CREATE TEMP TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    data JSONB
  );
  `
  // create our temp table
  await client.query(createTableText)
   
  const newUser = { email: 'brian.m.carlson@gmail.com' }
  // create a new user
  await client.query('INSERT INTO users(data) VALUES($1)', [newUser])
   
  const { rows } = await client.query('SELECT * FROM users')
   
  console.log(rows)
  /*
  output:
  [{
    id: 'd70195fd-608e-42dc-b0f5-eee975a621e9',
    data: { email: 'brian.m.carlson@gmail.com' }
  }]
  */
  ```

  

* node-postgres will convert instances of JavaScript date objects into the expected input value for your PostgreSQL server. Likewise, when reading a `date`, `timestamp`, or `timestamptz` column value back into JavaScript, node-postgres will parse the value into an instance of a JavaScript `Date` object.

  ```javascript
  const createTableText = `
  CREATE TEMP TABLE dates(
    date_col DATE,
    timestamp_col TIMESTAMP,
    timestamptz_col TIMESTAMPTZ
  );
  `
  // create our temp table
  await client.query(createTableText)
   
  // insert the current time into it
  const now = new Date()
  const insertText = 'INSERT INTO dates(date_col, timestamp_col, timestamptz_col) VALUES ($1, $2, $3)'
  await client.query(insertText, [now, now, now])
   
  // read the row back out
  const result = await client.query('SELECT * FROM dates')
   
  console.log(result.rows)
  // {
  // date_col: 2017-05-29T05:00:00.000Z,
  // timestamp_col: 2017-05-29T23:18:13.263Z,
  // timestamptz_col: 2017-05-29T23:18:13.263Z
  // }
  ```

