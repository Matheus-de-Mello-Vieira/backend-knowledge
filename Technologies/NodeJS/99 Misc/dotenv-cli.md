A too to load the .env from comand line, perfect to load the .env on local enviroment, but now on the cloud (it is normally is made by docker)

To use it, install:/

```javascript
npm install --save-dev dotenv-cli
```

So on `package.json`

```javascript
"scripts": {
    "start": "dotenv -e .env --  node ./src/index.js"
  },
```

