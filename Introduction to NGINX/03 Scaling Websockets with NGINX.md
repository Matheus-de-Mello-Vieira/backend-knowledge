# Scaling websockets with NGINX

Websockets are stateful, so it a lot harder to scale than stateless stuff, as HTTP.

## L4 Proxying

* Layer 4 Proxying on WebSockets is done as a tunnel.
* NGINX intercepts the SYN for a connection and creates another connection on the backend. Any data sent on the frontend connection is tunneled to the backend connection.
* TLS Pass-through
* Define timeouts properly.

### demo

* Listen to 80
* Paths don't matter: `ws://localhost/` and `ws://localhost/blablabla` are both threated as websocket apps.

```nginx
stream {
    upstream wsbackends {
        server nodeapp1:8080;
        server nodeapp2:8080;
        server nodeapp3:8080;
    }

    server {
        listen 80;
        proxy_pass wsbackends;
    }
}

events {}
```



## L7 Proxying

* The nginx first establish a connection with client, so it start to establish one with the backend.
* TLS Termination: fronted connections and backend connections are encrypted independently. 
* nginx can manipulate the data that pass through the websocket.
* each backend connection handles only front-end connection per time, there is no sharing (as there is on HTTP).

### demo

* Intercept the path and "route" appropriately
  * `http://localhost/`: open main html page
  * `ws://localhost/wsapp`: websocket app
  * `ws://localhost/chat`: another websocket app in another server

```nginx
http {
    upstream httpbackends  {
        server nodeapp1:8080;
    }
    upstream wsapp {
        server nodeapp2:8080;
        server nodeapp3:8080;
    }
    upstream wschat {
        server nodeapp4:8080;
    }

    server {
        listen 80;
        
        location / {
            proxy_pass httpbackends;
        }
        
        location /wsapp {
            proxy_pass wsapp;
            
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade; # will upgrade any protocol 
            proxy_set_header Connection "Upgrade";
            proxy_set_header Host $host;
        }
        
        location /chat {
            proxy_pass wschat;
            
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade; # will upgrade any protocol 
            proxy_set_header Connection "Upgrade";
            proxy_set_header Host $host;
        }
    }
}

events {}
```

You should put `proxy_set_header Upgrade "websocket"`, so the client can't upgrade to any other protocol.