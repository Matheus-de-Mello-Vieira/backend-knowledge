# Signals in Go

Operating systems use [POSIX signals](../../../Operating%20Systems/05%20Process%20Management.md#POSIX%20Signals) to notify a process about events such as an interactive interrupt or a termination request. The `os/signal` package turns selected incoming signals into ordinary Go control flow, so an application can begin a deliberate shutdown rather than executing cleanup in a low-level signal handler.

On Unix-like systems, `SIGINT` normally comes from `Ctrl-C`, and process managers commonly use `SIGTERM` to request a cooperative shutdown. Go exits by default for both signals. `SIGKILL` and `SIGSTOP` cannot be caught, blocked, or redirected, so they cannot trigger cleanup code.

## Signal-triggered cancellation

`signal.NotifyContext` derives a [context](../01%20Essentials/09%20Concurrency.md#Context) that becomes done when one of the selected signals arrives. It is the usual boundary between a process-level shutdown request and work that already accepts context cancellation.

```go
ctx, stop := signal.NotifyContext(
    context.Background(),
    os.Interrupt,
    syscall.SIGTERM,
)
defer stop()

<-ctx.Done() // a shutdown signal arrived
stop()       // restore the default signal behavior during shutdown
```

The canceled context does not stop goroutines, close listeners, or release resources on its own. The application must use it to stop admitting work, ask in-flight operations to finish or cancel, and apply a bounded shutdown policy. Calling `stop` releases the registration; after a received interrupt, calling it promptly also allows a second `Ctrl-C` to use its normal exit behavior instead of extending graceful shutdown indefinitely.

> [!note] Unix-like signal selection
> `syscall.SIGTERM` is a Unix-like signal. Cross-platform programs should account for their target platform: on Windows, `os.Interrupt` is the signal supported by `os/signal` for `Ctrl-C` and `Ctrl-Break`.

## Receiving the signal value

Use `signal.Notify` when the shutdown policy depends on which signal arrived, such as treating a termination request differently from an application-defined reload request.

```go
signals := make(chan os.Signal, 1)
signal.Notify(signals, os.Interrupt, syscall.SIGTERM)
defer signal.Stop(signals)

sig := <-signals
log.Printf("shutdown requested by %s", sig)
```

`Notify` never blocks while sending to the registered channel. A buffer of one is sufficient when the program needs one notification; it prevents losing that notification merely because the receiver has not started waiting. `signal.Stop` removes all registrations made with that channel and guarantees that it receives no more signal notifications when `Stop` returns.

Register an explicit set of signals rather than subscribing to every signal. Signals are process-control events, not a durable message queue: a program must make its own policy for repeated requests and perform the resulting work through normal Go code.

## Graceful-shutdown lifecycle

Signal handling only initiates the lifecycle. A service then performs its own ordered shutdown:

1. Register for the signals before starting work that needs graceful termination.
2. On notification, stop accepting new work.
3. Propagate cancellation to work that supports it and allow bounded in-flight work to complete.
4. Release resources and exit; if the deadline expires, apply the service's forced-shutdown policy.

An HTTP server, for example, uses this cancellation request to decide when to call [`http.Server.Shutdown`](HTTP%20Server.md#Graceful%20shutdown).
