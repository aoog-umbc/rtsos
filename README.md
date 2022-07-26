The following are instructions to compile and run the atmospheric correction look-up-tables on the Poseidon High-Performance Computer. The instructions are adapted from what was delivered by Pengwang Zhai and modified to run on Poseidon.



This radiative transfer package includes the PACE Simulator, a new aerosol scattering matrix package, a new wrapper for calculating the aerosol reflectance table for atmospheric correction, and several scripts that help manage the workloads.



Section 1: Compiling

Compile the package, configure the input files, and run the code with the executable file.

To compile, open a terminal and go to:



Step 1: Setup the environment

1)

In the compile directory, change the following in Makefile

DIRCore is the path for the core Fortran scripts

DIRCore=../src/core/



DIRMain is the path for the main monochromatic Fortran program

DIRMain=../src/main_program_monochromatic/



2)

In the compile directory,  change the following in makefile_GSFC_AC_LUT

HDF5DIR = /mnt/beegfs/poseidon/hpc/ocssw-develop/opt

HDF5LIB=-I$(HDF5DIR)/include/shared/

H5FC=$(HDF5DIR)/bin/h5fc

LIBSHDF= $(HDF5LIB) -L$(HDF5DIR)/lib/ -lhdf5 -lhdf5_fortran



DIRCore=../src/core/

DIRMain=../src/AC_Aerosols_LUT/

Step 2: Compile

If the environment has been setup correctly, then you can compile:



$ cd compile

$ make



If it compiles without issues, then we can compile the PACE simulator 

$ make -f makefile_PACE_Simulator_DoubleK



Then compile the aerosol LUT code

$ make -f makefile_GSFC_AC_LUT



Then compile the aerosol LUT code

$ make -f makefile_aerosol_phmx_cal



	Step 2: Run tables



	Here we will generate RT input files and run the RT code on Poseidon as well as generate outputs for each sensor.

We will use MODIS Aqua as an example:



$ cd lut-gen

$ vi MODIS_MIE_DIR.txt

add the path to the Mie tables here: ../share/RT/pwzrt/Mie_Database/MODIS_Mie_Database

$ vi auxiliary_directory

Add in this file the path to Data

../share/RT/pwzrt/Data

$ vi gas_absorption_coeff_dir

Add in this file the path to gas absorption tables

../share/RT/pwzrt/Gas_Absorption_Coefficients

To generate RT input files for a sensor:

$python rt_GSFC_LUT_pre.py

Select instrument: instrument_label=?, enter 1 for OCI, 2 for MODIS, 3 for SeaWifs, 4 for MISR: 

Enter 2 for MODIS



Now the Python script will create RT input files inside the lut-gen directory inside MODISa.



Then check run_luts.py to ensure the instrument label is setup correctly for MODISa, which is 2.



To run the slurm job, type the following:



$ sbatch run_luts.sbatch


