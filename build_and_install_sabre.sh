#!/bin/bash

# This scripts builds all components of Sabre.

# Build Firecracker with Sabre:
#   - main instructions: https://github.com/barabanshek/firecracker/tree/sabre/sabre .
pushd firecracker/
docker pull barabanshik/firecrackder_sabre_devctr:latest
tools/devtool build --release --libc gnu

FIRECRACKER_PATH=$(pwd)

popd

# Build firecracker-containerd with Sabre:
#   - main instructions: https://github.com/barabanshek/firecracker-containerd/tree/sabre/sabre .
# 
# Due to a weird bug: https://github.com/barabanshek/sabre/issues/1, we clone the repo separately
# outside of this folder.
pushd ~/
git clone https://github.com/barabanshek/firecracker-containerd.git
cd firecracker-containerd/
git fetch origin sabre; git checkout sabre
cd sabre/
./install_contrainerd.sh
./configure_node_for_containerd.sh ${FIRECRACKER_PATH}
./configure_node_for_containerd.sh ${FIRECRACKER_PATH} # need to run twice due to a bug

popd

# Setup node to run Firecracker with Sabre.
#   - main instructions: https://github.com/barabanshek/firecracker/tree/sabre/sabre .
pushd firecracker/sabre/scripts/
sudo ./setup_node.sh 1700000
popd
