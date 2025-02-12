#!/bin/bash

KERNEL=kernel_2712
make bcm2712_defconfig

make -j6 Image.gz modules dtbs
