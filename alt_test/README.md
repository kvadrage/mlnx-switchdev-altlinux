# LNST tests for spectrum switchdev on Alt Linux

## Test pools
* bulldog1-2hosts
  * 1x **SN2100** (Bulldog) switch with 16x 40/100G QSFP28 ports
  * 2x **Alt Linux** hosts with dual 40/100G uplinks

## Test recipes
* basic
  * links test
* L2 bridge
  * bridge test
  * bridge FDB test
  * bridge STP test
  * bridge bond test
  * bridge bond failover test
  * bridge team test
  * bridge team failover
  * bridge 802.1q VLAN test
  * bridge 802.1q VLAN sanity test
  * bridge 802.1d VLAN test
  * bridge 802.1d VLAN sanity test
  * bridge 802.1d VLAN test with bonding
  * bridge 802.1d VLAN sanity test with bonding
  * bridge 802.1d VLAN test with teaming
  * bridge 802.1d VLAN sanity test with teaming
  * bridge 802.1d VLAN FDB test
  * bridge team FDB test
  * bridge 802.1d VLAN FDB test with teaming
  * SPAN test (port mirroring)
* L3 router
  * router port test
  * VLAN interface test
  * bond L3 interface test
  * team L3 interface test
* QoS test
  * ToDo

## How to run?
* Install LNST on switch and all hosts
* Install LNST on management host
* Run **lnst-slave -d on switch and hosts**
* Run **lnst-ctl --pools ./lnst_pools/<pool> run lnst_recipes/<recipe>**
