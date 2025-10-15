# Documentation

* Making documentation is boring, but it is necessary
  * Crucial for the API usage
  * Makes it easier to use
  * Attracts developer
  * Improves your image
* It servers as a well defined contract between API provider and consumer

## Design first

* There are two approach: Design First (first write the documentation, then the code), and Design Last
  * The problem of Design last is tough keep the documentation updated, because it isn't important on the creation of the API.
* The design first depends on the collaboration between the API consumer and the API developer, they discuss the requirements, talk about specifications, and create mocks to the data.
  * if that mock satifies the needs of API consumer, the specification is used to create the API. Otherwise a new specification is made (repeat the process).

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
    * Client code generation
  * Generate client libraries
  * Generate the API (Design-First)
    * You write a API documentation on the OpenAPI platform, and it generates the API for you.
  * Service visualization (Mocking)
* Can be automatically generated
  * http://inspector.swagger.io/: It is like a postman, but allows you access the history and writes a documentation
* Compatible with many API platforms
* Demo
  * https://petstore.swagger.io/4

## Reusable Documentation Templates

### Basic CRUD

| Method     | Route                                           | `summary`                       | `description`                                                | `operationId`         | `OK Response` description |
| ----------- | ----------------------------------------------- | ------------------------------- | ------------------------------------------------------------ | --------------------- | -------------------------- |
| **GET** | `/api/{entityPlural}` | List {EntityPlural} | Returns a subset of all {EntityPlural} available in the system, according to query parameters. | list{EntityPlural} | Returns a list of {EntityPlural} matching the query parameters. |
| **GET**    | `/api/{entityPlural}/{id}`                      | Get a {Entity} by ID            | Retrieves the full details of a specific {Entity} identified by its unique ID. | get{Entity}ById       | Returns the requested {Entity} details. |
| **POST**   | `/api/{entityPlural}`                           | Create a new {Entity}           | Creates a new {Entity} using the data provided in the request body. | create{Entity}        | Returns the newly created {Entity}. |
| **PUT**    | `/api/{entityPlural}/{id}`                      | Update a {Entity} by ID         | Updates an existing {Entity} identified by its unique ID with the provided data. | update{Entity}ById    | Returns the updated {Entity}. |
| **DELETE** | `/api/{entityPlural}/{id}`                      | Delete a {Entity} by ID         | Removes the specified {Entity} from the system by its unique ID. | delete{Entity}ById    | Indicates that the {Entity} was successfully deleted. |

### Common Routes

#### Authentication

| Method     | Route              | `summary`                     | `description`                                                                 | `operationId`          | `OK Response` description |
| ----------- | ----------------- | ----------------------------- | ----------------------------------------------------------------------------- | ---------------------- | -------------------------- |
| **POST**    | `/auth/basic`     | Basic Authentication Login     | Authenticates a user using basic credentials (e.g., username and password) and returns an access token upon success. | basicAuthLogin         | Returns an access token and user information upon successful authentication. |
| **GET**     | `/auth/saml`      | SAML Login Initiation          | Initiates the SAML single sign-on (SSO) flow by redirecting the user to the identity provider (IdP) for authentication. | samlLogin              | Redirects the user to the SAML identity provider for authentication. |
| **POST**    | `/auth/callback`  | SAML Login Callback            | Handles the callback from the SAML identity provider, validating the response and establishing a session or returning an access token. | samlLoginCallback      | Returns an access token or establishes a session after successful SAML authentication. |
| **POST**    | `/auth/logout`    | User Logout                    | Logs out the authenticated user by invalidating their session or token. | logoutUser             | Confirms that the user has been successfully logged out. |
| **POST**    | `/auth/refresh`   | Refresh Access Token           | Issues a new access token using a valid refresh token, extending user session validity. | refreshAccessToken     | Returns a new access token and refresh token pair. |
| **GET**     | `/auth/me`        | Get Current User Info          | Retrieves information about the currently authenticated user. | getCurrentUser         | Returns details of the currently authenticated user. |

---

#### System & Monitoring

| Method     | Route         | `summary`            | `description`                                                         | `operationId`       | `OK Response` description |
| ----------- | ------------- | -------------------- | --------------------------------------------------------------------- | ------------------- | -------------------------- |
| **GET**     | `/health`     | Health Check         | Returns a simple status message indicating that the API is operational. | getHealthStatus     | Returns a message confirming that the API is operational. |
| **GET**     | `/status`     | System Status        | Provides detailed system or service status, often used for monitoring or readiness probes. | getSystemStatus     | Returns detailed information about the system or service status. |
| **GET**     | `/metrics`    | Metrics Endpoint     | Exposes application performance metrics, typically in Prometheus format. | getMetrics          | Returns application performance metrics data. |
| **GET**     | `/version`    | API Version Info     | Returns metadata about the current API version and build details. | getApiVersion       | Returns API version and build metadata information. |

---

#### Configuration & Documentation

| Method     | Route       | `summary`                | `description`                                                            | `operationId`     | `OK Response` description |
| ----------- | ------------ | ------------------------ | ------------------------------------------------------------------------ | ----------------- | -------------------------- |
| **GET**     | `/config`    | Public Configuration     | Returns configuration or environment details needed by the frontend (e.g., feature flags, endpoints). | getPublicConfig   | Returns public configuration details required by the frontend. |
| **GET**     | `/docs`      | API Documentation        | Returns or redirects to the interactive API documentation (e.g., Swagger or Redoc UI). | getApiDocs        | Returns or redirects to the interactive API documentation interface. |

---

#### File Management

| Method     | Route                     | `summary`        | `description`                                                             | `operationId`      | `OK Response` description |
| ----------- | ------------------------- | ---------------- | ------------------------------------------------------------------------- | ------------------ | -------------------------- |
| **POST**    | `/upload`                 | File Upload      | Uploads a file or binary data to the system, returning metadata or an access URL. | uploadFile         | Returns metadata and access information for the uploaded file. |
| **GET**     | `/download/{fileId}`      | File Download    | Downloads a file previously uploaded, identified by its unique file ID. | downloadFile       | Returns the requested file content as a downloadable resource. |

## Format

The documentation can be written in yaml or json

The structure have three parts:

* global information:
  * Metadata
  * Root Document
  * External Documentation
  * Tags (for search)
* Components
  * schemas
  * parameters
  * securitySchemes
* Paths
  * makes references to the first two parts

Every documentation should start with `swagger: 2.0` or `openapi: 3.0.4`, depending on the version.

### Global information

* `info`
  * `version`
  * `title`
  * `description`
  * `contact` (optional)
    * `name`
    * `url`
    * `email`
  * `license`  (optional)
    * `name`
    * `url`
  ```yaml
  info:
    title: Swagger Petstore - OpenAPI 3.0
    description: |-
  	This is a sample Pet Store Server based on the OpenAPI 3.0 specification...
      Some useful links:
      - [The Pet Store repository](https://github.com/swagger-api/swagger-petstore)
      - [The source API definition for the Pet Store](https://github.com/swagger-api/swagger-petstore/blob/master/src/main/resources/openapi.yaml)
    termsOfService: https://swagger.io/terms/
    contact:
      email: apiteam@swagger.io
    license:
      name: Apache 2.0
      url: https://www.apache.org/licenses/LICENSE-2.0.html
    version: 1.0.12
  ```
  
* `servers` (list)

  * `url`: The base URL of your API, you have to include the schema prefix (eg.: `https://`).

* `tags`

  * serves to:

    * Metadata - used by the developer portal tools

    * Refereed in Paths or Operations

    * Always use tags, because it makes your API searchable and filterable

  * each tag have `name` and `description`

  ```yaml
  tags:
    - name: pets
      description: Everything about your Pets
    - name: store
      description: Store operations
  ```

* `externalDocs`: Often the specification document can't hold al information needed to consume the API, so you can link external documentation here.

  ```yaml
  externalDocs:
    description: Find out more about Swagger
    url: https://swagger.io
  ```

### Components

the `components` attribute is a top-level object that holds reusable parts for your API definition. It helps avoid repetition and makes your API spec cleaner and more maintainable.

You can reuse them by `$ref: '#/components/<section>/<name>'`

* `schemas` Reusable data models

  ```yaml
  User:
    type: object
    properties:
      id:
        type: integer
      username:
        type: string
  ```

* `responses` Reusable response objects

  ```yaml
  NotFound:
    description: Resource not found
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Error'
  ```

* `parameters` Reusable parameter definitions

  ```yaml
  userIdParam:
    name: userId
    in: path
    required: true
    schema:
      type: integer
  ```

* `examples` Reusable example objects

  ```yaml
  userExample:
    summary: Sample user
    value:
      id: 1
      username: johndoe
  ```

* `requestBodies` Reusable request body definitions

  ```yaml
  UserInput:
    description: User data to add
    required: true
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/User'
  ```

* `headers` Reusable header definitions

  ```yaml
  RateLimit-Limit:
    description: The maximum number of requests allowed in a time period
    schema:
      type: integer
  ```

* `securitySchemes`: Security definitions (e.g., OAuth2, API keys)

  ```yaml
  ApiKeyAuth:
    type: apiKey
    in: header
    name: X-API-Key
  ```


* `links` Reusable link definitions

  ```yaml
  GetUserById:
    operationId: getUser
    parameters:
      userId: '$response.body#/id'
  ```


* `callbacks` Reusable callback objects (for async APIs)

  ```yaml
  onData:
    '{$request.body#/callbackUrl}':
      post:
        requestBody:
          description: New data payload
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Data'
        responses:
          '200':
            description: callback received
  ```

```yaml
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
  responses:
    NotFound:
      description: Resource not found
  parameters:
    userId:
      name: userId
      in: path
      required: true
      schema:
        type: integer
```



### Paths

A path is describe with a string, as `/pets` or `/users/{userId}`. One path can have multiple verbs (`get`, `put`, `post`, etc), that can have:

* `summary` short description
* `description` long description
* `operationId` a unique identifier used to refer to a specific API operation (e.g.: `updatePet`)
* `tags` (list)
  * you can create new tags here, but it is recommended always predefine the tags
* `requestBody`
* `responses`
* `externalDocs`: same ideia of the `externalDocs` root
* **deprecated** (boolean)

media types are specified directly in each operation under `requestBody.content` (for input) and each `response` under `content` (for output).

```yaml
paths:
  /pets:
    post:
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Pet'
      responses:
        '201':
          description: Created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Pet'
```

````yaml
/pet:
  put:
    tags:
      - pet
    summary: Update an existing pet.
    description: Update an existing pet by Id.
    operationId: updatePet
    requestBody:
      description: Update an existent pet in the store
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Pet'
        application/xml:
          schema:
            $ref: '#/components/schemas/Pet'
        application/x-www-form-urlencoded:
          schema:
            $ref: '#/components/schemas/Pet'
      required: true
    responses:
      '200':
        description: Successful operation
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Pet'
          application/xml:
            schema:
              $ref: '#/components/schemas/Pet'
      '400':
        description: Invalid ID supplied
      '404':
        description: Pet not found
      '422':
        description: Validation exception
      default:
        description: Unexpected error
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Error'
    security:
      - petstore_auth:
          - 'write:pets'
          - 'read:pets'
````

## Specification file 

### YAML

You can write a yaml that creates a swagger, there is many tools, as

* https://editor.swagger.io/
* node tools:
  * `swagger-editor`
  * `swagger` (includes swagger-editor)

### JSON

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