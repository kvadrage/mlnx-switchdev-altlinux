#!/bin/bash

POOL=./lnst_pools/bulldog1-2hosts/
RECIPE=$1

lnst-ctl -d --pools=$POOL run $RECIPE
