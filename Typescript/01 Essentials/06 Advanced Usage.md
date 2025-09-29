# Advanced Usage

## Intersection Types

```typescript
type FileData = {
  path: string;
  content: string;
}

type DatabaseData = {
  connectionUrl: string;
  credentials: string;
}

type Status = {
  isOpen: boolean;
  errorMessage?: string;
}

type AccessedFileData = FileData & Status;
type AccessedDatabaseData = DatabaseData & Status;
```

*   this code is similar to

    ```typescript
    interface FileData {
      path: string;
      content: string;
    }
    
    interface DatabaseData {
      connectionUrl: string;
      credentials: string;
    }
    
    interface Status {
      isOpen: boolean;
      errorMessage?: string;
    }
    
    interface AccessedFileData extends FileData, Status {}
    interface AccessedDatabaseData extends DatabaseData, Status {}
    ```

*   It combines all the properties of multiple types into a single type.

    *   You can think of it as "A **and** B at the same time."
    *   The resulting type must satisfy *all* constraints.

*   Comparing with Union Types, the type

    ```typescript
    type FileOrStatus = FileData | Status;
    ```

    means a `FileOrStatus` object can be:

    -   Just a `FileData`, **or**

        ```typescript
        const f: FileOrStatus = { path: "/tmp/file.txt", content: "hello" };
        ```

    -   Just a `Status`, **or**

        ```typescript
        const s: FileOrStatus = { isOpen: false, errorMessage: "Permission denied" };
        ```

    -   Something that satisfies *both* (because that still fits "either/or").

        ```typescript
        const both: FileOrStatus = {
          path: "/tmp/file.txt",    // from File
          content: "hello",         // from File
          isOpen: true,             // from Status
          errorMessage: "None"      // from Status (optional)
        };
        ```

        

## Union Types

A union type represents either one type or the other (but not necessarily both).

```typescript
type FileSource = { path: string };
type DBSource = { connectionUrl: string };
type Source = FileSource | DBSource;

function loadData(source: Source) {
  if('path' in source) {
    // source.path; => use that to open the file
    // the typescript already figures out that we have a FileSource
    return
  }
  source.connectionUrl //the typescript already figures out that we have a DBSource
}
```

### Discriminated unioun:

A common pattern for unions is have a key do differ between the types:

```typescript
type FileSource = { type: "file"; path: string };
const fileSource: FileSource = {
  type: "file",
  path: "some/path/to/file.csv",
};

type DBSource = { type: "db"; connectionUrl: string };
const dbSource: DBSource = {
  type: "db",
  connectionUrl: "some-connection-url",
};

type Source = FileSource | DBSource;

function loadData(source: Source) {
  if (source.type === 'file') {
    // the typescript already figures out that we have a FileSource
    console.log("Path: ", source.path)
    return;
  }
  console.log("Connection URL: ", source.connectionUrl)
  source.connectionUrl; // the typescript already figures out that we have a DBSource
}

```

The `instance of` doesn't works here because it is a runtime check against a class (constructor function). But in your code, `FileSource` and `DBSource` are just type aliases for plain object shapes. They don’t exist at runtime as constructors.

### Instance of

It works only on classes, not types:

```typescript
class User {
  constructor(public name: string) {}

  join() {
    // ...
  }
}

class Admin {
  constructor(permissions: string[]) {}

  scan() {
    /// ...
  }
}

type Entity = User | Admin;

function init(entity: Entity) {
  if (entity instanceof User) {
    entity.join();
    return;
  }

  entity.scan();
}
```

## "Outsourcing" type guards

For example the function

```typescript
function isFile(source: Source) {
    return source.type == 'file'
}
```

Have the type `source is FileSource`, so typescript can use to safeguard time on compiling type, or the vscode can reckoning it.

```typescript
function loadData(source: Source) {
  if(isFile(source)) {
    // source.path; => use that to open the file
    // the typescript already figures out that we have a FileSource
    return
  }
  source.connectionUrl //the typescript already figures out that we have a DBSource
}
```

## Function Overload

```typescript
function getLength(val: string | any[]) {
  if (typeof val === "string") {
    const numberOfWords = val.split(" ").length;
    return `${numberOfWords} words`;
  }

  return val.length;
}

const numberOfWords = getLength("does this works?")
const numberOfItems = getLength([1, 2, 3])
```

In this case, both `numberOfWords` and `numberOfItems` are recognized as `string | number` even if by logic, `numberOfWords` only can be `string` and `numberOfItems` only can be `number`.

So you can add multiple function signatures to the same function:

```typescript
function getLength(val: string) : string;
function getLength(val: any[]) : number
function getLength(val: string | any[]) {
  if (typeof val === "string") {
    const numberOfWords = val.split(" ").length;
    return `${numberOfWords} words`;
  }

  return val.length;
}

const numberOfWords = getLength("does this works?")
const numberOfItems = getLength([1, 2, 3])
```

Now `numberOfWords` is deemed as `string`, and `numberOfItems` as `number`

## Index Types

You allows the developer to choose the name of the property:

```typescript
type DataStore = {
  [prop: string]: number
}
```

That means:

-   Any property name (`string`) is allowed.
-   But the value **must** be either a `number` or a `boolean`.

It is the same of:

```typescript
type DataStore = Record<string, number>
```

Examples:

Valid assignments:

```typescript
const store1: DataStore = {
  count: 42,
  isActive: true,
  retries: 0,
  debug: false,
};

const store2: DataStore = {}; // empty object is fine

const store3: DataStore = {
  "some key with spaces": 123,
  anotherKey: false,
};
```

Invalid assignments:

```typescript
const bad1: DataStore = {
  name: "Alice", // ❌ string not allowed
};

const bad2: DataStore = {
  values: [1, 2, 3], // ❌ array not allowed
};

const bad3: DataStore = {
  nested: { x: 1 }, // ❌ object not allowed
};

const bad4: DataStore = {
  maybe: null, // ❌ null not part of number | boolean
};

const bad5: DataStore = {
  pi: 3.14,
  valid: true,
  invalid: "hello", // ❌ string again
};

```

## `as const` statement

It makes the typescript be narrower as possible on typing inference:

```typescript
let roles = ['admin', 'guest', 'editor'] as const
```

The type will be `let roles: readonly ["admin", "guest", "editor"]`

*   If try to push, it will error:

    ```typescript
    roles.push("max") // ❌ Property 'push' does not exist on type 'readonly ["admin", "guest", "editor"]' 
    ```

*   If you get the value, the typescript will infer the value for you:

    ```typescript
    const firstRole = roles[0] // type: "admin"
    ```


## `satisfies` keyword

Given

```typescript
const dataEntries: Record<string, number> = {
  entry1: 0.51,
  entry2: -1.23,
};
```

You can run

```typescript
dataEntries.entry3
```

without type error, because the typescript deems `dataEntries` as a object that can have any string as propriety. 

To avoid it, you can:

```typescript
const dataEntries = {
  entry1: 0.51,
  entry2: -1.23,
} satisfies Record<string, number>;

dataEntries.entry3; // Property 'entry3' does not exist on type '{ entry1: number; entry2: number; }'
```

It will check if the given values satisfies `Record<string, number>`, but will assign the variable the narrower type 

*   ```typescript
    const dataEntries = {
      entry1: 0.51,
      entry2: ' ', // ❌ Type 'string' is not assignable to type 'number'.
    } satisfies Record<string, number>;
    ```
