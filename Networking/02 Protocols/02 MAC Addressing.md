# MAC Addressing

MAC stands for **Media Access Control**. A MAC address is the Layer 2 identifier used inside a local network segment so switches and network interface cards can decide where an Ethernet frame should go.

At the [Data Link layer](../03%20Network%20Models.md#The%207%20Layers%20of%20OSI), communication happens with **frames**, not IP packets. This is why Layer 2 devices reason about MAC addresses instead of IP addresses.

## What a MAC Address Is

A MAC address is usually a **48-bit** hardware identifier assigned to a network interface card (NIC).

* It is commonly written as six octets, such as `00:1A:2B:3C:4D:5E`
* It identifies an interface on the local link
* It is a **physical address** in the sense of Layer 2 addressing, even though many systems allow it to be changed in software
* It is mainly relevant inside the same LAN or broadcast domain

The [NIC](../02%20Network%20Components.md#The%20Network%20Interface%20Card%20%28NIC%29) is the component that owns this address at the hardware edge of the machine.

## Why MAC Addresses Exist

IP addresses solve inter-network routing, but a machine still needs a way to deliver traffic on the local medium.

* IP tells you **which host or network** should receive the packet logically
* MAC tells the local network **which interface** should receive the frame physically
* Switches forward traffic based on MAC addresses
* Routers move traffic between networks, but the last local hop still depends on Layer 2 delivery

In practice:

* if two hosts are in the same subnet, communication is delivered through MAC addressing on the local link
* if the destination is outside the subnet, the sender still uses a MAC address locally, but it sends the frame to the default gateway's interface

## MAC Addresses and Ethernet

Ethernet is the most common Layer 2 technology in LANs, so MAC addressing is usually discussed together with Ethernet frames.

An Ethernet frame contains at least:

* a **source MAC address**
* a **destination MAC address**
* payload data coming from upper layers

When a switch receives a frame, it learns which source MAC address was seen on which port. Over time, it builds a table that allows it to forward future frames only to the correct destination port instead of broadcasting everything.

## MAC vs. IP

These two address types solve different problems:

* **MAC Address:** Local delivery on the same Layer 2 segment
* **IP Address:** Logical addressing and routing across multiple networks

This separation is fundamental because a single packet traveling across the Internet may keep the same source and destination IPs while the source and destination MAC addresses change at every local hop.

## Security Relevance

MAC addresses appear in security discussions because Layer 2 controls often depend on them.

* **MAC filtering:** Permit or deny traffic based on the source MAC address seen on a switch port
* **Port security:** Restrict how many MAC addresses are allowed on a port, or bind one expected MAC to that port
* **Device inventory:** Track which device is expected on which switch port

These controls can reduce accidental misuse and raise the bar for simple attacks, but they are not strong identity guarantees by themselves because MAC addresses can often be spoofed.

For a security-oriented view of this control, see [Layered Security Techniques](../../Security/05%20Architecture%20and%20Infrastructure%20Security/Network%20Security/Layered%20Security%20Techniques.md#2.%20Data%20Link%20Layer%20Techniques%20%28OSI%20Layer%202%29%20and%20MAC%20Addressing).

## Practical Model

You can think about the delivery path like this:

1. An application creates data.
2. Upper layers prepare transport and IP information.
3. Layer 2 wraps that data in a frame with source and destination MAC addresses.
4. The switch forwards the frame based on its MAC table.
5. The receiving NIC accepts the frame addressed to its interface and passes the payload up the stack.

This is why MAC addressing is best studied as a dedicated Layer 2 concept rather than only as a detail inside switch or security notes.
