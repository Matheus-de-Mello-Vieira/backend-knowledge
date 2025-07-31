# Documentation

* Making documentation is boring, but it is necessary
  * Crucial for the API usage
  * Makes it easier to use
  * Attracts developer
  * Improves your image

## OpenAPI

* Standard for API Documentation
* A standard format (usually a YAML or JSON file) for describing REST APIs.
* Many developers say "Swagger" when they mean "OpenAPI," but technically, OpenAPI is the standard, and Swagger is just one implementation/toolset.
  * Swagger is originally the name of the spec and tooling, now refers mostly to tools that support the OpenAPI spec. Examples: Swagger UI, Swagger Editor, Swagger Codegen.

* Describes
  * Endpoints
  * Parameters
  * Authentication
  * Information about the API
* Can be used to
  * Provide documentation and test bed for developers
    * the documentation creates a REST client to test the API
  * Generate client libraries
  * Generate the API (Design-First)
    * You write a API documentation on the OpenAPI platform, and it generates the API for you.
* Can be automatically generated
  * http://inspector.swagger.io/: It is like a postman, but allows you access the history and writes a documentation
* Compatible with many API platforms
* Demo
  * https://petstore.swagger.io/

## Format

The OpenAPI used a `.json` file to specify the documentation, for example https://petstore.swagger.io/v2/swagger.json

```json
{
  "swagger": "2.0",
  "info": {
    "description": "This is a sample server Petstore server.  You can find out more about Swagger at [http://swagger.io](http://swagger.io) or on [irc.freenode.net, #swagger](http://swagger.io/irc/).  For this sample, you can use the api key `special-key` to test the authorization filters.",
    "version": "1.0.7",
    "title": "Swagger Petstore",
    "termsOfService": "http://swagger.io/terms/",
    "contact": {
      "email": "apiteam@swagger.io"
    },
    "license": {
      "name": "Apache 2.0",
      "url": "http://www.apache.org/licenses/LICENSE-2.0.html"
    }
  },
  "host": "petstore.swagger.io",
  "basePath": "/v2"
}
```

```json
{
  "/pet": {
    "post": {
      "tags": [
        "pet"
      ],
      "summary": "Add a new pet to the store",
      "description": "",
      "operationId": "addPet",
      "consumes": [
        "application/json",
        "application/xml"
      ],
      "produces": [
        "application/json",
        "application/xml"
      ],
      "parameters": [
        {
          "in": "body",
          "name": "body",
          "description": "Pet object that needs to be added to the store",
          "required": true,
          "schema": {
            "$ref": "#/definitions/Pet"
          }
        }
      ],
      "responses": {
        "405": {
          "description": "Invalid input"
        }
      },
      "security": [
        {
          "petstore_auth": [
            "write:pets",
            "read:pets"
          ]
        }
      ]
    }
}
}
```

Make tools generate it for you

## Tools

### For Express.JS

There is tools to help you generate the spec, and tools to help render it into html

#### swagger-jsdoc

Generates OpenAPI specs. based on comments

##### How to set it up:

```bash
npm install swagger-jsdoc
```

##### Example

```javascript
jsCopyEditconst express = require('express');
const swaggerJsdoc = require('swagger-jsdoc');

const app = express();

const swaggerOptions = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'My API',
      version: '1.0.0',
      description: 'API documentation for my Express app',
    },
  },
  apis: ['./routes/*.js'], // Path to your API route files
};

const swaggerSpec = swaggerJsdoc(swaggerOptions);
// you can use the swaggerSpec on a UI tool
```

in your route files (like `routes/user.js`), you can add JSDoc comments:

```javascript
 /* @openapi
 * /users:
 *   get:
 *     summary: Get all users
 *     responses:
 *       200:
 *         description: Success
 */
app.get('/users', (req, res) => {
  res.send([...]);
});
```

#### Swagger UI

Generates a classic UI based on OpenAPI specs.

##### How to set it up

```bash
npm install swagger-ui-express
```

##### Example

```javascript
const express = require('express');
const swaggerUi = require('swagger-ui-express');

const app = express();

app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));
```

#### Redoc

Redoc is a beautiful alternative to Swagger UI for rendering OpenAPI specs.

* You can still use swagger-jsdoc to generate the spec and then plug it into Redoc.

##### How to set it up:

```bash
npm install redoc
```

##### Example

```javascript
app.get('/redoc', (req, res) => {
  res.send(`
    <!doctype html>
    <html>
      <head>
        <title>API Docs</title>
        <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
      </head>
      <body>
        <redoc spec-url='/swagger.json'></redoc>
      </body>
    </html>
  `);
});

app.get('/swagger.json', (req, res) => {
  res.json(swaggerSpec);
});
```

### For Nest.JS

####  @nestjs/swagger

* The official OpenAPI module for NestJS, purpose-built to work with Nest’s decorators and architecture.
  * Auto-generates models from DTO
  * Works well with `nest-cli` projects
* Generates the specs ands renders it
  * it uses `swagger-ui-express` internally

##### How to setup

```bash
npm install @nestjs/swagger swagger-ui-express
```

##### Example

* on `main.ts`

  ```javascript
  import { NestFactory } from '@nestjs/core';
  import { AppModule } from './app.module';
  import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
  
  async function bootstrap() {
    const app = await NestFactory.create(AppModule);
  
    const config = new DocumentBuilder()
      .setTitle('My API')
      .setDescription('API documentation')
      .setVersion('1.0')
      .addTag('users')
      .build();
  
    const document = SwaggerModule.createDocument(app, config);
    SwaggerModule.setup('api-docs', app, document); // /api-docs
  
    await app.listen(3000);
  }
  bootstrap();
  ```

* on `create-user.dto.ts`

  ```javascript
  import { ApiProperty } from '@nestjs/swagger';
  
  export class CreateUserDto {
    @ApiProperty()
    name: string;
  
    @ApiProperty()
    age: number;
  }
  ```

* on `users.controller.ts`

  ```javascript
  import { Controller, Get } from '@nestjs/common';
  import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
  
  @ApiTags('users')
  @Controller('users')
  export class UsersController {
    @Get()
    @ApiOperation({ summary: 'Get all users' })
    @ApiResponse({ status: 200, description: 'Success' })
    getAll() {
      return [{ id: 1, name: 'Alice' }];
    }
  }
  
  ```

Doing so, it you server the Swagger UI at `/api-docs`

To use Redoc instead of `swagger-ui-express`, you can create a custom module and server the `document` (on `main.ts` line 15) on `/swagger.json'`.

### Platform-agnostic (transform spec into HTML)

##### Redoc CLI

```javascript
npx @redocly/cli build-docs openapi.json -o docs.html
```

##### ReDoc Standalone HTML

Creates a html with:

```html
<!DOCTYPE html>
<html>
  <head>
    <title>API Docs</title>
    <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
  </head>
  <body>
    <redoc spec-url="openapi.json"></redoc>
  </body>
</html>
```

The `.json` have to be accessible

##### openapi-generator-cli

```bash
npx @openapitools/openapi-generator-cli generate \
  -i openapi.json \
  -g html \
  -o ./html-docs
```