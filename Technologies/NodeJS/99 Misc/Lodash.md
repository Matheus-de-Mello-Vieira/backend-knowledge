# Javascript

Lodash makes JavaScript easier by taking the hassle out of working with arrays, numbers, objects, strings, etc.

- Iterating arrays, objects, & strings
- Manipulating & testing values
- xxxxxxxxxx1 1(variable != null ? variable.value : undefined)javascript

```bash
npm install lodash
```

https://lodash.com/docs/4.17.15

Before writing anything using lodash, consider using chain: https://lodash.com/docs/4.17.15#chain

You can run loadash code to a json on the website `https://www.jsonquerytool.com/`.

## Examples

### **Order & Page from Array**

*(paginate directly from an array)*

```javascript
return chain(post.comments)
  .orderBy("id", "asc")   // sort
  .slice(offset, offset + limit) // page
  .value();
```

### **Order & Page from Object**

*(paginate values of a map/dictionary)*

```javascript
return chain(post.comments)
  .values()               // object → array
  .orderBy("id", "asc")   // sort
  .slice(offset, offset + limit) // page
  .value();
```