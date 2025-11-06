# Rate Limit

## Problem

You're express server is being harassed by an unwanted visitor. If a client makes more than 10 requests in a second, or 500 in one minute, block them as early as possible to keep your server running optimally. Respond with a 429 http code.

## Solution

I installed https://www.npmjs.com/package/express-rate-limit

```javascript
import { rateLimit } from 'express-rate-limit'

app.use(rateLimit({
	windowMs: 1000,
	limit: 10,
}))

app.use(rateLimit({
	windowMs: 60 * 1000,
	limit: 500,
}))
```

It uses `store: memory-store`, the default, that saves the data on the local server memory, that is fine for a single instance of backend. However, if you want horizontally scale your server, you need to put it in a shared storage, that can be:

| Name                                                         | Description                                                  | Legacy/Modern API   |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------- |
| [memory-store](https://github.com/express-rate-limit/express-rate-limit/blob/main/source/memory-store.ts) | *(default)* Simple in-memory option. Does not share state when app has multiple processes or servers. | Modern as of v6.0.0 |
| [cluster-memory-store](https://npm.im/@express-rate-limit/cluster-memory-store) | A memory-store wrapper that shares state across all processes on a single server via the [node:cluster](https://nodejs.org/api/cluster.html) module. Does not share state across multiple servers. | Modern              |
| [rate-limit-redis](https://npm.im/rate-limit-redis)          | A [Redis](http://redis.io/)-backed store, more suitable for large or demanding deployments. | Modern as of v3.0.0 |
| [rate-limit-memcached](https://npmjs.org/package/rate-limit-memcached) | A [Memcached](https://memcached.org/)-backed store.          | Modern as of v1.0.0 |
| [rate-limit-mongo](https://www.npm.im/rate-limit-mongo)      | A [MongoDB](https://www.mongodb.com/)-backed store.          | Legacy              |
| [precise-memory-rate-limit](https://www.npm.im/precise-memory-rate-limit) | A memory store similar to the built-in one, except that it stores a distinct timestamp for each key. | Modern as of v2.0.0 |
| [rate-limit-postgresql](https://www.npm.im/@acpr/rate-limit-postgresql) | A [PostgreSQL](https://www.postgresql.org/)-backed store.    | Modern              |
| [typeorm-rate-limit-store](https://www.npmjs.com/package/typeorm-rate-limit-store) | Supports a variety of databases via [TypeORM](https://typeorm.io/): MySQL, MariaDB, CockroachDB, SQLite, Microsoft SQL Server, Oracle, SAP Hana, and more. | Modern              |