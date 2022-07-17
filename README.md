When an Arista switch boots up, it will seek out DHCP information across all ports.

Set up a TFTP server and download the scripts:
```
apt-get install git
apt-get install tftpd-hpa
vi /etc/default/tftpd-hpa
root@ubuntu:/tftp# cat /etc/default/tftpd-hpa 
TFTP_USERNAME="root"
TFTP_DIRECTORY="/tftp"
TFTP_ADDRESS=":69"
TFTP_OPTIONS="--secure --create"
sudo mkdir /tftp
sudo chown root:root /tftp
sudo systemctl restart tftpd-hpa
cd /tftp
git clone https://github.com/netnem/arista_ztp.git

vi /etc/ssh/sshd_config and set:
PermitRootLogin yes

Make sure root password is set:
sudo passwd root
```

On an EdgeOS/VYOS router pointing to a TFTP server located at 192.168.2.117:
```
set service dhcp-server shared-network-name LAN subnet 192.168.0.0/16 bootfile-name 'tftp://192.168.2.117/arista_ztp/ztp'
```

This bootstrap script will enable the pyeapi Management interface, download the proper ZTP script, and then run it.  The bootstrap script will error out once and then run properly. 

Order of operations for ZTP script is as followed: 

Spine 1 must be auto-provisioned first, then at LEAST 1 leaf must be turned up. 

After that, any order is OK. At least 1 leaf must be available for spine2 to be provisioned. Everything else will be turned up as leafs

Use the following topology:

![Alt text](arista_lab.png?raw=true "Lab Setup")


Outcome of the script is as followed:

### spine

```
spine-lab-2-usiqh-veos1-ds00#show bgp summary
BGP summary information for VRF default
Router identifier 10.10.10.1, local AS number 65001.1
Neighbor                               AS Session State AFI/SAFI                AFI/SAFI State   NLRI Rcd   NLRI Acc
----------------------------- ----------- ------------- ----------------------- -------------- ---------- ----------
fd00::2:1                         65002.1 Established   L2VPN EVPN              Negotiated              2          2
fd00::2:2                         65002.2 Established   L2VPN EVPN              Negotiated              2          2
fd00::2:3                         65002.3 Established   L2VPN EVPN              Negotiated              3          3
fd00::2:4                         65002.4 Established   L2VPN EVPN              Negotiated              4          4
fe80::5251:cbff:fec6:8d29%Et2     65002.2 Established   IPv6 Unicast            Negotiated              6          6
fe80::5269:aaff:feb6:f8c2%Et4     65002.4 Established   IPv6 Unicast            Negotiated              4          4
fe80::5299:f3ff:fe67:c270%Et3     65002.3 Established   IPv6 Unicast            Negotiated              8          8
fe80::52de:d4ff:fe20:3ad9%Et1     65002.1 Established   IPv6 Unicast            Negotiated              6          6


spine-lab-2-usiqh-veos1-ds00#show running-config 
! Command: show running-config
! device: spine-lab-2-usiqh-veos1-ds00 (vEOS-lab, EOS-4.28.0F)
!
! boot system flash:/vEOS-lab.swi
!
no aaa root
!
transceiver qsfp default-mode 4x10G
!
service routing protocols model multi-agent
!
hostname spine-lab-2-usiqh-veos1-ds00
ip name-server vrf default 192.168.1.1
dns domain home.mydomain.com
!
spanning-tree mode mstp
!
management api http-commands
   protocol http
   protocol unix-socket
   no shutdown
!
interface Ethernet1
   mtu 9000
   no switchport
   ipv6 enable
!
interface Ethernet2
   mtu 9000
   no switchport
   ipv6 enable
!
interface Ethernet3
   mtu 9000
   no switchport
   ipv6 enable
!
interface Ethernet4
   mtu 9000
   no switchport
   ipv6 enable
!
interface Ethernet5
   mtu 9000
   no switchport
   ipv6 enable
!
interface Ethernet6
   mtu 9000
   no switchport
   ipv6 enable
!
interface Ethernet7
   mtu 9000
   no switchport
   ipv6 enable
!
interface Ethernet8
   mtu 9000
   no switchport
   ipv6 enable
!
interface Loopback0
   description "router-id"
   ipv6 address fd00::1:1/128
!
interface Management1
   ip address 192.168.3.253/16
   ipv6 enable
   ipv6 address auto-config
   ipv6 nd ra rx accept default-route
!
ip routing
!
ipv6 unicast-routing
!
peer-filter AS-FILTER
   10 match as-range 1-4294967295 result accept
!
router bgp 65001.1
   bgp asn notation asdot
   router-id 10.10.10.1
   bgp default ipv4-unicast transport ipv6
   maximum-paths 4 ecmp 4
   bgp listen range fd00::/8 peer-group EVPN peer-filter AS-FILTER
   bgp listen range fe80::/10 peer-group UNDERLAY peer-filter AS-FILTER
   neighbor EVPN peer group
   neighbor EVPN next-hop-unchanged
   neighbor EVPN update-source Loopback0
   neighbor EVPN ebgp-multihop 5
   neighbor EVPN password 7 qHTi18SilZAHr/5ZpEAbOg==
   neighbor EVPN send-community extended
   neighbor EVPN maximum-routes 12000
   neighbor UNDERLAY peer group
   neighbor UNDERLAY password 7 qUVY5FTrMckx90KgE8blBQ==
   neighbor UNDERLAY send-community extended
   redistribute connected
   !
   address-family evpn
      neighbor EVPN activate
      no neighbor UNDERLAY activate
   !
   address-family ipv4
      no neighbor EVPN activate
      no neighbor UNDERLAY activate
   !
   address-family ipv6
      no neighbor EVPN activate
      neighbor UNDERLAY activate
!
end
```

### leaf:


```
leaf-lab-2-usiqh-veos1-dl00#show bgp summary
BGP summary information for VRF default
Router identifier 10.10.20.1, local AS number 65002.1
Neighbor                               AS Session State AFI/SAFI                AFI/SAFI State   NLRI Rcd   NLRI Acc
----------------------------- ----------- ------------- ----------------------- -------------- ---------- ----------
fd00::1:1                         65001.1 Established   L2VPN EVPN              Negotiated              2          2
fd00::1:2                         65001.2 Established   L2VPN EVPN              Negotiated              2          2
fe80::5259:faff:fe4d:b25e%Et2     65001.2 Established   IPv6 Unicast            Negotiated              5          5
fe80::526d:34ff:fedd:4cbf%Et1     65001.1 Established   IPv6 Unicast            Negotiated              5     


leaf-lab-2-usiqh-veos1-dl00#show running-config 
! Command: show running-config
! device: leaf-lab-2-usiqh-veos1-dl00 (vEOS-lab, EOS-4.28.0F)
!
! boot system flash:/vEOS-lab.swi
!
no aaa root
!
transceiver qsfp default-mode 4x10G
!
service routing protocols model multi-agent
!
hostname leaf-lab-2-usiqh-veos1-dl00
ip name-server vrf default 192.168.1.1
dns domain home.domain.com
!
spanning-tree mode mstp
!
vlan 3304
!
management api http-commands
   protocol http
   protocol unix-socket
   no shutdown
!
interface Ethernet1
   mtu 9000
   no switchport
   ipv6 enable
!
interface Ethernet2
   mtu 9000
   no switchport
   ipv6 enable
!
interface Ethernet3
   switchport access vlan 3304
   ipv6 enable
!
interface Ethernet4
   switchport access vlan 3304
   ipv6 enable
!
interface Ethernet5
   switchport access vlan 3304
   ipv6 enable
!
interface Ethernet6
   switchport access vlan 3304
   ipv6 enable
!
interface Ethernet7
   switchport access vlan 3304
   ipv6 enable
!
interface Ethernet8
   switchport access vlan 3304
   ipv6 enable
!
interface Loopback0
   description "router-id"
   ipv6 address fd00::2:1/128
!
interface Loopback1
   description "vxlan-source"
   ipv6 address fd00::20:1/128
!
interface Management1
   ip address 192.168.3.242/16
   ipv6 enable
   ipv6 address auto-config
   ipv6 nd ra rx accept default-route
!
interface Vlan3304
   ip address virtual 193.168.104.1/24
   ipv6 address virtual 2600:1000::1/64
!
interface Vxlan1
   vxlan source-interface Loopback1
   vxlan udp-port 4789
   vxlan encapsulation ipv6
   vxlan vlan 3304 vni 3304
!
ip virtual-router mac-address 00:1c:73:00:00:99
!
ip routing
!
ipv6 unicast-routing
!
!
peer-filter AS-FILTER
   10 match as-range 1-4294967295 result accept
!
router bgp 65002.1
   bgp asn notation asdot
   router-id 10.10.20.1
   bgp default ipv4-unicast transport ipv6
   maximum-paths 4 ecmp 4
   neighbor EVPN peer group
   neighbor EVPN next-hop-unchanged
   neighbor EVPN update-source Loopback0
   neighbor EVPN ebgp-multihop 5
   neighbor EVPN password 7 qHTi18SilZAHr/5ZpEAbOg==
   neighbor EVPN send-community extended
   neighbor EVPN maximum-routes 12000
   neighbor UNDERLAY peer group
   neighbor UNDERLAY password 7 qUVY5FTrMckx90KgE8blBQ==
   neighbor UNDERLAY send-community extended
   neighbor fd00::1:1 peer group EVPN
   neighbor fd00::1:1 remote-as 65001.1
   neighbor fd00::1:2 peer group EVPN
   neighbor fd00::1:2 remote-as 65001.2
   redistribute connected
   neighbor interface Et1 peer-group UNDERLAY remote-as 65001.1
   neighbor interface Et2 peer-group UNDERLAY remote-as 65001.2
   !
   vlan-aware-bundle all-vlans
      rd 1:1
      route-target both 1:1
      redistribute learned
      vlan 1-4094
   !
   address-family evpn
      neighbor EVPN activate
      no neighbor UNDERLAY activate
   !
   address-family ipv4
      no neighbor EVPN activate
      no neighbor UNDERLAY activate
   !
   address-family ipv6
      no neighbor EVPN activate
      neighbor UNDERLAY activate
!
end
```
