# Developing GraphQL Client

You can use plain Javascript for that

*   No special libraries required
*   There are some clients that can be used, mainly for advanced capabilities, but in most cases - there's no need for them.

## Simple example

```js
// Usage:
//   node run-query-cli.js http://localhost:4000/graphql
// or set env GRAPHQL_ENDPOINT (arg takes precedence)

const endpoint =
  process.argv[2] ||
  process.env.GRAPHQL_ENDPOINT ||
  'http://localhost:4000/graphql';

const query = `
  query GetBooks {
    books {
      name
      pages
    }
  }
`;

async function main() {
  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({ query })
    });

    const data = await res.json();
    console.log(JSON.stringify(data, null, 2));
  } catch (err) {
    console.error('Error:', err?.message || err);
    process.exit(1);
  }
}

main();
```



## Not-so-simple example

*   `script.js`

    ```js
    async function runQueryFromHtml() {
      const btn = document.querySelector('input[type="button"]');
      const queryEl = document.getElementById('query');
      const resultsEl = document.getElementById('results');
    
      const query = queryEl?.value?.trim();
      if (!query) {
        resultsEl.value = 'Please enter a GraphQL query.';
        return;
      }
    
      try {
        btn && (btn.disabled = true);
        resultsEl.value = 'Running...';
    
        const res = await fetch('/graphql', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
          body: JSON.stringify({ query })
        });
    
        const data = await res.json();
        resultsEl.value = JSON.stringify(data, null, 4);
      } catch (err) {
        resultsEl.value = 'Error: ' + (err?.message || err);
      } finally {
        btn && (btn.disabled = false);
      }
    }
    ```

*   `style.css`

    ```css
    textarea {
      width: 100%;
      min-height: 30rem;
      font-family: "Lucida Console", Monaco, monospace;
      font-size: 0.8rem;
      line-height: 1.2;
    }
    ```

*   `index.html`

    ```html
    <!-- index.html -->
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8" />
      <title>GraphQL Client</title>
      <link rel="stylesheet" href="style.css" />
      <script src="script.js" defer></script>
    </head>
    <body>
      <input type="button" value="Run GraphQL Query" onclick="runQueryFromHtml()" />
      <br /><br />
    
      <!-- NEW: user-editable GraphQL query -->
      <textarea id="query" cols="30" rows="10">
    query GetBooks {
      books {
        name
        pages
      }
    }
      </textarea>
    
      <br /><br />
      <textarea id="results" cols="30" rows="10" readonly></textarea>
    </body>
    </html>
    ```