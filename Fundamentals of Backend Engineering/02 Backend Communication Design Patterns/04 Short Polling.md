# Short polling

Request is taking a while, I'll check with you later

* Client send a request
* Server responds immediately with a handle (a unique identifier, for example Job ID)
* Servers continues to process the request
* Client uses that handle to check for status
* Multiple "short" request response as polls

The short pooling is made of many requests-responses.

* The check if the processing is done is fast

## Pros and Cons

* Pros
  * Simple
  * Good for long running requests
  * Client can disconnect
* Cons
  * Too chatty: Imagine many clients, each one making hundreds of polls — a huge number of requests that can easily congest the network. In addition, most of those requests are useless because statistically, it's far more likely that a job isn't done than that it is.
  * wasted backend resources

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

app.get("/checkstatus", (req, res) => {
    console.log(jobs[req.query.jobId]);
    res.end("\n\nJobStatus: " + jobs[req.query.jobId] + "%\n\n");
})

app.listen(8080, () => console.log("listening on 8080"));

function updateJob(jobId, prg) {
    jobs[jobId] = prg
    console.log(`updated ${jobId} to ${prg}`)
    if (prg == 100) return;
    setTimeout(() => updateJob(jobId, prg+10), 3000)
}
```

