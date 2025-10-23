subroutine gauss_legendre(x1,x2,x,w,order)
implicit none

INTEGER,intent(in) :: order
DOUBLE PRECISION,intent(in):: x1,x2
DOUBLE PRECISION,intent(out):: x(order),w(order)
DOUBLE PRECISION,PARAMETER :: tolerance=2.d-14
DOUBLE PRECISION, PARAMETER :: PI=3.141592653589793238462643383279502884197d0

INTEGER inttmp,jnttmp,np1o2
DOUBLE PRECISION p1,p2,p3,pp,xhlength,xmid,yval,yval1
DOUBLE PRECISION fjnttmp,forder
forder=1.0d0*order

np1o2=(order+1)/2
xmid=0.5d0*(x2+x1)
xhlength=0.5d0*(x2-x1)
yval=1.0d0
yval1=0.0d0
do inttmp=1,np1o2
  yval=cos(PI*(1.0d0*inttmp-.25d0)/(forder+.5d0))
  do while (abs(yval-yval1).gt.tolerance)
	p1=1.d0
	p2=0.d0
	do jnttmp=1,order
	  fjnttmp=1.0d0*jnttmp
	  p3=p2
	  p2=p1
	  p1=((2.d0*fjnttmp-1.d0)*yval*p2-(fjnttmp-1.d0)*p3)/fjnttmp
    enddo
	pp=order*(yval*p1-p2)/(yval*yval-1.d0)
	yval1=yval
	yval=yval1-p1/pp
  enddo

  x(inttmp)=xmid-xhlength*yval
  x(order+1-inttmp)=xmid+xhlength*yval
  w(inttmp)=2.d0*xhlength/((1.d0-yval*yval)*pp*pp)
  w(order+1-inttmp)=w(inttmp)
enddo

end subroutine gauss_legendre

! Pengwang's new math libraries
FUNCTION bisearch(nxx,xx,x)
IMPLICIT NONE
INTEGER, INTENT(IN) :: nxx
DOUBLE PRECISION, DIMENSION(nxx), INTENT(IN) :: xx
DOUBLE PRECISION, INTENT(IN) :: x
INTEGER :: bisearch
INTEGER :: jlo,jmid,jub
LOGICAL :: mono_increase

mono_increase = (xx(nxx) > xx(1))
jlo=0
jub=nxx+1
do while (jub-jlo > 1)
	jmid=(jub+jlo)/2
	if (mono_increase .eqv. (x >= xx(jmid))) then
		jlo=jmid
	else
		jub=jmid
	end if
end do
if (x == xx(1)) then
	bisearch=1
else if (x == xx(nxx)) then
	bisearch=nxx-1
else
	bisearch=jlo
end if
END FUNCTION bisearch

DOUBLE PRECISION FUNCTION Func_UVIP3P(NXX,XX,YY,X,ORDER)
IMPLICIT NONE
INTEGER,intent(in) :: NXX,ORDER
DOUBLE PRECISION,intent(in) :: XX(NXX),YY(NXX)
DOUBLE PRECISION,intent(in) :: X

DOUBLE PRECISION,DIMENSION(1) :: XI,YI
INTEGER :: IU_LO,M_PL,K_LO
integer,external :: bisearch
DOUBLE PRECISION :: RTMP,RTMP1
LOGICAL :: mono_increase,mono_decrease

mono_increase=XX(2)>XX(1)
mono_decrease=XX(2)<XX(1)
IF((mono_increase .AND. (X<=XX(1).OR.X>=XX(NXX))) .OR. &
   (mono_decrease .AND. (X>=XX(1).OR.X<=XX(NXX))))       THEN

if( (mono_increase .and. X<=XX(1)) .or. &
    (mono_decrease .and. X>=XX(1)) ) then
   RTMP=XX(2)-XX(1)
   RTMP1=X-XX(1)
   IF(ABS(RTMP1)<=abs(RTMP))THEN
		Func_UVIP3P=YY(1)+RTMP1*(YY(2)-YY(1))/RTMP
        RETURN
   ELSE
		WRITE(*,*) 'Warning: Func_UVIP3P, X=',X,'OUT OF XX RANGE,XX(1),XX(2)=',XX(1),XX(2)
        WRITE(*,*) 'Use nearest point approximation'
		Func_UVIP3P=YY(1)
        RETURN
   ENDIF
else
	RTMP=XX(NXX-1)-XX(NXX)
	RTMP1=X-XX(NXX)
    IF(ABS(RTMP1)<=abs(RTMP))THEN
		Func_UVIP3P=YY(NXX)+RTMP1*(YY(NXX-1)-YY(NXX))/RTMP
		RETURN
   ELSE
	 WRITE(*,*) 'Func_UVIP3P, X=',X,'OUT OF XX RANGE,XX(NXX-1),XX(NXX)=',XX(NXX-1),XX(NXX)
     WRITE(*,*) 'Use nearest point approximation'
     Func_UVIP3P=YY(NXX)
     RETURN
   ENDIF
endif

RETURN ! FINISH HANDLING OF LINEAR EXTRAPOLATION

ENDIF


M_PL=ORDER+1
XI=X

IU_LO=bisearch(NXX,XX,X)
K_LO=min(max(IU_LO-(M_PL-1)/2,1),NXX+1-M_PL)

CALL UVIP3P(ORDER,M_PL,XX(K_LO),YY(K_LO),1,XI,YI)
Func_UVIP3P=YI(1)

RETURN

END FUNCTION Func_UVIP3P

SUBROUTINE interpl2d(x1a,x2a,ya,mord,nord,x1,x2,y,dy)
implicit none
INTEGER,intent(in):: mord,nord
DOUBLE PRECISION,intent(in):: x1,x2,x1a(mord),x2a(nord),ya(mord,nord)
DOUBLE PRECISION,intent(out):: dy,y
DOUBLE PRECISION,external :: Func_UVIP3P
DOUBLE PRECISION, dimension(:), allocatable:: ymtmp,yntmp

INTEGER j,k,ORDER
ORDER=2
allocate(ymtmp(mord),yntmp(nord))
do j=1,mord
  do k=1,nord
	yntmp(k)=ya(j,k)
  enddo
  ymtmp(j)=Func_UVIP3P(nord,x2a,yntmp,x2,ORDER)
enddo
y=Func_UVIP3P(mord,x1a,ymtmp,x1,ORDER)
deallocate(ymtmp,yntmp)
return
END SUBROUTINE interpl2d


DOUBLE PRECISION FUNCTION TRAPZOID(NXX,XX,YY)
IMPLICIT NONE
! CALCULATE INTEGRATION(YY,d_XX)
INTEGER,INTENT(IN) :: NXX
DOUBLE PRECISION,INTENT(IN),DIMENSION(1:NXX) :: XX,YY
INTEGER :: IXX

TRAPZOID=0.0D0
DO IXX=1,NXX-1
  TRAPZOID=TRAPZOID+0.5D0*(YY(IXX+1)+YY(IXX))*(XX(IXX+1)-XX(IXX))
ENDDO

END FUNCTION TRAPZOID

SUBROUTINE  UVIP3P(NP,ND,XD_IN,YD_IN,NI,XI, YI)

! Univariate Interpolation (Improved Akima Method)

! Hiroshi Akima
! U.S. Department of Commerce, NTIA/ITS
! Version of 89/07/04

! This subroutine performs univariate interpolation.  It is based
! on the improved A method developed by Hiroshi Akima, 'A method
! of univariate interpolation that has the accuracy of a third-
! degree polynomial,' ACM TOMS, vol. xx, pp. xxx-xxx, 19xx.  (The
! equation numbers referred to in the comments below are those in
! the paper.)

! In this method, the interpolating function is a piecewise
! function composed of a set of polynomials applicable to
! successive intervals of the given data points.  This method
! uses third-degree polynomials as the default, but the user has
! an option to use higher-degree polynomial to reduce undulations
! in resulting curves.

! This method has the accuracy of a third-degree polynomial if
! the degree of the polynomials for the interpolating function is
! set to three.

! The input arguments are
!   NP = degree of the polynomials for the interpolating
!        function,
!   ND = number of input data points
!        (must be equal to 2 or greater),
!   XD = array of dimension ND, containing the abscissas of
!        the input data points
!        (must be in a monotoni! increasing order),
!   YD = array of dimension ND, containing the ordinates of
!        the input data points,
!   NI = number of points for which interpolation is desired
!        (must be equal to 1 or greater),
!   XI = array of dimension NI, containing the abscissas of
!        the desired points.

! The output argument is
!   YI = array of dimension NI, where the ordinates of the
!        desired points are to be stored.

! If an integer value smaller than 3 is given to the NP argument,
! this subroutine assumes NP = 3.

! The XI array elements need not be monotonic, but this
! subroutine interpolates faster if the XI array elements are
! given in a monotoni! order.

! If the XI array element is less than XD(1) or greater than
! XD(ND), this subroutine linearly interpolates the YI value.


! Specification statement
IMPLICIT NONE
INTEGER,INTENT(IN) :: NP,ND,NI
DOUBLE PRECISION,INTENT(IN),DIMENSION(ND)::   XD_IN,YD_IN
DOUBLE PRECISION,INTENT(IN),DIMENSION(NI):: XI
DOUBLE PRECISION,INTENT(OUT),DIMENSION(NI):: YI

DOUBLE PRECISION,DIMENSION(:),ALLOCATABLE::   XD,YD

INTEGER :: ID,ID0,ID1,ID2,ID3,IDMD,IDMN,IDMX,II,IINT,IPE,NP0,NPM1,IEPT,IINTPV
DOUBLE PRECISION :: A0,A1,A12,A13,A2,A3,AA0,AA1,B0,B1,DLT,DNM,DX,DY,DY0,DY1,&
					DY2,DY3,EPSLN,PE,RENNM2,RENPM1,SMPEF,SMPEI,SMWTF,SMWTI, &
					SX,SXX,SXY,SY,T0,T1,U,UC,V,VOL,WT,X0,X1,X2,X3,XII,XX,Y0,&
					Y1,Y2,Y3,YP,YP0,YP1
DOUBLE PRECISION,PARAMETER :: TINYNUMBER=1.0D-100

! Error check
   10 IF (ND.LE.1)   GO TO 90
	  IF (NI.LE.0)   GO TO 91

   ALLOCATE(XD(ND),YD(ND))
   IF (XD_IN(2).LT.XD_IN(1)) THEN
		DO ID=1,ND
           XD(ID)=XD_IN(ND-ID+1)
           YD(ID)=YD_IN(ND-ID+1)
		ENDDO
   ELSE
		XD(1:ND)=XD_IN(1:ND)
		YD(1:ND)=YD_IN(1:ND)
   ENDIF


	  DO 11  ID=2,ND
		IF (XD(ID).LE.XD(ID-1)) GO TO 92
   11 CONTINUE
! Branches off special cases.
	  IF (ND.LE.4)   GO TO 50
! General case  --  Five data points of more
! Calculates some local variables.
   20 NP0=MAX(3,NP)
	  NPM1=NP0-1
	  RENPM1=NPM1
	  RENNM2=NP0*(NP0-2)
! Main calculation for the general case
! First (outermost) DO-loop with respect to the desired points
   30 DO 39  II=1,NI
		IF (II.EQ.1)      IINTPV=-1
		XII=XI(II)
! Locates the interval that includes the desired point by binary
! search.
		IF (XII.LE.XD(1))  THEN
		  IINT=0
		ELSE IF (XII.LT.XD(ND))  THEN
		  IDMN=1
		  IDMX=ND
		  IDMD=(IDMN+IDMX)/2
   31     IF (XII.GE.XD(IDMD))  THEN
			IDMN=IDMD
		  ELSE
			IDMX=IDMD
		  END IF
		  IDMD=(IDMN+IDMX)/2
		  IF (IDMD.GT.IDMN)    GO TO 31
		  IINT=IDMD
		ELSE
		  IINT=ND
		END IF
! End of locating the interval of interest
! Interpolation or extrapolation in one of the three subcases
		IF (IINT.LE.0)  THEN
! Subcase 1  --  Linear extrapolation when the abscissa of the
!                desired point is equal to that of the first data
!                point or less.
! Estimates the first derivative when the interval is not the
! same as the one for the previous desired point.  --
! cf. Equation (8)
		  IF (IINT.NE.IINTPV)  THEN
			IINTPV=IINT
			X0=XD(1)
			X1=XD(2)-X0
			X2=XD(3)-X0
			X3=XD(4)-X0
			Y0=YD(1)
			Y1=YD(2)-Y0
			Y2=YD(3)-Y0
			Y3=YD(4)-Y0
			DLT=X1*X2*X3*(X2-X1)*(X3-X2)*(X3-X1)
			A1=(((X2*X3)**2)*(X3-X2)*Y1 &
			  +((X3*X1)**2)*(X1-X3)*Y2 &
			  +((X1*X2)**2)*(X2-X1)*Y3)/DLT
		  END IF
! Evaluates the YI value.
		  YI(II)=Y0+A1*(XII-X0)
! End of Subcase 1
		ELSE IF (IINT.GE.ND)  THEN
! Subcase 2  --  Linear extrapolation when the abscissa of the
!                desired point is equal to that of the last data
!                point or greater.
! Estimates the first derivative when the interval is not the
! same as the one for the previous desired point.  --
! cf. Equation (8)
		  IF (IINT.NE.IINTPV)  THEN
			IINTPV=IINT
			X0=XD(ND)
			X1=XD(ND-1)-X0
			X2=XD(ND-2)-X0
			X3=XD(ND-3)-X0
			Y0=YD(ND)
			Y1=YD(ND-1)-Y0
			Y2=YD(ND-2)-Y0
			Y3=YD(ND-3)-Y0
			DLT=X1*X2*X3*(X2-X1)*(X3-X2)*(X3-X1)
			A1=(((X2*X3)**2)*(X3-X2)*Y1 &
			  +((X3*X1)**2)*(X1-X3)*Y2 &
			  +((X1*X2)**2)*(X2-X1)*Y3)/DLT
		  END IF
! Evaluates the YI value.
		  YI(II)=Y0+A1*(XII-X0)
! End of Subcase 2
		ELSE
! Subcase 3  --  Interpolation when the abscissa of the desired
!                point is  between those of the first and last
!                data points.
! Calculates the coefficients of the third-degree polynomial (for
! NP.LE.3) or the factors for the higher-degree polynomials (for
! NP.GT.3), when the interval is not the same as the one for the
! previous desired point.
		  IF (IINT.NE.IINTPV)  THEN
			IINTPV=IINT
! The second DO-loop with respect to the two endpoints of the
! interval
			DO 37  IEPT=1,2
! Calculates the estimate of the first derivative at an endpoint.
! Initial setting for calculation
			  ID0=IINT+IEPT-1
			  X0=XD(ID0)
			  Y0=YD(ID0)
			  SMPEF=0.0d0
			  SMWTF=0.0d0
			  SMPEI=0.0d0
			  SMWTI=0.0d0
! The third (innermost) DO-loop with respect to the four primary
! estimate of the first derivative
			  DO 36  IPE=1,4
! Selects point numbers of four consecutive data points for
! calculating the primary estimate of the first derivative.
				IF (IPE.EQ.1)  THEN
				  ID1=ID0-3
				  ID2=ID0-2
				  ID3=ID0-1
				ELSE IF (IPE.EQ.2)  THEN
				  ID1=ID0+1
				ELSE IF (IPE.EQ.3)  THEN
				  ID2=ID0+2
				ELSE
				  ID3=ID0+3
				END IF
! Checks if any point number falls outside the legitimate range
! (between 1 and ND).  Skips calculation of the primary estimate
! if any does.
				IF (ID1.LT.1.OR.ID2.LT.1.OR.ID3.LT.1.OR. &
				   ID1.GT.ND.OR.ID2.GT.ND.OR.ID3.GT.ND) &
					GO TO 36
! Calculates the primary estimate of the first derivative  --
! cf. Equation (8)
				X1=XD(ID1)-X0
				X2=XD(ID2)-X0
				X3=XD(ID3)-X0
				Y1=YD(ID1)-Y0
				Y2=YD(ID2)-Y0
				Y3=YD(ID3)-Y0
				DLT=X1*X2*X3*(X2-X1)*(X3-X2)*(X3-X1)
				PE=(((X2*X3)**2)*(X3-X2)*Y1 &
				  +((X3*X1)**2)*(X1-X3)*Y2 &
				  +((X1*X2)**2)*(X2-X1)*Y3)/DLT
! Calculates the volatility factor, VOL, and distance factor,
! SXX, for the primary estimate.  --  cf. Equations (9) and (11)
				SX=X1+X2+X3
				SY=Y1+Y2+Y3
				SXX=X1*X1+X2*X2+X3*X3
				SXY=X1*Y1+X2*Y2+X3*Y3
				DNM=4.0d0*SXX-SX*SX
				B0=(SXX*SY-SX*SXY)/DNM
				B1=(4.0d0*SXY-SX*SY)/DNM
				DY0=-B0
				DY1=Y1-(B0+B1*X1)
				DY2=Y2-(B0+B1*X2)
				DY3=Y3-(B0+B1*X3)
				VOL=DY0*DY0+DY1*DY1+DY2*DY2+DY3*DY3
! Calculates the EPSLN value, which is used to decide whether or
! not the volatility factor, VOL, is essentially zero.
				EPSLN=(YD(ID0)**2+YD(ID1)**2  &
					 +YD(ID2)**2+YD(ID3)**2)*1.0D-12
				EPSLN=MAX(EPSLN,TINYNUMBER)
! Accumulates the weighted primary estimates.  --
! cf. Equations (13) and (14)
				IF (VOL*SXX.GT.EPSLN)  THEN
! - For finite weight.
				  WT=1.0d0/(VOL*SXX)
				  SMPEF=SMPEF+PE*WT
				  SMWTF=SMWTF+WT
				ELSE
! - For infinite weight.
				  SMPEI=SMPEI+PE
				  SMWTI=SMWTI+1.0d0
				END IF
   36         CONTINUE
! End of the third DO-loop
! Calculates the final estimate of the first derivative.  --
! cf. Equation (14)
			  IF (SMWTI.LT.0.5d0)  THEN
! - When no infinite weights exist.
				YP=SMPEF/SMWTF
			  ELSE
! - When infinite weights exist.
				YP=SMPEI/SMWTI
			  END IF
			  IF (IEPT.EQ.1)  THEN
				YP0=YP
			  ELSE
				YP1=YP
			  END IF
! End of the calculation of the estimate of the first derivative
! at an endpoint
   37       CONTINUE
! End of the second DO-loop
			IF (NP0.LE.3)  THEN
! Calculates the coefficients of the third-degree polynomial
! (when NP.LE.3).  --  cf. Equation (4)
			  DX=XD(IINT+1)-XD(IINT)
			  DY=YD(IINT+1)-YD(IINT)
			  A0=YD(IINT)
			  A1=YP0
			  YP1=YP1-YP0
			  YP0=YP0-DY/DX
			  A2=-(3.0d0*YP0+YP1)/DX
			  A3= (2.0d0*YP0+YP1)/(DX*DX)
			ELSE
! Calculates the factors for the higher-degree polynomials
! (when NP.GT.3).  --  cf. Equation (20)
			  DX=XD(IINT+1)-XD(IINT)
			  DY=YD(IINT+1)-YD(IINT)
			  T0=YP0*DX-DY
			  T1=YP1*DX-DY
			  AA0= (T0+RENPM1*T1)/RENNM2
			  AA1=-(RENPM1*T0+T1)/RENNM2
			END IF
		  END IF
! End of the calculation of the coefficients of the third-degree
! polynomial (when NP.LE.3) or the factors for the higher-degree
! polynomials (when NP.GT.3), when the interval is not the same
! as the one for the previous desired point.
! Evaluates the YI value.
		  IF (NP0.LE.3)  THEN
! - With a third-degree polynomial.  --  cf. Equation (3)
			XX=XII-XD(IINT)
			YI(II)=A0+XX*(A1+XX*(A2+XX*A3))
		  ELSE
! - With a higher-degree polynomial.  --  cf. Equation (19)
			U=(XII-XD(IINT))/DX
			UC=1.0d0-U
			V=AA0*((U**NP0)-U)+AA1*((UC**NP0)-UC)
			YI(II)=YD(IINT)+DY*U+V
		  END IF
! End of Subcase 3
		END IF
   39 CONTINUE
! End of the first DO-loop
! End of general case
	  DEALLOCATE(XD,YD)
	  RETURN
! Special cases  --  Four data points or less
! Preliminary processing for the special cases
   50 X0=XD(1)
	  Y0=YD(1)
	  X1=XD(2)-X0
	  Y1=YD(2)-Y0
	  IF (ND.EQ.2)   GO TO 60
	  X2=XD(3)-X0
	  Y2=YD(3)-Y0
	  IF (ND.EQ.3)   GO TO 70
	  X3=XD(4)-X0
	  Y3=YD(4)-Y0
	  GO TO 80
! Special Case 1  --  Two data points
! (Linear interpolation and extrapolation)
   60 A1=Y1/X1
	  DO 61  II=1,NI
		YI(II)=Y0+A1*(XI(II)-X0)
   61 CONTINUE
! End of Special Case 1
		DEALLOCATE(XD,YD)
	  RETURN
! Special Case 2  --  Three data points
! (Quadrati! interpolation and linear extrapolation)
   70 DLT=X1*X2*(X2-X1)
	  A1=(X2*X2*Y1-X1*X1*Y2)/DLT
	  A2=(X1*Y2-X2*Y1)/DLT
	  A12=2.0d0*A2*X2+A1
	  DO 71  II=1,NI
		XX=XI(II)-X0
		IF (XX.LE.0.0d0)  THEN
		  YI(II)=Y0+A1*XX
		ELSE IF (XX.LT.X2) THEN
		  YI(II)=Y0+XX*(A1+XX*A2)
		ELSE
		  YI(II)=Y0+Y2+A12*(XX-X2)
		END IF
   71 CONTINUE
! End of Special Case 2
	  DEALLOCATE(XD,YD)
	  RETURN
! Special Case 3  --  Four data points
! (Cubi! interpolation and linear extrapolation)
   80 DLT=X1*X2*X3*(X2-X1)*(X3-X2)*(X3-X1)
	  A1=(((X2*X3)**2)*(X3-X2)*Y1 &
		+((X3*X1)**2)*(X1-X3)*Y2 &
		+((X1*X2)**2)*(X2-X1)*Y3)/DLT
	  A2=(X2*X3*(X2*X2-X3*X3)*Y1 &
		+X3*X1*(X3*X3-X1*X1)*Y2 &
		+X1*X2*(X1*X1-X2*X2)*Y3)/DLT
	  A3=(X2*X3*(X3-X2)*Y1 &
		+X3*X1*(X1-X3)*Y2 &
		+X1*X2*(X2-X1)*Y3)/DLT
	  A13=(3.0d0*A3*X3+2.0d0*A2)*X3+A1
	  DO 81  II=1,NI
		XX=XI(II)-X0
		IF (XX.LE.0.0d0)  THEN
		  YI(II)=Y0+A1*XX
		ELSE IF (XX.LT.X3) THEN
		  YI(II)=Y0+XX*(A1+XX*(A2+XX*A3))
		ELSE
		  YI(II)=Y0+Y3+A13*(XX-X3)
		END IF
   81 CONTINUE
! End of Special Case 3
	  DEALLOCATE(XD,YD)
	  RETURN
! Error exit
   90 WRITE (*,99090) ND
	  GO TO 99
   91 WRITE (*,99091) NI
	  GO TO 99
   92 WRITE (*,99092)ND,XD(1),XD(2),ID,XD(ID-1),XD(ID)
   99 WRITE (*,99099)
	  DEALLOCATE(XD,YD)
	  RETURN
! Format statements for error messages
99090 FORMAT (1X/ ' ***   Insufficient data points.',7X,'ND =',I3)
99091 FORMAT (1X/ ' ***   No desired points.',7X,'NI =',I3)
99092 FORMAT (1X/ ' ***   Two data points identical or out of ','sequence.'/ &
	   7X,'ND,XD(1),XD(2),ID, XD(ID-1), XD(ID) =',I5,2F10.3,I5,2F10.3)
99099 FORMAT (' Error detected in the UVIP3P subroutine'/)
	  ENDSUBROUTINE  UVIP3P



SUBROUTINE bisection(func, x1, x2, root, tol)
  IMPLICIT NONE
  DOUBLE PRECISION, INTENT(INout) :: x1, x2, tol
  DOUBLE PRECISION, INTENT(OUT) :: root
  INTEGER, PARAMETER :: max_iter=100
  INTEGER :: iter
  DOUBLE PRECISION :: fx1, fx2, froot, xmid

  INTERFACE
	  DOUBLE PRECISION FUNCTION func(x)
		  DOUBLE PRECISION, INTENT(IN) :: x
      END FUNCTION func
  END INTERFACE

  fx1 = func(x1)
  fx2 = func(x2)

  IF (fx1 * fx2 >= 0.0d0) THEN
	STOP "Root not bracketed"
	RETURN
  END IF

  DO iter = 1, max_iter
	xmid = (x1 + x2) / 2.0d0
	froot = func(xmid)

	IF (ABS(froot) < tol) THEN
	  root = xmid
	  RETURN
	END IF

	IF (fx1 * froot < 0.0d0) THEN
	  x2 = xmid
	  fx2 = froot
	ELSE
	  x1 = xmid
	  fx1 = froot
	END IF
  END DO

  PRINT*, "Max iterations reached"
END SUBROUTINE bisection

SUBROUTINE Err_MSG(string)
CHARACTER(LEN=*), INTENT(IN) :: string
write (*,*) 'Error Message: ',string
STOP
END SUBROUTINE Err_MSG



SUBROUTINE qsort2a(NDIM,frr1,frr2)
IMPLICIT NONE
INTEGER,INTENT(IN):: NDIM
DOUBLE PRECISION,DIMENSION(NDIM),INTENT(INOUT):: frr1,frr2

INTEGER, PARAMETER :: MSIZE=7,NSTACK=50
INTEGER,DIMENSION(NSTACK):: arr_stack

INTEGER :: itmp,idr,jtmp,pstack,ktmp,ltmp
DOUBLE PRECISION :: f1t,f2t,temp

pstack=0
ltmp=1
idr=NDIM

largeloop: do

if(idr-ltmp < MSIZE)then

  do jtmp=ltmp+1,idr
	f1t=frr1(jtmp)
	f2t=frr2(jtmp)
	do itmp=jtmp-1,1,-1
	  if(frr1(itmp)<=f1t) exit
	  frr1(itmp+1)=frr1(itmp)
	  frr2(itmp+1)=frr2(itmp)
	enddo
    frr1(itmp+1)=f1t
	frr2(itmp+1)=f2t
  enddo

  if(pstack==0)return

  idr=arr_stack(pstack)
  ltmp=arr_stack(pstack-1)
  pstack=pstack-2

else

  ktmp=(ltmp+idr)/2
  temp=frr1(ktmp)
  frr1(ktmp)=frr1(ltmp+1)
  frr1(ltmp+1)=temp
  temp=frr2(ktmp)
  frr2(ktmp)=frr2(ltmp+1)
  frr2(ltmp+1)=temp
  if(frr1(ltmp+1)>frr1(idr))then
	temp=frr1(ltmp+1)
	frr1(ltmp+1)=frr1(idr)
	frr1(idr)=temp
	temp=frr2(ltmp+1)
	frr2(ltmp+1)=frr2(idr)
	frr2(idr)=temp
  endif

  if(frr1(ltmp)>frr1(idr))then
	temp=frr1(ltmp)
	frr1(ltmp)=frr1(idr)
	frr1(idr)=temp
	temp=frr2(ltmp)
	frr2(ltmp)=frr2(idr)
	frr2(idr)=temp
  endif

  if(frr1(ltmp+1)>frr1(ltmp))then
	temp=frr1(ltmp+1)
	frr1(ltmp+1)=frr1(ltmp)
	frr1(ltmp)=temp
	temp=frr2(ltmp+1)
	frr2(ltmp+1)=frr2(ltmp)
	frr2(ltmp)=temp
  endif

  itmp=ltmp+1
  jtmp=idr
  f1t=frr1(ltmp)
  f2t=frr2(ltmp)


  itmploop : do
	  itmp=itmp+1

	  if(frr1(itmp)<f1t) cycle itmploop

	  jtmp=jtmp-1
	  do while (frr1(jtmp)>f1t)
		  jtmp=jtmp-1
	  enddo

	  if(jtmp<itmp) exit itmploop

	  temp=frr1(itmp)
	  frr1(itmp)=frr1(jtmp)
	  frr1(jtmp)=temp
	  temp=frr2(itmp)
	  frr2(itmp)=frr2(jtmp)
	  frr2(jtmp)=temp
  enddo itmploop

  frr1(ltmp)=frr1(jtmp)
  frr1(jtmp)=f1t
  frr2(ltmp)=frr2(jtmp)
  frr2(jtmp)=f2t
  pstack=pstack+2

  if(pstack>NSTACK) stop 'NSTACK is too small in qsort2a'

  if(idr-itmp+1 >= jtmp-ltmp)then
	arr_stack(pstack)=idr
	arr_stack(pstack-1)=itmp
	idr=jtmp-1
  else
	arr_stack(pstack)=jtmp-1
	arr_stack(pstack-1)=ltmp
	ltmp=itmp
  endif

endif

enddo largeloop

ENDSUBROUTINE qsort2a

SUBROUTINE REMOVE_DUP(NARRAYINPUT,ARRAYINPUT,NARRAYOUTPUT,ARRAYOUTPUT)
implicit none
integer,intent(in) :: NARRAYINPUT
integer,intent(out) :: NARRAYOUTPUT
DOUBLE PRECISION,DIMENSION(NARRAYINPUT),intent(inout) :: ARRAYINPUT  ! The input
DOUBLE PRECISION,DIMENSION(NARRAYINPUT),intent(inout) :: ARRAYOUTPUT

integer :: itmp, jtmp

ARRAYINPUT=ARRAYOUTPUT

NARRAYOUTPUT = 1
ARRAYOUTPUT(1) = ARRAYINPUT(1)
LOOP_SEARCH: do itmp=2,NARRAYINPUT
do jtmp=1,NARRAYOUTPUT
  if (ABS(ARRAYOUTPUT(jtmp) - ARRAYINPUT(itmp))<1.0D-6) then
! Found a match, restart searching again
	cycle LOOP_SEARCH
  endif
end do
! No match found, add it to the output
NARRAYOUTPUT = NARRAYOUTPUT + 1
ARRAYOUTPUT(NARRAYOUTPUT) = ARRAYINPUT(itmp)
end do LOOP_SEARCH

END SUBROUTINE REMOVE_DUP
