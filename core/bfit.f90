
!c----------------------------------------------------------------------------
!c----------------------------------------------------------------------------
!c  bfit(fn,nstr,pmom,pfit):
!c 
!c  Input variables: 
!        ANG(i):i=1,NN      'scattering angles in degree(0-180)
!        phs(i):i=1,NN      ' Normalized phase function
!	 NN: (0-2000): Number of scattering anngle
!c      nstr (2-300) : the number of streams
!c         (the phase function has to be normalized to 2: int_-1^1  P d mu = 2.
!c          for example, P = 1 for isotropic phase function)


!c  Output:  
!c   pmom    the regular moments which DISORT needs for PMOM
!c           (DOUBLE PRECISION number starting at dimension0, 
!c           1-d vector with length 0:300) 
!c                            -------------
!c   pfitdm  the fitted "moments" which DISORT needs for PMOM
!c           (DOUBLE PRECISION number starting at dimension0,
!c           1-d vector with length 0:300) 
!c                            -------------
!c   pfit and ftrunc    in case you do not use disort, this is  
!c           the "moments" from the delta-fit after delta-truncation 
!c           with truncation factor ftrunc
!c 	    (ftrunc: DOUBLE PRECISION)
!c           (pfit: DOUBLE PRECISION number starting at dimension0, 
!c           1-d vector with length 0:300) 
!c    ftrunc: traunction factor
!c----------------------------------------------------------------------------
MODULE BFIT_PARAMETERS
INTEGER,PARAMETER ::NQUAD_REGION1=1000,NQUAD_REGION2=1000,&
                 NQUAD_TOTAL=NQUAD_REGION1+NQUAD_REGION2
DOUBLE PRECISION,PARAMETER :: pi=3.141592653589793238462643383279502884197d0
DOUBLE PRECISION,dimension(NQUAD_REGION1):: x1,w1,y1
DOUBLE PRECISION,dimension(NQUAD_REGION2):: x2,w2,y2
DOUBLE PRECISION,dimension(NQUAD_TOTAL):: x,w,xx,y,ysig

CONTAINS
SUBROUTINE BFIT_QUAD_SETUP(angtrun)
DOUBLE PRECISION :: angtrun
call gauss_legendre(angtrun,1.0d0,x1,w1,NQUAD_REGION1/2)
call gauss_legendre(0.0d0,angtrun,x2,w2,NQUAD_REGION2/2)
do i=1,NQUAD_REGION1/2
  w(i)=w1(NQUAD_REGION1/2+1-i)
  x(i)=-x1(NQUAD_REGION1/2+1-i)
  w(NQUAD_TOTAL+1-i)=w1(NQUAD_REGION1/2+1-i)
  x(NQUAD_TOTAL+1-i)=x1(NQUAD_REGION1/2+1-i)
enddo

do i=1,NQUAD_REGION2/2
  w(i+NQUAD_REGION1/2)=w2(i)
  x(i+NQUAD_REGION1/2)=-x2(NQUAD_REGION2/2+1-i)
  w(NQUAD_TOTAL-NQUAD_REGION1/2+1-i)=w2(i)
  x(NQUAD_TOTAL-NQUAD_REGION1/2+1-i)=x2(NQUAD_REGION2/2+1-i)
enddo

do i=1,NQUAD_TOTAL
  xx(i)=acos(x(i))*180.0d0/pi
enddo

END SUBROUTINE BFIT_QUAD_SETUP

END MODULE BFIT_PARAMETERS

    subroutine bfit(nstr,NN,ang,phs,angtrun,pfit,ftrunc,deltam)
    USE BFIT_PARAMETERS
    implicit none
!	character*80 fn	
    integer :: nstr, NN, i,j
    DOUBLE PRECISION,dimension(0:NSTR):: pmom,pfit,pfitdm
    DOUBLE PRECISION,dimension(1:NN):: ang,phs

    integer :: deltam,deltamlocal
    DOUBLE PRECISION :: angtrun,ftrunc,ctrunc,sigma_sq
    DOUBLE PRECISION :: Func_UVIP3P
    deltamlocal=deltam
!ccc   ang are in degrees (Theta), not cos(Theta)

	if (abs(ang(NN)).le.1.0d0 .and. abs(ang(1)).le.1.0d0) then
	do i=1,NN
        ang(i)=acos(ang(i))*180.0d0/pi
	enddo
	endif

    CALL BFIT_QUAD_SETUP(angtrun)

! SPLINE INTERPOLATION
! 	call myspline(NN,ang,phs,NQUAD_TOTAL,xx,y)
! or use LINEAR INTERPOLATION
	do i=1,NQUAD_TOTAL
      y(i)=Func_UVIP3P(NN,ang,phs,xx(i),2)
    enddo

!ccc  compute the moments
    call calmom(nstr,pmom)

    if((pmom(nstr-1)/(2*nstr-1) < pmom(nstr)/(2*nstr+1) .or. pmom(nstr)<1.0e-5) &
        .and. deltamlocal==1)then
       write(*,*) 'pmom(nstr-1) < pmom(nstr) .or. pmom(nstr)<1.0e-5,Delta M is used'
       deltamlocal=0
    endif
!!   renormalize
    if (abs(pmom(0)-1.0d0) .lt.0.001) then
!        write(*,*) 'pmom(0)=', pmom(0)
        do i=1,NQUAD_TOTAL
          y(i)=y(i)/pmom(0)
        enddo
        do j=1,nstr
          pmom(j)=pmom(j)/pmom(0)
        enddo
        pmom(0)=1.0d0
    else
       write(*,'("warning pmom(0)=",E12.4," NOT equal to 1, Delta fit is used")')pmom(0)
!       write(*,*) 'double check your phase function input'
!       if (abs(pmom(0)-1.0d0) .gt.0.05) stop
!       write(*,*) 'Guessing it is due to infinite forward scattering peak'
!       write(*,*) 'Delta fit is used for this case'
       deltamlocal=2
    endif

    if(deltamlocal==0)then
        ftrunc=pmom(nstr)/(2*nstr+1)
        do i=0,nstr
           pfit(i)=(pmom(i)/(2.*i+1.0)-ftrunc)/(1.0d0-ftrunc)
           pfit(i)=pfit(i)*(2.*i+1.0)
        enddo
    elseif(deltamlocal==1)then
        ftrunc=pmom(nstr-1)/(2*nstr-1)
        sigma_sq = ( (nstr)**2 - (nstr-1)**2 ) / &
                   ( log((pmom(nstr-1)/(2*nstr-1))**2) &
                   - log((pmom(nstr  )/(2*nstr+1))**2) )
        ctrunc = exp( (nstr-1)**2/(2*sigma_sq) )
        ftrunc = ctrunc*ftrunc
!write(*,*)'sigma_sq,ctrunc=',sigma_sq,ctrunc
        do i=0,nstr-1
           pfit(i)=(pmom(i)/(2.*i+1.0)-ftrunc*exp(-i**2/(2*sigma_sq)))/(1.0d0-ftrunc)
           pfit(i)=pfit(i)*(2.*i+1.0)
!write(*,*)'deltam plus test:',i,pfit(i),ftrunc
        enddo
        pfit(nstr)=0.0d0
    elseif(deltamlocal==2)then
!ccc  compute pfit 
 	    call calfit(nstr,pmom,pfitdm)
        ftrunc=1.0d0-pfitdm(0)
        do i=0,nstr
           pfit(i)=pfitdm(i)/(1.0d0-ftrunc)
        enddo
        if(deltam<2)write(*,*)'deltam option changed, ftrunc=',ftrunc
    else
        write(*,*)'DELTAM=',deltamlocal
        stop 'deltam should be within 0 - 2, out of bound'
    endif
    end

! ___START___  THE DELTA FIT FOR COEFFICIENTS OF THE WIGNER D FUNCTIONS
	subroutine bfit_ger(intflag,nstr,NN,ang,phs,phssig,angtrun,pfit,DELTAM)
!	character*80 fn	
    USE BFIT_PARAMETERS
    implicit none
	integer intflag,nstr, NN, i
    DOUBLE PRECISION,dimension(0:NSTR):: pmom,pfit,pfitdm
    DOUBLE PRECISION,dimension(1:NN):: ang,phs,phssig
    DOUBLE PRECISION Func_UVIP3P
    DOUBLE PRECISION :: angtrun
    integer :: DELTAM
!ccc   ang are in degrees (Theta), not cos(Theta)


	if (abs(ang(NN)).le.1.d0 .and. abs(ang(1)).le.1.d0) then
	do i=1,NN
        ang(i)=acos(ang(i))*180.d0/pi
	enddo
	endif

! LINEAR INTERPOLATION
    do i=1,NQUAD_TOTAL
      y(i)=Func_UVIP3P(NN,ang,phs,xx(i),2)
      ysig(i)=Func_UVIP3P(NN,ang,phssig,xx(i),2)
    enddo

!ccc  in case you want to compare interpolated phs with the true phs
!	print *,intflag
!	do i=1,NQUAD_TOTAL
!	print '(2(1X,e15.8))', acos(x(i))*180./3.1415926, y(i)
!	enddo
!ccc  compute the moments 

  	call calmom_ger(intflag,nstr,pmom,DELTAM)

    if(DELTAM<1)then
      do i=0,nstr
         pfit(i)=pmom(i)
!         write(*,*)'delta m',intflag,i,pfit(i)
      enddo
    else
!ccc  compute pfit
 	  call calfit_ger(intflag,nstr,pmom,pfitdm)

      do i=0,nstr
         pfit(i)=pfitdm(i)
!        pfit(i)=pmom(i)
!         write(*,*)'delta fit',intflag,i,pfit(i)
      enddo
    endif
	end subroutine bfit_ger

subroutine calfit_ger(intflag,nstr,pmom,pfitdm)
USE BFIT_PARAMETERS
implicit none
integer intflag,nstr,ndata,ma, i, j, k, l, nkp

DOUBLE PRECISION,dimension(0:nstr):: pmom,pfitdm

DOUBLE PRECISION ABSDIFF,tmp,cor

DOUBLE PRECISION,DIMENSION(:),ALLOCATABLE :: pl,dl00,&
                    dl20,dl2p2,dl2n2,b,a
DOUBLE PRECISION,DIMENSION(:,:),ALLOCATABLE :: apl,u

! DGELSD definitions
INTEGER          Mrow, Ncolu, NRHS
INTEGER          LDA, LDB,NLVL
INTEGER,PARAMETER :: LWMAX=50000,SMALLSIZE=25

!     .. Local Scalars ..
INTEGER          INFO, LWORK, RANK
DOUBLE PRECISION RCOND
!     IWORK dimension should be at least 3*MIN(Mrow,Ncolu)*NLVL + 11*MIN(Mrow,Ncolu),
!     where NLVL = MAX( 0, INT( LOG_2( MIN(Mrow,Ncolu)/(SMALLSIZE+1) ) )+1 )
!     and SMALLSIZE = 25
INTEGER,allocatable,dimension(:) :: IWORK !( 3*Mrow*0+11*Mrow )
DOUBLE PRECISION,ALLOCATABLE,dimension(:,:) :: AMATR, BVEC
DOUBLE PRECISION,ALLOCATABLE,dimension(:) :: SMATR
DOUBLE PRECISION :: WORK(LWMAX)


INTERFACE
SUBROUTINE GETDMLlocal(XJ,NUMLORD,DL00,DL20,DL2P2,DL2N2)
IMPLICIT NONE

DOUBLE PRECISION, INTENT(IN) ::XJ
INTEGER, INTENT(IN) ::NUMLORD
DOUBLE PRECISION,INTENT(OUT),DIMENSION(0:NUMLORD)::DL00,DL20,DL2P2,DL2N2

END SUBROUTINE GETDMLlocal
END INTERFACE

! specify variance for different angles
! forward directions are set with larger variance.

!do i=1,NQUAD_TOTAL
!  if(i<NQUAD_TOTAL-NQUAD_REGION1/2) then
!  ysig(i)=1.0d0
!write(*,*)acos(x(i))/3.14159*180, ysig(i)
! else
!    ysig(i)=1.0d6
! endif
!enddo
Mrow=NQUAD_TOTAL
Ncolu=nstr+1
LDA = Mrow
LDB = max(1,Mrow,Ncolu)
NRHS=1
RCOND = -1.0
NLVL= MAX( 0, INT( LOG( MIN(Mrow,Ncolu)/(SMALLSIZE+1.0D0) )/LOG(2.0D0) )+1 )

ALLOCATE(IWORK(3*MIN(Mrow,Ncolu)*NLVL + 11*MIN(Mrow,Ncolu)))
ALLOCATE(AMATR(LDA,Ncolu),BVEC(LDB,NRHS),SMATR(Mrow))

allocate(u(NQUAD_TOTAL,nstr+1),b(NQUAD_TOTAL),a(nstr+1),pl(nstr+1),apl(0:nstr,NQUAD_TOTAL),&
         dl00(0:nstr+1),dl20(0:nstr+1),dl2p2(0:nstr+1),dl2n2(0:nstr+1))

!ccc   compute all the legendre polynormials at all quadreatures
do i=1,NQUAD_TOTAL
  CALL GETDMLlocal(x(i),nstr+1,dl00,dl20,dl2p2,dl2n2)
  do j=0,nstr
    if(intflag==1)then
      apl(j,i)=dl20(j)
    else if(intflag==2)then
      apl(j,i)=dl2p2(j)+dl2n2(j)
    else if(intflag==3)then
      apl(j,i)=dl2p2(j)-dl2n2(j)
    else if(intflag==4)then
      apl(j,i)=dl00(j)
    else if(intflag==5)then
      apl(j,i)=dl20(j)
    else
      stop 'error ingflag'
    endif
  enddo
enddo
!ccc  compute b and u for the fits 
    u=0.0d0
    b=0.0d0
    a=0.0d0
    ndata=NQUAD_TOTAL
    if(intflag==4)then
	  ma=nstr+1
    else
	  ma=nstr-1
	endif
	do k=1,NQUAD_TOTAL
        do l=1,ma
          if(intflag==4)then
            u(k,l)=apl(l-1,k)/ysig(k)
          else
            u(k,l)=apl(l+1,k)/ysig(k)
	      endif
        enddo
        b(k)=y(k)/ysig(k)
	enddo 

!ccc  singular value decomposition fitting to derive b

AMATR=u
BVEC=0.0d0
BVEC(1:Mrow,1)=b(1:Mrow)

LWORK = -1
CALL DGELSD( Mrow, Ncolu, NRHS, AMATR, LDA, BVEC, LDB, SMATR, RCOND, RANK, WORK, &
             LWORK, IWORK, INFO )
LWORK = MIN( LWMAX, INT( WORK( 1 ) ) )

CALL DGELSD( Mrow, Ncolu, NRHS, AMATR, LDA, BVEC, LDB, SMATR, RCOND, RANK, WORK, &
			 LWORK, IWORK, INFO )
a(1:Ncolu)=BVEC(1:Ncolu,1)

!write(*,*)'testing dgelsd,Mrow,Ncolu,LWORK=',Mrow,Ncolu,LWORK,a(1:Ncolu)

IF( INFO /= 0 )THEN
   IF(INFO>0 )STOP 'The LAPACK SVD failed to converge;'
   IF(INFO<0 )WRITE(*,*)'DGELSD INFO=',INFO,'LWORK=',LWORK,'WORK(1)=',INT(WORK(1))
ENDIF
    if(intflag==4)then
	  do i=0,nstr
       pfitdm(i)=a(i+1)
	  enddo
	else
	  pfitdm(0)=0.0d0
	  pfitdm(1)=0.0d0

	  do i=2,nstr
       pfitdm(i)=a(i-1)
	  enddo
!	  tmp=ABSDIFF(nstr,y,ysig,apl,a)
!	  write(*,*)intflag,'th call error and cor=',tmp,cor
!      return
    endif
deallocate(pl,dl00,dl20,dl2p2,dl2n2,b,a,apl,u)
DEALLOCATE(IWORK,AMATR,BVEC,SMATR)

end


 	subroutine calmom_ger(intflag,nstr,pmom,DELTAM)
    USE BFIT_PARAMETERS
    implicit none

    DOUBLE PRECISION,dimension(0:nstr) :: pmom

	integer intflag,nstr,DELTAM
    integer :: i, j, k
    DOUBLE PRECISION :: ftrunc,sigma_sq,ctrunc
    DOUBLE PRECISION,DIMENSION(:),ALLOCATABLE :: pl,dl00,dl20,dl2p2,dl2n2
    DOUBLE PRECISION,DIMENSION(:,:),ALLOCATABLE :: apl

	allocate(pl(nstr+1),apl(0:nstr,NQUAD_TOTAL), dl00(0:nstr+1),&
               dl20(0:nstr+1),dl2p2(0:nstr+1),dl2n2(0:nstr+1))

!ccc   compute all the Wigner d functions at all quadreatures

	do i=1,NQUAD_TOTAL

     CALL GETDMLlocal(x(i),nstr+1,dl00,dl20,dl2p2,dl2n2)
	 do j=0,nstr
		if(intflag==1)then
		  apl(j,i)=dl20(j)
		else if(intflag==2)then
		  apl(j,i)=dl2p2(j)+dl2n2(j)
		else if(intflag==3)then
		  apl(j,i)=dl2p2(j)-dl2n2(j)
   		else if(intflag==4)then
		  apl(j,i)=dl00(j)
   		else if(intflag==5)then
		  apl(j,i)=dl20(j)
        else
		  stop 'error ingflag'
		endif
	 enddo

	enddo

!ccc   compute the moments

	do j=0,nstr
	 pmom(j)=0.0d0
	 do i=1,NQUAD_TOTAL
       pmom(j)=pmom(j)+w(i)*y(i)*apl(j,i)*(j+0.5d0)	  
	 enddo
	enddo	
	deallocate(pl,apl,dl00,dl20,dl2p2,dl2n2)
	return

	end subroutine calmom_ger

!  GENERLIZED WIGNER D FIT OVER

subroutine calfit(nstr,pmom,pfitdm)
USE BFIT_PARAMETERS
implicit none
integer nstr,ndata,ma, i, j, k, l, nkp
DOUBLE PRECISION,dimension(0:nstr):: pmom,pfitdm
DOUBLE PRECISION,DIMENSION(:),ALLOCATABLE :: b,a,pl
DOUBLE PRECISION,DIMENSION(:,:),ALLOCATABLE ::u,apl
DOUBLE PRECISION cor
DOUBLE PRECISION xpol(2),ypol(2),ytmp(NQUAD_TOTAL),tmp,dytmp

! DGELSD definitions
INTEGER          Mrow, Ncolu, NRHS
INTEGER          LDA, LDB,NLVL
INTEGER,PARAMETER :: LWMAX=50000,SMALLSIZE=25

!     .. Local Scalars ..
INTEGER          INFO, LWORK, RANK
DOUBLE PRECISION RCOND
!     IWORK dimension should be at least 3*MIN(Mrow,Ncolu)*NLVL + 11*MIN(Mrow,Ncolu),
!     where NLVL = MAX( 0, INT( LOG_2( MIN(Mrow,Ncolu)/(SMALLSIZE+1) ) )+1 )
!     and SMALLSIZE = 25
INTEGER,allocatable,dimension(:) :: IWORK !( 3*Mrow*0+11*Mrow )
DOUBLE PRECISION,ALLOCATABLE,dimension(:,:) :: AMATR, BVEC
DOUBLE PRECISION,ALLOCATABLE,dimension(:) :: SMATR
DOUBLE PRECISION :: WORK(LWMAX)

Mrow=NQUAD_TOTAL
Ncolu=nstr+1
LDA = Mrow
LDB = max(1,Mrow,Ncolu)
NRHS=1
RCOND = -1.0
NLVL= MAX( 0, INT( LOG( MIN(Mrow,Ncolu)/(SMALLSIZE+1.0D0) )/LOG(2.0D0) )+1 )

ALLOCATE(IWORK(3*MIN(Mrow,Ncolu)*NLVL + 11*MIN(Mrow,Ncolu)))
ALLOCATE(AMATR(LDA,Ncolu),BVEC(LDB,NRHS),SMATR(Mrow))

	allocate(u(NQUAD_TOTAL,nstr+1),b(NQUAD_TOTAL),a(nstr+1), &
               pl(nstr+1),apl(0:nstr,NQUAD_TOTAL))


! specify weight for each angle
do i=1,NQUAD_TOTAL
  if(i<NQUAD_TOTAL-NQUAD_REGION1/2) then
     ysig(i)=1.0d0
  else
!     ysig(i)=1.0d2
     ysig(i)=1.0d0
  endif
enddo

!ccc   compute all the legendre polynormials at all quadreatures

	do i=1,NQUAD_TOTAL
     call poly_leg(x(i),pl,nstr+1) 
	 do j=0,nstr
	  apl(j,i)=pl(j+1)
	 enddo
	enddo

! use polynomial interpolation to get angles 
!between 0 - angle to be truncated

    xpol(1)=x(NQUAD_TOTAL-NQUAD_REGION1/2-1)
    xpol(2)=x(NQUAD_TOTAL-NQUAD_REGION1/2-2)

    ypol(1)=y(NQUAD_TOTAL-NQUAD_REGION1/2-1)
    ypol(2)=y(NQUAD_TOTAL-NQUAD_REGION1/2-2)

!ccc  compute b and u for the fits 
!open(unit=1,file='testphase',status='new')
	ndata=NQUAD_TOTAL
	ma=nstr+1
    b=0.0d0
	u=0.0d0
	do k=1,NQUAD_TOTAL
    if(k>NQUAD_TOTAL-NQUAD_REGION1/2) then
	  ytmp(k)=ypol(1)+(ypol(2)-ypol(1))*(x(k)-xpol(1))/(xpol(2)-xpol(1))
    else
	  ytmp(k)=y(k)
    endif
!    write(1,*)x(k),ytmp(k)
	 b(k)=1.0d0/ysig(k)
	 do l=1,nstr+1
          u(k,l)=apl(l-1,k)/ytmp(k)/ysig(k)
	 enddo
	enddo 
!close(1)
!ccc  singular value decomposition fitting to derive b
AMATR=u
BVEC=0.0d0
BVEC(1:Mrow,1)=b(1:Mrow)

LWORK = -1
CALL DGELSD( Mrow, Ncolu, NRHS, AMATR, LDA, BVEC, LDB, SMATR, RCOND, RANK, WORK, &
			 LWORK, IWORK, INFO )
LWORK = MIN( LWMAX, INT( WORK( 1 ) ) )

CALL DGELSD( Mrow, Ncolu, NRHS, AMATR, LDA, BVEC, LDB, SMATR, RCOND, RANK, WORK, &
			 LWORK, IWORK, INFO )
a(1:Ncolu)=BVEC(1:Ncolu,1)

!write(*,*)'testing dgelsd in calfit',a(1:Ncolu)

IF( INFO /= 0 )THEN
   IF(INFO>0 )STOP 'The LAPACK SVD failed to converge;'
   IF(INFO<0 )WRITE(*,*)'DGELSD INFO=',INFO,'LWORK=',LWORK,'WORK(1)=',INT(WORK(1))
ENDIF


	do i=0,nstr
      pfitdm(i)=a(i+1)
	enddo

	deallocate(u,b,a,pl,apl)
    DEALLOCATE(IWORK,AMATR,BVEC,SMATR)
	end subroutine calfit

subroutine calmom(nstr,pmom)
USE BFIT_PARAMETERS
implicit none

integer nstr
DOUBLE PRECISION,dimension(0:nstr) :: pmom
DOUBLE PRECISION,dimension(:),ALLOCATABLE:: pl
DOUBLE PRECISION,dimension(:,:),ALLOCATABLE::apl

integer i, j, k

allocate(pl(nstr+1),apl(0:nstr,NQUAD_TOTAL))
!ccc   compute all the legendre polynormials at all quadreatures

do i=1,NQUAD_TOTAL
   call poly_leg(x(i),pl,nstr+1)
   do j=0,nstr
     apl(j,i)=pl(j+1)
   enddo
enddo

!ccc   compute the moments

do j=0,nstr
   pmom(j)=0.0d0
   do i=1,NQUAD_TOTAL
     pmom(j)=pmom(j)+w(i)*y(i)*apl(j,i)*(j+0.5d0)
   enddo
enddo
deallocate(pl,apl)

return
end


SUBROUTINE poly_leg(x, poly_legendre, NORD)
implicit none
INTEGER  NORD
double precision x, poly_legendre( NORD)
INTEGER lord
double precision np1,coeff1,coeff2,twox
 poly_legendre(1)=1.0d0
 poly_legendre(2)=x

if( NORD.le.2)return

twox=2.0d0*x
coeff2=x
np1=1.0d0
do lord=3, NORD
  coeff1=np1
  coeff2=coeff2+twox
  np1=np1+1.0d0
  poly_legendre(lord)=(coeff2* poly_legendre(lord-1)-coeff1* poly_legendre(lord-2))/np1
enddo
!write(*,*)'pleg2 test', nord,poly_legendre(2),poly_legendre(3),poly_legendre(4)
END SUBROUTINE poly_leg


! GENERATE WIGNER D FUNCTIONS GIVEN XJ=COS(ANG)

SUBROUTINE GETDMLlocal(XJ,NUMLORD,DL00,DL20,DL2P2,DL2N2)
IMPLICIT NONE

DOUBLE PRECISION, INTENT(IN) ::XJ
INTEGER, INTENT(IN) ::NUMLORD
DOUBLE PRECISION,INTENT(OUT),DIMENSION(0:NUMLORD)::DL00,DL20,DL2P2,DL2N2

DOUBLE PRECISION,DIMENSION(:,:),ALLOCATABLE :: DML0,WD2,WDN2
DOUBLE PRECISION,DIMENSION(:) ,ALLOCATABLE  ::DMM0FCTR,DMM2FCTR
DOUBLE PRECISION,DIMENSION(:),ALLOCATABLE :: COEF1,COEF2,COEF3,COEF4,COEF5,COEF6

INTEGER ::L,M,MAXLORD,MAXMORD,MMAX

DOUBLE PRECISION :: U,DUP,DUM,DU,ONEMU2,D6,MSQ,SGNF,TWOFM,&
            TMT,DML0LN1,DML2LN1,DMLN2LN1,RTMP,RTMP1

MAXLORD=NUMLORD
MAXMORD=3
ALLOCATE(WD2(0:MAXLORD,0:MAXMORD),    &
         WDN2(0:MAXLORD,0:MAXMORD),   &
         DML0(0:MAXLORD,0:MAXMORD), &
		 DMM0FCTR(0:MAXMORD), DMM2FCTR(0:MAXMORD),&
         COEF1(0:MAXLORD),COEF2(0:MAXLORD),   &
		 COEF3(0:MAXLORD),COEF4(0:MAXLORD),   &
		 COEF5(0:MAXLORD),COEF6(0:MAXLORD)       )

DMM0FCTR(0)=1.0D0
DMM0FCTR(1)=DSQRT(2.0D0)
DO MMAX=2,MAXMORD
RTMP=1.0D0
RTMP1=2.0D0
DO M=1,MMAX-1
  RTMP=RTMP*(1.0D0-DFLOAT(M)/DFLOAT(MMAX))
  RTMP1=RTMP1*(2.0D0-DFLOAT(M)/DFLOAT(MMAX))
ENDDO
DMM0FCTR(MMAX)=DSQRT(RTMP1)/DSQRT(RTMP)
ENDDO

DMM2FCTR(0)=1.0D0
DMM2FCTR(1)=1.0D0
DO MMAX=2,MAXMORD
RTMP=(1.0D0+1.0D0/DFLOAT(MMAX))*(1.0D0+2.0D0/DFLOAT(MMAX))
RTMP1=2.0D0*(1.0D0-1.0D0/DFLOAT(MMAX))
DO M=1,MMAX-1
  RTMP=RTMP*(1.0D0-DFLOAT(M)/DFLOAT(MMAX))
  RTMP1=RTMP1*(2.0D0-DFLOAT(M)/DFLOAT(MMAX))
ENDDO
DMM2FCTR(MMAX)=DSQRT(RTMP1)/DSQRT(RTMP)
ENDDO
  

DO L=0,MAXLORD-1
   COEF1(L)=DFLOAT(2*L+1) 
   COEF2(L)=DFLOAT(L*L)                                            
   COEF3(L)=DFLOAT((L+1)*(L+1))

   COEF4(L)=DFLOAT(L*(L+1))
   COEF5(L)=DFLOAT(L+1)*SQRT(max(0.0d0,(L*L-4.0d0)))
   COEF6(L)=DFLOAT(L)*SQRT(max(0.0d0,((L+1)*(L+1)-4.0d0)))
ENDDO

DML0=0.0D0
DML0(0,0)=1.0D0

WD2=0.0D0
WDN2=0.0D0

  U=XJ
  DUP=1.0D0+U                                              
  DUM=1.0D0-U
  ONEMU2=DUP*DUM                                 
  DU=U*U
  D6=SQRT(6.0D0)*0.25D0
!  LOOP OVER ORDER M

  TWOFM=0.5D0
  SGNF=-1.0D0
  WD2(2,0)=D6*ONEMU2
  WDN2(2,0)=D6*ONEMU2
  
  WD2(2,1)=0.5D0*SQRT(ONEMU2)*DUP
  WDN2(2,1)=-0.5D0*SQRT(ONEMU2)*DUM

  
DO M=0,2
	MSQ=DFLOAT(M*M)
    SGNF=-SGNF
	TWOFM=2.0D0*TWOFM
	TMT=2.0D0*DFLOAT(M)
	
	DML0(M,M)=SGNF*DMM0FCTR(M)*SQRT(ONEMU2**M)/TWOFM

	IF(M>=2)THEN
      WD2(M,M)=SGNF*DMM2FCTR(M)*                     &
              SQRT((DUM**(M-2)) * (DUP**(M+2)))/TWOFM
	  WDN2(M,M)=SGNF*DMM2FCTR(M)*                    &
	          SQRT((DUM**(M+2)) * (DUP**(M-2)))/TWOFM
    ENDIF

    IF(M==MAXLORD-1) CYCLE 


   ! LOOP OVER ORDER L
DO L=M,MAXLORD-1

! RECURRENCE FOR d^l_{m,0}
      IF(L-1<M)THEN 
        DML0LN1=0.0D0
	  ELSE
        DML0LN1=DML0(L-1,M)
      ENDIF
      DML0(L+1,M)=(COEF1(L)*U*DML0(L,M) &
			-SQRT(COEF2(L)-MSQ)*DML0LN1          ) &
			/SQRT(COEF3(L)-MSQ)

! RECURRENCE FOR d^l_{m,2}

IF(L>=2)THEN

   IF(L-1<M)THEN 
     DML2LN1=0.0D0
     DMLN2LN1=0.0D0
   ELSE
     DML2LN1=WD2(L-1,M)
     DMLN2LN1=WDN2(L-1,M)
   ENDIF

   WD2(L+1,M)=(COEF1(L)*(COEF4(L)*U - TMT)*WD2(L,M) &
   - COEF5(L)*SQRT(COEF2(L)-MSQ)*DML2LN1 ) &
   /COEF6(L)/SQRT(COEF3(L)-MSQ)

   WDN2(L+1,M)=(COEF1(L)*(COEF4(L)*U + TMT)*WDN2(L,M) &
   - COEF5(L)*SQRT(COEF2(L)-MSQ)*DMLN2LN1  ) &
   /COEF6(L)/SQRT(COEF3(L)-MSQ)

ENDIF
  
ENDDO  ! LOOP L OVER
ENDDO   ! LOOP M OVER


!  GET DML2P AND DML2N FROM WD AND WD2.
DO L=0,NUMLORD
  DL00(L)=DML0(L,0)
  DL20(L)=DML0(L,2)
  DL2P2(L)=0.5D0*(WD2(L,2) + WDN2(L,2))
  DL2N2(L)=0.5D0*(WD2(L,2) - WDN2(L,2))
ENDDO

DEALLOCATE(DML0,WD2,WDN2,DMM0FCTR,DMM2FCTR,COEF1,COEF2,COEF3,COEF4, &
           COEF5,COEF6)

END SUBROUTINE GETDMLlocal


FUNCTION ABSDIFF(NSTR,PHS,YSIG,APL,COEFFLFIT)
USE BFIT_PARAMETERS,only:NQUAD_TOTAL
implicit none
INTEGER :: NSTR
DOUBLE PRECISION,DIMENSION(0:NSTR,NQUAD_TOTAL)::APL
DOUBLE PRECISION,DIMENSION(NQUAD_TOTAL) ::PHS,YSIG
DOUBLE PRECISION,DIMENSION(NSTR) :: COEFFLFIT

INTEGER IDIM,IDATA
DOUBLE PRECISION :: ABSDIFF,TMP

ABSDIFF=0.0D0
DO IDATA=1,NQUAD_TOTAL
  TMP=0.0D0
  DO IDIM=2,NSTR
    TMP=TMP+COEFFLFIT(IDIM-1)*APL(IDIM,IDATA)
  ENDDO
  TMP=DABS(PHS(IDATA)-TMP)/YSIG(IDATA)
  ABSDIFF=ABSDIFF+TMP
ENDDO

ENDFUNCTION ABSDIFF
