#!/bin/bash

# To enablle these features:
# 1. Compile the linux kernel with CAn support
# 2. Compile the appropriate driver for your CAN devide
# 3. emerge -av sys-apps/iproute2

# For PEAK PCAN-USB Pro FD High-Speed CAN
# Plug in the red cable first for can0 and can1 (FD-CAN, HS-CAN1)
# Plug in the black cable second for can2 and can3 (HS-CAN2, HS-CAN3)
# Plug in the purple cable third for can4 and can5 (HS-CAN4, MS-CAN)

# For systems running the PEAK API Linux driver, unload the driver to get
# access to the userspace USB interfaces
rmmod pcan
modprobe peak_usb

# can0 - FD-CAN, ISO CAN FD frame format is the default
echo "FD-CAN on can0"
ip link set can0 type can restart-ms 100 bitrate 500000 sample-point 0.800 dbitrate 2000000 dsample-point 0.800 fd on

# HS-CAN1
echo "HS-CAN1 on can1"
ip link set can1 type can restart-ms 100 bitrate 500000 sample-point 0.800 dbitrate 2000000 dsample-point 0.800 fd on

# HS-CAN2
echo "HS-CAN2 on can2"
ip link set can2 type can restart-ms 100 bitrate 500000 sample-point 0.800 dbitrate 2000000 dsample-point 0.800 fd on

# HS-CAN3 - This interface is NOT CAN FD, but the car complains unless we connect with the FD settings
echo "HS-CAN3 on can3"
ip link set can3 type can restart-ms 100 bitrate 500000 sample-point 0.800 dbitrate 2000000 dsample-point 0.800 fd on

# HS-CAN4
echo "HS-CAN4 on can4"
ip link set can4 type can restart-ms 100 bitrate 500000 triple-sampling on

# MS-CAN
echo "MS-CAN on can5"
ip link set can5 type can restart-ms 100 bitrate 125000 triple-sampling on

ifconfig can0 up
ifconfig can1 up
ifconfig can2 up
ifconfig can3 up
ifconfig can4 up
ifconfig can5 up

# Optional - trying to make sure we get all data in a FD-CAN message
ifconfig can0 txqueuelen 1024
ifconfig can1 txqueuelen 1024
ifconfig can2 txqueuelen 1024
ifconfig can3 txqueuelen 1024
ifconfig can4 txqueuelen 1024
ifconfig can5 txqueuelen 1024
