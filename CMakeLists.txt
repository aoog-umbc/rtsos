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

# rtsos_rao_dg static library
add_library(rtsos_rao_dg
    src/core/Atmosphere_Profile.f90
    src/core/Gas_Absorption_CS_Readin.f90
    src/core/Save_Ocean_Rad.f90
    src/core/aerosol_microphysical_model.f90
    src/core/bessel.f
    src/core/bfit.f90
    src/core/deltafit.f90
    src/core/nrlib.f90
    src/core/rt_single_scattering.f90
    src/core/rtsos_rao_dg.f90
    src/core/rtspecfunc.f90
    src/core/rttype_sos_rao_dg.f90
    src/core/spher.f
    src/core/surface_glint.f90
)
target_link_libraries(rtsos_rao_dg
    ${LIBS}
)

# rtsos_rao_dg executable
add_executable(rtsos_rao_dg.exe
    src/main_program_monochromatic/main.f90
)
target_link_libraries(rtsos_rao_dg.exe
    rtsos_rao_dg
)

# pace_simlator static library
add_library(pace_simulator
    src/pace_simulator/PACE_Instrument.f90
)
target_link_libraries(pace_simulator
    ${LIBS}
)

# rtsos_PACE_Simulator_DoubleK executable
add_executable(rtsos_PACE_Simulator_DoubleK.exe
    src/pace_simulator/PACE_MIE_PHMX_Init.f90
    src/pace_simulator/main_PACE_Simulator_DoubleK.f90
)
target_link_libraries(rtsos_PACE_Simulator_DoubleK.exe
    pace_simulator
    rtsos_rao_dg
)

# rtsos_GSFC_AC_LUT.exe executable
add_executable(rtsos_GSFC_AC_LUT.exe
    src/AC_Aerosols_LUT/main_GSFC_AC_LUT.f90
)
target_link_libraries(rtsos_GSFC_AC_LUT.exe
    rtsos_rao_dg
)

# rtsos_Aerosol_Phmx_Cal.exe executable
add_executable(rtsos_Aerosol_Phmx_Cal.exe
    src/aerosol_phasematrix_preparation/auxiliary_dir_readin.f90
    src/aerosol_phasematrix_preparation/read_dust_data.f90
    src/aerosol_phasematrix_preparation/Mie_PHMX_Cal.f90
    src/aerosol_phasematrix_preparation/main_aerosol_phmx_cal.f90
)
target_link_libraries(rtsos_Aerosol_Phmx_Cal.exe
    pace_simulator
    rtsos_rao_dg
)

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
