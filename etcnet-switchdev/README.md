## Etcnet fork, patched to work with [Mellanox Switchdev](http://www.mellanox.com/related-docs/prod_switch_software/PB_Switchdev.pdf) driver.

Please use [switchdev mlxsw driver wiki](https://github.com/Mellanox/mlxsw/wiki/Overview) as a reference.

Key changes:
* Added support for **VLAN-aware** (802.1q) bridges
  * Can create only **one** VLAN-aware bridge to the system
  * Enabled with `BRIDGE_OPTIONS="vlan_filtering 1` in *options* file
  * VLANs can be added with `VLANS="<VLAN1> <VLAN2> ..."` in *options* file
  * PVID (native VLAN) is set with `PVID=<VLAN>` in *options* file
  * All ports under bridge are inheriting bridge VLAN settings by default
* Added support for custom VLAN setting per port
  * VLANs can be set with `VLANS="<VLAN1> <VLAN2> ..."` in *options* file
  * PVID (native VLAN) is set with `PVID=<VLAN>` in *options* file

Tested on Alt Linux Sisyphus under un-def kernel (4.9.10).
