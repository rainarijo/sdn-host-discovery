# SDN Host Discovery Service

## Problem Statement
In a Software Defined Network (SDN), the controller has no automatic knowledge of which hosts exist in the network. This project implements a Host Discovery Service using Mininet and the POX OpenFlow controller that automatically detects hosts when they join the network, maintains a real-time host database with MAC address, IP address, Switch ID and Port, installs OpenFlow flow rules for efficient packet forwarding, and demonstrates controller-switch interaction using the OpenFlow protocol.

## Setup & Execution Steps

**Step 1 - Install Mininet:**
```bash
sudo apt install mininet -y
```

**Step 2 - Clone POX Controller:**
```bash
git clone https://github.com/noxrepo/pox ~/pox
```

**Step 3 - Start POX Controller (Terminal 1):**
```bash
cd ~/pox
python3 pox.py host_discovery
```

**Step 4 - Start Mininet (Terminal 2):**
```bash
sudo mn --topo single,3 --controller remote
```

**Step 5 - Run tests in Mininet CLI:**
```bash
pingall
h1 ping h2 -c 5
iperf h1 h2
```
## Proof of Execution

### 1. Mininet Topology Creation and Full Network Connectivity Test
Normal case:
<img width="666" height="495" alt="image" src="https://github.com/user-attachments/assets/ff1f5b9c-2425-4854-bb52-a6ad64befa32" />
Failure case:
<img width="202" height="145" alt="image" src="https://github.com/user-attachments/assets/ca70053b-54a8-408a-af2e-c3736ef8e404" />

Allowed Case:
<img width="289" height="83" alt="image" src="https://github.com/user-attachments/assets/f4fe6a62-a02e-4959-b396-a18fb04af98a" />

Blocked Case:
<img width="331" height="70" alt="image" src="https://github.com/user-attachments/assets/24544e2d-946e-441b-a03c-8ed7f89addb5" />



### 2. Individual Host Communication - h1 to h2 Ping Test
<img width="742" height="307" alt="image" src="https://github.com/user-attachments/assets/ccfa2f79-6dd8-4caf-af97-2d72e5e2e288" />

### 3. POX Controller - Host Discovery and Host Database Logs
<img width="909" height="471" alt="image" src="https://github.com/user-attachments/assets/43f24e52-0ded-4afd-b536-c4fdf2f151d9" />

### 4. Network Throughput Measurement using iperf
<img width="725" height="118" alt="image" src="https://github.com/user-attachments/assets/11160353-bb3b-4518-824e-b792faf41d3b" />

### 5. OpenFlow Flow Table Dump after pingall
<img width="933" height="302" alt="image" src="https://github.com/user-attachments/assets/62a18c30-ae74-48ca-abdf-95cbf211232a" />

## References

1. Mininet Official Site - http://mininet.org
2. Mininet Walkthrough - http://mininet.org/walkthrough/
3. POX Controller Wiki - https://github.com/noxrepo/pox/wiki
4. POX Controller Repository - https://github.com/noxrepo/pox
5. OpenFlow Specification - https://opennetworking.org/sdn-resources/openflow/
6. Open vSwitch Documentation - https://www.openvswitch.org/
7. Software Defined Networking (SDN) Overview - https://opennetworking.org/sdn-definition/
8. Mininet GitHub Repository - https://github.com/mininet/mininet
9. Mininet Installation Guide - https://github.com/mininet/mininet/blob/master/INSTALL
