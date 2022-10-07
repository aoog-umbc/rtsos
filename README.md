# Atmospheric Correction (AC) Look Up Tables (LUT)

The following are instructions to compile and run the atmospheric correction
look-up-tables on the Poseidon High-Performance Computer. The instructions are
adapted from what was delivered by Pengwang Zhai and modified to run on
Poseidon.

This radiative transfer package includes the PACE Simulator, a new aerosol
scattering matrix package, a new wrapper for calculating the aerosol reflectance
table for atmospheric correction, and several scripts that help manage the
workloads.

In the following sections we will compile the software, configure the input
files, and run the code with the executable file.

## Compile

> What follows works on the OEL's Poseidon HPC at GSFC. A more general
> `CMakeLists.txt` is needed for other platforms, primarily to handle the HDF5
> dependency.

Configure your preferred intall location by editing the `CMakeLists.txt`
file where indicated. The default is to put the binaries on a path in a Python
virutal environment.

To compile, open a terminal and change to the project root directory, which
contains "CMakeLists.txt". Thence ...

```
$ mkdir build
$ cd build
$ cmake ../
-- The Fortran compiler identification is GNU 8.5.0
-- Detecting Fortran compiler ABI info
-- Detecting Fortran compiler ABI info - done
-- Check for working Fortran compiler: /usr/bin/f95 - skipped
-- Checking whether /usr/bin/f95 supports Fortran 90
-- Checking whether /usr/bin/f95 supports Fortran 90 - yes
-- Configuring done
-- Generating done
-- Build files have been written to: /home/icarroll/projects/nngc/zhai_rt/build2
$ make
...
$ make install
```

## Generate Configuration Files

Here we will generate RT input files and run the RT code on Poseidon as well as
generate outputs for each sensor.

We will use MODIS Aqua as an example.

You need to have the `RT` data available at `<PATH>` in the examples below.
Then within the `lut-gen` folder, ensure the following file contents:

- Mie database for MODIS
  ```
  $ cat lut-gen/MODIS_MIE_DIR.txt
  <PATH>/RT/pwzrt/Mie_Database/MODIS_Mie_Database
  ```
- pwzrt data
  ```
  $ cat lut-gen/auxiliary_directory
  <PATH>/RT/pwzrt/Data/
  ```
- gas absorption tables
  ```
  $ cat lut-gen/gas_absorption_coeff_dir
  <PATH>/RT/pwzrt/Gas_Absorption_Coefficients/
  ```

To generate RT input files for a sensor, run the `rt_GSFC_LUT_pre.py` script.

```
$ cd lut-gen
$ python rt_GSFC_LUT_pre.py
instrument_label=?, enter 1 for OCI, 2 for MODIS, 3 for SeaWifs, 4 for MISR:
```

Enter 2 for MODIS

The Python script will create RT input files inside the `lut-gen/MODISa`
directory.

Then check run_luts.py to ensure the instrument label is setup correctly for
MODISa, which is 2.

## Calculate LUTs

Run the slurm job:

```
$ sbatch run_luts.sbatch
```
