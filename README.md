# Artifacts for Sabre

This repository contains all 6 dependent repositories for artifacts for the paper ["Sabre: Improving Memory Prefetching in Serverless MicroVMs with Near-Memory Hardware-Accelerated Compression"]() alongside with the instructions to reproduce our results.

We also put all Serverless benchmarks used for the end-to-end evaluation. They are adopted from [serverless-faas-workbench](https://github.com/ddps-lab/serverless-faas-workbench), [SeBS](https://github.com/spcl/serverless-benchmarks), and [vSwarm](https://github.com/vhive-serverless/vSwarm).

## Structure of the artifacts

The projects involves 6 sub-projects described in the table ...

TODO

## Reproduction instructions

### Reproducing IAA benchamrks

### Reproducing characterization of Sabre

### Reproducing end-to-end experiments

```
# Setup local docker registry
docker run -d -p 5000:5000 --name registry registry:2.7

# Get hello-world image (used for warming-up environment) and put it in the local registry
docker run hello-world
IMG_ID=`docker image ls | grep hello_world | awk '{ print $3 }'`
docker tag ${IMG_ID} localhost:5000/hello_world:latest
docker push localhost:5000/hello_world:latest

# Install grpc_cli
git clone https://github.com/grpc/grpc.git
pushd grpc/
git submodule update --init
mkdir -p cmake/build; cd cd cmake/build
cmake -DgRPC_BUILD_TESTS=ON ../..
make grpc_cli
popd

# Make sure you have a lot of disk space available;
# Install all benchmarks into the local registry, this will take a while
./benchmarks/build_all_images.sh

# In a separate window: start firecracker-containerd
sudo firecracker-containerd --config /etc/firecracker-containerd/config.toml

#
# Go to vHive/sabre folder
#
# Test things on some default image first
sudo env "PATH=$PATH" go run hello_world.go -image=docker.io/library/hello-world:latest -memsize=256 -example=start-sabre-diff-snapshot-stop-resume-stop

# Finally, run some end-to-end benchmark
# Make sure go is in the PATH, for example:
export GO_VERSION='1.21'
export PATH=/usr/lib/go-${GO_VERSION}/bin:$PATH

sudo -E env "PATH=$PATH" go run run_end2end.go -image=127.0.0.1:5000/video_processing:latest -memsize=256
```
