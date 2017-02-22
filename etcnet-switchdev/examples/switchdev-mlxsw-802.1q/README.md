Example network configuration for Mellanox Spectrum switches with
[mlsw](https://github.com/Mellanox/mlxsw/wiki/Overview) switchdev driver.

* bonds:
  * bond1 - 802.3ad, ports: swp1,swp2
  * bond2 - 802.3ad, ports: swp3,swp4
* bridges:
  * br0 - VLAN aware (802.1q) bridge
    * ports: bond1, bond2
    * VLANs: 10 40 30 40
    * PVID: 1 (default)
* Routed interfaces
  * br0 (VLAN 1)
    * 172.16.1.254/24
  * swp16 - uplink
    * 10.0.255.1/24
* Physical interfaces
  * swp1, swp2, swp3, swp4, swp16
