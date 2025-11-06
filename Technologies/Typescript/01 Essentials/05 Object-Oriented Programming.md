# Object-Oriented Programming

## Classes

```typescript
class User {
  name: string;
  age: number;

  constructor(name: string, age: number) {
    this.name = name;
    this.age = age;
  }
}
```

Differently from JavaScript, you need define the attributes beforehand:

*   For example, the JavaScript code:

    ```javascript
    class User {
      constructor() {
        this.name ="Max";
      }
    }
    ```

    Is perfectly ok at JavaScript, but on TypeScript it will raise `Property 'name' does not exist on type 'User'.`. To fix it:

    ```typescript
    class User {
        name = "Max";
    
        constructor () {
            this.name = "Max"
        }
    }
    ```

### Shotcuts

The code

```typescript
class User {
  public name: string;
  private age: number;

  constructor(name: string, age: number) {
    this.name = name;
    this.age = age;
  }
}
```

Is equivalent of

```typescript
class User {
  constructor(public name: string, private age: number) {}
}
```

### Attributes visibility

*   `public` anyone can access
*   `private` only the class can access
*   `protected` only the own class or heirs can access

### `readonly`

Attributes assigned as `readonly` can be assigned only once. 

*   It is like a `const`, but works with properties instead of variables.

```typescript
class User {
  readonly id: number;   // cannot be reassigned later
  name: string;

  constructor(id: number, name: string) {
    this.id = id;       // ✅ allowed here
    this.name = name;
  }
}

const u = new User(1, "Alice");
u.name = "Bob";   // ✅ okay
u.id = 2;         // ❌ Error: Cannot assign to 'id' because it is a read-only property
```

### Getters and Setters

```typescript
class User {
  private _firstName: string = "";

  constructor(private lastName: string) {}

  set firstName(name: string) {
    if (name.trim() === "") {
      throw new Error("Invalid name.");
    }

    this._firstName = name;
  }

  get fullName() {
    return this._firstName + " " + this.lastName;
  }Q
}

const person = new User("Vieira");
person.firstName = "Matheus";
console.log(person.fullName);
```

### Static

#### Static attribute

```typescript
class User {
  private static nextId = 1; // shared across all instances

  public id: number;
  public name: string;

  constructor(name: string) {
    this.id = User.nextId++; // access static property via class name
    this.name = name;
  }

  // static method (doesn't need an instance)
  static resetIds(): void {
    User.nextId = 1;
  }
}

const u1 = new User("Alice");
const u2 = new User("Bob");
const u3 = new User("Charlie");

console.log(u1.id); // 1
console.log(u2.id); // 2
console.log(u3.id); // 3
```

#### Static method

```typescript
class User {
  constructor(
    public id: number,
    public name: string,
    public role: string
  ) {}

  // static factory method
  static createGuest(): User {
    return new User(0, "Guest", "reader");
  }
}

// usage
const guest = User.createGuest();
console.log(guest); // User { id: 0, name: "Guest", role: "reader" }

const alice = new User(1, "Alice", "admin");
console.log(alice);

```

## Inheritance

```typescript
// Base class (Parent)
class Animal {
  // accessible everywhere
  public name: string;

  // accessible in Animal AND classes that extend it
  protected species: string;

  // accessible ONLY within Animal
  private age: number;

  constructor(name: string, species: string, age: number) {
    this.name = name;
    this.species = species;
    this.age = age;
  }

  public makeSound(): void {
    console.log("Some generic animal sound");
  }

  protected getSpecies(): string {
    // protected method can be used by subclasses
    return this.species;
  }

  private getAge(): number {
    // private method can only be used inside Animal
    return this.age;
  }
}

// Derived class (Child)
class Dog extends Animal {
  public breed: string;

  constructor(name: string, breed: string, age: number) {
    super(name, "Dog", age);
    this.breed = breed;
  }

  // Override method
  public makeSound(): void {
    console.log("Woof! Woof!");
  }

  public describe(): void {
    // ✅ Can access `name` (public)
    console.log(`My dog's name is ${this.name}`);

    // ✅ Can access `species` (protected from parent)
    console.log(`It is a ${this.getSpecies()}`);

    // ❌ Cannot access `age` (private in parent)
    // console.log(this.age); // ❌ ERROR
  }
}

// Usage
const myDog = new Dog("Buddy", "Golden Retriever", 5);
myDog.makeSound();   // Output: Woof! Woof!
myDog.describe();
// Output:
// My dog's name is Buddy
// It is a Dog

// ❌ myDog.species  --> ERROR (protected, not accessible outside)
// ❌ myDog.age      --> ERROR (private, not accessible outside)
// ✅ myDog.name     --> Works (public)
```

## Abstract class

```typescript
// Abstract class
abstract class Animal {
  constructor(public name: string) {}

  // Abstract method (must be implemented in subclasses)
  abstract makeSound(): void;

  // Concrete method (shared by all subclasses)
  move(): void {
    console.log(`${this.name} is moving...`);
  }
}

// Subclass implementing abstract method
class Dog extends Animal {
  makeSound(): void {
    console.log("Woof! Woof!");
  }
}

class Cat extends Animal {
  makeSound(): void {
    console.log("Meow!");
  }
}

// Usage
const dog = new Dog("Buddy");
dog.makeSound();  // Woof! Woof!
dog.move();       // Buddy is moving...

const cat = new Cat("Whiskers");
cat.makeSound();  // Meow!
cat.move();       // Whiskers is moving...
```

## Interfaces

```typescript
interface Authenticatable {
  email: string;
  passpord: string;

  login(): void;
  logout(): void;
}

let user: Authenticatable;

user = {
  email: "test@example.com",
  passpord: "abc1",
  login() {
    // reach out to a database, check credentials, create a session
  },
  logout() {
    // clear the session
  },
};
```

### Interface vs TypeAlias

The above code is similar to:

```typescript
type Authenticatable = {
  email: string;
  passpord: string;

  login(): void;
  logout(): void;
}
```

And it is truly similar, and normally it is personal preference.

In some scenarios, the `interface` is a lot easier to merge with others `interfaces` that the type alias.

*   You can declare other interface with the same name, and the TypeScript will merge both:

    ```typescript
    interface Authenticatable {
      email: string;
      passpord: string;
    
      login(): void;
      logout(): void;
    }
    
    interface Authenticatable {
      role: string;
    }
    
    let user: Authenticatable;
    
    user = { // ❌ Property 'role' is missing in type '{ email: string; passpord: string; login(): void; logout(): void; }' but required in type 'Authenticatable'
      email: "test@example.com",
      passpord: "abc1",
      login() {},
      logout() {},
    };
    
    ```

    *   While you can't do it using type:

    ```typescript
    type Authenticatable = { // ❌ Duplicate identifier 'Authenticatable'.
        email: string;
        passpord: string;
    
        login(): void;
        logout(): void;
    }
    
    type Authenticatable = { // ❌ Duplicate identifier 'Authenticatable'.
        role: string;
    }
    ```


###   Interface to define function types

The code

```typescript
type SumFn = (a: number, b: number) => number;
```

is equivalent of

```typescript
interface SumFn {
  (a: number, b: number): number;
}
```

### Implementing interfaces

```typescript
interface Authenticatable {
  email: string;
  passpord: string;

  login(): void;
  logout(): void;
}

class AuthenticatableUser implements Authenticatable {
  constructor(public email: string, public passpord: string) {}

  login(): void {}
  logout(): void { }
}
```

The same class can implements multiple interfaces

### Extending interfaces

```typescript
interface Authenticatable {
  email: string;
  passpord: string;

  login(): void;
  logout(): void;
}

interface AuthenticatableAdmin extends Authenticatable {
  role: 'admin' | 'superadmin'
}
```
