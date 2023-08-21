
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
!c           (real*8 number starting at dimension0, 
!c           1-d vector with length 0:300) 
!c                            -------------
!c   pfitdm  the fitted "moments" which DISORT needs for PMOM
!c           (real*8 number starting at dimension0,
!c           1-d vector with length 0:300) 
!c                            -------------
!c   pfit and ftrunc    in case you do not use disort, this is  
!c           the "moments" from the delta-fit after delta-truncation 
!c           with truncation factor ftrunc
!c 	    (ftrunc: real*8)
!c           (pfit: real*8 number starting at dimension0, 
!c           1-d vector with length 0:300) 
!c    ftrunc: traunction factor
!c----------------------------------------------------------------------------
MODULE BFIT_PARAMETERS
INTEGER,PARAMETER ::NQUAD_REGION1=1000,NQUAD_REGION2=1000,&
                 NQUAD_TOTAL=NQUAD_REGION1+NQUAD_REGION2
REAL*8,PARAMETER :: pi=3.141592653589793238462643383279502884197d0
real*8,dimension(NQUAD_REGION1):: x1,w1,y1
real*8,dimension(NQUAD_REGION2):: x2,w2,y2
real*8,dimension(NQUAD_TOTAL):: x,w,xx,y,ysig

CONTAINS
SUBROUTINE BFIT_QUAD_SETUP(angtrun)
REAL*8 :: angtrun
call gauleg(angtrun,1.0d0,x1,w1,NQUAD_REGION1/2)
call gauleg(0.0d0,angtrun,x2,w2,NQUAD_REGION2/2)
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
    real*8,dimension(0:NSTR):: pmom,pfit,pfitdm
    real*8,dimension(1:NN):: ang,phs

    integer :: deltam,deltamlocal
    real*8 :: angtrun,ftrunc,ctrunc,sigma_sq
    real*8 :: POLINT_SIMPLE
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
      y(i)=POLINT_SIMPLE(NN,ang,phs,xx(i),2)
    enddo

!ccc  compute the moments
    call calmom(nstr,pmom)

    if((pmom(nstr-1)/(2*nstr-1) < pmom(nstr)/(2*nstr+1) .or. pmom(nstr)<1.0e-5) &
        .and. deltamlocal==1)then
       write(*,*) 'pmom(nstr-1) < pmom(nstr) .or. pmom(nstr)<1.0e-5'
       write(*,*) 'Delta M is used for this case'
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
       write(*,*) 'pmom(0)=', pmom(0)
       write(*,*) 'warning pmom(0) is not equal to 1'
       write(*,*) 'double check your phase function input'
!       if (abs(pmom(0)-1.0d0) .gt.0.05) stop
       write(*,*) 'Guessing it is due to infinite forward scattering peak'
       write(*,*) 'Delta fit is used for this case'
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
    real*8,dimension(0:NSTR):: pmom,pfit,pfitdm
    real*8,dimension(1:NN):: ang,phs,phssig
    real*8 POLINT_SIMPLE
    real*8 :: angtrun
    integer :: DELTAM
!ccc   ang are in degrees (Theta), not cos(Theta)


	if (abs(ang(NN)).le.1.d0 .and. abs(ang(1)).le.1.d0) then
	do i=1,NN
        ang(i)=acos(ang(i))*180.d0/pi
	enddo
	endif

! SPLINE INTERPOLATION
!    call myspline(NN,ang,phs,NQUAD_TOTAL,xx,y)
!    call myspline(NN,ang,phssig,NQUAD_TOTAL,xx,ysig)
! or use LINEAR INTERPOLATION
    do i=1,NQUAD_TOTAL
      y(i)=POLINT_SIMPLE(NN,ang,phs,xx(i),2)
      ysig(i)=POLINT_SIMPLE(NN,ang,phssig,xx(i),2)
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

real*8,dimension(0:nstr):: pmom,pfitdm

real*8 ABSDIFF,tmp,cor

real*8,DIMENSION(:),ALLOCATABLE :: pl,dl00,&
                    dl20,dl2p2,dl2n2,b,a
real*8,DIMENSION(:,:),ALLOCATABLE :: apl,u

INTERFACE
SUBROUTINE GETDMLlocal(XJ,NUMLORD,DL00,DL20,DL2P2,DL2N2)
IMPLICIT NONE

real*8, INTENT(IN) ::XJ
INTEGER, INTENT(IN) ::NUMLORD
real*8,INTENT(OUT),DIMENSION(0:NUMLORD)::DL00,DL20,DL2P2,DL2N2

END SUBROUTINE GETDMLlocal
END INTERFACE

INTERFACE
	SUBROUTINE gsh_svdfit(a,u,b,chisq)
	USE nrtype; USE nrutil, ONLY : assert_eq,vabs
	USE nr, ONLY : svbksb,svdcmp
	IMPLICIT NONE
	REAL(DP), DIMENSION(:), INTENT(OUT) :: a
	REAL(DP), DIMENSION(:), INTENT(IN) :: b
	REAL(DP), DIMENSION(:,:), INTENT(IN) :: u
	REAL(DP), INTENT(OUT) :: chisq
      END SUBROUTINE gsh_svdfit
ENDINTERFACE

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

!    call svdfit(ndata,a,ma,u,b,cor)
    call gsh_svdfit(a,u,b,cor)

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
end


 	subroutine calmom_ger(intflag,nstr,pmom,DELTAM)
    USE BFIT_PARAMETERS

    real*8,dimension(0:nstr) :: pmom

	integer intflag,nstr,DELTAM
    integer :: i, j, k
    real*8 :: ftrunc,sigma_sq,ctrunc
    real*8,DIMENSION(:),ALLOCATABLE :: pl,dl00,dl20,dl2p2,dl2n2
    real*8,DIMENSION(:,:),ALLOCATABLE :: apl

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

	end

!  GENERLIZED WIGNER D FIT OVER

	subroutine calfit(nstr,pmom,pfitdm)
    USE BFIT_PARAMETERS
    integer nstr,ndata,ma, i, j, k, l, nkp
    real*8,dimension(0:nstr):: pmom,pfitdm
    real*8,DIMENSION(:),ALLOCATABLE :: b,a,pl
    real*8,DIMENSION(:,:),ALLOCATABLE ::u,apl
    real*8 cor
	real*8 xpol(2),ypol(2),ytmp(NQUAD_TOTAL),tmp,dytmp

    INTERFACE
	SUBROUTINE gsh_svdfit(a,u,b,chisq)
	  USE nrtype; USE nrutil, ONLY : assert_eq,vabs
	  USE nr, ONLY : svbksb,svdcmp
	  IMPLICIT NONE
	  REAL(DP), DIMENSION(:), INTENT(OUT) :: a
	  REAL(DP), DIMENSION(:), INTENT(IN) :: b
	  REAL(DP), DIMENSION(:,:), INTENT(IN) :: u
	  REAL(DP), INTENT(OUT) :: chisq
      END SUBROUTINE gsh_svdfit
    ENDINTERFACE

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
     call fleg(x(i),pl,nstr+1) 
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
	  call polint(xpol,ypol,2,x(k),tmp,dytmp)
	  ytmp(k)=tmp
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

!    call svdfit(ndata,a,ma,u,b,cor)
    call gsh_svdfit(a,u,b,cor)

	do i=0,nstr
      pfitdm(i)=a(i+1)
	enddo

	deallocate(u,b,a,pl,apl)

	end

subroutine calmom(nstr,pmom)
USE BFIT_PARAMETERS
integer nstr
real*8,dimension(0:nstr) :: pmom
real*8,dimension(:),ALLOCATABLE:: pl
real*8,dimension(:,:),ALLOCATABLE::apl

integer i, j, k

allocate(pl(nstr+1),apl(0:nstr,NQUAD_TOTAL))
!ccc   compute all the legendre polynormials at all quadreatures

do i=1,NQUAD_TOTAL
   call fleg(x(i),pl,nstr+1)
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

	SUBROUTINE gsh_svdfit(a,u,b,chisq)
	USE nrtype; USE nrutil, ONLY : assert_eq,vabs
	USE nr, ONLY : svbksb,svdcmp
	IMPLICIT NONE
	REAL(DP), DIMENSION(:), INTENT(OUT) :: a
	REAL(DP), DIMENSION(:), INTENT(IN) :: b
	REAL(DP), DIMENSION(:,:), INTENT(IN) :: u
	REAL(DP), INTENT(OUT) :: chisq

	REAL(DP), DIMENSION(size(a)) :: w
	REAL(DP), DIMENSION(size(a),size(a)) :: v
	REAL(DP), DIMENSION(size(u,1),size(u,2)) :: usav

	REAL(DP), PARAMETER :: TOL=1.0e-5_DP
	INTEGER(I4B) :: ma,n
	n=size(b)
	ma=size(a)
	usav=u
	call svdcmp(usav,w,v)
	where (w < TOL*maxval(w)) w=0.0
	call svbksb(usav,w,v,b,a)
	chisq=vabs(matmul(u,a)-b)**2
	END SUBROUTINE gsh_svdfit


      SUBROUTINE sort2(n,arr,brr) 
      INTEGER n,M,NSTACK 
      real*8 arr(n),brr(n) 
      PARAMETER (M=7,NSTACK=50) 
      INTEGER i,ir,j,jstack,k,l,istack(NSTACK) 
      real*8 a,b,temp 

      jstack=0 

      l=1 

      ir=n 

1     if(ir-l.lt.M)then 

        do j=l+1,ir 
          a=arr(j) 
          b=brr(j) 
          do i=j-1,1,-1 
            if(arr(i).le.a)goto 2 
            arr(i+1)=arr(i) 
            brr(i+1)=brr(i) 
          enddo
          i=0 
2         arr(i+1)=a 
          brr(i+1)=b 
        enddo

        if(jstack.eq.0)return 

        ir=istack(jstack) 
        l=istack(jstack-1) 
        jstack=jstack-2 

      else 

        k=(l+ir)/2 
        temp=arr(k) 
        arr(k)=arr(l+1) 
        arr(l+1)=temp 
        temp=brr(k) 
        brr(k)=brr(l+1) 
        brr(l+1)=temp 
        if(arr(l+1).gt.arr(ir))then 
          temp=arr(l+1) 
          arr(l+1)=arr(ir) 
          arr(ir)=temp 
          temp=brr(l+1) 
          brr(l+1)=brr(ir) 
          brr(ir)=temp 
        endif 

        if(arr(l).gt.arr(ir))then 
          temp=arr(l) 
          arr(l)=arr(ir) 
          arr(ir)=temp 
          temp=brr(l) 
          brr(l)=brr(ir) 
          brr(ir)=temp 
        endif 

        if(arr(l+1).gt.arr(l))then 
          temp=arr(l+1) 
          arr(l+1)=arr(l) 
          arr(l)=temp 
          temp=brr(l+1) 
          brr(l+1)=brr(l) 
          brr(l)=temp 
        endif 

        i=l+1 
        j=ir 
        a=arr(l) 
        b=brr(l) 

3       continue 

          i=i+1 

        if(arr(i).lt.a)goto 3 

4       continue 

          j=j-1 

        if(arr(j).gt.a)goto 4 

        if(j.lt.i)goto 5 

        temp=arr(i) 
        arr(i)=arr(j) 
        arr(j)=temp 
        temp=brr(i) 
        brr(i)=brr(j) 
        brr(j)=temp 

        goto 3 

5       arr(l)=arr(j) 
        arr(j)=a 
        brr(l)=brr(j) 
        brr(j)=b 
        jstack=jstack+2 

        if(jstack.gt.NSTACK)stop 'NSTACK too small in sort2' 

        if(ir-i+1.ge.j-l)then 
          istack(jstack)=ir 
          istack(jstack-1)=i 
          ir=j-1 
        else 
          istack(jstack)=j-1 
          istack(jstack-1)=l 
          l=i 
        endif 

      endif 

      goto 1 

      END 

!C  (C) Copr. 1986-92 Numerical Recipes Software 71a. 
 

      SUBROUTINE fleg(x,pl,nl) 
      INTEGER nl 
      real*8 x,pl(nl) 
      INTEGER j 
      real*8 d,f1,f2,twox 
      pl(1)=1.0d0
      pl(2)=x 

      if(nl.gt.2) then 
        twox=2.0d0*x 
        f2=x 
        d=1.0d0 
        do j=3,nl 
          f1=d 
          f2=f2+twox 
          d=d+1.0d0 
          pl(j)=(f2*pl(j-1)-f1*pl(j-2))/d 
        enddo
      endif 
      return 
      END 

! GENERATE WIGNER D FUNCTIONS GIVEN XJ=COS(ANG)

SUBROUTINE GETDMLlocal(XJ,NUMLORD,DL00,DL20,DL2P2,DL2N2)
IMPLICIT NONE

real*8, INTENT(IN) ::XJ
INTEGER, INTENT(IN) ::NUMLORD
real*8,INTENT(OUT),DIMENSION(0:NUMLORD)::DL00,DL20,DL2P2,DL2N2

real*8,DIMENSION(:,:),ALLOCATABLE :: DML0,WD2,WDN2
real*8,DIMENSION(:) ,ALLOCATABLE  ::DMM0FCTR,DMM2FCTR
real*8,DIMENSION(:),ALLOCATABLE :: COEF1,COEF2,COEF3,COEF4,COEF5,COEF6

INTEGER ::L,M,MAXLORD,MAXMORD,MMAX

real*8 :: U,DUP,DUM,DU,ONEMU2,D6,MSQ,SGNF,TWOFM,&
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
REAL*8,DIMENSION(0:NSTR,NQUAD_TOTAL)::APL
REAL*8,DIMENSION(NQUAD_TOTAL) ::PHS,YSIG
REAL*8,DIMENSION(NSTR) :: COEFFLFIT

INTEGER IDIM,IDATA
REAL*8 :: ABSDIFF,TMP

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
