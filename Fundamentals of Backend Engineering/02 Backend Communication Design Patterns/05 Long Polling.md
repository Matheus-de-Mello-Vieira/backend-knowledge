# Long Polling

Request is taking long, I'll check with you later But talk to me only when it's ready.

It avoid the chattiness of the short polling

## What is it?

* Client send a request
* Server responds immediately with a handle (a unique identifier, for example Job ID)
* Servers continues to process the request
* Client uses that handle to check for status

These steps are not strictly needed for a process to be considered long polling. For example, Kafka is polled by the client for messages with a maximum wait time, so the broker will hold the connection open until either a new message shows up or time is up. Notice that even though Kafka uses long polling, it skips straight to the status checking step, as the client already knows which topic it needs to consume from.

## Pos and Cons

* Pros
  * Less chatty and backend friendly
  * Client can still disconnect
* Cons
  * Not real time: it is real time if and only if there is an ongoing long-polling request when the message arrives at the broker.

## Demo

```javascript
const app = require("express")();
const jobs = {};

app.post("/submit", (req, res) => {
    const jobId = `job:${Date.now()}`;
    jobs[jobId] = 0;
    updateJob(jobId, 0);
    res.end("\n\n" + jobId + "\n\n");
})

app.get("/checkstatus", async (req, res) => {
    console.log(jobs[req.query.jobId]);
    while(await checkJobComplete(req.query.jobId) == false);
    res.end("\n\nJobStatus: " + jobs[req.query.jobId] + "%\n\n");
})

app.listen(8080, () => console.log("listening on 8080"));

function checkJobComplete(jobId) {
    return new Promise((resolve, reject) => {
        if (jobs[jobId] < 100)
            setTimeout(() => resolve(false), 1000)
        else
            resolve(true)
    })
}

function updateJob(jobId, prg) {
    jobs[jobId] = prg
    console.log(`updated ${jobId} to ${prg}`)
    if (prg == 100) return;
    setTimeout(() => updateJob(jobId, prg+10), 3000)
}
```



## Note

In JavaScript, particularly in Node.js, it's important to understand how the **event loop** works to avoid writing code that blocks the system. The event loop is a mechanism that allows Node.js to handle many operations asynchronously, such as timers, file reads, and HTTP requests, all on a single thread. This means that while one operation is waiting (like a timer or I/O), other code can continue running — but only if the event loop remains unblocked.

Consider this code:

```js
while (jobs[jobId] < 100);
```

At first glance, it looks like a simple way to wait until a job reaches 100% completion. However, this line is a **tight, synchronous loop** that runs continuously without yielding control back to the event loop. Because of this, **no other asynchronous operations — including the `setTimeout` calls that are meant to update the job progress — can run.** The loop effectively freezes the entire program in a busy wait. As a result, the job will never finish, and the loop will never exit.

To fix this, we use an asynchronous function like `checkJobComplete`, which internally uses `setTimeout` to pause before checking the job status again:

```js
function checkJobComplete(jobId) {
    return new Promise((resolve) => {
        if (jobs[jobId] < 100)
            setTimeout(() => resolve(false), 1000);
        else
            resolve(true);
    });
}
```

When we use this in an `async` loop with `await`, the loop pauses without blocking the event loop:

```js
while (!(await checkJobComplete(jobId)));
```

Now, the event loop remains free to handle other tasks — such as timers that update job progress — and the system continues to function as expected. This approach ensures smooth operation without freezing the application, which is a core principle in writing non-blocking, asynchronous code in JavaScript.