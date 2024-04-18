#!/bin/bash

# Clean-up previous stuff
docker rm -v $(docker ps --filter status=exited -q)

# Setup local docker registry
docker run -d -p 5000:5000 --name registry registry:2.7

# Get hello-world image (used for warming-up environment) and put it in the local registry
docker run hello-world
IMG_ID=`docker image ls | grep hello-world | awk '{ print $3 }'`
docker tag ${IMG_ID} localhost:5000/hello_world:latest
docker push localhost:5000/hello_world:latest

# Install grpc_cli
rm -fr grpc/
git clone https://github.com/grpc/grpc.git
pushd grpc/
git submodule update --init
mkdir -p cmake/build; cd cmake/build
cmake -DgRPC_BUILD_TESTS=ON ../..
make grpc_cli
popd
