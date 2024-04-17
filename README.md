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
# Prepare environment.
./prepare_end_to_end_env.sh

# In a separate window: start firecracker-containerd.
sudo firecracker-containerd --config /etc/firecracker-containerd/config.toml

# Add go to PATH if needed.
export GO_VERSION='1.21'
export PATH=/usr/lib/go-${GO_VERSION}/bin:$PATH

#
# Running a single end-to-end benchmark (e.g. image_processing)
#
# Build the benchmark and push into local registry.
cd benchmarks/image_processing
docker build -t localhost:5000/image_processing .
docker push localhost:5000/image_processing

# Run default Diff snapshotting with on-demand paging.
# Go to vHive/sabre folder;
sudo -E env "PATH=$PATH" go run run_end2end.go -image=127.0.0.1:5000/image_processing:latest -memsize=256

# Run Diff snapshotting with Sabre page prefetching.
TODO
```
