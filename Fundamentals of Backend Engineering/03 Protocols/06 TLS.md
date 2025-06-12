# Transport Layer Security (TLS)

* You can build a TLS on any layer 7 protocol 
* the OSI layer of TLS is arguable
  * some people say that it is layer 5 because it is stateful
  * other people say that it is layer 4 because follow the script of TCP handshake
* on the handshake, the both ends get the same key, so they can encrypt their messages.

## Why TLS

* We encrypt with symmetric key algorithms
  * symmetric keys are way faster than asymmetric keys
    * symmetric uses `XOR` on the content and the key, so it is one a bit-wise operation
    * asymmetric encryptions and decryption is exponential
* We need to exchange the symmetric key
  * to use symmetric, the both sides must know the key
  * Key exchange uses asymmetric key (PKI)
    * so there is two encryption algorithms: one to key exchange, and another to the actual data.
* Authenticate the server
* Extensions (SNI, preshared, 0RTT)

## TLS 1.2

The server have a pair of public and private keys for handshake, and the client have a symmetric key 

* The client send a "hello" to the server
* The server send the public key
* The client uses the public key to encrypt the symmetric key, and send it to server
  * actually, it is the info need to generate the symmetric key, not the symmetric key itself.
* The server will use the private key to get the symmetric key
* The server confirms it

So the data can be actually encryption

The problem is that the transactions can be intercepted, and if the server private key was leak, the data can be exposed. 
* for example, the server private key can be helped by a bug of a library that the server uses
* many servers stores all the transitions, that make the data vulnerable in any time of the future
* the many cause of this problem is the fact the private key still the same.
  * some server change the private key regularly, so the data leaks are less harmful.

## Diffie-Hellman

The symmetric key is derived using two private keys and one public key as part of the key exchange process

* The combination the public key with one of the private keys is unbreakable.
  * for example: `g^x % n` where `g` and `n` came from public key and `x` came from one of the private keys
  * so you can share that combination safely.
  * will also can use the other private key to get `g^y % n`. Also can be shared safely
  * However: `(g^x % n)^y = (g^y % n)^x = g^(xy) % n`
* The idea is each side knows the public key and one of the private keys
  * they send the combination of public key and their private key
  * So they combine the other side combination with their own private key
  * as the combination algorithm are associative, they get the same value that is used to generate the symmetric key

## TLS 1.3

Uses the Diffie-Hellman algorithm 

1) The client sends the public key and the combination of its private key and the public key.
2) The server combine the sent combination with its private key and get the symmetric key.
3) The server sent the combination of its private key and the public key.
4) So the client combine the sent combination with its private key and get the symmetric key.