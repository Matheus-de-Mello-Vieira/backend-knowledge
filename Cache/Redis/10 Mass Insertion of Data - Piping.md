# Mass Insertion of Data into Redis

## The problem

When working with large datasets—such as thousands of rows from a CSV file—manually inserting data into Redis using `redis-cli` does not scale.

Example CSV input:

```
LB,Lebanon
FR,France
DE,Germany
... (hundreds or thousands of rows)
```

Inserting entries one at a time:

```
SET country:LB Lebanon
```

has several drawbacks:

- **High latency**
  Each command is sent individually, incurring network round trips and parsing overhead.
- **Poor scalability**
  Interactive insertion becomes impractical as data volume grows.
- **Manual and error-prone**
  Repetitive commands are easy to mistype and hard to reproduce.
- **Not automation-friendly**
  This approach does not fit well into scripts or deployment pipelines.

## Solution: Pipelining plain commands with `redis-cli --pipe`

The simplest and most maintainable solution is to generate standard Redis commands and pipe them into `redis-cli --pipe`.

Given a CSV file:

```
LB,Lebanon
FR,France
DE,Germany
```

You can transform each row into a Redis command using `awk`:

```bash
awk -F',' '
{
  print "SET country:" $1 " " $2
}
' countries.csv | redis-cli --pipe
```

### How this works

- `awk` converts each CSV row into a valid Redis `SET` command.
- `redis-cli --pipe` reads commands from standard input.
- Commands are sent to Redis in a continuous stream using pipelining.
- `redis-cli` parses each command and converts it to RESP internally.

### Why this is usually enough

This approach:

- Eliminates interactive usage
- Dramatically reduces network round trips
- Scales well for large datasets
- Is easy to read, debug, and automate

For most bulk imports, this method provides excellent performance with minimal complexity.

## Solution: Generating RESP directly for maximum performance

Although `redis-cli --pipe` accepts plain commands, it can also accept [raw RESP](./12 Redis Protocol.md). In this case, `redis-cli` forwards the data directly to Redis without parsing.

Example using `awk`:

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

### Why generating RESP can be faster

- No client-side command parsing
- Higher throughput for very large imports
- Binary-safe values
- Explicit lengths eliminate quoting and escaping issues

This approach is especially useful when importing millions of keys or building high-performance ingestion pipelines.