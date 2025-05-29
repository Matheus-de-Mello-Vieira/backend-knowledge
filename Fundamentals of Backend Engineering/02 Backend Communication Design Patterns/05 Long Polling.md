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



The `this.setTimeout(() => resolve(false), 1000)` is needed because if we don't use a the `setTimeout`, the nodeJS main thread will be blocked on the while, 