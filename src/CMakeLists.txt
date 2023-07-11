# rtsos_rao_dg static library
add_library(rtsos_rao_dg
    core/Atmosphere_Profile.f90
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

# pace_simlator static library
add_library(pace_simulator
    pace_simulator/MAP_Instrument.f90
    pace_simulator/PACE_Instrument.f90
)
target_link_libraries(pace_simulator
    ${LIBS}
)

# rtsos_rao_dg executable
add_executable(rtsos_rao_dg.exe
    main_program_monochromatic/main.f90
)
target_link_libraries(rtsos_rao_dg.exe
    rtsos_rao_dg
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

# rtsos_GSFC_AC_LUT.exe executable
add_executable(rtsos_GSFC_AC_LUT.exe
    AC_Aerosols_LUT/main_GSFC_AC_LUT.f90
)
target_link_libraries(rtsos_GSFC_AC_LUT.exe
    rtsos_rao_dg
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
