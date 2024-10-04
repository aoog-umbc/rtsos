# rtsos_rao_dg static library
add_library(rtsos_rao_dg
    core/Atmosphere_Profile.f90
	core/SnowBRDF.f90
	core/RossLiBRDF.f90
	core/emis_sea.f90
	core/refwat1.f
    core/Gas_Absorption_CS_Readin.f90
    core/Save_Ocean_Rad.f90
    core/aerosol_microphysical_model.f90
    core/bessel.f
    core/bfit.f90
    core/deltafit.f90
    core/nrlib.f90
    core/rt_single_scattering.f90
    core/rtsos_rao_dg.f90
    core/rtspecfunc.f90
    core/rttype_sos_rao_dg.f90
    core/spher.f
    core/surface_glint.f90
)
target_link_libraries(rtsos_rao_dg
    ${LIBS}
)
set_target_properties(rtsos_rao_dg
    PROPERTIES
        Fortran_MODULE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/mod/rtsos_rao_dg
)
target_include_directories(rtsos_rao_dg
    PUBLIC
        ${CMAKE_CURRENT_BINARY_DIR}/mod/rtsos_rao_dg
)

# pace_simlator static library
add_library(pace_simulator
    pace_simulator/MAP_Instrument.f90
    pace_simulator/PACE_Instrument.f90
)
target_link_libraries(pace_simulator
    ${LIBS}
)
set_target_properties(pace_simulator
    PROPERTIES
        Fortran_MODULE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/mod/pace_simulator
)
target_include_directories(pace_simulator
    PUBLIC
        ${CMAKE_CURRENT_BINARY_DIR}/mod/pace_simulator
)

# rtsos_rao_dg executable
add_executable(rtsos_rao_dg.exe
    main_program_monochromatic/main.f90
)
target_link_libraries(rtsos_rao_dg.exe
    rtsos_rao_dg
)
set_target_properties(rtsos_rao_dg.exe
    PROPERTIES
        Fortran_MODULE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/mod/rtsos_rao_dg.exe
)
target_include_directories(rtsos_rao_dg.exe
    PUBLIC
        ${CMAKE_CURRENT_BINARY_DIR}/mod/rtsos_rao_dg.exe
)

# rtsos_PACE_Simulator_DoubleK executable
add_executable(rtsos_PACE_Simulator_DoubleK.exe
    pace_simulator/PACE_MIE_PHMX_Init.f90
    pace_simulator/main_PACE_Simulator_DoubleK.f90
)
target_link_libraries(rtsos_PACE_Simulator_DoubleK.exe
    pace_simulator
    rtsos_rao_dg
)
set_target_properties(rtsos_PACE_Simulator_DoubleK.exe
    PROPERTIES
        Fortran_MODULE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/mod/rtsos_PACE_Simulator_DoubleK.exe
)
target_include_directories(rtsos_PACE_Simulator_DoubleK.exe
    PUBLIC
        ${CMAKE_CURRENT_BINARY_DIR}/mod/rtsos_PACE_Simulator_DoubleK.exe
)

# rtsos_GSFC_AC_LUT.exe executable
add_executable(rtsos_GSFC_AC_LUT.exe
    AC_Aerosols_LUT/main_GSFC_AC_LUT.f90
)
target_link_libraries(rtsos_GSFC_AC_LUT.exe
    rtsos_rao_dg
)
set_target_properties(rtsos_GSFC_AC_LUT.exe
    PROPERTIES
        Fortran_MODULE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/mod/rtsos_GSFC_AC_LUT.exe
)
target_include_directories(rtsos_GSFC_AC_LUT.exe
    PUBLIC
        ${CMAKE_CURRENT_BINARY_DIR}/mod/rtsos_GSFC_AC_LUT.exe
)

# rtsos_Aerosol_Phmx_Cal.exe executable
add_executable(rtsos_Aerosol_Phmx_Cal.exe
    aerosol_phasematrix_preparation/read_dust_data.f90
    aerosol_phasematrix_preparation/Mie_PHMX_Cal.f90
    aerosol_phasematrix_preparation/main_aerosol_phmx_cal.f90
)
target_link_libraries(rtsos_Aerosol_Phmx_Cal.exe
    pace_simulator
    rtsos_rao_dg
)
set_target_properties(rtsos_Aerosol_Phmx_Cal.exe
    PROPERTIES
        Fortran_MODULE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/mod/rtsos_Aerosol_Phmx_Cal.exe
)
target_include_directories(rtsos_Aerosol_Phmx_Cal.exe
    PUBLIC
        ${CMAKE_CURRENT_BINARY_DIR}/mod/rtsos_Aerosol_Phmx_Cal.exe
)
