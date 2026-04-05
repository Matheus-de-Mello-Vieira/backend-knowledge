# HTTPS Communication Basics

HTTPS is everywhere, so there are so many configuration to HTTPS.

* You want configure your backend to the right configuration.
* Establish Connection
* Establish Encryption
* Send Data
* Close Connection

## HTTP over TLS with TLS 1.2

* To establish Connection, we need to: 
  1. TCP handshake: establish a TCP connection
  2. TLS handshake: agree a symmetric key.
  3. HTTP handshake: establish a HTTP connection

## HTTP over TLS with TLS 1.3

Same thing of HTTP over TLS with TLS 1.2, but safer because uses a safer symmetric key agreement algorithm.

* [more details](../06 TLS.md).
* except for compatibly problems, there is no reasons to use TLS 1.2 instead of TLS 1.3

## HTTP3: HTTPS over QUIC

* There is only one handshake
  * The connection hand shake and the TLS hand shake happens on the three messages.
    * the HTTPS1 and HTTP2 have three handshakes, with three messages each, totaling 9. The HTTP3 have only one handshake with three messages.
* encrypted by default
* Build on top of UDP

## HTTPS over TFC with TLS1.3 0RTT

* "0RTT" stand for Zero Round-Trip Time.
* If there is a prior connection was established with client and server, and they still know about it, they can reuse it
* The client send the `ClientHello` (the first of HTTP handshake) message with a `pre_shared_key` extension with the pre-shared key (PSK).
  * If the server response with the `ServeHello` normally, they start to use that key, skipping the whole HTTPS handshake.

## HTTP3 over QUIC 0RTT

* the fastest possible
* Uses the same tenants of  "HTTPS over TFC with TLS1.3 0RTT
* Allows the client make request along with the first message of QUIP handshake, and allows the server response them along with the second message of handshake.
