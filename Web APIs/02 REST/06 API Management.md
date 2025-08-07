# API Management

API Management is the process of publishing, document and overseeing API in a secure, scalable environment.

There are two modes of API management:

* Agent based: Each machine that runs the API have a agent
* Proxy based: The management is made on a reverse proxy
  * Tools like Apigee, AWS API gateway

Another aspect is the developer portal, to consumers could get information about API:

* API documentation
* Access Request
  * Manual Provisioning: app developer contacts the API owner, that generates manually key and secret
  * Self Provisioning; the key and secrets are created automatically when App developer request
    * but you can keep the manual provisioning when something with self provisioning goes wrong.
* Support
  * FAQ
  * Provide best practices
  * Contact forms
  * Bugs reporting

* Build a developer community
  * Social media

* There are out-of-the-box tools for developer portals, such as Apigee.

## Life-cycle

1) Build: a version is created
2) Publish: a version is published
3) Deprecated: a version is deprecated, replaced by a new version
4) Retired: the API stops serving that version, even removing its code from the infrastructure.

So you should:

* Establish processes, practices and roles
* Public roadmap in advance
* Setup App developer communication

## Security

* All API must require a minimal security of API Key
  * even the public APIs
  * So you can invalidate the key for misbehaving client.
  * Generate analytics with key as the identify
  * Usage metrics
* Engage third party for vulnerability assessments
* Continuous monitoring to detect attacks/threats
* Pro-active in protecting API from new attack types
* Implement threat protection in the proxy