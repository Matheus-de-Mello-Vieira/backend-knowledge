# Transport Layer Security (TLS)

* Stands for Transport Layer Security
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

## Encryption

* Encryptions are two types
  * Symmetric: You encrypt with key and decrypt with the same key
    * one key
    * Fast but both client and server must have the same key
  * Asymmetric: You encrypt with a key and decrypt with another
    * Comes in pair: one private and one public
    * Slower but both client and server can have their own public keys
    * you can generate the public key using the private one, but you can't generate the private key using the public one.
    * there is two ways:
      * you can encrypt with the public key, and decrypt with the private one
        * only owner of private Key can decrypt it
        * it can prove receiver authenticity
      * you can encrypt with the private key, and decrypt with the public one
        * only the corresponding public key can decrypt it
        * only owner of the private key could have signed this document
        * Protects confidentially, nobody could have missed with it.
* We always want to encrypt with Symmetric encryptions
* Exchange the symmetric key with asymmetric encryption

### Certificates

* We need a way to proof authenticity

  * for example, proof my website name is mine.

* process:

  1) Generate a pair of public/private key

  2) Put a public key in a certificate

  3) Sign the certificate with the a private key

  4) Meet x509: the standard for certificates today

* certificates can be "self signed"

  * i.e. private key signing the cert belong to the public key
  * Usually untrusted and used for test/local

* certificates can sign "other certificates"

  * creating a trust chain
  * Issuer name is who issued it
  * Leys enctypts

* Ultimately a ROOT cert is found

  * Root certs are always self signed
  * They are trusted by everyone
  * Installed with OS root (certificate store), with a big list of trusted root certs
    * some systems have their on certificate store, so they don't need to trust the OS' one.

The trust a certificates:

* Is the certificate a root?
  * if yes, it is trusted
  * else, it looks for the certificate that signed it, and repeat the process recessively. 
    * servers can send the full chain of certificates, because sometimes clients don't have some of the intermediate certificate authorities in their certificate store.
      * the server supports more clients, in spite of having to transfer more data.

## TLS Versions

### TLS 1.2 (RSA)

The server have a pair of public and private keys for handshake, and the client have a symmetric key 

* The client send a "hello" to the server
* The server send the public key
  * the public key is wrapped on a certificate
    * it avoid any attacker to intercept it and send their own public key

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

### Diffie-Hellman

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

### TLS 1.3

Uses the Diffie-Hellman algorithm 

1) The client sends the public key and the combination of its private key and the public key.
   * the public key is wrapped on a certificate
     * it avoid any attacker to intercept it and send their own public key
2) The server combine the sent combination with its private key and get the symmetric key.
3) The server sent the combination of its private key and the public key.
4) So the client combine the sent combination with its private key and get the symmetric key.