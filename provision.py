#!/usr/bin/env python3

import pyeapi
from pprint import pprint
import re

# create a node object by specifying the node to work with

node = pyeapi.connect_to("localhost")


#default the config:
node.config('no banner login')
node.config('default logging level all')
node.config('default logging console')
node.config('default logging policy')
#delete the default route from dhcp/ztp config
node.config('no ip route 0.0.0.0/0')
node.config('switchport default mode access')
node.config('no match-list input string ztpFilter')
node.config(['system control-plane', 'default service-policy input copp-system-policy'])

#begin provisioning
node.config('lldp run')
neighbors = node.enable('show lldp neighbors')

#may need to loop/until in a future release, but seems to work well in vEOS
try:
    interface = (neighbors[0]['result']['lldpNeighbors'][0]['neighborPort'])
except:
    interface = 'Ethernet0' 
try:
    neighbor = (neighbors[0]['result']['lldpNeighbors'][0]['neighborDevice'])
except:
    neighbor = 'none'

#split the number off the end of Ethernet
interfacenum = re.split(r"^.+?(?=\d)", interface)
interfacenum = interfacenum[1]

if re.search(r'^spine.+', neighbor):
    node.config('hostname leaf-lab-2-usiqh-veos' + interfacenum + '-dl00') 
elif re.search(r'^leaf', neighbor):
    node.config('hostname spine-lab-2-usiqh-veos' + '2' + '-ds00') 
else:
    node.config('hostname spine-lab-2-usiqh-veos' + '1' + '-ds00') 

node.config('service routing protocols model multi-agent')
node.config('ip routing')
node.config('ipv6 unicast-routing')

#configure interfaces
if re.search(r'^spine.+', neighbor):
    node.config(['interface Ethernet 1 - 2', 'mtu 9000', 'no switchport', 'ipv6 enable', 'no ipv6 address auto-config', 'no ipv6 nd ra rx accept default-route'])
    node.config(['interface Ethernet 3 - 8', 'switchport access vlan 3304', 'ipv6 enable', 'no ipv6 address auto-config', 'no ipv6 nd ra rx accept default-route'])
else:
    node.config(['interface Ethernet 1 - 8', 'mtu 9000', 'no switchport', 'ipv6 enable', 'no ipv6 address auto-config', 'no ipv6 nd ra rx accept default-route'])


node.config([\
'peer-filter AS-FILTER', \
'10 match as-range 1-4294967295 result accept', \
     ])

if re.search(r'^spine.+', neighbor):
    node.config([\
     'router bgp 65002.'+ interfacenum, \
     'router-id 10.10.20.' + interfacenum, \
     'bgp asn notation asdot', \
     'bgp default ipv4-unicast transport ipv6', \
     'maximum-paths 4 ecmp 4', \
     'neighbor UNDERLAY peer group', \
     'neighbor UNDERLAY send-community extended', \
     'neighbor UNDERLAY password 0 UNDERLAYPASS', \
     'neighbor EVPN peer group', \
     'neighbor EVPN next-hop-unchanged', \
     'neighbor EVPN update-source Loopback0', \
     'neighbor EVPN ebgp-multihop 5', \
     'neighbor EVPN password 0 EVPNPASS', \
     'neighbor EVPN send-community extended', \
     'neighbor EVPN maximum-routes 12000', \
     'neighbor fd00::1:1 peer group EVPN', \
     'neighbor fd00::1:1 remote-as 65001.1', \
     'neighbor fd00::1:2 peer group EVPN', \
     'neighbor fd00::1:2 remote-as 65001.2', \
     'redistribute connected', \
     'neighbor interface Et1-2 peer-group UNDERLAY peer-filter AS-FILTER', \
     'neighbor interface Et1 peer-group UNDERLAY remote-as 65001.1', \
     'neighbor interface Et2 peer-group UNDERLAY remote-as 65001.2', \
     'address-family evpn', \
     'no neighbor UNDERLAY activate', \
     'neighbor EVPN activate', \
     'address-family ipv4', \
     'no neighbor UNDERLAY activate', \
     'no neighbor EVPN activate', \
     'address-family ipv6', \
     'neighbor UNDERLAY activate', \
     'no neighbor EVPN activate', \
     ])

#if neighbor is "leaf", then provision as spine 2
elif re.search(r'^leaf', neighbor):
    node.config([\
    'router bgp 65001.'+ '2', \
    'router-id 10.10.10.' + '2', \
    'bgp asn notation asdot', \
    'bgp default ipv4-unicast transport ipv6', \
    'maximum-paths 4 ecmp 4', \
    'bgp listen range fd00::/8 peer-group EVPN peer-filter AS-FILTER', \
    'bgp listen range fe80::/10 peer-group UNDERLAY peer-filter AS-FILTER', \
    'neighbor UNDERLAY peer group', \
    'neighbor UNDERLAY send-community extended', \
    'neighbor UNDERLAY password 0 UNDERLAYPASS', \
    'neighbor EVPN peer group', \
    'neighbor EVPN next-hop-unchanged', \
    'neighbor EVPN update-source Loopback0', \
    'neighbor EVPN ebgp-multihop 5', \
    'neighbor EVPN password 0 EVPNPASS', \
    'neighbor EVPN send-community extended', \
    'neighbor EVPN maximum-routes 12000', \
    'redistribute connected', \
    'address-family evpn', \
    'no neighbor UNDERLAY activate', \
    'neighbor EVPN activate', \
    'address-family ipv4', \
    'no neighbor UNDERLAY activate', \
    'no neighbor EVPN activate', \
    'address-family ipv6', \
    'neighbor UNDERLAY activate', \
    'no neighbor EVPN activate', \
    ])

else:
    node.config([\
     'router bgp 65001.'+ '1', \
     'router-id 10.10.10.' + '1', \
     'bgp asn notation asdot', \
     'bgp default ipv4-unicast transport ipv6', \
     'maximum-paths 4 ecmp 4', \
     'bgp listen range fd00::/8 peer-group EVPN peer-filter AS-FILTER', \
     'bgp listen range fe80::/10 peer-group UNDERLAY peer-filter AS-FILTER', \
     'neighbor UNDERLAY peer group', \
     'neighbor UNDERLAY send-community extended', \
     'neighbor UNDERLAY password 0 UNDERLAYPASS', \
     'neighbor EVPN peer group', \
     'neighbor EVPN next-hop-unchanged', \
     'neighbor EVPN update-source Loopback0', \
     'neighbor EVPN ebgp-multihop 5', \
     'neighbor EVPN password 0 EVPNPASS', \
     'neighbor EVPN send-community extended', \
     'neighbor EVPN maximum-routes 12000', \
     'redistribute connected', \
     'address-family evpn', \
     'no neighbor UNDERLAY activate', \
     'neighbor EVPN activate', \
     'address-family ipv4', \
     'no neighbor UNDERLAY activate', \
     'no neighbor EVPN activate', \
     'address-family ipv6', \
     'neighbor UNDERLAY activate', \
     'no neighbor EVPN activate', \
     ])


#configure vlans
if re.search(r'^spine', neighbor):
    node.config('vlan 3304')

    node.config([\
    'interface Vxlan1', \
    'vxlan source-interface Loopback1', \
    'vxlan udp-port 4789', \
    'vxlan encapsulation ipv6', \
    'vxlan vlan 3304 vni 3304', \
        ])

    node.config('ip virtual-router mac-address 00:1c:73:00:00:99')

#using public IPs here as they are going to need to be unique per SVIs / org 
    node.config([\
    'interface Vlan3304', \
    'ip address virtual 193.168.104.1/24', \
    'ipv6 address virtual 2600:1000::1/64', \
    ])


    node.config([\
    'interface Loopback0', \
    'description \"router-id\"', \
    'ipv6 address fd00::2:' + interfacenum + '/128', \
    ])

    node.config([\
    'interface Loopback1', \
    'description "vxlan-source"', \
    'ipv6 address fd00::20:' + interfacenum + '/128', \
    ])

    node.config([\
    'router bgp 65002.'+ interfacenum, \
    'vlan-aware-bundle all-vlans', \
    'rd 1:1', \
    'route-target both 1:1', \
    'vlan add 1-4094', \
    'redistribute learned', \
    ])

#if neighbor is "leaf", then provision as spine 2
elif re.search(r'^leaf', neighbor):
    node.config([\
    'interface Loopback0', \
    'description \"router-id\"', \
    'ipv6 address fd00::1:' + '2'+ '/128', \
    ])
else:
    node.config([\
    'interface Loopback0', \
    'description \"router-id\"', \
    'ipv6 address fd00::1:' + '1' + '/128', \
    ])
