add_library(aerosol_phasematrix_preparation
    Mie_PHMX_Cal.f90
    read_dust_data.f90
)
target_link_libraries(aerosol_phasematrix_preparation
    pace_simulator
    ${HDF5_Fortran_LIBRARIES}
)
