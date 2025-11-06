# Redis Data Management

## Keys and Values

* Redis is a Key based data structure
* Redis is in the family of database called "Key-Value stores"
* Important: the data can only be retrieved if we know the exact 'key'used to store it

* To define a value:

  ```
  > set key value
  ```

* To get the value:

  ```
  > get key
  ```

### Example

```
127.0.0.1:6379> set name "Matheus"
OK
127.0.0.1:6379> get name
"Matheus"
```

You you try to get a key that doesn't exists, you will receive a `nil`

```
127.0.0.1:6379> get no-existent
(nil)
```

## Deleting Keys

* To delete a key:

  ```
  > del key
  ```

  * You can deleted many keys at once:

    ```
    > del key1 key2 key3
    ```

  * You will receive the number of deleted entitiies.

### Example

To delete:

```
127.0.0.1:6379> del name
(integer) 1
```

If you try to delete a a key that doesn't exists, you will receive a `0`:

```
127.0.0.1:6379> del name
(integer) 1
```

## Check if exists

To check if a key exists:
```
> exists name
```

* You will receive `1` if it exists, `0` otherwise.

* You can test multiples keys

  ```
  > exists key1 key2
  ```

  * You will receive the number of found entitiies.

### Example
If you check the key:

```
127.0.0.1:6379> exists name
(integer) 1
```

## Expirations

A key can be:

* **volatile**: a key with an expire set
* **persistent**: a key that will never expire as no timeout is associated.

To define a key with 120 seconds of TTL:

```
set name "Matheus" ex 120
```

You can check the remaning time with:

```
ttl name
```

* If the key is persistent (no timeout associated), you will receive a `-1`.
* If the key is already expired, you will receive a `-2`. 

You can overide the expiration time with:

```
expire name 10
```

* This means that the key `name` will be set to expire 10 seconds from the moment the `expire` command is executed.

You can remove the expiration form a key

```
persist name
```

* It will return `1` if the key had it's timeout removed, and `0` if it is already persistent or it don't exists.

You can also do it using millisecond:

```
set name "Matheus" px 120000
```

To check the ttl in milliseconds:

```
pttl name 
```

You can overide the expiration time in milliseconds:

```
pexpire name 10000
```

### How Redis handle keys expirations

Two ways

* **passive way**: A key is passively expired simply when some client tries to access it, and the key is found to be timed out.
* **active way** Test 20 random keys from the set of volatile keys, and delete all the keys found expired. If more than 25% of keys are expired, start again from step 1.
  * Redis does it 10 times per second by default, but it is configurable.