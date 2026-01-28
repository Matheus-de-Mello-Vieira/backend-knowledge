# **Expressing RDBMS Tables in Redis**

## **Data Mapping Principles**

When representing relational tables in Redis (e.g., for caching rows or creating high-speed lookup tables), the design shifts from monolithic tables to individual keys.

- **Key Granularity:** Do not hesitate to generate a large number of key-value pairs; Redis is designed to handle millions of small keys efficiently.
- **Row Representation:** Store each table row as a distinct key.
  - **Data Type:** Use **Redis Hashes** (`Hash Map`) as the standard equivalent for a row. This allows you to retrieve (`HGETALL`) or delete (`DEL`) the entire "row" object at once.
- **Key Naming Convention:** Construct key names by combining the table name and primary key values with a separator (e.g., `:`).
  - *Composite Keys:* If the table has a composite primary key, concatenate the values directly in the Redis key string (e.g., `orderline:{order_id}:{product_id}`).
- **Attribute Storage:** Store the columns of the row as fields within the Hash.

## Querying & Indexing Patterns

Since Redis does not have a built-in query engine like SQL, you must build "access paths" manually.

- **Direct Access (Single Row):** If you know the Primary Key, construct the Redis key strings directly to fetch data.
- **Pattern Matching:** Use wildcards (e.g., `*`) to scan for keys that match a specific structure.
- **Secondary Indexes:** To replicate SQL `WHERE` clauses (e.g., "Find by Role"), create separate data structures—such as **Sets** or **Sorted Sets**—that map values back to the Primary Keys.

## **Example 1: Simple Primary Key**

```sql
CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    role VARCHAR(50),
    hire_date DATE
);
```

Map the Primary Key `id` directly to the Redis key suffix.

### **Store Row Data (Hash):**

```
HSET employee:42 name "Ana Silva" role "Engineer" hire_date "2024-09-01"
```

### **Retrieve Data:**

- **Get specific entity:**

  ```
  HGETALL employee:42
  ```

- **Get all entities (Scan):**

  ```
  SCAN 0 MATCH employee:*
  ```

### **Implement Secondary Indexes:**

- **Index by Role (Set):** Maps a role to a list of IDs.
  - *Add to index:* `SADD employees:role:Engineer 42`
  - *Query index:* `SMEMBERS employees:role:Engineer`
- **Index by Hire Date (Sorted Set):** Maps a timestamp to an ID for range queries.
  - *Add to index:* `ZADD employees:by_hire_date 1725148800 42`
  - *Query range (Newest 10):* `ZREVRANGE employees:by_hire_date 0 9`

## **Example 2: Composite Primary Key**

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

Flatten the composite key `(order_id, product_id)` into the Redis key string itself.

### **Store Row Data:**

Key format: `orderline:{order_id}:{product_id}`

```
HSET orderline:1001:77 quantity 2 price 19.90
```

### **Manual Indexing for Relationships**

Because you cannot join tables in Redis, you maintain Sets to track relationships.

#### **A. Index: "What products are in this order?"**

- **Structure:** Set (Key: `order:{id}:products`, Member: `product_id`)

- **Add:**

  ```
  SADD order:1001:products 77
  ```

- **Query:**

  ```
  SMEMBERS order:1001:products
  ```

  *(Logic: Get the list of product IDs, then loop through them to `HGETALL` the orderline details.)*

#### **B. Index: "Which orders contain this product?"**

- **Structure:** Set (Key: `product:{id}:orders`, Member: `order_id`)

- **Add:**

  ```
  SADD product:77:orders 1001
  ```

- **Query:**

  ```
  SMEMBERS product:77:orders
  ```

### **Optional Metadata Structures**

- **Global Lookup:** A Set containing all valid Order IDs to perform existence checks.

  ```
  SADD orders 1001
  ```

- **Order Header:** A Hash for the parent `orders` table data.

  ```
  HSET order:1001 status "paid" order_date "2026-01-10" customer_id 555
  ```

- **Sorted Lookup:** A Sorted Set to retrieve orders by date.

  ```
  ZADD orders:by_date 1768003200 1001
  ```

  *(Allows `ZREVRANGE` to fetch the latest orders.)*
