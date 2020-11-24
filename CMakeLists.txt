cmake_minimum_required(VERSION 2.8)

set_ocssw_policy()

set(CMAKE_Fortran_FLAGS "-fbounds-check -ffpe-trap=invalid,zero,overflow -finit-real=nan -fcheck=all -std=legacy ${CMAKE_Fortran_FLAGS}")

if(${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
    set(BUILD_SHARED_LIBS OFF)
endif()

find_package(HDF5 REQUIRED COMPONENTS Fortran Fortran_HL) 
include_directories(${HDF5_INCLUDE_DIRS})
list(APPEND LIBS ${HDF5_LIBRARIES} ${HDF5_Fortran_LIBRARIES} ${HDF5_Fortran_HL_LIBRARIES})

add_executable(zhai_rt_pace
  core/nrlib.f90
  core/rttype_sos_rao_dg.f90
  core/Atmosphere_Profile.f90
  core/Gas_Absorption_CS_Readin.f90
  pace_simulator/PACE_Instrument.f90
  core/Save_Ocean_Rad.f90
  core/bessel.f
  core/rtspecfunc.f90
  core/rtsos_rao_dg.f90
  core/rt_single_scattering.f90
  core/spher.f
  core/bfit.f90
  core/deltafit.f90
  core/aerosol_microphysical_model.f90
  pace_simulator/PACE_MIE_PHMX_Init.f90
  pace_simulator/main_PACE_Simulator_DoubleK.f90
)

# Leaving this here in case the code gets MPI-ified
if (USE_MPI)
    set(CMAKE_CXX_COMPILER $ENV{LIB3_DIR}/bin/mpic++)

    find_package(MPI REQUIRED)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DWITH_MPI")
    include_directories(SYSTEM ${MPI_INCLUDE_PATH})
    target_link_libraries(zhai_rt_pace ${LIBS} ${MPI_CXX_LIBRARIES})
else(USE_MPI)
    target_link_libraries(zhai_rt_pace  ${LIBS})
endif(USE_MPI)

target_include_directories(zhai_rt_pace PUBLIC ".")

set_target_properties(zhai_rt_pace PROPERTIES LINKER_LANGUAGE Fortran)

install (TARGETS zhai_rt_pace DESTINATION bin)
