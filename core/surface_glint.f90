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

MODULE SURFACE_GLINT
IMPLICIT NONE
LOGICAL :: SURFACE_GLINT_FLAG = .FALSE.
! if SURFACE_GLINT_FLAG==.true. output glint contribution to DSTOKES_GLINT

DOUBLE PRECISION,DIMENSION(:,:,:,:),ALLOCATABLE :: DSTOKES_GLINT
! DSTOKES_GLINT(NDET,       NTHETAOUT,       NPHIOUT,         4)

CONTAINS

SUBROUTINE SURFACE_GLINT_ALLO(NDET,NTHETA,NPHI)
INTEGER,INTENT(IN) :: NDET,NTHETA,NPHI

ALLOCATE(DSTOKES_GLINT(NDET,NTHETA,NPHI,4))

END SUBROUTINE SURFACE_GLINT_ALLO

SUBROUTINE SURFACE_GLINT_DEALLO

DEALLOCATE(DSTOKES_GLINT)

END SUBROUTINE SURFACE_GLINT_DEALLO


END MODULE SURFACE_GLINT
