# Relational Model

A **relation** is a set of **tuples** described by a **relation schema**. The schema defines the attributes; each tuple assigns a value to every attribute. This describes the logical structure of data, independently of how a database stores or retrieves it.

## Attributes, Tuples, and Relation Values

- **Attribute:** A named component of the schema, corresponding to a table column. Its **domain** specifies the values it can take.
- **Tuple:** One combination of attribute values in the relation, corresponding to a table row.
- **Relation value:** The set of tuples belonging to the relation at a particular time. As a set, it has no duplicate tuples or inherent row order.

The schema describes the structure; the relation value describes the data conforming to that structure at a given time.

## Relations and SQL Tables

A **table** is the SQL database object that organizes data into columns and rows. It resembles a relation, but the terms are not interchangeable:

- **Duplicates:** A relation contains no duplicate tuples. A SQL table permits duplicate rows unless constraints prevent them.
- **Missing values:** SQL supports `NULL` in nullable columns, whereas a tuple in the classical relational model assigns a value from each attribute's domain.
- **Ordering:** Neither a relation nor a SQL table guarantees an order for its tuples or rows. A query needs `ORDER BY` to specify result order.

## Keys and Referential Integrity

Keys express row identity and valid references through values in the table schema, rather than through physical storage locations.

A **superkey** is a set of attributes whose combined values uniquely identify a tuple in every relation value permitted by the schema's constraints. Uniqueness in the current data alone does not establish a superkey: future valid tuples must also satisfy that uniqueness rule. Adding attributes to a superkey preserves uniqueness, but adds no identifying power.

A **candidate key** is a minimal superkey: no proper subset of its attributes is itself a superkey. Minimal means that no attribute is redundant, not that the key has the fewest attributes among all candidate keys. A schema can have several candidate keys, with different numbers of attributes.

The choice among candidate keys gives them different roles:

- **Primary key:** The candidate key designated as the schema's identifier for each row. Its values must be unique and non-null.
- **Alternate key:** Any candidate key not chosen as the primary key. It remains a valid unique identifier; choosing a primary key does not remove the other candidate keys.

A **composite key** contains multiple attributes. For a composite candidate key, their combination is unique and every attribute is necessary: removing any attribute loses the uniqueness guarantee. A **composite primary key** is such a candidate key chosen as the primary key. Each column need not be unique on its own; uniqueness belongs to the combination.

Keys and the functional dependencies they imply constrain how attributes belong together in a schema; [normalization](05%20Relational%20Schema%20Normalization.md) uses these dependencies to reduce redundancy and modification anomalies.

A **foreign key** is a constraint requiring a reference to match an existing referenced key. This relationship enforces **referential integrity**: a non-null reference must not point to a nonexistent referenced row.

A database-enforced constraint rejects changes that violate its declared rule. It does not automatically enforce application rules beyond that constraint: a foreign key checks a reference, not whether a stored total agrees with the records it summarizes.

## Logical Keys and Index Search Keys

A logical key constrains identity or valid references; an [index](../Internals/01%20Tables,%20Pages,%20and%20Indexes.md#Indexes) organizes values for searching. These are different roles even when an index supports enforcement of a key constraint.

A **secondary index key** is the column or combination of columns used to search by other values. It need not be unique; a unique secondary index enforces uniqueness separately. The word *key* here describes search values, not a second primary-key constraint.
