#!/bin/bash

# This scripts builds all components needed to run Sabre with all dependencies.
# Run it on a fresh machine.

# Build Firecracker with Sabre:
#   - main instructions: https://github.com/barabanshek/firecracker/tree/sabre/sabre .
pushd firecracker/
docker pull barabanshik/firecrackder_sabre_devctr:latest
tools/devtool build --release --libc gnu

popd

# Build firecracker-containerd with Sabre:
#   - main instructions: https://github.com/barabanshek/firecracker-containerd/tree/sabre/sabre .
# 
# Due to a weird bug: https://github.com/barabanshek/sabre/issues/1, we clone the repo separately
# outside of this folder.
pushd ~/
rm -fr firecracker-containerd/; git clone https://github.com/barabanshek/firecracker-containerd.git
cd firecracker-containerd/
git fetch origin sabre; git checkout sabre
cd sabre/
./install_contrainerd.sh

popd

# Build and install grpc_cli.
rm -fr grpc/
git clone https://github.com/grpc/grpc.git
pushd grpc/
git submodule update --init
mkdir -p cmake/build; cd cmake/build
cmake -DgRPC_BUILD_TESTS=ON ../..
make grpc_cli -j

popd
