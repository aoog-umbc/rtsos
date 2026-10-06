cmake_minimum_required(VERSION 3.22...3.31)

if(DEFINED SKBUILD_PROJECT_NAME)
    set(_PROJECT "${SKBUILD_PROJECT_NAME}")
else()
    set(_PROJECT "RTSOS")
endif()
project(${_PROJECT}
    LANGUAGES
        C
        CXX
        Fortran
)
include(GNUInstallDirs)

# ensure RPATH is defined for relocatable binaries
set(CMAKE_INSTALL_RPATH "$ORIGIN/../lib")
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)

# for Conda environment installation with cmake
if(DEFINED ENV{CONDA_PREFIX})
    message(STATUS "Building with conda environment: $ENV{CONDA_PREFIX}")
    list(APPEND CMAKE_PREFIX_PATH "$ENV{CONDA_PREFIX}")
    set(CMAKE_INSTALL_PREFIX "$ENV{CONDA_PREFIX}" CACHE PATH "Default install prefix for Conda environment" FORCE)
endif()

# import targets that satisfy the HDF5 dependency
find_package(HDF5
    REQUIRED
    COMPONENTS
        Fortran
        HL
)

# import targets that satisfy the Lapack dependency (includes BLAS)
find_package(LAPACK
    REQUIRED
)

# recurse into source tree
add_subdirectory(src)
