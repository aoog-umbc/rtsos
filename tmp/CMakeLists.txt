cmake_minimum_required(VERSION 3.31)
project(${SKBUILD_PROJECT_NAME}
    LANGUAGES Fortran C CXX
)

# for environment installation
set(CMAKE_INSTALL_RPATH $ORIGIN/../lib)
if(DEFINED ENV{CONDA_PREFIX})
    message("Building with conda environment: $ENV{CONDA_PREFIX}")
    list(APPEND CMAKE_PREFIX_PATH $ENV{CONDA_PREFIX})
endif()

# import targets that satisfy the HDF5 dependency
find_package(HDF5
    REQUIRED
    COMPONENTS Fortran HL
)

# import targets that satisfy the Lapack dependency (includes BLAS)
find_package(LAPACK
    REQUIRED
)

# recurse into source tree
add_subdirectory(src)

# specify targets for installation
install(
    TARGETS
        rtsos_GSFC_AC_LUT
        rtsos_Aerosol_Phmx_Cal
        rtsos_rao_dg
        rtsos_PACE_Simulator_DoubleK
    DESTINATION
        ${SKBUILD_SCRIPTS_DIR}
)
