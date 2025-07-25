# MongoDB

## MongoDB native driver

The official MongoDB driver for Node.js.

* NPM package: https://www.npmjs.com/package/mongodb

* Documentation: https://mongodb-node.netlify.app/docs/drivers/node/current/

* Install command

  ```bash
  npm install mongodb
  ```

### Overview

It is a straight map of the MongoDB features 

```javascript
const { MongoClient } = require("mongodb");

// Replace the uri string with your connection string
const uri = "<connection string uri>";

const client = new MongoClient(uri);

async function run() {
  try {
    const database = client.db('sample_mflix');
    const movies = database.collection('movies');

    // Queries for a movie that has a title value of 'Back to the Future'
    const query = { title: 'Back to the Future' };
    const movie = await movies.findOne(query);

    console.log(movie);
  } finally {
    await client.close();
  }
}
run().catch(console.dir);
```

### Cursor

```javascript
async function run() {
  ...
  const cursor = myColl.find();

  while (await cursor.hasNext()) {
    console.log(await cursor.next());
  }
}
```

## Mongoose

* NPM package: https://www.npmjs.com/package/mongoose

* Documentation: https://mongoosejs.com/

* Install command

  ```bash
  npm install mongodb
  ```

* Mongoose is a higher-level abstraction built on top of the MongoDB native driver.
* It adds features like schemas, validation, population, middleware, and models on top of the lower-level driver.

Mongoose forces a semi-rigid schema from the beginning. With Mongoose, developers must define a Schema and Model.

* A schema defines the structure of your collection documents. A Mongoose schema maps directly to a MongoDB collection.

  ```javascript
  const blog = new Schema({
    title: String,
    slug: String,
    published: Boolean,
    author: String,
    content: String,
    tags: [String],
    createdAt: Date,
    updatedAt: Date,
    comments: [{
      user: String,
      content: String,
      votes: Number
    }]
  });
  ```

* Models take your schema and apply it to each document in its collection. Models are responsible for all document interactions like creating, reading, updating, and deleting (CRUD).

  ```javascript
  const Blog = mongoose.model('Blog', blog);
  ```


### Example

* On `index.js`

  ```javascript
  import mongoose from 'mongoose'
  
  mongoose.connect("mongodb+srv://<username>:<password>@cluster0.eyhty.mongodb.net/myFirstDatabase?retryWrites=true&w=majority") 
  ```

* On `model/Blog.js`

  ```javascript
  import mongoose from 'mongoose';
  const { Schema, model } = mongoose;
  
  const blogSchema = new Schema({
    title:  {
      type: String,
      required: true,
    },
    slug:  {
      type: String,
      required: true,
      lowercase: true,
    },
    published: {
      type: Boolean,
      default: false,
    },
    author: {
      type: String,
      required: true,
    },
    content: String,
    tags: [String],
    createdAt: {
      type: Date,
      default: () => Date.now(),
      immutable: true,
    },
    updatedAt: Date,
    comments: [{
      user: String,
      content: String,
      votes: Number
    }]
  });
  
  const Blog = model('Blog', blogSchema);
  export default Blog;
  ```

#### Create

1) 
    ```javascript
    import mongoose from 'mongoose';
    import Blog from './model/Blog';
    
    mongoose.connect("mongodb+srv://mongo:mongo@cluster0.eyhty.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    
    // Create a new blog post object
    const article = new Blog({
      title: 'Awesome Post!',
      slug: 'awesome-post',
      published: true,
      content: 'This is the best post ever',
      tags: ['featured', 'announcement'],
    });
    
    // Insert the article in our MongoDB database
    await article.save();
    ```

2. ```javascript
   // Create a new blog post and insert into database
   const article = await Blog.create({
     title: 'Awesome Post!',
     slug: 'awesome-post',
     published: true,
     content: 'This is the best post ever',
     tags: ['featured', 'announcement'],
   });
   
   console.log(article);
   ```


#### Read

* Finding data

  ```javascript
  const article = await Blog.findById("62472b6ce09e8b77266d6b1b").exec();
  console.log(article);
  ```

* Project document fields

  ````javascript
  const article = await Blog.findById("62472b6ce09e8b77266d6b1b", "title slug content").exec();
  console.log(article);
  ````

* Making queries by mongoose style

  * `where()` makes the filtration

    ```javascript
    // Instead of using a standard find method
    const blogFind = await Blog.findOne({ author: "Jesse Hall" });
    
    // Use the equivalent where() method
    const blogWhere = await Blog.findOne().where("author").equals("Jesse Hall");
    console.log(blogWhere)
    ```

  * `select()` makes the projection

    ```javascript
    // Instead of using a standard find method
    const blog = await Blog.find(
      { author: "Jesse Hall" },
      { title: 1, author: 1 }
    );
    
    // Use the equivalent where() method
    const blog = await Blog.where("author").equals("Jesse Hall").select("title author")
    console.log(blog)
    ```

#### Update

```javascript
article.title = "The Most Awesomest Post!!";
await article.save();
console.log(article);
```

#### Delete

```javascript
const blog = await Blog.deleteOne({ author: "Jesse Hall" })
console.log(blog)

const blog = await Blog.deleteMany({ author: "Jesse Hall" })
console.log(blog)
```

#### Other useful methods

* `exists()`: returns either `null` or the ObjectId of a document that matches the provided query.

  ```javascript
  const blog = await Blog.exists({ author: "Jesse Hall" })
  console.log(blog)
  ```

### Reference between Schemas

* `User.js`

  ```javascript
  import mongoose from 'mongoose';
  const {Schema, model} = mongoose;
  
  const userSchema = new Schema({
    name: {
      type: String,
      required: true,
    },
    email: {
      type: String,
      minLength: 10,
      required: true,
      lowercase: true
    },
  });
  
  const User = model('User', userSchema);
  export default User;
  ```

* `blog.js`

  ```javascript
  import mongoose from 'mongoose';
  const { Schema, SchemaTypes, model } = mongoose;
  
  const blogSchema = new Schema({
    ...,
    author: {
      type: SchemaTypes.ObjectId,
      ref: 'User',
      required: true,
    },
    ...,
    comments: [{
      user: {
        type: SchemaTypes.ObjectId,
        ref: 'User',
        required: true,
      },
      content: String,
      votes: Number
    }];
  });
  ...
  ```

we set the `author` and `comments.user` to `SchemaTypes.ObjectId` and added a `ref`, or reference, to the user model.

This will allow us to “join” our data a bit later.

To write

```javascript
const user = await User.create({
  name: 'Jesse Hall',
  email: 'jesse@email.com',
});
const article = await Blog.create({
  title: 'Awesome Post!',
  slug: 'Awesome-Post',
  author: user._id,
  content: 'This is the best post ever',
  tags: ['featured', 'announcement'],
});
console.log(article);
```

To read

```javascript
const article = await Blog.findOne({ title: "Awesome Post!" }).populate("author");
console.log(article);
```

### Middleware

In Mongoose, middleware are functions that run before and/or during the execution of asynchronous functions at the schema level.

Here’s an example. Let’s update the `updated` date every time an article is saved or updated. We’ll add this to our `Blog.js` model.

```javascript
blogSchema.pre('save', function(next) {
  this.updated = Date.now(); // update the date every time a blog post is saved
  next();
});
```

Besides `pre()`, there is also a `post()` mongoose middleware function.

```javascript
blogSchema.pre('save', function (next) {
  console.log(`About to save the blog post titled: "${this.title}"`);
  next();
});

blogSchema.post('save', function (doc) {
  console.log(`Successfully saved blog post with ID: ${doc._id}`);
});
```

