# Logging

* Winston - https://www.npmjs.com/package/winston
* Morgan (what the express generator uses) - https://www.npmjs.com/package/morgan
* Express-logging - https://www.npmjs.com/package/express-logging

## Morgan

 Specifically designed to log incoming HTTP requests in Express apps.

```javascript
const express = require('express');
const morgan = require('morgan');
const app = express();

app.use(morgan('dev')); // logs requests like GET /home 200 10ms
```

That `dev` is the format of the log, see documentation, in section "Predefined Formats"

Look at possibilities 

```javascript
var express = require('express')
var morgan = require('morgan')
var path = require('path')
var rfs = require('rotating-file-stream') // need to install

var app = express()

const accessLogStream = rfs.createStream('access.log', {
    interval: '1d',
    path: path.join(__dirname, 'log')
});

const errorLogStream = rfs.createStream('error.log', {
    interval: '1d',
    path: path.join(__dirname, 'log')
});

app.use(morgan('combined', {
    stream: accessLogStream, // can't declare here because it would cause recreation on each time the server starts
    skip: (req, res) => res.statusCode >= 400
}));

app.use(morgan('combined', {
    stream: errorLogStream,
    skip: (req, res) => res.statusCode < 400
}));

app.get('/', function (req, res) {
    res.send('hello, world!')
})
```

## Winston

A full-featured logging library for logging everything from info/debug to error logs, including to files, consoles, external service

```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.simple(),
  transports: [
    new winston.transports.Console({
      stderrLevels: ['error'] // error-level logs go to stderr
    })
  ]
});

logger.info('Server started');
logger.warn('Disk usage high');
logger.error('Fatal error occurred');

```

### Levels

You can create your own set of levels, the default is ` winston.config.npm.levels`, that is:

| Level     | Numeric | Purpose                             |
| --------- | ------- | ----------------------------------- |
| `error`   | 0       | Critical errors — system failure    |
| `warn`    | 1       | Warnings — something might go wrong |
| `info`    | 2       | General information                 |
| `http`    | 3       | HTTP-related logs                   |
| `verbose` | 4       | Verbose debugging info              |
| `debug`   | 5       | Internal debugging messages         |
| `silly`   | 6       | Very low-level, noisy output        |

The basic pratices are:

* Use:

  - `error` for things that broke

  - `warn` for recoverable issues

  - `info` for startup, shutdown, and high-level events

  - `debug`/`verbose` during development or detailed analysis

* Adjust `level` based on environment:
    ```javascript
    level: process.env.NODE_ENV === 'production' ? 'info' : 'debug'
    ```



### Formats

1.  * If you use
        ```javascript
        winston.format.simple()
        ```
    * the logs would be
        ```
        info: Server started
        warn: Disk usage high
        error: Fatal error occurred
        ```
1. * If you use
        ```javascript
        format: winston.format.combine(
          winston.format.timestamp(),
          winston.format.simple()
        )
        ```
    * the logs would be
        ```
        2025-07-24T14:22:15.123Z info: Server started
        2025-07-24T14:22:15.123Z warn: Disk usage high
        2025-07-24T14:22:15.125Z error: Fatal error occurred
        ```
1. * If you use
        ```javascript
        winston.format.json()
        ```
    * the logs would be
        ```
        {"level":"info","message":"Server started"}
        {"level":"warn","message":"Disk usage high"}
        {"level":"error","message":"Fatal error occurred"}
        ```
1. * If you use
        ```javascript
        format: winston.format.combine(
          winston.format.timestamp(),
          winston.format.json()
        )
        ```
    * the logs would be
        ```
        {"level":"info","message":"Server started","timestamp":"2025-07-24T14:23:01.123Z"}
        {"level":"warn","message":"Disk usage high","timestamp":"2025-07-24T14:23:01.124Z"}
        {"level":"error","message":"Fatal error occurred","timestamp":"2025-07-24T14:23:01.125Z"}
        ```

### Transports

A **transport** in Winston is like a pipe: it takes your log message and sends it somewhere.

| Transport         | Description                           |
| ----------------- | ------------------------------------- |
| `Console`         | Logs to `stdout` and `stderr`         |
| `File`            | Writes logs to a file                 |
| `Http`            | Sends logs via HTTP to an endpoint    |
| `Stream`          | Sends logs to any writable stream     |
| `DailyRotateFile` | [External plugin] Rotates files daily |

#### Console

You can specify which levels send to `stderr`

 ```javascript
 new winston.transports.Console({
   level: 'info', // logs this level and above
   format: winston.format.simple(),
   stderrLevels: ['error', 'warn'] // send these to stderr
 })
 ```

### File

```javascript
new winston.transports.File({
  filename: 'combined.log',
  level: 'info'
})
```

```javascript
new winston.transports.File({
  filename: 'errors.log',
  level: 'error'
})
```

### HTTP

Rarely used directly — more common when integrating with logging services.

```javascript
new winston.transports.Http({
  host: 'logserver.mycompany.com',
  port: 9000,
  path: '/logs'
})
```

### Stream

Send logs to any writable Node.js stream

```javascript
const fs = require('fs');
const logStream = fs.createWriteStream('/tmp/custom.log');

new winston.transports.Stream({ stream: logStream });
```

### Community Transports

* `winston-daily-rotate-file`: Rotates log files daily or by size
* `winston-loggly-bulk`: Sends logs to Loggly
* `winston-cloudwatch`: Sends to AWS CloudWatch
* `winston-transport-graylog2`: Graylog integration
* `@sentry/winston`: Sends error logs to Sentry

Example with daily rotating file

```javascript
require('winston-daily-rotate-file');

new winston.transports.DailyRotateFile({
  filename: 'application-%DATE%.log',
  datePattern: 'YYYY-MM-DD',
  dirname: 'logs',
  maxFiles: '7d'
});
```

## Morgan + Winston

* Morgan

  * Middleware for logging **incoming HTTP requests** in Express.
  * Logs things like: method, URL, status code, response time.
  * Designed for web request logs only.

* Winston's `http` leve

  - Just a **custom log level name**, nothing special by itself.

  - Used **by convention** to represent HTTP-related logs.

  - Typically used when **replacing Morgan** or **piping Morgan logs into Winston**.

```javascript
const express = require('express');
const morgan = require('morgan');
const winston = require('winston');

const logger = winston.createLogger({
  level: 'http',
  format: winston.format.json(),
  transports: [
    new winston.transports.Console({ stderrLevels: ['error', 'warn'] })
  ]
});

const app = express();

// Use Morgan, pipe to Winston at `http` level
app.use(morgan('combined', {
  stream: {
    write: message => logger.http(message.trim())
  }
}));

app.get('/', (req, res) => {
  res.send('hello, world!');
});

app.listen(3000, () => logger.info('Server running on port 3000'));
```

