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

MODULE RossLiBRDF
USE RTUTILITY, ONLY : PI,SCL,NMBRE,NMBIM

IMPLICIT NONE
LOGICAL :: fRossLiBRDF=.FALSE.

DOUBLE PRECISION :: fiso,fvol,fgeo,Bpol
DOUBLE PRECISION, PARAMETER :: PARA_HoB=2.0d0,PARA_BoR=1.0d0
!DOUBLE PRECISION, PARAMETER :: PI=3.141592653589793d0
!LOGICAL :: SCL=.FALSE.
!DOUBLE PRECISION :: NMBRE=1.45,NMBIM=0.0D0
CONTAINS

SUBROUTINE RossLi_Kernel_vol(COST1,PHI1,COST2,PHI2,BRDML)
IMPLICIT none

DOUBLE PRECISION,INTENT(IN) :: COST1,PHI1,COST2,PHI2
DOUBLE PRECISION,DIMENSION(4,4),INTENT(OUT) :: BRDML

DOUBLE PRECISION :: SINT1,SINT2,THETA1,THETA2, PHIV

DOUBLE PRECISION :: thetascat,costhetascat,sinthetascat

SINT1=DSQRT(1.0D0-COST1*COST1)
SINT2=DSQRT(1.0D0-COST2*COST2)
PHIV=PHI2-PHI1+PI
!IF(PHIV<0.0D0)PHIV=PHIV+2.0D0*PI
!IF(PHIV>2.0D0*PI)PHIV=PHIV-2.0D0*PI

costhetascat=abs(COST1*COST2)+SINT1*SINT2*COS(PHIV)
IF(ABS(costhetascat)>1.0D0) STOP 'CHECK COST1 AND COST2 IN RossLi_Kernel_vol'
sinthetascat=DSQRT(1.0D0-costhetascat*costhetascat)
thetascat=ACOS(costhetascat)
BRDML=0.0D0
BRDML(1,1)=((0.5D0*PI-thetascat)*costhetascat+sinthetascat)/(abs(COST1)+abs(COST2))
BRDML(1,1)=BRDML(1,1)-0.25D0*PI
ENDSUBROUTINE RossLi_Kernel_vol

SUBROUTINE RossLi_Kernel_geo(COST1,PHI1,COST2,PHI2,BRDML)
IMPLICIT none
! LiSparse-R kernel per atbd_mod09.pdf
DOUBLE PRECISION,INTENT(IN) :: COST1,PHI1,COST2,PHI2
DOUBLE PRECISION,DIMENSION(4,4),INTENT(OUT) :: BRDML

DOUBLE PRECISION :: SINT1,SINT2,THETA1,THETA2, PHIV,TANT1,TANT2

DOUBLE PRECISION :: thetaP1,thetaP2,cosphaseanglep,CapD,rtmp1,rtmp2,costl,sintl,secP1,secP2,Ofunc

SINT1=DSQRT(1.0D0-COST1*COST1)
SINT2=DSQRT(1.0D0-COST2*COST2)
TANT1=SINT1/ABS(COST1)
TANT2=SINT2/ABS(COST2)

thetaP1=atan(PARA_BoR*TANT1)
thetaP2=atan(PARA_BoR*TANT2)

PHIV=PHI2-PHI1+PI
!IF(PHIV<0.0D0)PHIV=PHIV+2.0D0*PI
!IF(PHIV>2.0D0*PI)PHIV=PHIV-2.0D0*PI

cosphaseanglep=cos(thetaP1)*cos(thetaP2)+sin(thetaP1)*sin(thetaP2)*cos(PHIV)
rtmp1=tan(thetaP1)
rtmp2=tan(thetaP2)

CapD=sqrt(rtmp1**2+rtmp2**2-2.0d0*rtmp1*rtmp2*cos(PHIV))
secP1=1.0d0/cos(thetaP1)
secP2=1.0d0/cos(thetaP2)

costl=PARA_HoB*sqrt(CapD**2+(rtmp1*rtmp2*sin(PHIV))**2)/(secP1+secP2)
if(abs(costl)>1.0d0)then
	Ofunc=0.0d0
else
	sintl=sqrt(1.0d0-costl*costl)
	Ofunc=(acos(costl)-sintl*costl)*(secP1+secP2)/PI
!  write(*,*)'debugging Ross-Li geo kernel,thetaP1,thetaP2,CapD,costl='
!  write(*,'(4(f12.6,2x))')thetaP1,thetaP2,CapD,costl
endif
BRDML=0.0d0

BRDML(1,1)=Ofunc-secP1-secP2+0.5d0*(1.0d0+cosphaseanglep)*secP2*secP1

ENDSUBROUTINE RossLi_Kernel_geo

SUBROUTINE pBRDM_RossLi(COST1,PHI1,COST2,PHI2,BRDML)
IMPLICIT none
DOUBLE PRECISION,INTENT(IN) :: COST1,PHI1,COST2,PHI2
DOUBLE PRECISION, PARAMETER :: vfac=0.1D0
DOUBLE PRECISION :: RTMP,SINT1,SINT2,COST,THETA1
DOUBLE PRECISION,DIMENSION(4,4),INTENT(OUT) :: BRDML

DOUBLE PRECISION,DIMENSION(4,4) :: BRDML_vol,BRDML_geo,FRES_MTRX

BRDML=0.0d0
call RossLi_Kernel_vol(COST1,PHI1,COST2,PHI2,BRDML_vol)
call RossLi_Kernel_geo(COST1,PHI1,COST2,PHI2,BRDML_geo)
BRDML(1,1)=fiso+fvol*BRDML_vol(1,1)+fgeo*BRDML_geo(1,1)
BRDML(1,1)=BRDML(1,1)*abs(COST1)

IF(BRDML(1,1)<0.0D0)BRDML(1,1)=0.0d0

IF(Bpol>0.0D0)THEN
    IF(ABS(NMBRE-1.5D0)>1.0E-6)STOP 'CHECK NMBRE INPUT'
    IF(ABS(NMBIM)>1.0E-6)STOP 'CHECK NMBIM INPUT'

	SINT1=DSQRT(1.0D0-COST1*COST1)
	SINT2=DSQRT(1.0D0-COST2*COST2)

	COST=COST1*COST2+SINT1*SINT2*DCOS(PHI2-PHI1)
	IF(DABS(COST)>1.0D0)COST=COST/ABS(COST)
	THETA1=(PI-DACOS(COST))/2.0d0
    CALL FRSNL_R2(NMBRE,NMBIM,THETA1,FRES_MTRX)
! Eq. 21 of Fabienne Maignan, François-Marie Bréon, Emilie Fédèle, Marc Bouvier,
! Polarized reflectances of natural surfaces: Spaceborne measurements and analytical modeling,
! Remote Sensing of Environment, Volume 113, Issue 12, 2009, Pages 2642-2650, ISSN 0034-4257,
! https://doi.org/10.1016/j.rse.2009.07.022.
! also Eq. 66 of Hasekamp et al. ATBD for SPEXone RemoTAP Aerosol Processing,
! SRON Netherlands Institute For Space Research, Utrecht,
! The Netherlands, SRON-SPEXoneL1-2020-02, issue: 0.90, 2020

    FRES_MTRX=Bpol*EXP(-tan(THETA1))*EXP(-vfac)*FRES_MTRX/(4.0d0*(abs(COST1)+abs(COST2)))
    FRES_MTRX=FRES_MTRX*abs(COST1)
	IF(SCL)THEN
		RTMP=FRES_MTRX(1,1)
		FRES_MTRX=0.0D0
		FRES_MTRX(1,1)=RTMP
	ENDIF

    BRDML=BRDML+FRES_MTRX
ENDIF
!IF(BRDML(1,1)<0.0D0 .AND. ABS(BRDML(1,1)*COST2)>0.01D0) THEN
!  WRITE(*,*)'fiso,fvol,fgeo=',fiso,fvol,fgeo
!  WRITE(*,*)'THETA1,PHI1,THETAV,PHI2=',ACOS(COST1)/PI*180.0,PHI1,ACOS(COST2)/PI*180.0,PHI2
!  write(*,*)'BRDML_vol,BRDML_geo,BRDML,=',BRDML_vol(1,1),BRDML_geo(1,1),BRDML(1,1)
!  write(*,*)'BRDML*COST2,=',BRDML(1,1)*ABS(COST2)
!  STOP 'CHECK Ross-Li BRDF routine or coefficients'
!ENDIF

END SUBROUTINE pBRDM_RossLi

END MODULE RossLiBRDF

!SUBROUTINE FRSNL_R2(NRE,NIM,THETA1,FRES_REFL)
!!USE RTTYPE
!USE RossLiBRDF,ONLY : SCL
!
!IMPLICIT NONE
!DOUBLE PRECISION,INTENT(IN) :: NRE,NIM,THETA1
!DOUBLE PRECISION,DIMENSION(4,4),INTENT(OUT) :: FRES_REFL
!
!DOUBLE PRECISION :: SINT1,COST1,SINT2,ALPHA2,BETA2
!COMPLEX*16::UNIT_COM,NREL,NREL2,CFCT1,CFCT2,ALPHA,BETA,GAMMA
!
!!IF(THETA1<0 .OR. THETA1>PI/2) then
!!   write(*,*) 'theta2-',THETA2
!!   STOP 'THETA1 WRONG'
!!ENDIF
!
!UNIT_COM=(0.0D0,1.0D0)
!NREL=NRE+NIM*UNIT_COM
!NREL2=NREL*NREL
!SINT1=SIN(THETA1)
!COST1=COS(THETA1)
!SINT2=SINT1*SINT1
!
!CFCT1=NREL2*COST1
!CFCT2=CDSQRT(NREL2-SINT2)
!ALPHA=(CFCT1-CFCT2)/(CFCT1+CFCT2)
!  
!CFCT1=COST1
!CFCT2=CDSQRT(NREL2-SINT2)
!BETA=(CFCT1-CFCT2)/(CFCT1+CFCT2)
!
!GAMMA= CONJG(ALPHA)*BETA
!
!ALPHA2=0.5D0*ABS(ALPHA)**2
!BETA2=0.5D0*ABS(BETA)**2
!
!FRES_REFL=0.0D0
!
!FRES_REFL(1,1)=ALPHA2+BETA2
!IF(SCL)RETURN
!FRES_REFL(1,2)=ALPHA2-BETA2
!FRES_REFL(2,1)=FRES_REFL(1,2)
!FRES_REFL(2,2)=FRES_REFL(1,1)
!FRES_REFL(3,3)=REAL(GAMMA)
!FRES_REFL(4,4)=FRES_REFL(3,3)
!FRES_REFL(3,4)=-IMAG(GAMMA)
!FRES_REFL(4,3)=-FRES_REFL(3,4)
!
!END SUBROUTINE FRSNL_R2
!
!program main
!use RossLiBRDF
!
!implicit none
!DOUBLE PRECISION,DIMENSION(4,4) :: BRDML_vol,BRDML_geo
!
!integer :: inttmp0,inttmp,inttmp1
!DOUBLE PRECISION :: thetav,thetai,PHI1,PHI2,rtmp,rtmp1,rtmp0
!DOUBLE PRECISION :: COST1,COST2,albedo_geo,albedo_vol
!PHI1=0.0d0
!
!rtmp0=PI/2.0d0/18.0d0

!rtmp=PI/2.0d0/180.0d0
!rtmp1=2.0d0*PI/180.0d0
!write(*,*)'thetai/PI*180.0d0,albedo_vol,albedo_geo'
!
!do inttmp0=0,17
!
!thetai=inttmp0*rtmp0
!COST1=cos(thetai)
!
!albedo_geo=0.0d0
!albedo_vol=0.0d0
!do inttmp=0,179
!do inttmp1=0,179
!	thetav=inttmp*rtmp
!	PHI2=inttmp1*rtmp1
!	COST2=cos(thetav)
!
!	call RossLi_Kernel_vol(COST1,PHI1,COST2,PHI2,BRDML_vol)
!	call RossLi_Kernel_geo(COST1,PHI1,COST2,PHI2,BRDML_geo)
!    albedo_geo=albedo_geo+BRDML_geo(1,1)*COST2*sin(thetav)
!    albedo_vol=albedo_vol+BRDML_vol(1,1)*COST2*sin(thetav)
!enddo
!enddo
!albedo_geo=albedo_geo*rtmp*rtmp1
!albedo_vol=albedo_vol*rtmp*rtmp1
!write(*,'(3(f12.6,2x))')thetai/PI*180.0d0,albedo_vol,albedo_geo
!enddo
!
!thetai=120.0d0*PI/180.0d0
!write(*,*)'thetai=',thetai*180.0d0/PI
!write(*,*)'thetav,K_vol,K_geo'
!COST1=cos(thetai)
!
!PHI2=PI !0.5*PI
!rtmp=PI/2.0d0/18.0d0
!
!do inttmp=17,0,-1
!    thetav=inttmp*rtmp
!    COST2=cos(thetav)
!
!    call RossLi_Kernel_vol(COST1,PHI1,COST2,PHI2,BRDML_vol)
!    call RossLi_Kernel_geo(COST1,PHI1,COST2,PHI2,BRDML_geo)
!    write(*,'(3(f12.6,2x))')-thetav/PI*180.0d0,BRDML_vol(1,1),BRDML_geo(1,1)
!enddo
!
!PHI2=0.0d0     !1.5*PI
!do inttmp=1,17
!	thetav=inttmp*rtmp
!	COST2=cos(thetav)
!
!	call RossLi_Kernel_vol(COST1,PHI1,COST2,PHI2,BRDML_vol)
!	call RossLi_Kernel_geo(COST1,PHI1,COST2,PHI2,BRDML_geo)
!	write(*,'(3(f12.6,2x))')thetav/PI*180.0d0,BRDML_vol(1,1),BRDML_geo(1,1)
!enddo
!endprogram main
