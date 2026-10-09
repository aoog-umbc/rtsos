<!--
RTSOS — Radiative Transfer model based on Successive Orders of Scattering
Copyright © 2025 Pengwang Zhai.

Licensed under the Creative Commons Attribution–NonCommercial 4.0
International License (CC BY-NC 4.0).
You may use, modify, and share this code for research and
educational purposes with proper attribution.
Commercial use requires written permission from the author.

Full license: https://creativecommons.org/licenses/by-nc/4.0/
Contact: Pengwang Zhai  |  [pwzhai@gmail.com]
-->

# Radiative Transfer model based on Successive Orders of Scattering (RTSOS)

RTSOS can solve the multiple scattering radiative transfer equation from UV, visible, to
infrared. It can handle atmosphere-land or atmosphere-ocean coupled systems. The
atmosphere can be a mixture of molecules, aerosols, and cloud droplets. The land bottom
can be Lambertian, snow surface, Ross-Li, and a number of other surfaces. The ocean
waters are modeled by a mixture of pure ocean water, phytoplankton, and colored
dissolved organic matter (CDOM), and other hydrosols. The sensors can be placed at
arbitrary levels in the Earth system. The output of the sensor can include the full
polarized Stokes parameters (I, Q, U, V). For more information, see
[References](#references) at the end of this document.

PACE simulator is a wrapper built around the monochromatic RTSOS, which has a list of
built-in aerosol and ocean inherent optical properties. A publication on the PACE
simulator is published on Frontiers in Remote Sensing (Zhai et al., 2022). 

GSFC AC LUT is a wrapper built around the monochromatic RTSOS which builds look up
tables for atmospheric correction for retrievals of surface reflectance from
top-of-atmosphere measurements.

## 1. Installation

The software is distributed as source code, so the programs must be built locally. There
are two options for building:
- use `cmake` to build and install the binary RTSOS executables
- use `pip` to build and install the binary RTSOS executables along with their Python
   wrappers

### 1.1A First Option

The software is configured for building with `cmake` on a system with the following
prerequistes available:

- [CMake] >= 3.31
- [HDF5] >= 1.10
- [LAPACK] >= 3.9
- a modern [Fortran] compiler (e.g. gfortran)

One option for installing these prerequistes is through [Conda], which is described in
[section 1.1B](#11b-second-option), but installation with a system package manager is
also suitable.

#### Get the Source Code

You can retrieve the [latest release] by downloading the `.zip` or `.tar.gz` assets from
GitHub. Alternatively, to retrieve the development version, use `git`:

```shell
git clone --filter=blob:none https://github.com/aoog-umbc/rtsos
```

#### Build and Install

Open a Terminal with the working directory at the project root (i.e. where this
README.md is located). Choose an unused name for the RTSOS build directory, and
optionally an existing installation prefix, and call `cmake`. For example, to use a
folder named "build" for the build files and the `.local` folder within your home
directory as the prefix for installation:

```shell
$ cmake -B build --install-prefix ~/.local
```

The `--install-prefix` argument is optional. Now change to the build directory and run
cmake twice more, first with `--build` and then with `--install`.

```shell
$ cd build
$ cmake --build .
$ cmake --install .
```

CMake will display the locations of the binary executables installed. If CMake cannot
find the prerequisties, you can provide an environment variable with the prefix, e.g.
`export HDF5_ROOT=...`. The prefix is the path up to the folder containing the "lib"
folder with the HDF5 libraries.

### 1.1B Second Option

The software is configured for building with `pip` on a system with the following
prerequistes available:

- [Python] >= 3.11
- [HDF5] >= 1.10
- [LAPACK] >= 3.9
- a modern [Fortran] compiler (e.g. gfortran)

The installer `pip` calls the Python wrapper's build-system, `scikit-build-core`, which
also uses `cmake` to compile the source code. Those tools are fetched by `pip` as
needed.

One option for installing the prerequistes is through [Conda], which is our recommended
approach for preparing a Python environment for use with the Python wrapper. Choose a
name for the Conda environment and create it with the required prerequistes. For
example, with "my-project" as the environment name:

```shell
$ conda create --yes --name my-project python hdf5 lapack
$ conda activate my-project
```

To install the [latest release] from PyPI:

```shell
(my-project) $ pip install rtsos
```

To install the development version from GitHub:

```shell
(my-project) $ pip install git+https://github.com/aoog-umbc/rtsos
```

If installation fails with the message `ERROR: Could not build wheels for rtsos...`,
then CMake may not have found the prerequisties. You can provide an environment variable
with their prefix, e.g. `export HDF5_ROOT=...`. The prefix is the path up to the folder
containing the "lib" folder with the HDF5 libraries.

### 1.2 Auxiliary Data

In addition to the software, simulating the PACE instruments and generating atmospheric
correction look-up tables requires a collection of data files available from a Zenodo
repository:

https://doi.org/10.5281/zenodo.17410093

The auxiliary data file is named as `RTSOS_data_v1.0_20251022.tar.gz`, which can be
extracted into a convenient location of your choice. You can extract the files by doing
the following in a Terminal with your chosen location as the working directory.

```shell
$ tar -zxf RTSOS_data_v1.0_20251022.tar.gz
```

You will get two directories. One is `Gas_Absorption_Coefficients`, which contains the
gas absorption cross section lookup table for H2O, O2, CH4, CO2, NO2, ozone. This lookup
table was generated by using ARTS: The [Atmospheric Radiative Transfer
Simulator](https://www.radiativetransfer.org) version 2.3 with
[HITRAN2020](https://hitran.org/media/refs/HITRAN-2020.pdf) database.

The other is `Data`, which contains the absorption coefficients of pure water, plankton
particles, the bidirectional reflectance distribution functions of snow surface,
scattering matrix of dust particles, the instrument response functions of ocean color
instrument, HARP2, and SPEXone, and a number of other data files used in the PACE
simulator.

## 2. Usage

The first or two ways to use RTSOS is with a single parameterization given to the binary
executables as a plain text file. You can do this regardless of the installation method
above; follow the procedures in [section 2.1A](#21a-binary-executables). The second way
to use RTSOS is with multiple parameterizations given to the Python wrapper in a single
NetCDF file. You can do this if you used the second installation option [section
1.1B](#11b-second-option); follow the procedures
in [section 2.1B](#21b-python-wrapper).

### 2.1A Binary Executables

For monochromatic simulation, users are referred to the documentation located at
"Documentation/Describtion_of_input_files/SOS_io.pdf" in the source code repository.

### 2.1A.1 PACE Simulator

#### Input Files 

The current version can conveniently generate synthetic datasets for OCI, HARP, and SPEX
for flexible atmospheric and ocean conditions given as parameters. To run the PACE
simulator from the binary executables, users should become familiar with the parameter
file formats. We provided two Python scripts to generate these input files, one for
ocean and the other for land surfaces, respectively, which are located in the
`test/PACE_Simulator/python_script/` folder of the source code repository:

- [pace_simulator_twolayer_inputfile_land.py](https://github.com/aoog-umbc/rtsos/blob/main/test/PACE_Simulator/python_script/pace_simulator_twolayer_inputfile_land.py)
- [pace_simulator_twolayer_inputfile_ocean.py](https://github.com/aoog-umbc/rtsos/blob/main/test/PACE_Simulator/python_script/pace_simulator_twolayer_inputfile_ocean.py)

For ocean simulations, ocean inherent optical properties are documented in Zhai et al.,
(2017, 2018, 2022).

Study each file before you execute them. Most importantly, set `aux_dir` to the path
ending in the `Data` folder and `gas_absorption_coeff_dir` to the path ending in the
`Gas_Absorption_Coefficients` folder.

####  Aerosol Models

The `Aerosol_Model[iaerosol]` value in the input file generator scripts is used in the
PACE simulator input file to specify the aerosol models.

In the Python script, `Aerosol_Model` is a array, and `iaerosol` specifies which one of
the aerosol models to use. In the following we use `IAEROSOL` as
`Aerosol_Model[iaerosol]` equivalently.

- The `IAEROSOL` values from 1-10 use the Shettle & Fenn (1979) model.
- The `IAEROSOL` values from 11-20 are the operational aerosol models currently used in
  the atmospheric correction at GSFC (Ahmad et al. 2010). The values span a range of
  fine mode fractions. When using these aerosol models, a value `irh` is also used to
  select relative humidity from the array `RH`.
- The `IAEROSOL` value of `-99` is reserved for the case that a user supplies aerosol
  and cloud phase matrices. See [section 2.2](#21a2-single-scattering-matrix-code) for
  more information.

#### Run the Simulator

Now you may try out the pace simulator. First generate an input file:

```shell
$ python pace_simulator_twolayer_inputfile_land.py
```

The script will write a parameter file with a long name, which we refer to here as
`input.txt`. Call the executable with the parameter file as the only argument.

```shell
$ rtsos_PACE_Simulator_DoubleK input.txt
```

### 2.1A.2 Single Scattering Matrix Code

If you set `IAEROSOL=-99` in the pace simulator input file, you will need to prepare the
aerosol phase matrix. A tool was written by Neranga K. Hannadige
(https://scholar.google.com/citations?user=0lAwqNsAAAAJ&hl=en) to generate the input
scattering matrix files for the pace simulator.

We provided a Python script to generate the input files in the
`test/PACE_Simulator/python_script/` folder of the source code repository:

- [Aerosol_PhaseMatrix_Cal_InputPre.py](https://github.com/aoog-umbc/rtsos/blob/main/test/PACE_Simulator/python_script/Aerosol_PhaseMatrix_Cal_InputPre.py)

In this script, you want to specify `aux_dir` as for the PACE simulator.

```shell
$ python Aerosol_PhaseMatrix_Cal_InputPre.py
```

The script will write a parameter file with a long name, which we refer to here as
`input.txt`. Call the executable with the parameter file as the only argument.

```shell
$ rtsos_Aerosol_Phmx_Cal input.txt
```

The output is an aerosol phase matrix that can be referenced in the parameter file for
the PACE simulator. To do so, set the `aerosol_phasematrix_file_hi` or the
`aerosol_phasematrix_file_low` to the files that are generated with the procedure shown
above.

The single scattering matrix simulation uses the Mie code developed by M. Mishchenko
(Scattering, absorption, and emission of light by small particles, MI Mishchenko, LD
Travis, AA Lacis - 2002)

A non spherical dust scattering matrix database is included, which was provided by Prof.
Ping Yang at Texas A&M University (Meng, Z., P. Yang, G. Kattawar, L. Bi, K. Liou, and
I. Laszlo, 2010: Single-scattering properties of tri-axial ellipsoidal mineral dust
aerosols: A database for application to radiative transfer calculations. J. Aerosol
Sci., 41, 501–512, https://doi.org/10.1016/j.jaerosci.2010.02.008.)

The single scattering matrix code assumes either bimodal (NMODE=2) or trimodal (NMODE=3)
size distribution, see the following structure:

```
----------------------------------------------------------------------
NMODE=2
----------------------------------------------------------------------
Available aerosol modes: 

	*fine mode 		(fmfrac)
		dust like 		(rf1)
		water soluble 	(rf2)
		BrC 			(rf3)
		soot			(1-(rf1+rf2+rf3))
	
	*coarse mode 	(1-fmfrac)
		sea salt		(cmsfrac)
		dust			(1-cmsfrac)
----------------------------------------------------------------------
NMODE=3
----------------------------------------------------------------------
Available aerosol modes:

	*fine mode		(fmfrac)
		water soluble 	(rf2)
		BrC 			(rf3)
		soot			(1-(rf2+rf3))

	*dust mode		(dustfrac)
		dust like		(dsfrac)
		dust			(1-dsfrac)

	*coarse mode 	(1-(fmfrac+dustfrac))
		coarse mode includes sea salt only
----------------------------------------------------------------------

*Note: Different sets of parameters are used for nmode=2 and nmode=3 
		For nmode=2 dustfrac and dsfrac do not exist
		For nmode=3 rf1 and cmsfrac do not exist
```

### 2.1B Python Wrapper

The Python wrapper adds the command line tools `rt-AC-LUT`, `rt-PACE`, and `rt-PHMX`,
which all accept the same command line arguments (see, for example `rt-PACE --help`).
These wrappers presently work by calling the binary executables `rtsos_GSFC_AC_LUT`,
`rtsos_PACE_Simulator_DoubleK`, and `rtsos_Aerosol_Phmx_Cal` which are included with the
install.

The Python wrapper adds the ability to run the programs over arrays of parameters
provided in NetCDF files.  To run the PACE simulator with default values, call
`rt-PACE` with two arguments giving, first, the path where default parameters will be
written and second, the path for outputs.

```shell
$ rt-PACE intputs.nc outputs.nc
```

To run the PACE simulator over non-default parameters, you must provide a suitable
NetCDF file.

1. Generate a template for the parameter sets over which you wish to run the
   PACE simulator.
   ```shell
   $ rt-PACE --pre defaults.nc
   ```
1. Using whatever tools you want, generate a new input dataset with the same variables
   as the default dataset. New dimensions are allowed, but every coordinate variable
   must be either scalar or one dimensional. Certain coordinates must be scalar, but
   which ones is not yet presently documented.
1. Choose to run on the outer-product of all parameterizations or of subsets (e.g. for
   parallel execution):
    - To run all parameterizations in one process, provide inputs and outputs file
      paths.
      ```shell
      $ rt-PACE inputs.nc outputs.nc
      ```
    - To run subsets of the parameterizations as separate jobs, add the `--cluster`
      argument to indicate dimensions and indices over which to slice the inputs.
      ```shell
      $ rt-PACE --cluster=RH:0,theta0:0-2 inputs.nc outputs.nc
      $ rt-PACE --cluster=RH:0,theta0:2-4 inputs.nc outputs.nc
      $ rt-PACE --cluster=RH:1,theta0:0-2 inputs.nc outputs.nc
      $ rt-PACE --cluster=RH:1,theta0:2-4 inputs.nc outputs.nc
      ```
      Note that instead of writing to `outputs.nc`, a tree is written under `outputs/`
      with results from each job. Once each jobs is complete, use the `--post` argument
      to combine existing outputs into a single file.
      ```shell
      $ rt-PACE --post=RH,theta0 intputs.nc outputs.nc
      ```

## References

Zhai, P., Hu, Y., Trepte, C. R., Lucker, P. L. (2009). A vector radiative transfer model
for coupled atmosphere and ocean systems based on successive order of scattering method.
Optics express, 17(4), 2057-2079.

Zhai, P., Hu, Y., Chowdhary, J., Trepte, C. R., Lucker, P. L., Josset, D. B. (2010). A
vector radiative transfer model for coupled atmosphere and ocean systems with a rough
interface. Journal of Quantitative Spectroscopy and Radiative Transfer, 111(7),
1025-1040.

Zhai, P., Hu, Y., Josset, D. B., Trepte, C. R., Lucker, P. L., Lin, B. (2013). Advanced
angular interpolation in the vector radiative transfer for coupled atmosphere and ocean
systems. Journal of Quantitative Spectroscopy and Radiative Transfer, 115, 19-27.

Zhai, P., Hu, Y., Winker, D. M., Franz, B., Boss, E. (2015). Contribution of Raman
scattering to polarized radiation field in ocean waters. Optics Express, 23(18),
23582-23596.

Zhai, P., Hu, Y., Winker, D. M., Franz, B., WERDELL, J., BOSS, E. (2017). Inelastic
vector radiative transfer solution in ocean waters. Optics Express, 25, A223-A239. 

Zhai, P., Boss, E., Franz, B., Werdell, J., Hu, Y. (2018). Radiative transfer modeling
of phytoplankton fluorescence quenching  processes. MDPI Remote Sensing, 10(8), 1039.

Zhai, P., Hu, Y. (2022). An improved pseudo spherical shell algorithm for vector
radiative transfer. Journal of Quantitative Spectroscopy and Radiative Transfer, 282,
108132. https://www.sciencedirect.com/science/article/pii/S0022407322000693.

Zhai, P., Gao, M., Franz, B. A., Werdell, P. J., Ibrahim, A., Hu, Y., Chowdhary, J.
(2022). A Radiative Transfer Simulator for PACE: Theory and Applications. Frontiers in
Remote Sensing, 3. https://www.frontiersin.org/article/10.3389/frsen.2022.840188.

E. P. Shettle and R. W. Fenn. (1979). “Models for the aerosols of the lower atmosphere
and the effects of humidity variations on their optical properties,” AFGL-TR 790214, U.
S. Air Force Laboratory, Hanscom Air Force Base, Mass..

Z. Ahmad, B. A. Franz, C. R. McClain, E. J. Kwiatkowska, J. P. Werdell, E. P. Shettle,
and B. N. Holben. 2010. "New aerosol models for the retrieval of aerosol optical
thickness and normalized water-leaving radiances from the SeaWiFS and MODIS sensors over
coastal regions and open oceans," Appl. Opt. 49, 5545-5560.

[CMake]: https://cmake.org/
[LAPACK]: https://www.netlib.org/lapack/
[Fortran]: https://fortran-lang.org/
[HDF5]: https://www.hdfgroup.org/solutions/hdf5/
[Python]: https://python.org
[latest release]: https://github.com/aoog-umbc/rtsos/releases/latest
[Conda]: https://conda.org/
