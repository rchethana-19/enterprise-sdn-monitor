# OVS-Vision Architecture

## Overview

OVS-Vision is an enterprise-inspired Security Operations Center (SOC) platform for Software Defined Networks. It combines SDN telemetry, security detection, 
MITRE ATT&CK enrichment, SOAR automation, and Splunk Enterprise into a unified monitoring solution.

---

## High-Level Architecture

```text
                    Enterprise SDN Network
                             │
                             ▼
                  Mininet + Open vSwitch
                             │
                             ▼
                 Telemetry Collection Engine
                      (monitor.py)
                             │
       ┌─────────────────────┼─────────────────────┐
       ▼                     ▼                     ▼
Security Detection     MITRE ATT&CK        Splunk Enterprise
                           Mapping               (HEC)
       │                     │
       └─────────────┬───────┘
                     ▼
             SOAR Playbook Engine
                     │
                     ▼
              Flask Dashboard
```

---

# Components

## 1. Mininet

Provides a virtual enterprise SDN environment containing multiple hosts and Open vSwitch switches.

Responsibilities:

- Enterprise network simulation
- Host communication
- Traffic generation

---

## 2. Open vSwitch

Acts as the SDN switching layer.

Responsibilities:

- Packet forwarding
- OpenFlow statistics
- Network telemetry generation

---

## 3. Telemetry Engine (`monitor.py`)

Collects and analyzes network telemetry.

Responsibilities:

- Host latency monitoring
- OpenFlow port statistics
- Firewall monitoring
- Packet loss monitoring
- Security event generation

---

## 4. MITRE ATT&CK Mapper (`mitre.py`)

Maps detected alerts to the corresponding MITRE ATT&CK tactics and techniques.

Example mappings:

| Alert | MITRE Technique |
|--------|-----------------|
| Firewall Disabled | T1562 |
| High Packet Loss | T1498 |
| High Network Latency | T1499 |
| Internal Port Scan | T1595 |

---

## 5. SOAR Engine (`soar.py`)

Generates incident playbooks based on detected security events.

Responsibilities:

- Incident generation
- Automated response recommendations
- Playbook creation

---

## 6. Splunk Enterprise

Receives telemetry and security events through the HTTP Event Collector (HEC).

Stored data includes:

- Security alerts
- MITRE mappings
- SOAR incidents
- Network telemetry

---

## 7. Flask Dashboard

Provides real-time visualization of network health.

Displays:

- Network topology
- Host latency
- OpenFlow statistics
- Security alerts
- SOAR playbooks

---

# Security Workflow

```text
Network Activity
        │
        ▼
Telemetry Collection
        │
        ▼
Security Detection
        │
        ▼
MITRE ATT&CK Mapping
        │
        ▼
SOAR Playbook Generation
        │
        ▼
Splunk Enterprise
        │
        ▼
Dashboard Visualization
```

---

# Detection Capabilities

OVS-Vision currently supports:

- Firewall monitoring
- High packet loss detection
- High latency detection
- Security Scenario Simulator for demonstrations

Each detected event is automatically enriched with MITRE ATT&CK mappings, processed by the SOAR engine, forwarded to Splunk Enterprise, and displayed on the monitoring dashboard.
