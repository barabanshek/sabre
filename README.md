# Artifacts for Sabre

This repository contains all 5 dependent repositories for artifacts for the paper ["Sabre: Improving Memory Prefetching in Serverless MicroVMs with Near-Memory Hardware-Accelerated Compression"]() alongside with the instructions to reproduce our results.

We also put all Serverless benchmarks used for the end-to-end evaluation. They are adopted from [serverless-faas-workbench](https://github.com/ddps-lab/serverless-faas-workbench), [SeBS](https://github.com/spcl/serverless-benchmarks), and [vSwarm](https://github.com/vhive-serverless/vSwarm).

## Structure of the artifacts

The projects involves 5 sub-projects described in the table bellow.

| sub-repo | Description |
| --- | --- |
| [IAA_benchmarking](https://github.com/barabanshek/IAA_benchmarking) | A set of our benchmarks to understand performance implications of IAA (de)compression hardware on page compression and restoration. |
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

## What machine to use

Firecracker, firecracker-containerd, vHive, and all the infrastructure run on any x86/64 machine with Ubuntu 22.04 or higher. However, the Sabre plugin is based on Intel IAA technology and requires at least the 4th Gen Intel Xeon Scalable processor (Sapphire Rapids - SPR). Note that not any SPR machine (as of Feb 2024) comes with the IAA hardware, and the exact configuration depends on the SKU. In theory, any IAA-enabled SPR machine should run Sabre with potentially varying performance.

**CAUTION:** The host kernel support for IAA hardware is still under active development; as of *Ubuntu 23.10*, the driver and kernel stack still has unsolved issues preventing using IAA hardware (e.g. [IOMMU](https://lore.kernel.org/lkml/c67754fc-9fff-43b4-82ce-078e71134815@linux.intel.com/T/) issue). If your node runs *Ubuntu 22.04 - Ubuntu 23.10*, please, manually update the host kernel to *6.8.2* which we tested to work with IAA. We expect all changes to finally converge in the next release.

**CAUTION** If you use your own SPR node, make sure the system (BIOS, kernel boot args, etc.) is configured as per [Intel Analytics Accelerator User Guide](https://cdrdv2-public.intel.com/780887/354834_IAA_UserGuide_June23.pdf).

For artifact evaluation, we welcome reviewers to use our instance of an SPR node which runs the correct patched OS, BIOS, and other settings. This will allow to reliably reproduce our results.

## Preparing machine
- install docker, make sure your user is added in the docker group;
- install `idxd-config` system-wide as instructed [here](https://github.com/intel/idxd-config).

### Caution

Depending on the IAA hardware configuration in your SKU, you might want to consider adjusting the `accel-config config-wq ...` line in [configure_iaa_user.sh] accordingly.

## Reproducing IAA benchmarks

This reproduces **Figure 2, 3, 4, 5, 6, 7** from our paper.

```
cd IAA_benchmarking/
```

To reproduce, please, follow [Instructions](https://github.com/barabanshek/IAA_benchmarking?tab=readme-ov-file#run-with-docker) on running our IAA benchmarks in the prepared docker container. Please, use the CPU frequency of `1.7 GHz` as per paper (`./prepare_machine.sh 1700000`) and use the [same hardware configuration](https://github.com/barabanshek/IAA_benchmarking?tab=readme-ov-file#appendix-configuration-used-for-the-paper). We use `1.7 GHz` as the highest possible frequency of our experimental node; if you have a faster SPR node, feel free to re-run the benchmarks on them. Note that this is the CPU frequency, and it **does NOT affect** the performance of IAA.

## Reproducing Firecracker snapshotting results

### Build, install, and test the environment

Build Firecracker with Sabre and firecracker-containerd with Sabre API; install all; prepare IAA hardware.
```
# Run on a fresh machine.
./build_and_install_sabre.sh

# Run after every reboot.
./prepare_end_to_end_env.sh

# Export some env vars.
source env.sh
```

After reboot, only `./prepare_end_to_end_env.sh` needs to be executed. In a new session, `source env.sh` needs to be invoked. For convenience, you can add both scripts in your `bash_profile`.

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
# In a separate window: start firecracker-containerd.
sudo firecracker-containerd --config /etc/firecracker-containerd/config.toml

# In main window:
pushd vHive/sabre

# Simple uVM start-stop test
sudo env "PATH=$PATH" go run hello_world.go -image=docker.io/library/hello-world:latest -memsize=256 -example=start-stop

# Diff snapshotting with Sabre
sudo env "PATH=$PATH" go run hello_world.go -image=docker.io/library/hello-world:latest -memsize=256 -example=start-sabre-diff-snapshot-stop-resume-stop
# Check the Sabre snapshot file (`mem_file.snapshot` size should be MUCH less than uVM's memsize size)
ls -sh /fccd/snapshots/myrev-4/*

# REAP snapshots
sudo env "PATH=$PATH" ./hello_world -image=docker.io/library/hello-world:latest -memsize=256 -example=start-snapshot-stop-resume-record-stop-replay-stop
# WS files can be found in the same dir (mem_file.ws.partitions, mem_file.ws.snapshot);
# in this example, they are small as we don't really record much in the hello_world image.
ls -sh /fccd/snapshots/myrev-4/*

# REAP snapshots with Sabre
sudo env "PATH=$PATH" ./hello_world -image=docker.io/library/hello-world:latest -memsize=256 -example=start-snapshot-stop-resume-record-stop-replay-stop-sabre
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

This allows to (manually) reproduce compresison ratio, prefetching speed-up, and end-to-end cold start impact of Serverless functions for **Figure 11, 12, and Table 2**.

#### First, build benchmarks and push them into the local registry.
```
pushd benchmarks/python_list/
docker build -t localhost:5000/python_list .
docker push localhost:5000/python_list
popd

# ... or for `cnn_image_classification`
pushd benchmarks/cnn_image_classification/
docker build -t localhost:5000/cnn_image_classification .
docker push localhost:5000/cnn_image_classification
popd

# ... or do the same for any other benchmark you want...
```

#### Then, start firecracker-containerd (in a separate window)
```
sudo firecracker-containerd --config /etc/firecracker-containerd/config.toml 2>&1 | tee vm.log
```

#### Run Diff and Diff-Compressed snapshots (**Figure 11**).
```
pushd vHive/sabre/

# Clean things which might have been left after previous runs.
sudo ./../../clean_up.sh

# Run default Diff snapshotting with on-demand paging
sudo -E env "PATH=$PATH" go run run_end2end.go -image=127.0.0.1:5000/python_list:latest -invoke_cmd='python_list' -snapshot='Diff' -memsize=512

# Run Diff snapshotting with Sabre compression and page prefetching.
sudo -E env "PATH=$PATH" go run run_end2end.go -image=127.0.0.1:5000/python_list:latest -invoke_cmd='python_list' -snapshot='DiffCompressed' -memsize=512

# ... or same for something real like `cnn_image_classification`
sudo -E env "PATH=$PATH" go run run_end2end.go -image=127.0.0.1:5000/cnn_image_classification:latest -invoke_cmd='cnn_image_classification' -snapshot='Diff' -memsize=512
sudo -E env "PATH=$PATH" go run run_end2end.go -image=127.0.0.1:5000/cnn_image_classification:latest -invoke_cmd='cnn_image_classification' -snapshot='DiffCompressed' -memsize=512

# Run any other benchmark in a similar way:
#   - refer to [README.md](benchmarks/README.md) to match benchmark names;
#   - refer to the [invoker](vHive/sabre/invoke.sh) to see invocation commands.
```

Finding results:

- Size of default Diff snapshots is here: `ls -sh /fccd/snapshots/myrev-4/mem_file`;
- Size of Sabre compressed Diff snapshots is here: `ls -sh /fccd/snapshots/myrev-4/mem_file.snapshot`;
- VM start and cold start latencies will be printed after each run in red color.

#### Run REAP and REAP-Compressed snapshots (**Figure 12, and Table 2**).
```
# Clean things which might have been left after previous runs.
sudo ./../../clean_up.sh

# Run baseline REAP snapshotting.
sudo -E env "PATH=$PATH" go run run_reap_end2end.go -image=127.0.0.1:5000/python_list:latest -invoke_cmd='python_list' -snapshot='reap' -memsize=512

# Run REAP snapshotting with Sabre compression.
sudo -E env "PATH=$PATH" go run run_reap_end2end.go -image=127.0.0.1:5000/python_list:latest -invoke_cmd='python_list' -snapshot='reapCompressed' -memsize=512

# ... or same for something real like `cnn_image_classification`
sudo -E env "PATH=$PATH" go run run_reap_end2end.go -image=127.0.0.1:5000/cnn_image_classification:latest -invoke_cmd='cnn_image_classification' -snapshot='reap' -memsize=1024
sudo -E env "PATH=$PATH" go run run_reap_end2end.go -image=127.0.0.1:5000/cnn_image_classification:latest -invoke_cmd='cnn_image_classification' -snapshot='reapCompressed' -memsize=1024

# Run any other benchmark in a similar way:
#   - refer to [README.md](benchmarks/README.md) to match benchmark names;
#   - refer to the [invoker](vHive/sabre/invoke_reap.sh) to see invocation commands.
```

Finding results:
- To check the original and compressed snapshot size, look at vm.log: `cat vm.log | grep 'compressed size'`
    - x1 ratio means no compression was used (default REAP run);
- To check the time for memory prefetching (and speed-up over REAP with no compression), look at vm.log: `cat vm.log | grep 'Memory restoration, took'`;
- VM start and cold start latencies will be printed after each run in red color.
