# Linked List Challenge

## Description

### 🚀 Challenge: Implement a Singly Linked List

**Objective:**
Create a singly linked list from scratch in the programming language of your choice (e.g., Python, Java, C++, JavaScript).

**Requirements:**

2. **LinkedList Class**
   Implement the following methods:

   * `append(value)` → Add a new node with the given value at the end of the list.
   * `prepend(value)` → Add a new node with the given value at the beginning of the list.
   * `insert(value, position)` → Insert a new node at a specific index (0-based).
   * `delete(value)` → Remove the first occurrence of a node with the given value.
   * `find(value)` → Return the index of the first occurrence of the value, or `-1` if not found.
   * `print_list()` → Print all elements in the list in order.

3. **Bonus (Optional):**

   * Implement a `reverse()` method to reverse the entire linked list in place.
   * Implement a `length()` method that returns the number of nodes.

## Solution

It created a typescript, and test using `vitest`

```typescript
class EmptyNode<T> {
  constructor(public nextNode: Node<T> | null = null) {}
}

class Node<T> extends EmptyNode<T> {
  constructor(public readonly value: T) {
    super();
  }
}

class LinkedList<T> {
  private root: EmptyNode<T> = new EmptyNode<T>();

  append(value: T): void {
    const newNode = new Node(value);

    const tail = this.tail();

    tail.nextNode = newNode;
  }

  private tail(): EmptyNode<T> {
    let tail = this.root;

    for (const node of this.iterNodes()) {
      tail = node;
    }

    return tail;
  }

  prepend(value: T): void {
    this._insert(value, 0);
  }

  insert(value: T, position: number): void {
    if (position < 0) {
      throw Error("Position must be non-negative");
    }

    this._insert(value, position);
  }

  private _insert(value: T, position: number): void {
    const newNode = new Node(value);

    const previousNode = this._iloc(position - 1);

    newNode.nextNode = previousNode.nextNode;
    previousNode.nextNode = newNode;
  }

  delete(value: T): void {
    const { previous, current } = this._find(value);

    if (current === null) {
      throw Error("Value not found");
    }
    previous.nextNode = current.nextNode;
  }

  find(value: T): number {
    const { index } = this._find(value);

    return index;
  }

  private _iloc(index: number): EmptyNode<T> {
    let currentNode: EmptyNode<T> | null = this.root;

    for (let i = -1; i < index && currentNode !== null; i++) {
      currentNode = currentNode.nextNode;
    }

    if (currentNode === null) {
      throw Error("Index out of bounds");
    }

    return currentNode;
  }

  private _find(value: T): {
    index: number;
    current: Node<T> | null;
    previous: EmptyNode<T>;
  } {
    let previousNode = this.root;
    let index = -1;

    for (let currentNode of this.iterNodes()) {
      if (currentNode.value === value) {
        return {
          index: index + 1,
          current: currentNode,
          previous: previousNode,
        };
      }

      index++;
      previousNode = currentNode;
    }

    return {
      index: -1,
      current: null,
      previous: this.root,
    };
  }

  toList(): T[] {
    return [...this.iterNodes()].map((node) => node.value);
  }

  length(): number {
    let result = 0;

    for (const _ of this.iterNodes()) {
      result++;
    }

    return result;
  }

  private *iterNodes(): IterableIterator<Node<T>> {
    let currentNode = this.root.nextNode;

    while (currentNode !== null) {
      yield currentNode;
      currentNode = currentNode.nextNode;
    }
  }

  reverse(): void {
    let pivotNode = this.root.nextNode;

    while (pivotNode !== null && pivotNode.nextNode !== null) {
      const newFirstNode = pivotNode.nextNode;

      pivotNode.nextNode = newFirstNode.nextNode;
      newFirstNode.nextNode = this.root.nextNode;
      this.root.nextNode = newFirstNode;
    }
  }
}

export default LinkedList;
```

```typescript
import LinkedList from "./app.js";
import { describe, it, expect } from "vitest";

describe("LinkedList", () => {
  it("append", () => {
    const sut = createLinkedListWith(["a"]);

    sut.append("b");

    expect(sut.toList()).toEqual(["a", "b"]);
  });

  it("prepend", () => {
    const sut = createLinkedListWith(["a", "b"]);

    sut.prepend("c");

    expect(sut.toList()).toEqual(["c", "a", "b"]);
  });

  describe("insert", () => {
    it("valid", () => {
      const sut = createLinkedListWith(["a", "b"]);

      sut.insert("c", 1);

      expect(sut.toList()).toEqual(["a", "c", "b"]);
    });

    it("negative", () => {
        const sut = createLinkedListWith(["a", "b"]);

        expect(() => sut.insert("d", -1)).toThrowError();
    })

    it("out bounds", () => {
        const sut = createLinkedListWith(["a", "b"]);

        expect(() => sut.insert("d", 4)).toThrowError();
    })
  });

  describe("delete", () => {
    it("found", () => {
      const sut = createLinkedListWith(["a", "b", "c"]);

      sut.delete("b");

      expect(sut.toList()).toEqual(["a", "c"]);
    });

    it("not found", () => {
      const sut = createLinkedListWith(["a", "b", "c"]);

      expect(() => sut.delete("d")).toThrowError();
    });
  });

  it("find", () => {
    const sut = createLinkedListWith(["a", "b", "c"]);

    expect(sut.find("a")).toEqual(0);
    expect(sut.find("b")).toEqual(1);
  });

  describe("reverse", () => {
    const baseValues = ["a", "b", "c", "d", "e"];

    for (let i = 0; i < baseValues.length; i++) {
      it(`${i} elements`, () => {
        {
          return () => {
            const slice = baseValues.slice(0, i);
            expect(slice.length).toEqual(i);

            const sut = createLinkedListWith(slice);

            sut.reverse();

            expect(sut.toList()).toEqual(slice.reverse());
          };
        }
      });
    }
  });

  it("length", () => {
    const sut = createLinkedListWith(["a", "b", "c"]);

    expect(sut.length()).toEqual(3);
  });

  function createLinkedListWith(initial: string[]) {
    const sut = new LinkedList<string>();

    initial.forEach((item) => sut.append(item));

    return sut;
  }
});

```

