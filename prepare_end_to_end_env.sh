#!/bin/bash

# Setup local docker registry
docker run -d -p 5000:5000 --name registry registry:2.7

# Get hello-world image (used for warming-up environment) and put it in the local registry
docker run hello-world
IMG_ID=`docker image ls | grep hello_world | awk '{ print $3 }'`
docker tag ${IMG_ID} localhost:5000/hello_world:latest
docker push localhost:5000/hello_world:latest

# Install grpc_cli
git clone https://github.com/grpc/grpc.git
git submodule update --init
mkdir -p cmake/build; cd cd cmake/build
cmake -DgRPC_BUILD_TESTS=ON ../..
make grpc_cli