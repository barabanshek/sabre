# Artifacts for Sabre

This repository contains all 5 dependent repositories for artifacts for the paper ["Sabre: Improving Memory Prefetching in Serverless MicroVMs with Near-Memory Hardware-Accelerated Compression"]() alongside with the instructions to reproduce our results.

We also put all Serverless benchmarks used for the end-to-end evaluation. They are adopted from [serverless-faas-workbench](https://github.com/ddps-lab/serverless-faas-workbench), [SeBS](https://github.com/spcl/serverless-benchmarks), and [vSwarm](https://github.com/vhive-serverless/vSwarm).

## Structure of the artifacts

The projects involves 5 sub-projects described in the table bellow.

| sub-repo | Description |
| --- | --- |
| [IAA_benchmarking](https://github.com/barabanshek/IAA_benchmarking) | A set of our benchmarks to understand the performance implications of IAA (de)compression hardware on page compression and restoration. |
| [Firecracker](https://github.com/barabanshek/firecracker/) | Sabre plugin for Firecracker microVMs. [README](https://github.com/barabanshek/firecracker/tree/sabre/sabre), [Full Diff](https://github.com/barabanshek/firecracker/compare/532677328480b7f4149192ec121ac076451ac098...sabre) |
| [firecracker-containerd](https://github.com/barabanshek/firecracker-containerd/) | firecracker-continerd with exposed Sabre API [README](https://github.com/barabanshek/firecracker-containerd/tree/sabre/sabre), [Full Diff](https://github.com/barabanshek/firecracker-containerd/compare/6b2d23241ad47456283917c5f3a15638cbd66027...sabre) |
| [firecracker-go-sdk](https://github.com/barabanshek/firecracker-go-sdk) | firecracker-go-sdk with exposed Sabre API. [Full Diff](https://github.com/barabanshek/firecracker-go-sdk/compare/1f800728632d4e45a384080a51676c5a43665ffd..sabre) |
| [vHive](https://github.com/barabanshek/vHive) | Our clone of [vHive](https://dl.acm.org/doi/10.1145/3445814.3446714) project with exposed Sabre API. [README](https://github.com/barabanshek/vHive/tree/sabre/sabre), [Full Diff](https://github.com/barabanshek/vHive/compare/5143a83ba38f9e6a644fe5d64110cdb75f63d82d...sabre) |

Each project contains the corresponding `README` with **detailed** instructions on how to build, install, test, and use each component. Please refer to these instructions for hacking.

The next of this documentation describes the high-level and minimal instructions to reproduce results reported in our paper.

First, clone this repo:
```
git clone --recursive https://github.com/barabanshek/sabre.git
```

## Reproducing IAA benchmarks

This reproduces **Figure 2, 3, 4, 5, 6, 7** from our paper.

```
cd IAA_benchmarking/
```

To reproduce, please, follow [Instructions](https://github.com/barabanshek/IAA_benchmarking?tab=readme-ov-file#run-with-docker) on running our IAA benchmarks in the prepared docker container. Please, use the frequency of 1.7 GHz as per paper (`./prepare_machine.sh 1700000`). This is the maximum supported frequency of our experimental Sapphire Rappids node.

## Reproducing Firecracker snapshotting results

### Build, install, and test the environment

Build Firecracker with Sabre and firecracker-containerd with Sabre API; install all; prepare IAA hardware.
```
./build_and_install_sabre.sh

# Export some env vars.
source env.sh
```

Test Sabre. All tests should pass.
```
sudo -E ./firecracker/build/sabre/memory_restorator_test
```

Test Firecracker + firecracker-containerd. The test will run the standard `docker.io/library/hello-world` image inside firecracker, if it does - all works!
```
# In another window, execute:
sudo firecracker-containerd --config /etc/firecracker-containerd/config.toml

# In main window, run tests:
sudo firecracker-ctr --address /run/firecracker-containerd/containerd.sock image pull --snapshotter devmapper docker.io/library/hello-world:latest
sudo firecracker-ctr --address /run/firecracker-containerd/containerd.sock run --snapshotter devmapper --runtime aws.firecracker --rm --tty --net-host docker.io/library/hello-world:latest test
```

Run `Hello, World` tests with end-to-end Serverless images in firecracker-containerd with Sabre. The test will run the standard `docker.io/library/hello-world` image inside firecracker using vHive Serverless infrastructure and do test snapshotting.
```
pushd vHive/sabre

# Simple uVM start-stop test
sudo env "PATH=$PATH" go run hello_world.go -image=docker.io/library/hello-world:latest -memsize=256 -example=start-stop

# Diff snapshotting with Sabre
sudo env "PATH=$PATH" go run hello_world.go -image=docker.io/library/hello-world:latest -memsize=256 -example=start-sabre-diff-snapshot-stop-resume-stop

# Check the Sabre snapshot file (`mem_file.snapshot` size should be MUCH less than uVM's memsize size)
ls -sh /fccd/snapshots/myrev-4/*
```

If all works well, we can now run the benchmarks!

### Reproducing characterization of Sabre

This reproduces **Figure 9** from our paper.
```
# Make sure you installed the IAA benchmark earlier as we use datasets from there
export SABRE_DATASET_PATH=IAA_benchmarking/dataset/snapshots_tmp
export SABRE_DATASET_NAME=pythongrpc

# Run benchmark (at least <N> = 3 times for best results)
sudo -E ./firecracker/build/sabre/memory_restoration_micro --benchmark_repetitions=<N> --benchmark_min_time=1x --benchmark_format=csv --logtostderr | tee results.csv

# Plot results
python3 firecracker/sabre/scripts/plot_microbenchmark.py results.csv
```

### Reproducing end-to-end experiments

This allows to (manually) reproduce end-to-end cold start of Serverless functions for **Figure 11 and 12**.

```
# Prepare environment for end-to-end Serverless experiments.
./prepare_end_to_end_env.sh

# Export required env variables.
source env.sh

# In a separate window: start firecracker-containerd.
sudo firecracker-containerd --config /etc/firecracker-containerd/config.toml

#
# Running a single end-to-end benchmark (e.g. image_processing).
#

# Build the benchmark and push into local registry (which should have been set-up
# with `prepare_end_to_end_env.sh` script).
cd benchmarks/image_processing
docker build -t localhost:5000/image_processing .
docker push localhost:5000/image_processing

# Run default Diff snapshotting with on-demand paging.
sudo -E env "PATH=$PATH" go run vHive/sabre/run_end2end.go -image=127.0.0.1:5000/image_processing:latest -memsize=256
# Check size of the snapshot.
ls -sh /fccd/snapshots/myrev-4/mem_file

# Run Diff snapshotting with Sabre page prefetching.
TODO
```
