# TypeScript compiler

## Project setup

Run

```bash
tsc --init
```

it will create the `tsconfig.json` file

## tsconfig.json

Over all those years, dozens of options and settings have been added - and trying to make sense of them all is almost impossible.

* Very often, you'll be working in a project created with build tools like [Vite](https://vite.dev/) which create a fitting `tsconfig.json` file for you.
* If you DO want to understand some of the settings you see in those generated `tsconfig.json` files, the [official reference](https://www.typescriptlang.org/tsconfig) can be helpful.

Basic `tsconfig.json`

```json
{
  "target": "ES2022", // Good for modern browsers or Node.js
  "compilerOptions": {
    "esModuleInterop": true, // Ensures ESM and CJS imports work together well
    "skipLibCheck": true, // Ensures .d.ts files from 3rd libraries are not type-checked
    "target": "es2022", // Sets a relatively modern ECMAScript version as compilation target
    "allowJs": true, // Allows importing .js files into .ts (helpful when migrating projects)
    "strict": true, // Ensures strict type checking (i.e., noImplicitAny etc)
    "noUncheckedIndexedAccess": true, // Adds undefined as a value when accessing by index
    // "noImplicitOverride": true, // Enable this when working with classes & inheritance
    "noUnusedLocals": true, // to avoid unused variables
    "module": "NodeNext", // Supports both ESM & CJS modules / imports
    "outDir": "dist", // Store compiled files in "dist" folder
    "sourceMap": true, // Enables source maps for easier debugging
    "lib": ["es2022", "dom", "dom.iterable"] // Or without "dom" libs when building for Node
  }
}
```

### General

* `target`control which version of JavaScript the TypeScript will produce.

    * |Node.js version|Recommended `target`|
        |---------------|------------------------------------------------|
        |Node 10|`es2018`|
        |Node 12|`es2019`|
        |Node 14|`es2020`|
        |Node 16|`es2021`|
        |Node 18 / 20|`es2022`|
        |Node 22+|`es2023` (or `esnext` if you want bleeding edge)|

* `lib` controls which built-in type declaration libraries (.d.ts files) are included in the compilation.

    * by default, it will set default set of libraries depending on the target you
        * If `"target"` is `"es5"`, the default libraries are `["DOM", "ES5", "ScriptHost"]`.
        * If `"target"` is `"es2015"`, the default libraries are `["DOM", "ES2015", "DOM.Iterable", "ScriptHost"]`.

* `module` controls what JavaScript module system TypeScript emits in the compiled output.

    * `none`: no module system, everything is global (rarely used).
    * `commonjs`: → Node.js’s older module system using `require()` and `module.exports`.
    * `amd`: Asynchronous Module Definition, used in older browsers and RequireJS.
    * `umd`: Universal Module Definition, works in both Node.js and browsers.
    * `system`: Uses SystemJS, a dynamic module loader.
    * `es6` / `es2015` / `esnext`: Emits standard ES module syntax (import/export). Best for modern projects.
    * `node16` / `nodenext`: Special modes that align with Node.js’s dual ESM/CommonJS resolution rules (important if you’re using `"type": "module"` in `package.json`).

* `rootDir` controls where the TypeScript code is.
* `outDir` controls where the TypeScript will produce the Javascript code.
    * alternatively, you can use `outFile` to bundle the whole project into one file, but normally third-parties bundlers are better.
* `sourceMap` is interesting for debugging.
* `noEmit` if true the TypeScript won't produce any JavaScript code, good when you need to check your code but don't need compile it.
* `noEmitOnError` If true, the TypeScript refrains from emitting any JavaScript if there is a error during compilation.
* The `types` option in TypeScript (`tsconfig.json`) controls which ambient type declaration packages (`@types/\*`) are included in your project.
    * **Default behavior:** If you omit `types`, TypeScript automatically includes all type packages found in `node_modules/@types` (e.g. `@types/node`, `@types/jest`, etc.).
    * **Explicit list (`"types": ["node"]`):** Only the specified packages are included, so you can whitelist exactly what you want.
    * **Empty list (`"types": []`):** Nothing is included; even if `@types/node` is installed, TypeScript won’t load it. This causes errors when using built-in Node globals (`process`, `Buffer`) or imports (`import * as fs from "node:fs"`).
    * **Typical usage:**
        * Leave `types` unset: easy, everything in `@types/*` is available.
        * Set `types` selectively: useful when you want to avoid “type pollution” from testing libraries or multiple global type sets.
        * Avoid setting it to `[]` unless you really want a “no globals at all” setup.

### Configuring Type Checking

* `strict` enables TypeScript's strict type-checking family of options. It does not convert every warning or diagnostic into an error.

There are many options like:`noImplicitAny`, `strictNullChecks`, `strictFunctionTypes`, go on and go forth. See the official documentation for a complete list.

### Code Quality Checks

Besides configuring compilation & type checking, you can also use the tsconfig.json file to enable some "quality of life" checks - checks that are not directly related to types but that can help you improve your code quality.

```json
{
  "noUnusedLocals": true, // helps you detect unused variable
  "noUnusedParameters": true, // helps you detect unused function parameters
  "noFallthroughCasesInSwitch": true // helps you detect switch cases without break or return
}
```

## Compile with tsconfig

Simply run `tsc`

## Watch Mode

`tsc --watch` will monitor any changes any regenerate the JavaScript code accordingly.

## Installing Type Packages

By default, TypeScript doesn't recognize types from third parties libraries as NodeJS. In order to use NodeJS' libraries as `node:fs`, you need to install it into TypeScript:

```bash
npm install @types/node --save-dev
```

* Notice that you need only need dev dependencies, because it won't be used after the compilation

You can use `ts-node` to compile + execute immediately.

```bash
npm install ts-node --save-dev
```

Now you need to run:

```bash
npx ts-node src/index.ts
```

Or configure the script on `package.json`:

```javascript
{
  "scripts": {
    "dev": "ts-node src/index.ts"
  }
}
```
