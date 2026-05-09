# Disaster Recovery Methods

## Introduction

While organizations worldwide are concerned about cybersecurity, cyberattacks are becoming increasingly sophisticated. Disasters can be of various types, and disaster recovery is all about ensuring that your organization can continue operating with minimal losses in these cases. Business continuity, data protection, loss minimization, and making improvements are essential for any business, and having a disaster recovery plan is fundamental.

## Summary

### Disaster and Disaster Recovery

Disaster recovery (DR) is the ability an organization must have to respond to and recover from an event of any nature that negatively affects operations and the business life cycle. The primary goal of DR methods is to allow the organization to regain use of critical systems and IT infrastructure as quickly and agilely as possible after a disaster occurs.

To prepare for this type of event, organizations typically perform a deep analysis of their systems, services, and structure to create a formal document that can be consulted and followed in times of crisis. This document involves everything from manual procedures to technologies and services, and it is known as a **Disaster Recovery Plan**.

The practice of DR revolves around events of a serious nature. These events are generally considered natural disasters, but they can also be caused by technical failures, system failures, or by humans conducting an intentional attack. They are significant enough to completely disrupt critical business operations for an unmeasured period.

Before an organization can determine its DR strategies, it must first analyze existing assets and priorities. Two different analyses are typically considered in DR decision-making:

* **Risk Analysis**: Risk analysis or risk assessment is an evaluation of all potential risks the business may face, as well as their outcomes. Risks can vary greatly depending on the industry the organization is in and its geographic location. The assessment must identify potential hazards, determine who or what these hazards might harm, and use the findings to create procedures that take these risks into account.
* **Business Impact Analysis (BIA)**: Business Impact Analysis evaluates the effects of identified risks on business operations. A BIA can help predict and quantify costs. It also examines the impact of different disasters on an organization's safety, finances, marketing, business reputation, legal compliance, and quality assurance.

Understanding the difference between risk analysis and business impact allows for conducting assessments that help an organization define its goals regarding data protection and backup needs. Organizations generally quantify this using measurements called **Recovery Point Objective (RPO)** and **Recovery Time Objective (RTO)**.

* **Recovery Point Objective**: This is the maximum point of files an organization must recover from backup storage so that normal operations can resume after a disaster. The RPO determines the minimum frequency of backups. For example, if an organization has an RPO of four hours, the system must perform a backup at least every four hours.
* **Recovery Time Objective**: This refers to the amount of time an organization estimates its systems can be down without causing significant or irreparable damage to the business. In some cases, applications can be down for several days without serious consequences; in others, seconds can cause substantial damage to the business.

#### Main Categories of Disasters:

* Natural disasters.
* Physical disasters.
* Technology-based disasters.

In the case of **natural disasters**, the focus will generally be on infrastructure, relocation, and new ways and methods of working. The pandemic is a major example of this. For most organizations, the infrastructure—routers, servers, workstations, and other technologies—did not suffer interruptions, but the way they were used, the routine, and the organization's workflow had to be modified and adapted.

* **Main Natural Disasters**: Fires, storms, floods, hurricanes, tornadoes, pandemics, among others.

In the case of **physical disasters**, such as a power loss, it may simply require the organization to have people work from home for a short period. Other times, depending on assets, you may have to relocate not only your personnel but also your technology infrastructure. With physical disasters, it is important to understand not only how to recreate your work temporarily but for how long.

* **Main Physical Disasters**: Power, structure and infrastructure, temperature, intrusions, terrorism, among others.

**Technological disasters** are probably the most likely disasters your organization will face. They can have different levels of impact and may require a higher degree of expertise to plan, control, and mitigate.

* **Main Technological Disasters**: Ransomware, hardware failures, network infrastructure failures, data loss by viruses or other means, cyberattacks.

---

### Disaster Recovery Plan

Disaster recovery plans are official documents prepared by an organization. They contain detailed instructions that must be followed to react to various unforeseen events, such as natural disasters, power outages, cyberattacks, and other incidents that can affect the company's functioning. The plan contains strategies to mitigate the effects of a disaster so that an organization continues to operate—or quickly resumes its main operations.

Interruptions can result in lost revenue, penalties for non-compliance with laws, brand damage, and dissatisfied customers. The longer the recovery time, the greater the impact on the business. Therefore, effective disaster recovery plans must allow for rapid recovery after disruptions of any type or origin.

The types of plans may vary based on the IT infrastructure and assets that need protection, as well as the backup and recovery method the organization decides to use. Depending on the size and scope of the organization, it may have separate DR plans and specific implementation teams for departments like data centers or networks. The main types of DR include:

* **Virtualized**: Allows organizations to replicate workloads at an alternative site or in the cloud. Benefits include flexibility, ease of implementation, efficiency, and speed. Replication can be done frequently, and failover can be initiated quickly.
* **Network**: Network connectivity is essential for internal and external communication, data sharing, and application access during a disaster. A network DR strategy must provide a plan to restore network services, especially regarding access to websites and backup data.
* **Cloud**: The widespread acceptance of cloud services allows organizations that traditionally used an alternative site for DR to be hosted in the cloud. Cloud DR goes beyond simple cloud backup; it requires an IT team to configure automatic failover of workloads to a public cloud platform in the event of an interruption.
* **DRaaS (Disaster Recovery as a Service)**: This is the commercially available version of cloud DR. In DRaaS, a third party provides replication and hosting of an organization's physical and virtual servers. The provider assumes responsibility for implementing the DR plan when a crisis arises, based on a service level agreement.
* **Data Center**: Organizations that house their own data centers must have a DR strategy that considers the entire IT infrastructure within the data center, as well as the physical facility.

---

### Main Steps of a DR

1. **Define Objectives**: The DR objectives outline which assets, structures, and services need to be protected in case of a disaster. In parallel, a team must be created to lead the plan if necessary; depending on the organization's size and complexity, several teams are needed. A planning commission or team must be appointed to oversee the development and implementation of the plan.
2. **Risk and Impact Analysis**: The planning committee must prepare a risk analysis and business impact analysis that includes a range of possible disasters, including natural, physical, or technological threats. Each functional area of the organization must be analyzed to determine the potential consequence and impact associated with various disaster scenarios.
3. **Evaluate Critical Needs**: The critical needs of each department within the organization must be carefully evaluated and prioritized. Operations must be analyzed to determine the maximum amount of time the department and the organization can operate without each critical system. Practical alternatives and strategies for processing the plan in case of a disaster must be researched and evaluated.
4. **Management Support**: Senior management must support and be involved in the development of the disaster recovery planning process. Management must be responsible for coordinating the disaster recovery plan and ensuring its effectiveness within the organization. It is important that all departments are aware of the plan and have the capacity to execute it.
5. **Documentation and Testing**: A documented outline of the plan's content should be prepared to guide properly detailed steps and processes. Senior management must review and approve the proposed plan. It is essential that the plan is thoroughly tested and evaluated regularly (at least annually). Procedures for testing and executing the plan must be documented, as tests provide the organization with the assurance that all necessary steps are included.

---

### Standards and Regulations

When it comes to regulations, standards are the first to be consulted, and it is no different for disasters. Many organizations propose the development of business continuity plans and systems, addressing different stages and systematic approaches.

* **ISO/IEC 24762 (2008)**: This standard provided guidelines for information technology disaster recovery services; however, there has been no update, and while its practices are functional, they are no longer in effect.

Two other standards currently stand out in this scenario:

* **NBR ISO/IEC 22301 (2020)**: *Security and resilience — Business continuity management systems — Requirements*. This describes how to manage business continuity in a company after adverse events—whether due to a digital security failure or other factors. The main idea of ISO 22301 is based on impact analysis and risk management. It seeks to identify which activities are most important and which risks may affect them to treat those risks systematically. The standard focuses on issues such as leadership, planning, support, operation, evaluation, and continuous improvement.
* **NIST 800-34**: *Contingency Planning Guide for Federal Information Systems*. This standard mentions that contingency planning is unique to each system, providing preventive measures, recovery strategies, and technical considerations appropriate to the confidentiality, integrity, and availability of system information and the system's impact level. Guidelines present principles for client/server systems, telecommunications systems, and mainframe systems.

The NIST document describes planning principles for a wide range of incidents, varying from small incidents causing short-term interruptions to disasters affecting normal operations for a prolonged period.

---

### How to Apply What You Have Learned in Practice

As any security professional agrees, going through a disaster scenario is a complicated situation. The best scenario is undoubtedly to prevent and have a plan for service recovery and high resilience. To achieve this, it is necessary for the **ISO 22300 series** standards and disaster plans to be known by security professionals.

The main standards in this series are:

* **ISO 22300**: Security and resilience.
* **ISO 22301**: Security and resilience — Business continuity management systems — Requirements.
* **ISO 22313**: Security and resilience — Business continuity management systems — Guidance on the use of ISO 22301.
* **ISO 22320** (cited as ISO 2230 in source): Security and resilience — Emergency management — Guidelines for incident management.

Try to understand what each standard is about and make a list of the main points of each one.