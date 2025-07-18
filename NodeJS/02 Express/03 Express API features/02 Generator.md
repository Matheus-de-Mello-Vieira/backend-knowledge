# Generator

https://expressjs.com/en/starter/generator.html

## install

```bash
$ npm install express-generator -g
```

## Basic use

```bash
$ express myNewExpressSite --ejs --git
```

It will create the folder `myNewExpressSite` with

```
.
├── app.js
├── bin
│   └── www
├── .gitignore
├── package.json
├── public
│   ├── images
│   ├── javascripts
│   └── stylesheets
│       └── style.css
├── routes
│   ├── index.js
│   └── users.js
└── views
    ├── error.ejs
    └── index.ejs
```

So you need run:

```bash
$ npm install
```

So

```bash
$ nodemon
```

will create a full-fledged api

They don't put helmet by default