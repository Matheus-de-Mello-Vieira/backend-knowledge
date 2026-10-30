# Expressing RDBMS Tables in Redis

## Mapping rows to keys

Representing relational tables in Redis—for example, to cache rows or build high-speed lookups—shifts the design from tables to individual keys. Redis is designed to handle millions of small keys, so each row can have its own key. A Redis Hash holds the row's columns as fields; `HGETALL` retrieves the hash and `DEL` deletes its key. Name each key by combining the table name and primary-key value with a separator such as `:`. For a composite primary key, include each component, as in `orderline:{order_id}:{product_id}`.

The available access path depends on what the query already knows:

- **Direct access:** When the primary key is known, construct the Redis key and fetch the row directly.
- **Pattern matching:** Wildcards such as `*` select keys with a matching name structure during a scan.
- **Secondary access paths:** Redis does not provide a SQL-style query engine. Sets or Sorted Sets map indexed values back to primary keys for `WHERE`-style queries such as “find employees by role.”

## Simple primary key

Consider an `employees` table:

```sql
CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    role VARCHAR(50),
    hire_date DATE
);
```

The primary key `id` becomes the Redis key suffix. Store the other columns in a Hash:

```redis
HSET employee:42 name "Ana Silva" role "Engineer" hire_date "2024-09-01"
```

`HGETALL employee:42` retrieves that row. `SCAN 0 MATCH employee:*` scans for keys using the `employee:` naming pattern.

Different queries require different index structures:

- **Role lookup:** A Set maps each role to employee IDs. `SADD employees:role:Engineer 42` indexes the employee; `SMEMBERS employees:role:Engineer` retrieves matching IDs.
- **Hire-date ordering:** A Sorted Set maps a timestamp score to each ID for range queries. `ZADD employees:by_hire_date 1725148800 42` indexes the employee; `ZRANGE employees:by_hire_date 0 9 REV` retrieves the newest ten entries.

> [!note] Earlier reverse-range command
> `ZREVRANGE` returns a reverse rank range. Since Redis 6.2.0, `ZRANGE ... REV` provides the same ordering.

## Composite primary key and relationships

An order-line row is identified by both its order and product IDs:

```sql
-- Parent Table
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    status VARCHAR(20),
    order_date DATE
);

-- Child Table with Composite PK
CREATE TABLE order_lines (
    order_id INT,
    product_id INT,
    quantity INT,
    price DECIMAL(10, 2),
    PRIMARY KEY (order_id, product_id)
);
```

Flatten `(order_id, product_id)` into the key `orderline:{order_id}:{product_id}`. The row's attributes remain Hash fields:

```redis
HSET orderline:1001:77 quantity 2 price 19.90
```

Redis does not perform relational joins here. Maintain access paths for each relationship query:

- **Products in an order:** `SADD order:1001:products 77` adds the product ID to a Set keyed by `order:{id}:products`. `SMEMBERS order:1001:products` yields IDs that the application can use to fetch the corresponding order-line Hashes with `HGETALL`.
- **Orders containing a product:** `SADD product:77:orders 1001` adds the order ID to a Set keyed by `product:{id}:orders`. `SMEMBERS product:77:orders` retrieves those order IDs.

Additional structures support other access needs:

- **Global order lookup:** `SADD orders 1001` adds a valid order ID to a Set for existence checks.
- **Order header:** `HSET order:1001 status "paid" order_date "2026-01-10" customer_id 555` stores the parent row's fields in a Hash.
- **Date-ordered lookup:** `ZADD orders:by_date 1768003200 1001` indexes an order by date; `ZRANGE ... REV` retrieves the latest orders.
