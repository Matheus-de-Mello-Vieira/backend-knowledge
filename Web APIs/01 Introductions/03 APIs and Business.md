# Business

* **Provider**: the entities that exposes the API
* **Consumers**: the entities that consume the APIS
  * There are three types of consumers
    * **private or internal**: the consumer and the provider belongs to the same organization
    * **public or external**: the consumer are outside the provider's organization
    * **partner**:  the consumer is trusted by the provider.
  * The type of API consumer don't influence it's implementation, only it's management.
    * influences the network settings
      * private apis could be placed at private networks
      * public apis always have to be placed on public exposure
      * patners could access the API through a peer connection between two private networks. 
    * you can provide different API capabilities to each type of consumer, for example:
      * private: all features
      * partner: many features
      * public api: least features
    * influences security concerns
      * **private apis**: as it is used by trusted developers, the security isn't the biggest concern.
        * you can use Basic Auth and Proprietary schemes
      * **private api and patners**: cannot be trusted, so the security is a lot bigger.
        * you can use Key/Secret or OAuth
    * influences documentation
      * **private or parner**: as they are on a controlled environments, so the provider can share the details of the API thought PDFs or internal websites.
      * **public api**: developer portal (the commercial website that divulge your API)
    * Access request
      * **private or parner**: email or ticket/process
      * **public api** developer portal

## API Value of chain

* An API makes the asset of value easily accessible inside and outside the bounds of the organization
  * There are three types of assets
    * Data | Integration
      * The Weather Company
      * FedEX Express
    * Service | Product
      * Netflix
    * Social network
      * facebook
      * twitter

* The organization can receive money because a API, the methods are framed in two broad categories:
  * direct revenue: The company expose data and service by the API, with a subscription model.
  * indirect benefits: The company expose a free API, but gain money through indirect ways, for example: Partner Ecosystem, agility, brand recognition, competitive advantage, social good, and go so.
* There are many types of many of end consumer
  * Individual Users
    * Public domain apps
    * Browsers | App stores
  * Enterprise Users
    * SAAS Solutions
    * Packaged solutions
    * Home grown application