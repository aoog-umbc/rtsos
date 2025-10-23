! ===============================================================
!  RTSOS – Radiative Transfer model based on Successive Orders of Scattering
!  Copyright (C) 2025  Pengwang Zhai, University of Maryland Baltimore County
!
!  Licensed under the Creative Commons Attribution–NonCommercial 4.0
!  International License (CC BY-NC 4.0).
!  You may use, modify, and share this code for research and
!  educational purposes with proper attribution.
!  Commercial use requires written permission from the author.
!
!  Full license: https://creativecommons.org/licenses/by-nc/4.0/
!  Contact: Pengwang Zhai  |  [pwzhai@umbc.edu]
! ===============================================================

MODULE MAP_INSTRUMENT_DESIGN
INTEGER,PARAMETER :: NWV_BAND_SEG4=4
DOUBLE PRECISION,DIMENSION(NWV_BAND_SEG4):: WV_BAND_SEG4=(/440.159d0, 549.465d0, 664.564d0, 865.283d0/)
DOUBLE PRECISION,DIMENSION(NWV_BAND_SEG4):: PACE_FWHM_SEG4=(/15.768D0, 9.426D0, 10.404D0, 40.148D0/)
! NWV_BAND_SEG4: Number of wavelengths for HARP-2 or similar discrete wavelength MAP.
END MODULE MAP_INSTRUMENT_DESIGN
