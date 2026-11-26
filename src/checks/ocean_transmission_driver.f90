! Exercise the actual transmission kernels with named input cases on stdin.
PROGRAM ocean_transmission_driver
USE RTUTILITY
IMPLICIT NONE
CHARACTER(LEN=20) :: kernel
INTEGER :: ios
DOUBLE PRECISION :: cost1,phi1,cost2,phi2,matrix(4,4),direct(4)
NAMELIST /transmission_case/ kernel,cost1,phi1,cost2,phi2,NWRE,NWIM, &
    SIGMASQ,SIGMACSQ,SIGMAUSQ,WIND_X,WIND_Y,Surf_c21,Surf_c03, &
    Surf_c40,Surf_c22,Surf_c04,SCL,SHDWFLG,WIND_VECTOR_PRESENT, &
    I_SURFACE_ROUGHNESS_PARA,FLATO,WNDSPD

NALYR=1
ALLOCATE(SECANT_THETAL_PRSV(1))
SECANT_THETAL_PRSV=1.0D0
OITAU=0.0D0
OITAU_PRSV=0.0D0
ESUN=(/PI,0.0D0,0.0D0,0.0D0/)

DO
    kernel='directional'
    cost1=-COS(PI/4.0D0)
    phi1=0.0D0
    NWRE=1.34D0
    NWIM=0.0D0
    cost2=-SQRT(1.0D0-(SIN(PI/4.0D0)/NWRE)**2)
    phi2=0.0D0
    WNDSPD=7.0D0
    SIGMASQ=0.003D0+0.00512D0*7.0D0
    SIGMACSQ=0.003D0+0.00192D0*7.0D0
    SIGMAUSQ=0.00316D0*7.0D0
    WIND_X=1.0D0
    WIND_Y=0.0D0
    Surf_c21=0.01D0-0.0086D0*7.0D0
    Surf_c03=0.04D0-0.033D0*7.0D0
    Surf_c40=0.40D0
    Surf_c22=0.12D0
    Surf_c04=0.23D0
    SCL=.FALSE.
    SHDWFLG=.FALSE.
    WIND_VECTOR_PRESENT=.TRUE.
    I_SURFACE_ROUGHNESS_PARA=1
    FLATO=.FALSE.
    READ(*,NML=transmission_case,IOSTAT=ios)
    IF(ios<0)EXIT
    IF(ios/=0)ERROR STOP 'Cannot read transmission test case'
    NSQW=NWRE*NWRE
    matrix=0.0D0
    SELECT CASE(TRIM(kernel))
    CASE('directional')
        CALL BTDM_AT_OCEAN_nonGaussian(cost1,phi1,cost2,phi2,NWRE,NWIM,matrix)
    CASE('isotropic')
        CALL BTDM_AT_OCEAN(cost1,phi1,cost2,phi2,NWRE,NWIM,matrix)
    CASE('direct')
        CALL RADOCMDRCT(cost1,0.0D0,cost2,phi2,direct,.TRUE.)
        matrix(:,1)=direct
    CASE DEFAULT
        ERROR STOP 'Unknown transmission test kernel'
    END SELECT
    WRITE(*,'(16ES27.18)')matrix
ENDDO
END PROGRAM ocean_transmission_driver
