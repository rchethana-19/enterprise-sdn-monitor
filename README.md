# SDN NOC Dashboard (OVS-Vision)

A secure, real-time Software-Defined Networking (SDN) Network Operations Center (NOC) Monitoring Dashboard. This project simulates a multi-departmental enterprise network infrastructure using **Mininet** and **Open vSwitch (OVS)**, utilizing a **Flask** and **D3.js** telemetry engine to visualize topology performance, live packet metrics, and latency logs.

---

## Features

- **Enterprise Topology Simulation:** Implements a multi-department corporate architecture (Engineering, HR, Finance, Server Zone, and Firewall) using Mininet.
- **Dynamic OVS Telemetry:** Polls Open vSwitch instances directly via `ovs-ofctl` to extract real-time packet counts (Rx/Tx) and calculate interface loss rates.
- **Namespace-Aware Monitoring:** Traverses Linux network namespaces (`ip netns`) to capture real-time host-to-host performance statistics.
- **D3.js Topology Rendering:** Features an interactive, force-directed graph displaying live structural relationships and node groupings.
- **Enterprise Dark Theme:** Responsive UI/UX designed to mimic a modern security-focused operations control center.

---

## Network Architecture

The infrastructure replicates a flat, secure corporate subnet environment where departmental switches route back to a centralized Core Switch layer protected by an administrative firewall gateway:

```text
               [ Internet ]
                    |
               [ Firewall ] (fw1)
                    |
             [ Core Switch ] (s1)
          /      /      \      \
        s2      s3       s4     s5 (Server Zone)
       /        |        |       | \
   [Eng]      [HR]   [Finance]  Web  DB
  h1,h2,h3   h4,h5     h6,h7    h8   h9
