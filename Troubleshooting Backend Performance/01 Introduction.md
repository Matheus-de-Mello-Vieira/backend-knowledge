# Introduction

## Analysis 

Several levels:

*   **Tier 1**: See only client perspective; The backend is treated as a black box, independently if it has CDN, API Gateway, Load balancer, etc.
    *   One example is the browsers' dev tools
*   **Tier 2**: A reverse proxy that serves to debugging, so it intercepts traffics between client and server.
    *   It is good for mobile applications, that have no dev tools.
    *   Good to debug traffic between two services.
*   **Tier 3**: Captures all network traffic, at OSI model's layer 3.