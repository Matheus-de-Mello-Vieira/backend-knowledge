# CLI tool

Create a CLI is like creating a node package with few extra steps

* add `!/usr/bin/env node` on the beggining of entrypoint (eg. `index.js`)

* add `bin` attribute on `package.json`, with the command name and the entrypoint

  ```json
  {
      ...
      "bin": {
          "your-command": "index.js"
      }
      ...
  }
  ```

* now you can install your command with `npm install -g` (don't need specify the package name)

## CLI Options

You can accept options with `process.argv`, that is:

* `process.argv[0]` The path to the Node.js executable
* `process.argv[1]` The path to the JavaScript file being executed
* `process.argv[2..]` The remaining command-line arguments

You can use the package `yargs` to help you out:

```java
const yargs = require("yargs")
const { argv } = yargs(process.argv)

// To pass the parameter from the command line, run:
//    node yourcommand.js --PARAMETER=VALUE
// Example:
//    node yourcommand.js --PARAMETER=Hello
// This will print:
//    Hello
console.log(argv.PARAMETER)
```

more advanced example:

```javascript
yargs
  .command(
    'add [num1] [num2]',
    'Add two numbers',
    (yargs) => {
      yargs
        .positional('num1', {
          describe: 'First number',
          type: 'number'
        })
        .positional('num2', {
          describe: 'Second number',
          type: 'number'
        });
    },
    (argv) => {
      console.log(`Result: ${argv.num1 + argv.num2}`);
    }
  )
  .command(
    'version',
    'Show app version',
    () => {},
    () => {
      console.log('App version: 1.0.0');
    }
  )
  .demandCommand(1, 'You need to specify at least one command')
  .help()
  .argv;
```



## Interactive CLI Tools

 `inquirer` is a library for creating interactive command-line prompts in Node.js. It’s often used to get user input in CLI applications.

### Install

```bash
npm install inquirer
```

------

### Basic usage

Here’s the simplest example:

```js
import inquirer from 'inquirer';

inquirer
  .prompt([
    {
      type: 'input',
      name: 'username',
      message: 'What is your name?',
    },
  ])
  .then((answers) => {
    console.log(`Hello, ${answers.username}!`);
  });
```

```
? What is your name? 
```

and then prints the result.

### Common question types

You can specify different `type`s:

| Type       | Example use                    |
| ---------- | ------------------------------ |
| `input`    | Free-text input                |
| `confirm`  | Yes/No (boolean)               |
| `list`     | Single choice from a list      |
| `checkbox` | Multiple choices               |
| `password` | Hidden input (e.g., passwords) |

#### Example with multiple types

```js
import inquirer from 'inquirer';

const questions = [
  {
    type: 'input',
    name: 'projectName',
    message: 'Project name:',
  },
  {
    type: 'list',
    name: 'language',
    message: 'Choose your language:',
    choices: ['JavaScript', 'TypeScript'],
  },
  {
    type: 'confirm',
    name: 'useGit',
    message: 'Initialize a git repo?',
    default: true,
  },
];

inquirer.prompt(questions).then((answers) => {
  console.log('Your answers:', answers);
});
```

Output:

```
? Project name: my-app
? Choose your language: JavaScript
? Initialize a git repo? Yes

Your answers: { projectName: 'my-app', language: 'JavaScript', useGit: true }
```

### Using async/await

Since `inquirer.prompt()` returns a promise, you can use it with `async`/`await`:

```js
import inquirer from 'inquirer';

async function main() {
  const answers = await inquirer.prompt([
    { type: 'input', name: 'email', message: 'Your email:' },
    { type: 'password', name: 'password', message: 'Your password:' },
  ]);
  console.log(answers);
}

main();
```

### Advanced: validate, filter, default

- **validate**: ensure input meets requirements
- **filter**: transform input
- **default**: default value

Example:

```js
const questions = [
  {
    type: 'input',
    name: 'age',
    message: 'Your age:',
    validate: (input) => {
      if (isNaN(input) || input < 0) {
        return 'Please enter a valid age';
      }
      return true;
    },
    filter: (input) => Number(input),
    default: 18,
  },
];

inquirer.prompt(questions).then(console.log);
```

### Choices can be objects

For `list` or `checkbox`, choices can be:

```js
[
  { name: 'Apple', value: '🍎' },
  { name: 'Banana', value: '🍌' },
  { name: 'Cherry', value: '🍒' }
]
```

Example:

```js
{
  type: 'list',
  name: 'fruit',
  message: 'Pick a fruit:',
  choices: [
    { name: 'Apple', value: '🍎' },
    { name: 'Banana', value: '🍌' },
    { name: 'Cherry', value: '🍒' }
  ],
}
```

### Running your script

Just do:

```bash
node myscript.js
```

If you use ES modules, ensure `"type": "module"` is in your `package.json`, or use `import()` dynamically.

### Common gotchas

If using `require` instead of `import`:

```js
const inquirer = require('inquirer');
```

For older Node versions without ES modules:

```js
const inquirer = require('inquirer');
```

###  Docs

- [Inquirer on npm](https://www.npmjs.com/package/inquirer)
- [GitHub repo](https://github.com/SBoudrias/Inquirer.js/)
