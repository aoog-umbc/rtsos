# Radiative Transfer Simulations

The `zhai-rt` package implements radiative transfer simulations for the purpose
of creating look-up tables (LUTs) for atmospheric correction (AC) or simulating
datasets from existing or planned sensors (e.g. PACE).

This radiative transfer package includes the PACE Simulator, a new aerosol
scattering matrix package, a new wrapper for calculating the aerosol reflectance
table for atmospheric correction, and several scripts that help manage the
workloads.

The following instructions apply for users and developers working on the
Poseidon High-Performance Computing infrastructure.

## Installation

Presently, the package is source-only, which means that compilation will happen
locally during installation. Your system must have a developer tool chain that
includes a Fortran compiler and CMake.

The `zhai-rt` package depends on the HDF5 Fortran library and does not
automatically install this dependency. If not possible to install with your system
package manager, the HDF5 libraries can be installed by Miniconda with
`conda install hdf5` or by Homebrew with `brew install hdf5`. Both methods
include the Fortran library component at time of writing.

If the HDF5 Fortran library is already installed on a standard path, then
the following routine `pip` command should suffice:

```
pip install git+https://oceandata.sci.gsfc.nasa.gov/rcs/rt/zhai_rt.git
```

If the above command fails with `ERROR: Could not build wheels for zhair-rt...`
and the HDF5 Fortran libaries defintiely exist at a known path, then
try installing with the `HDF5_ROOT` variable set. For example, if using `conda`
on a *nix system, with `hdf5` added by Miniconda to the base environment, try

```
HDF5_ROOT=~/miniconda3 pip install git+https://oceandata.sci.gsfc.nasa.gov/rcs/rt/zhai_rt.git
```

## Auxilliary Data

RT simulations require auxilliary data that must be available at paths given in
the simulation parameter file. Typically you will have a directory, say `pwzrt`,
that is available from your project root with the following structure:

```
$ tree -L 1 data/RT/pwzrt/
data/RT/pwzrt/
├── Data
├── Gas_Absorption_Coefficients
└── Mie_Database
```

## Quickstart

The package adds two command line tools: `rt-AC-LUT` and `rt-PACE`, which
accept the same command line arguments (see, for example `rt-PACE --help`).

To run the PACE simulator over the parameters provided as defaults, only
provide input and output paths.
```
$ rt-PACE data/defaults.nc data/outputs.nc
```

To run the PACE simulator over non-default parameters, you must provide a
suitable NetCDF file.

1. Generate a template for the parameter sets over which you wish to run the
   PACE simulator.
   ```
   $ rt-PACE --pre data/defaults.nc
   ```
1. Using whatever tools you want, generate a new dataset (say `data/inputs.nc`)
   with the same variables as the template. New dimensions are allowed, but
   every coordinate variable must be either scalar or one dimensional.
1. Choose serial or parallel execution:
    - To run all parameterizations in one process, provide inputs and outputs file
      paths.
      ```
      $ rt-PACE data/inputs.nc data/outputs.nc
      ```
    - To run subsets of the parameterizations as separate jobs, add the
      `--cluster` argument to indicate dimensions and indices over which to
      slice the inputs.
      ```
      $ rt-PACE --cluster=RH:0,theta0:0:2 data/inputs.nc data/outputs.nc &
      $ rt-PACE --cluster=RH:0,theta0:2:4 data/inputs.nc data/outputs.nc &
      $ rt-PACE --cluster=RH:1,theta0:0:2 data/inputs.nc data/outputs.nc &
      $ rt-PACE --cluster=RH:1,theta0:2:4 data/inputs.nc data/outputs.nc &
      ```
      Note that instead of writing to `data/outputs.nc`, a tree is written under
      `data/outputs/` with results from each job. Once each jobs is complete, use
      the `--post` argument to combine existing outputs into a single file.
      ```
      $ rt-PACE --post --cluster=RH,theta0:0:4 data/intputs.nc data/outputs.nc
      ```

## Repository Orientation for Developers

The repository has three components.

1. The `src` folder and `CMakeLists.txt` file create the Fortran binaries that
   perform the RT simulations.
1. The `scripts` folder and the `pyproject.toml` and `setup.py` files provide
   a Python API for the Fortran binaries.
1. Everything else is documentation.

### Compile

The `zhai-rt` Python packaging uses `skbuild` following the `pip install ...`
invocation to compile the Fortran source. To compile the Fortran code manually,
open a terminal and change to the project root directory, which contains
"CMakeLists.txt". Thence ...

```
$ cmake -B build
-- The Fortran compiler identification is GNU 8.5.0
-- Detecting Fortran compiler ABI info
-- Detecting Fortran compiler ABI info - done
-- Check for working Fortran compiler: /usr/bin/f95 - skipped
-- Checking whether /usr/bin/f95 supports Fortran 90
-- Checking whether /usr/bin/f95 supports Fortran 90 - yes
-- HDF5 Fortran compiler wrapper is unable to compile a minimal HDF5 program.
-- Found HDF5: <HDF5_ROOT>/lib/libhdf5_fortran.so;<HDF5_ROOT>/lib/libhdf5.so (found version "1.10.6") found components: Fortran
-- Configuring done
-- Generating done
-- Build files have been written to: <PWD>build
$ cd build
$ cmake --build .
```

If `cmake -B build` does not succeed with `Could NOT find HDF5`, try calling with the
`HDF5_ROOT` variable as described in the [Installation](#installation) section above:

```
$ HDF5_ROOT=~/miniconda3/ cmake -B build
```
