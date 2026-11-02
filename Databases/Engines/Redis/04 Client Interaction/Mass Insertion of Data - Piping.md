# Mass Insertion of Data into Redis

## Interactive insertion and its limits

Inserting a large dataset one command at a time through `redis-cli` requires an interactive operation for every row. For example, a CSV file might contain:

```csv
LB,Lebanon
FR,France
DE,Germany
... (hundreds or thousands of rows)
```

Inserting the first row manually requires a command such as:

```sh
SET country:LB Lebanon
```

This approach has several limitations:

- Each separately sent command incurs a network round trip and parsing overhead.
- Interactive insertion becomes impractical as the dataset grows.
- Repetitive commands are easy to mistype and difficult to reproduce.
- Manual interaction does not fit scripts or deployment pipelines.

## Pipelining generated commands

Instead of issuing commands interactively, generate one `SET` command per CSV row and send the stream to `redis-cli --pipe`. Given `countries.csv` containing:

```csv
LB,Lebanon
FR,France
DE,Germany
```

`awk` transforms each row into a command:

```bash
awk -F',' '
{
  print "SET country:" $1 " " $2
}
' countries.csv | redis-cli --pipe
```

The generated commands reach `redis-cli` through standard input. The CLI parses them into [RESP](Redis%20Serialization%20Protocol.md) and sends them to Redis in a continuous pipeline rather than waiting for each command's round trip before sending the next. This removes interactive work and reduces network round trips while keeping the import readable, reproducible, and easy to automate. For most bulk imports, it provides high throughput without the complexity of constructing protocol frames directly.

## Generating RESP directly

`redis-cli --pipe` also accepts raw RESP. When the input is already encoded, the CLI forwards it without parsing plain commands. For the same CSV input, `awk` can emit an array frame for each `SET` command:

```bash
awk -F',' '
{
  key = "country:" $1
  value = $2

  printf "*3\r\n$3\r\nSET\r\n$%d\r\n%s\r\n$%d\r\n%s\r\n", \
    length(key), key, length(value), value
}
' countries.csv | redis-cli --pipe
```

Direct RESP generation has distinct advantages when importing millions of keys or building high-performance ingestion pipelines:

- It avoids client-side parsing of plain commands and can increase throughput.
- Explicit lengths support binary-safe values without command quoting or escaping.

Constructing the frames adds complexity, so the plain-command pipeline remains the simpler default when its performance is sufficient.
