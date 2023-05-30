cmake_minimum_required(VERSION 3.20)

project(ZhaiRT LANGUAGES Fortran)

# import CMake targets that satisfy the HDF5 dependency
if(DEFINED ENV{CONDA_PREFIX})
    list(APPEND CMAKE_PREFIX_PATH $ENV{CONDA_PREFIX})
endif()
find_package(HDF5
    REQUIRED
    COMPONENTS Fortran HL
)
include_directories(${HDF5_Fortran_INCLUDE_DIRS})
list(APPEND LIBS ${HDF5_Fortran_LIBRARIES} ${HDF5_Fortran_HL_LIBRARIES})

# build customizations
SET(CMAKE_INSTALL_RPATH_USE_LINK_PATH True)
set(CMAKE_Fortran_FLAGS "-O3 ${CMAKE_Fortran_FLAGS}") # TODO confirm used
set(CMAKE_Fortran_MODULE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/Mod")

# targets
add_subdirectory(src)

# specify targets for installation
install(
    TARGETS
        rtsos_rao_dg.exe
        rtsos_PACE_Simulator_DoubleK.exe
        rtsos_Aerosol_Phmx_Cal.exe
        rtsos_GSFC_AC_LUT.exe
    DESTINATION
        bin
)
