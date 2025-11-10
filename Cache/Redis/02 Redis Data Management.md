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

## Key Spaces

Key Spaces in Redis is similar to database namespaces schemas.

* this allow you to have same key name in multiple key spaces

* you can manage keys per each key spaces

* The first and default key space is `0`.

* You can change the key space with

  ```
  select 1
  ```


* You can see all keys set on the current space using

  ````
  keys *
  ````

* You can delete all keys in the space using

  ```
  flushdb
  ```

* You cannot link keys with one key spcae to another key spaces.

Example

```
127.0.0.1:6379> set key1 value1
OK
127.0.0.1:6379> get key1
"value1"
127.0.0.1:6379> select 1
OK
127.0.0.1:6379[1]> set key1 value2
OK
127.0.0.1:6379[1]> get key1
"value2"
127.0.0.1:6379[1]> set key2 value2
OK
127.0.0.1:6379> keys *
1) "key1"
2) "key2"
127.0.0.1:6379[1]> select 0
OK
127.0.0.1:6379> get key1
"value1"
127.0.0.1:6379> keys *
1) "key1"
127.0.0.1:6379> flushdb
OK
127.0.0.1:6379> keys *
(empty array)
```

## Key naming conventions

* Keep it simpel but robuts
* Very short keys are often not a good idea - there are not very informative.
* Try best schema based on your database design
  * `object:<id>`
* The max allowed key size is 512 MB
* Redis keys are binary safe - you can use any binary sequence as a key
* Empty string is also a valid key

For example, given the entity `User` with attributes `id`, `name`, `group`, `friends`.

* You can use:

  * `user:100`

  * `user:100:group`

  * `user:100:friends`

* It is not recommended:

  * `userJohn`
    * use name is dangerous
      * it can happen to be written in non-English letters like "陽翔" or "عالي".
        * The redis will be OK with is on the technical perspective, but it will jeopardize the readability.
      * if you have multiple users named “John,” you immediately get collisions:
    * Redis key namespaces (using `:`) are a common convention
      * This lets you easily group and filter keys by prefix — e.g. `SCAN user:*` finds all user-related data.
        * You can use `SCAN user*`, which internally makes no difference, but it produces less predictable results because it can match things like `userSettings` or `userProfileBackup`.

## Key patterns matching

You can search for the keys that match a pattern with `keys <pattern>`

* `h?llo` matches `hello`, `hallo` and `hxllo`
* `h*llo` matches `hllo` and `heeeelo`.
* `h[ae]llo` matches `hello`and `hallo`, but not `hillo` nor `haello`
  * `h[ee]llo` will match `hello`, but not `heelo` 

* `h[^e]llo` matches `hallo`, `hbllo`..., but not `hello`
  * matches the same thing of `h*llo`, except `hello`

* `h[a-c]llo` matches `hallo`, `hbllo` and `hcllo`.
  * it is a range.


### Caveats:

* Redis running on an entry level laptop can scan a 1 million key database in 40 miliseconds.
* Consider `keys` as a command that should only be used in production environments with extreme care. It may ruin performance when it is executed against large databases.
  * Consider use `SCAN`.

### In pratice

You can: 

* look all users with:

  ```
  127.0.0.1:6379> keys user:*
  1) "user:101"
  2) "user:100"
  3) "user:100:group"
  4) "user:101:group"
  ```

* look the group of all users

  ```
  127.0.0.1:6379> keys user:*:group
  1) "user:100:group"
  2) "user:101:group"
  ```

  
