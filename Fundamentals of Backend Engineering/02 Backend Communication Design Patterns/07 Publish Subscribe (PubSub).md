# Publish Subscribe

Publish something to the server; The clients can consume it from the server.

* Publish-Subscribe is designed to solve the problem of multiple services trying to communicate with each other, creating a tangled communication mesh. Given the scenario of $n$ services, without Publish-Subscribe, the number of connections $O(n^2)$ because there are $\frac{n(n-1)}{2} = \Theta(n^2)$ possibilities, whereas with this approach, there would be just $n = \Theta(n)$ connections.
* Request-Response is elegant, simple and scalable; however, it handles multiple receivers poorly and both ends have to be running, leading to connection chaining and circuit breaking.


Request-Reponse:
```mermaid
sequenceDiagram
    participant User
    participant UploadService
    participant CompressService
    participant FormatService
    participant NotificationService

    User->>UploadService: Upload File
    UploadService->>CompressService: Process Upload
    CompressService->>FormatService: Compress File
    FormatService->>NotificationService: Format File
    NotificationService-->>FormatService: Notification Sent
    FormatService-->>CompressService: Formatted Data
    CompressService-->>UploadService: Compressed & Formatted Data
    UploadService-->>User: Final Result


```

It is called chaining, and the problem is that each services needs to know the other to participate on the mesh. As it is tightly coupled it is hard to add new services for example:

```mermaid
sequenceDiagram
    participant User
    participant UploadService
    participant CompressService
    participant FormatService
    participant NotificationService
    participant CopyrightService

    User->>UploadService: Upload File
    UploadService->>CompressService: Process Upload
    CompressService->>FormatService: Compress File
    FormatService->>NotificationService: Format File
    NotificationService-->>FormatService: Notification Sent
    FormatService-->>CompressService: Formatted Data

    CompressService->>CopyrightService: Register Copyright
    CopyrightService-->>CompressService: Copyright Registered

    CompressService-->>UploadService: Compressed & Formatted Data
    UploadService-->>User: Final Result
```

You can do it a lot more simpler with a message broker:

```mermaid
sequenceDiagram
    participant User
    participant UploadService
    participant MessageQueue
    participant CompressService
    participant FormatService
    participant NotificationService

    User->>UploadService: Upload File
    UploadService-->>User: Uploaded!

    UploadService->>MessageQueue: Publish to "Raw mp4 videos"

    MessageQueue-->>CompressService: Consume "Raw mp4 videos"
    CompressService->>MessageQueue: Publish to "Compressed video"

    MessageQueue-->>FormatService: Consume "Compressed video"
    FormatService->>MessageQueue: Publish to "480p video"
    FormatService->>MessageQueue: Publish to "1080p video"
    FormatService->>MessageQueue: Publish to "4k video"

    MessageQueue-->>NotificationService: Consume "4k video"

```


## Pros and Cons

* Pros
  * Scales well with multiple receivers
  * Great for micro-services
  * Loose Coupling
  * Works while clients not running
* Cons
  * Message delivery issue: the classic "to generals problem": Ho do I do to know if the consumer actually got the message?
    * Normally the message brokers as Kafka and Rabbit MQ have those warrants.
  *  Complexity
  * Network saturation: mainly because polling to the message broker.

