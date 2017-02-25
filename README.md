# mlnx-switchdev-altlinux
Alt Linux porting on Mellanox Spectrum with [mlxsw](https://github.com/Mellanox/mlxsw/wiki/Overview) switchdev driver


## Network topology
```
############# eth2    swp1 ############# swp3    eth2 #############
#           #--------------#    sw1    #--------------#           #
#  server3  # eth3    swp2 #           # swp3    eth2 #  server4  #
#           #--------------# switchdev #--------------#           #
#############              #############              #############
```
