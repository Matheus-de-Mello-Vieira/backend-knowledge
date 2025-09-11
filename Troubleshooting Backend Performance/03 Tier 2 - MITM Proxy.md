# Tier 2 - MITM Proxy

A proxy or reverse proxy that serves to debugging, so it intercepts traffics between client and server.

*   It is good for mobile and desktop applications, that have no DevTools.
*   Good to debug traffic between two services.

The tool that we will use is [Man-in-the-Middle (MITM) proxy](https://www.mitmproxy.org/).

*   There is the option to run in the docker, if you relish.

## as proxy

### Executing

#### mitmproxy

Execute the `mitmproxy` on terminal, that will start to listen

```bash
mitmproxy -p 8181
```

It will open a iterative window on your terminal

Configure you system, because many times it write the enviroment variable `NO_PROXY` with the value `localhost,127.0.0.0/8,::1`, so the proxy won't work

*   This is why we are using `--noproxy ""`

```bash
curl --proxy http://127.0.0.1:8181 --noproxy "" http://127.0.0.1:80/
```

Now back to the terminal running `mitmproxy` and you can click on the request log to see the same info of DevTools.

*   you can configure your system use that proxy
    *   the curl is one of the few examples that ignores the system configuration.

#### mitmdump

instead of `mitmproxy`, use `mitmdump`

```bash
mitmdump -p 8181
```

*   It wont open a iterative interface as `mitmproxy`, only print the info on the terminal
*   You can dial the information using the parameters `--verbose` and `--flow-detail 4`

#### mitmweb

```
mitmweb -p 8181
```

*   Instead of a iterative terminal interface, it will open a actual web server with a web interface.

### Intercepting SSL

The MTIM have the interrupt the SSL

In order to do it, you need to add the MTIM root certificate on your certificate store

1)   Access `http://mitm.it/`, the traffic have to be passing thought mtim
2)   Download the `.pem` corresponding to your OS of your client.
3)   Add that `.pem` on your certificate store
     *   Some clients have its own certificate store, and don't allow you add more.
         *   Some even hard code the expected public key, in a technique called certificate pinning.
             *   ex.: the app of twitter.

## as reverse proxy

In order to intercepting between two services, we need to install the MITM as a reverse proxy

*   The difference between proxy and reverse proxy is that the client knows the final destination on the first, but not on the second.

```bash
mitmweb --mode reverse:http://localhost:9002 -p 9000
```

Where the `http://localhost:9002` is the true backend.

