# How to horizontally scale nginx

* Each new connection adds overhead to nginx, and if there is so much connection, nginx can be overwhelmed.
* Spin multiple nginx instances is possible, but it is a hassle because each nginx instance is a new IP address
* To horizontally scale can:
  * offload the loadbalacing to the clients, you make available all nginx IPs and let them decide each one they uses.
    * zookeeper uses this ideia
    * We can put these IP addresses behind the same DNS record, so the client will access all of them.
      * clients can choose the IP address with lower latency, creating a location-based load-balancing.
  * you configure multiple nginx instances to have the same public IP, a trick called "Anycast IP".
    * Anycast IP is a method where multiple machines share the same public IP address on the global Internet, and routers choose the nearest one to use in their routing tables.