#!/bin/bash

# This scriptsprepares all components needed to run Sabre with all dependencies.
# Run it after build_and_install.sh or after a reboot.

# Configs:
CPU_FREQ=1700000
CONTAINER_SUBNET="172.16.0.1" # this must match the uVM IP address selection in vHive/networking/networkconfig.go

# Clean-up previous stuff
docker rm -v $(docker ps --filter status=exited -q)

# Setup local docker registry
docker run -d -p 5000:5000 --name registry registry:2.7

# Get hello-world image (used for warming-up environment) and put it in the local registry
docker run hello-world
IMG_ID=`docker image ls | grep hello-world | awk '{ print $3 }'`
docker tag ${IMG_ID} localhost:5000/hello_world:latest
docker push localhost:5000/hello_world:latest

# Setup node to run Firecracker with Sabre.
#   - main instructions: https://github.com/barabanshek/firecracker/tree/sabre/sabre .
pushd firecracker/sabre/scripts/
sudo ./setup_node.sh ${CPU_FREQ}
popd

# Setup firecracker-containerd node.
#   - main instructions: https://github.com/barabanshek/firecracker-containerd/tree/sabre/sabre .
FIRECRACKER_PATH=$(pwd)/firecracker

pushd ~/firecracker-containerd/sabre/
./configure_node_for_containerd.sh ${FIRECRACKER_PATH}
./configure_node_for_containerd.sh ${FIRECRACKER_PATH}

popd

# Make a tap device.
TAP_DEV="tap0"
TAP_IP=${CONTAINER_SUBNET}
MASK_SHORT="/30"

# Setup network interface
sudo ip link del "$TAP_DEV" 2> /dev/null || true
sudo ip tuntap add dev "$TAP_DEV" mode tap
sudo ip addr add "${TAP_IP}${MASK_SHORT}" dev "$TAP_DEV"
sudo ip link set dev "$TAP_DEV" up

# Enable ip forwarding
sudo sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"

# Set up microVM internet access
sudo iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE || true
sudo iptables -D FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT \
    || true
sudo iptables -D FORWARD -i tap0 -o eth0 -j ACCEPT || true
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables -I FORWARD 1 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
sudo iptables -I FORWARD 1 -i tap0 -o eth0 -j ACCEPT
