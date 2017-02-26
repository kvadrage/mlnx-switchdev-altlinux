# Switchdev and Alt Linux play for Ansible
Ansible play to configure Alt Linux setup with Mellanox Spectrum switch.
## Overview
This play automates network configuration for simple setup, based on Alt Linux servers and Mellanox Spectrum switch (also running Alt Linux with switchdev driver).

## Network topology
```
############# eth2    swp1 ############# swp3    eth2 #############
#           #--------------#    sw1    #--------------#           #
#  server3  # eth3    swp2 #           # swp4    eth3 #  server4  #
#           #--------------# switchdev #--------------#           #
#############              #############              #############
```

## Funtionality
* Templates the interfaces configuration for Etcnet network configuration subsystem
  * basic interfaces configuration
  * bonds configuration
  * VLAN-aware bridge configuration
  * static routing
* Enables IPv4 routing on a switch and disables RPF check
* Configures Quagga with OSPF
  * Templates /etc/quagga/zebra.conf with basic configuration and ACLs, prefix-lists, route_maps
  * Templates /etc/quagga/ospfd.conf with OSPF configuration

## Usage
* Install Ansible >= 2.0 on a management server
* Clone this repository
* Set your SSH usernames in `deploy_network.yml`
* Modify config in `group_vars/all` if required
* Run the play with `ansible-playbook deploy_network.yml`
