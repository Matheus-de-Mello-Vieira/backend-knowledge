# NPM

* NPM is the world's largest software library (registry)
* NPM is a software package manager
  * contains code packages written by various developers.

## Package.json

`package.json` is npm's configuration file

* It is a json file that typically lives in the root directory of your package and holds various meta-data relevant to the package.

* it is the central place to configure and describe how to interact with and run your package

* it is primarily used by the npm CLI

* To create a `package.json`, run `npm init` and follow the iterative console

  * you can use `npm init --yes` to create without iterative console, with default values:

    ```json
    {
      "name": "yourFolderName",
      "version": "1.0.0",
      "main": "index.js",
      "scripts": {
        "test": "echo \"Error: no test specified\" && exit 1"
      },
      "keywords": [],
      "author": "",
      "license": "ISC",
      "description": ""
    }
    ```

    

## Installing Packages

* You can search for packages in [npmjs.com](npmjs.com).
  * see:
    * the date of last publishment
    * the weekly downloads
    * unpacked size
    * number of issues
    * documentation
* to install a package, `npm install name-of-package --save
  * it will update the `package.json` and `package-lock.json` (which will be created if it doesn't exist)
  * now you can use `require(...)` to use the package on your code
  * it will add the package into your dependencies.
    * to install all the dependencies in `package.json`, run `npm install`
  * you can specify a version with `npm install name-of-package@1.2.0`
    * `^2.3.4` means `>=2.3.4 <3.0.0`
    * `~2.3.4` means `>=2.3.4 <2.4.0`
    * `*` will allow any available version
    * `>=2.3.4` means `2.3.4` or newer
    * `2.3.4` installs exactly `2.3.4`

## Global packages

packages intend to run on terminal, as a standalone CLI command

* install with `npm install -g package-name`
* they isn't marked as dependency in `package.json`
* one example is `nodemon`

  > nodemon is a tool that helps develop Node.js based applications by automatically restarting the node application when file changes in the directory are detected.
  >
  > nodemon does **not** require *any* additional changes to your code or method of development. nodemon is a replacement wrapper for `node`. To use `nodemon`, replace the word `node` on the command line when executing your script.
  >
  > https://www.npmjs.com/package/nodemon

## Scripts

An npm script is a convenient way to bundle common commands for use in a project
* They are typically entered in the command line in order to do something with the application
* npm scripts are stored in a project's package.json file, giving access to everyone who has access to the codebase
  * They also ensure that everyone is using the same command with the same options
  * Common use cases for npm scripts include building your project, starting a development server, compiling CSS, linting, minifying etc

* npm scripts are executed using the command `npm run SCRIPT_NAME`


To create one script, on `package.json`:

```js
{
	...
	"scripts": {
		"start": "node index.js"
	},
	...
}
```

* The script `start` specifically can also be run by `npm start`



## Publishing an npm Package

* `npm adduser USERNAME`
  * complete the iterative console
* `npm publish`