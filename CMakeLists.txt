foreach(t
    aerosol_phasematrix_preparation
    core
    pace_simulator
)
    add_subdirectory(${t})
    set_target_properties(${t}
        PROPERTIES
            Fortran_MODULE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/${t}/mod
    )
    target_include_directories(${t}
        PUBLIC
            ${CMAKE_CURRENT_BINARY_DIR}/${t}/mod
    )
endforeach()

add_executable(rtsos_GSFC_AC_LUT
    AC_Aerosols_LUT/main_GSFC_AC_LUT.f90
)
target_link_libraries(rtsos_GSFC_AC_LUT
    core
    ${HDF5_Fortran_LIBRARIES}
    ${HDF5_Fortran_HL_LIBRARIES}
)

add_executable(rtsos_Aerosol_Phmx_Cal
    aerosol_phasematrix_preparation/main_aerosol_phmx_cal.f90
)
target_link_libraries(rtsos_Aerosol_Phmx_Cal
    core
    aerosol_phasematrix_preparation
    ${HDF5_Fortran_LIBRARIES}
)

add_executable(rtsos_rao_dg
    main_program_monochromatic/main.f90
)
target_link_libraries(rtsos_rao_dg
    core
)

add_executable(rtsos_PACE_Simulator_DoubleK
    pace_simulator/main_PACE_Simulator_DoubleK.f90
)
target_link_libraries(rtsos_PACE_Simulator_DoubleK
    core
    pace_simulator
    ${HDF5_Fortran_HL_LIBRARIES}
)
