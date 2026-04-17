# SNMP

SNMP stands for Simple Network Management Protocol.

* It is an application-layer protocol used to monitor and manage network devices such as routers, switches, firewalls, printers, and UPS units.
* It follows a manager-agent model:
  * the **manager** is the monitoring or management system
  * the **agent** runs on the managed device and exposes management data

## Data Model

SNMP exposes data through a hierarchical namespace called the **MIB** (Management Information Base).

* Each managed value is identified by an **OID** (Object Identifier).
* Examples of values exposed through OIDs include:
  * interface counters
  * CPU and memory utilization
  * temperatures and fan status
  * device uptime

## Main Operations

SNMP supports both query and event-driven communication:

* **GET / GETNEXT / GETBULK:** The manager asks the device for values.
* **SET:** The manager changes a writable value on the device.
* **TRAP:** The device sends an unsolicited event to the manager.
* **INFORM:** Similar to a trap, but expects acknowledgment from the receiver.

This distinction matters operationally:

* polling with GET-style operations is **active**
* receiving traps or informs is **passive**

## Versions

### SNMPv1

* Early and simple
* Uses community strings
* Weak security

### SNMPv2c

* Common in practice
* Improves efficiency, especially for bulk retrieval
* Still relies on community strings, so security remains limited

### SNMPv3

* Adds authentication and encryption
* Preferred when security matters

## Operational Notes

* SNMP is very useful for structured device telemetry because vendors expose standard and vendor-specific OIDs.
* The value of SNMP depends on knowing which OIDs matter for the equipment you operate.
* In modern environments, SNMP often coexists with streaming telemetry and API-based management rather than replacing them completely.
