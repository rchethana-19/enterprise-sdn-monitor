#!/usr/bin/env python3
import time
import subprocess
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, Host
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def clean_stale_interfaces():
    """Forcefully cleans up background network namespace links to prevent 'File exists' crashes."""
    info('*** Pre-cleaning stale veth interfaces and configurations\n')
    subprocess.run("sudo mn -c", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)

def create_corporate_topology():
    # Automatically purge old runtime allocations before building nodes
    clean_stale_interfaces()

    # Pass controller=None to let switches operate in normal standalone learning mode
    net = Mininet(topo=None, build=False, ipBase='10.0.0.0/24', controller=None)

    info('*** Adding Switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch) # Core Switch
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch) # Engineering Switch
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch) # HR Switch
    s4 = net.addSwitch('s4', cls=OVSKernelSwitch) # Finance/Admin Switch
    s5 = net.addSwitch('s5', cls=OVSKernelSwitch) # Server Zone Switch

    info('*** Adding Hosts on a Flat Corporate Subnet\n')
    # Firewall node acting as standard gateway
    fw1 = net.addHost('fw1', ip='10.0.0.1/24')

    # Engineering Department 
    h1 = net.addHost('h1', ip='10.0.0.11/24', defaultRoute='via 10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.12/24', defaultRoute='via 10.0.0.1')
    h3 = net.addHost('h3', ip='10.0.0.13/24', defaultRoute='via 10.0.0.1')

    # HR Department
    h4 = net.addHost('h4', ip='10.0.0.14/24', defaultRoute='via 10.0.0.1')
    h5 = net.addHost('h5', ip='10.0.0.15/24', defaultRoute='via 10.0.0.1')

    # Finance / Admin Department
    h6 = net.addHost('h6', ip='10.0.0.16/24', defaultRoute='via 10.0.0.1')
    h7 = net.addHost('h7', ip='10.0.0.17/24', defaultRoute='via 10.0.0.1')

    # Server Zone
    h8 = net.addHost('h8', ip='10.0.0.8/24', defaultRoute='via 10.0.0.1')  # Web Server
    h9 = net.addHost('h9', ip='10.0.0.9/24', defaultRoute='via 10.0.0.1')  # Database Server

    info('*** Creating Links\n')
    # Infrastructure Core Interconnections
    net.addLink(s1, fw1)
    net.addLink(s1, s2)
    net.addLink(s1, s3)
    net.addLink(s1, s4)
    net.addLink(s1, s5)

    # Departmental Host Allocations
    net.addLink(s2, h1)
    net.addLink(s2, h2)
    net.addLink(s2, h3)

    net.addLink(s3, h4)
    net.addLink(s3, h5)

    net.addLink(s4, h6)
    net.addLink(s4, h7)

    # Server Zone Allocations
    net.addLink(s5, h8)
    net.addLink(s5, h9)

    info('*** Starting Network\n')
    net.build()
    
    # Force Open vSwitch switches to work as standard self-learning MAC engines
    for sw in [s1, s2, s3, s4, s5]:
        sw.start([])
        sw.cmd(f'ovs-vsctl set-fail-mode {sw.name} standalone')

    info('*** Simulating internal traffic routes...\n')
    h1.cmd('ping -c 2 10.0.0.8 &')
    h6.cmd('ping -c 2 10.0.0.9 &')

    info('*** Topology is running. Dropping into Mininet CLI.\n')
    CLI(net)

    info('*** Stopping Network\n')
    net.stop()
    subprocess.run("sudo mn -c", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == '__main__':
    setLogLevel('info')
    create_corporate_topology()
