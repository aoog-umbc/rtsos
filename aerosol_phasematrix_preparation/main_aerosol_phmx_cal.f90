PROGRAM AERSL_PHMX
!USE auxiliary_dir_readin
USE MIE_PHMX_CAL
USE PACE_INSTRUMENT_DESIGN
USE HDF5
USE DUST_DATA
IMPLICIT NONE
INTEGER :: WV_SEG_FLAG
REAL*8, ALLOCATABLE,DIMENSION(:,:) ::MRR1_Save,MRI1_Save,MRR2_Save,MRI2_Save,MRRD_save,MRID_save

INTEGER :: NUMMIEUSE,NUMMIERT,NWV_BAND_START,NWV_BAND_END
INTEGER :: IMIE,NMODE
REAL*8 :: POLINT_SIMPLE,TRAPZOID
INTEGER:: IAEROSOL, IRH, IWV ,INTTMP
REAL*8, ALLOCATABLE,DIMENSION(:) :: REFF1_Save, REFF2_Save, VEFF1_Save, VEFF2_Save, &
     ARSLND1_Save, ARSLND2_Save,ARSLNDDS,REFFDS,VEFFDS
REAL*8:: REFFD,VEFFD,ARSLNDD,Reff_Cloud,Veff_Cloud,MRR1_Cloud,MRI1_Cloud
LOGICAL :: HYSPECTRAL_FLAG, MONOCHROMATIC_FLA
REAL*8 :: rf1, rf2, rf3, FRACS,FMFRAC, r0f,r0c, rhi, r0dl, r0ws,r0bc,r0s, r0ss, sigf,sigc,dfrac,dsfrac
LOGICAL :: file_e
integer time_array_0(8), time_array_1(8)
real start_time, finish_time
Integer :: flex_flag, MIX_FLAG
real*8, dimension(19) :: inputs21
INTEGER*4 :: NARGS,IARGC, IVAR,IREFF

CHARACTER*360 :: CFILE1,CFILETMP,CFILE_AP
CHARACTER(LEN=360) :: INFILE   
CHARACTER(LEN=360) :: OUTFILE
CHARACTER(LEN=360) :: aux_dir
call date_and_time(values=time_array_0)
start_time = time_array_0 (5) * 3600 + time_array_0 (6) * 60 &
                             + time_array_0 (7) + 0.001 * time_array_0 (8)

NARGS = IARGC()
IF(NARGS.LT.1) THEN
    WRITE(*,*) ''
    WRITE(*,*) '***ERROR***'
    WRITE(*,*) 'TOO FEW INPUTS'
    WRITE(*,*) '***ERROR***'
    WRITE(*,*) ''
    WRITE(*,*) 'USEAGE:'
    WRITE(*,*) 'Aerosol_Phmx_Cal.exe input.file'
    WRITE(*,*) ''
    STOP
ENDIF

write(*,*) 'Start of program PACE_Aerosol_Model'

CALL GETARG(1,INFILE)

OPEN(unit=1,file=INFILE,status='old')

READ(1,*)IAEROSOL
IF(IAEROSOL>0) THEN
   READ(1,*)IRH
   READ(1,*)WV_SEG_FLAG
   READ(1,'(A)')aux_dir
   READ(1,'(A)')OUTFILE
ENDIF

IF(IAEROSOL==-98) THEN ! water clouds
   READ(1,*)Reff_Cloud
   READ(1,*)Veff_Cloud
   READ(1,*)WV_SEG_FLAG
   READ(1,'(A)')aux_dir
   READ(1,'(A)')OUTFILE
   NMODE=1
ENDIF

IF(IAEROSOL==-96) THEN ! mono-modal aerosol with spectrally flat mr and mi inputs
   READ(1,*)Reff_Cloud
   READ(1,*)Veff_Cloud
   READ(1,*)MRR1_Cloud
   READ(1,*)MRI1_Cloud
   READ(1,*)WV_SEG_FLAG
   READ(1,'(A)')aux_dir
   READ(1,'(A)')OUTFILE
   NMODE=1
ENDIF


IF(IAEROSOL==-99)THEN
   READ(1,*)NMODE
   IF(NMODE==2)THEN 
      READ(1,*)FMFRAC
      READ(1,*)FRACS
      READ(1,*)rf1
      READ(1,*)rf2
      READ(1,*)rf3
      READ(1,*)MIX_FLAG
      READ(1,*)IVAR
      READ(1,*)IREFF
      READ(1,*)RHI
      READ(1,*)r0f
      READ(1,*)r0c
      READ(1,*)sigf
      READ(1,*)sigc
      READ(1,*)r0dl
      READ(1,*)r0ws
      READ(1,*)r0bc
      READ(1,*)r0s
      READ(1,*)r0ss
      READ(1,*)WV_SEG_FLAG
      READ(1,'(A)')aux_dir
      READ(1,'(A)')OUTFILE
   ENDIF

   IF(NMODE==3)THEN
      READ(1,*)FMFRAC
      READ(1,*)DFRAC
      READ(1,*)DSFRAC
      READ(1,*)rf2
      READ(1,*)rf3
      READ(1,*)MIX_FLAG
      READ(1,*)IVAR
      READ(1,*)IREFF
      READ(1,*)RHI
      READ(1,*)r0f
      READ(1,*)r0c
      READ(1,*)sigf
      READ(1,*)sigc
      READ(1,*)r0dl
      READ(1,*)r0ws
      READ(1,*)r0bc
      READ(1,*)r0s
      READ(1,*)r0ss
      READ(1,*)WV_SEG_FLAG
      READ(1,'(A)')aux_dir
      READ(1,'(A)')OUTFILE
   ENDIF
ENDIF

IF (NMODE==3) THEN
RF1=0
ENDIF

CLOSE(1)

IF(index(aux_dir,'#')>1) &
  aux_dir=trim(aux_dir(1:index(aux_dir,'#')-1))
IF(index(OUTFILE,'#')>1) &
   OUTFILE=trim(OUTFILE(1:index(OUTFILE,'#')-1))

IF (NMODE==3) rf1=0

IF(NMODE==2 .AND. rf1+rf2+rf3>1) STOP 'Fine mode composition is not consistent; check rf1+rf2+rf3<1'
IF(NMODE==3 .AND. rf2+rf3>1) STOP 'Fine mode composition is not consistent; check rf2+rf3<1'

IF(IAEROSOL>20)THEN
   FLEX_FLAG=1
ELSE
   FLEX_FLAG=0
ENDIF

write(*,*)'OUTFILE ', OUTFILE

IF(WV_SEG_FLAG<0 .OR. WV_SEG_FLAG>4) STOP 'CHECK WV_SEG_FLAG INPUT'

write(*,*) 'main program started'
NUMMIEUSE=1
!call aux_dir_readin
CALL WV_PACE_SETUP(aux_dir)

IF(WV_SEG_FLAG==0)THEN
    NWV_BAND_START=1
    NWV_BAND_END=NWV_BAND
ELSEIF(WV_SEG_FLAG==1)THEN
    NWV_BAND_START=1
    NWV_BAND_END=NWV_BAND_SEG1P2+NWV_BAND_SEG3
ELSEIF(WV_SEG_FLAG==2)THEN
    NWV_BAND_START=NWV_BAND_SEG1+1
    NWV_BAND_END=NWV_BAND_SEG1P2
ELSEIF(WV_SEG_FLAG==4)THEN
    NWV_BAND_START=NWV_BAND_SEG1P2+NWV_BAND_SEG3+1
    NWV_BAND_END=NWV_BAND
ENDIF

INTTMP=len_trim(OUTFILE)
IF(OUTFILE(INTTMP-2:INTTMP) .ne. '.h5') OUTFILE=TRIM(OUTFILE)//'.h5'

INQUIRE(FILE=OUTFILE, EXIST=file_e)
IF(file_e) then
!  write(*,*) 'warning, filename exist, a string is appended'
!  OUTFILE='new_'//TRIM(OUTFILE)
  stop 'warning, output filename exist, exiting'
ENDIF


ALLOCATE(REFF1_Save(NUMMIEUSE),REFF2_Save(NUMMIEUSE),VEFF1_Save(NUMMIEUSE),     &
         VEFF2_Save(NUMMIEUSE),ARSLND1_Save(NUMMIEUSE),ARSLND2_Save(NUMMIEUSE),&
         MRR1_Save(NUMMIEUSE,NWV_BAND),MRI1_Save(NUMMIEUSE,NWV_BAND),           &
         MRR2_Save(NUMMIEUSE,NWV_BAND),MRI2_Save(NUMMIEUSE,NWV_BAND),&
         MRRD_save(NUMMIEUSE,NWV_BAND),MRID_save(NUMMIEUSE,NWV_BAND),ARSLNDDS(NUMMIEUSE),&
         REFFDS(NUMMIEUSE),VEFFDS(NUMMIEUSE))

CALL Particle_PHMX_Assign_StandAlone(aux_dir,NUMMIEUSE,NWV_BAND,NWV_BAND_START,NWV_BAND_END,&
          IAEROSOL,IRH, rf1, rf2, rf3, FRACS, FMFRAC, IREFF, IVAR,R0F,R0C,RHI, &
          R0DL,R0WS,R0BC,R0S,R0SS,MIX_FLAG,sigf,sigc,NMODE,DFRAC,DSFRAC,REFF1_Save,    &
          REFF2_Save,REFFDS,VEFF1_Save,VEFF2_Save,VEFFDS,Reff_Cloud,Veff_Cloud, &
          MRR1_Cloud,MRI1_Cloud,MRR1_Save,MRI1_Save,MRR2_Save,                  &
          MRI2_Save,MRRD_save,MRID_save,ARSLND1_Save,ARSLND2_Save,ARSLNDDS)

write(*,*) 'Writing output file'

IF(IAEROSOL==-99 .AND. NMODE==2)THEN
   inputs21(1) = flex_flag
   inputs21(2) = mix_flag
   inputs21(3) = rf1
   inputs21(4) = rf2
   inputs21(5) = rf3
   inputs21(6) = 1-(rf1+rf2+rf3)
   inputs21(7) = FRACS
   inputs21(8) = FMFRAC
   inputs21(9) = r0dl
   inputs21(10) = r0ws
   inputs21(11) = r0bc
   inputs21(12) = r0s
   inputs21(13) = r0ss
   inputs21(14) = rhi
   inputs21(15) = r0f
   inputs21(16) = r0c
   inputs21(17) = sigf
   inputs21(18) = sigc
   INPUTS21(19) = NMODE
ENDIF

IF(IAEROSOL==-99 .AND. NMODE==3)THEN
   inputs21(1) = flex_flag
   inputs21(2) = mix_flag
   inputs21(3) = DSFRAC
   inputs21(4) = rf2
   inputs21(5) = rf3
   inputs21(6) = 1-(rf1+rf2+rf3)
   inputs21(7) = DFRAC
   inputs21(8) = FMFRAC
   INPUTS21(9) = NMODE
   inputs21(10) = r0ws
   inputs21(11) = r0bc
   inputs21(12) = r0s
   inputs21(13) = r0ss
   inputs21(14) = rhi
   inputs21(15) = r0f
   inputs21(16) = r0c
   inputs21(17) = sigf
   inputs21(18) = sigc
   INPUTS21(19) = 0 !no variable assigned (blank)
ENDIF


CALL  PHMX_OUTPUT(OUTFILE,NMODE, NWV_BAND, NWV_BAND_START,&
     ARSLND1_Save,ARSLND2_Save,ARSLNDDS,NUMMIEUSE,  &
     REFF1_Save,REFF2_Save,REFFDS,VEFF1_Save,VEFF2_Save,VEFFDS,&
     MRR1_Save,MRR2_Save,MRI1_Save,MRI2_Save,MRRD_save,MRID_save, &
     CEXT_ARSL_BAND, CSCAT_ARSL_BAND, PHMXMIE_ARSL, inputs21, iaerosol)

CALL PHMXMIE_DEALLO
CALL PACE_FWHM_DEALLO

write(*,*) 'End of program PACE_Aerosol_Model'

call date_and_time(values=time_array_1)
finish_time = time_array_1 (5) * 3600 + time_array_1 (6) * 60 &
     + time_array_1 (7) + 0.001 * time_array_1 (8)

write(*,*)'elapsed time =', finish_time-start_time

       
ENDPROGRAM AERSL_PHMX






SUBROUTINE  PHMX_OUTPUT(CFILE1, NMODE,NWV_PHMX,NWV_BAND_START,&
     ARSLND1_Save,ARSLND2_Save,ARSLNDDS,NUMMIEUSE,  &
     REFF1_Save,REFF2_Save,REFFDS,VEFF1_Save,VEFF2_Save,VEFFDS,&
     MRR1_Save,MRR2_Save,MRI1_Save,MRI2_Save,MRRD_save,MRID_save, &
     CEXT_ARSL_BAND, CSCAT_ARSL_BAND, PHMXMIE_ARSL,&
     inputs, iaerosol)

USE PACE_INSTRUMENT_DESIGN
USE MIE_PHMX_CAL,ONLY : NUMMIEANGMAX,NUM_SCAT_ANG
USE hdf5
use iso_c_binding

IMPLICIT NONE
CHARACTER*360 :: CFILE1

REAL*8 :: rtmp
INTEGER :: NUMMIEUSE,IMIE,NMODE,NWV_PHMX,NWV_BAND_START
Integer :: NWVOS, IAEROSOL
REAL*8,DIMENSION(NUMMIEUSE) ::REFF1_Save,REFF2_Save,VEFF1_Save,VEFF2_Save,&
     ARSLND1_Save,ARSLND2_Save,ARSLNDDS,REFFDS,VEFFDS
REAL*8 ::REFFD,VEFFD,ARSLNDD
REAL*8,DIMENSION(NUMMIEUSE,NWV_PHMX) ::MRR1_Save,MRR2_Save,MRI1_Save,MRI2_Save,MRRD_save,MRID_save
REAL*8,DIMENSION(NWV_PHMX,NUMMIEANGMAX,0:6)::PHMXMIE_ARSL
REAL*8,DIMENSION(NWV_PHMX):: CEXT_ARSL_BAND,CSCAT_ARSL_BAND
REAL*8 ::rf1,rf2,rf3,FRACS,FMFRAC
INTEGER :: Flex_flag
CHARACTER(LEN=360) :: HDF5FILENAME
INTEGER(HID_T)  :: file, space, dset, attr! Handles
integer(hid_t) :: dspace_id     ! dataspace identifier
integer(hid_t) :: group_id     ! group
character(len=40) :: groupname
INTEGER :: hdferr
INTEGER(hsize_t),   DIMENSION(1:2) :: dims
INTEGER(hsize_t),DIMENSION(1) :: dimscl
INTEGER(HSIZE_T), DIMENSION(1:2) :: maxdims
TYPE(C_PTR) :: f_ptr
REAL*4,DIMENSION(1),TARGET :: HDF5RTMP
INTEGER,DIMENSION(1),TARGET :: HDF5ITMP
REAL*4,DIMENSION(:),TARGET,ALLOCATABLE :: HDF5RARR
REAL*4,DIMENSION(:,:),TARGET,ALLOCATABLE :: HDF5RARR2DIM
real*8 , DIMENSION(19) :: inputs
INTEGER(hsize_t), DIMENSION(1:3) :: dims3
INTEGER(HSIZE_T), DIMENSION(1:3) :: maxdims3
REAL*4,DIMENSION(:,:,:),TARGET,ALLOCATABLE :: HDF5RARR3DIM

IMIE=1



CALL h5open_f(hdferr)
call h5fcreate_f(CFILE1, h5f_acc_trunc_f, file, hdferr)

!General

dimscl=(/ 1 /)
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'NMODE', H5T_IEEE_F32LE, space, dset, hdferr)
HDF5ITMP=NMODE
f_ptr=C_LOC(HDF5ITMP(1))
CALL h5dwrite_f(dset,H5T_NATIVE_INTEGER,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)


dimscl=(/ 1 /)
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'NUM_SCAT_ANG', H5T_IEEE_F32LE, space, dset, hdferr)
HDF5ITMP=NUM_SCAT_ANG
f_ptr=C_LOC(HDF5ITMP(1))
CALL h5dwrite_f(dset,H5T_NATIVE_INTEGER,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)

dimscl=(/ 1 /)
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_Rf', H5T_IEEE_F32LE, space, dset, hdferr)
!RTMP=LOG(VEFF1_Save(IMIE)+1.0)
HDF5RTMP=REFF1_Save(IMIE) !*EXP(-2.5*RTMP)
f_ptr=C_LOC(HDF5RTMP(1))
CALL h5dwrite_f(dset,H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)

dimscl=(/ 1 /)
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_Vf', H5T_IEEE_F32LE, space, dset, hdferr)
!RTMP=LOG(VEFF1_Save(IMIE)+1.0)
!HDF5RTMP=SQRT(RTMP)
HDF5RTMP=VEFF1_Save(IMIE)
f_ptr=C_LOC(HDF5RTMP(1))
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)

dimscl=(/ 1 /)
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_Rc', H5T_IEEE_F32LE, space, dset, hdferr)
!RTMP=LOG(VEFF2_Save(IMIE)+1.0)
HDF5RTMP=REFF2_Save(IMIE) !*EXP(-2.5*RTMP)
f_ptr=C_LOC(HDF5RTMP(1))
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)

dimscl=(/ 1 /)
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_Vc', H5T_IEEE_F32LE, space, dset, hdferr)
!RTMP=LOG(VEFF2_Save(IMIE)+1.0)
!HDF5RTMP=SQRT(RTMP)
HDF5RTMP=VEFF2_Save(IMIE)
f_ptr=C_LOC(HDF5RTMP(1))
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)


dimscl=(/ 1 /)
ALLOCATE(HDF5RARR(1))
HDF5RARR=ARSLND2_Save(IMIE)
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_Ndc', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)

dimscl=(/ 1 /)
ALLOCATE(HDF5RARR(1))
HDF5RARR=ARSLND1_Save(IMIE)
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_Ndf', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)

dimscl=(/ 1 /)
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_RD', H5T_IEEE_F32LE, space, dset, hdferr)
IF(IAEROSOL==-99 .AND. NMODE==3)THEN
!   RTMP=LOG(VEFFDS(IMIE)+1.0)
   HDF5RTMP=REFFDS(IMIE)!*EXP(-2.5*RTMP)
ELSE
   HDF5RTMP=-999
ENDIF
f_ptr=C_LOC(HDF5RTMP(1))
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)

dimscl=(/ 1 /)
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_VD', H5T_IEEE_F32LE, space, dset, hdferr)
IF(IAEROSOL==-99 .AND. NMODE==3)THEN
!   RTMP=LOG(VEFFDS(IMIE)+1.0)
!   HDF5RTMP=SQRT(RTMP)
    HDF5RTMP=VEFFDS(IMIE)
ELSE
   HDF5RTMP=-999
ENDIF
f_ptr=C_LOC(HDF5RTMP(1))
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)

dimscl=(/ 1 /)
ALLOCATE(HDF5RARR(1))
IF(IAEROSOL==-99 .AND. NMODE==3)THEN
  HDF5RARR=ARSLNDDS(IMIE)
ELSE
  HDF5RARR=-999
ENDIF
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_NdD', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)

dimscl=(/ 1 /)
ALLOCATE(HDF5RARR(1))
HDF5RARR=inputs(14)
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Relative_Humidity', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)

dimscl=(/ 1 /)
ALLOCATE(HDF5RARR(1))
HDF5RARR=inputs(3)
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'FM_dust', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)

dimscl=(/ 1 /)
ALLOCATE(HDF5RARR(1))
HDF5RARR=inputs(4)
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'FM_water_soluable', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)

dimscl=(/ 1 /)
ALLOCATE(HDF5RARR(1))
HDF5RARR=inputs(5)
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'FM_BrC', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)


dimscl=(/ 1 /)
ALLOCATE(HDF5RARR(1))
HDF5RARR=inputs(6)
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'FM_soot', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)

dimscl=(/ 1 /)
ALLOCATE(HDF5RARR(1))
IF(IAEROSOL==-99 .AND. NMODE==2)THEN
  HDF5RARR=inputs(7)
ELSE
  HDF5RARR=-999
ENDIF
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'CM_spherical_fraction', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)

dimscl=(/ 1 /)
ALLOCATE(HDF5RARR(1))
HDF5RARR=inputs(8)
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'FineModeFraction', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)


!dimscl=(/ 1 /)
!ALLOCATE(HDF5RARR(1))
!HDF5RARR=1-rc
!CALL h5screate_simple_f(1, dimscl, space, hdferr)
!CALL h5dcreate_f(file, 'CM dust', H5T_IEEE_F32LE, space, dset, hdferr)
!CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
!CALL h5dclose_f(dset , hdferr)
!CALL h5sclose_f(space, hdferr)
!DEALLOCATE(HDF5RARR)

!dimscl=(/ 1 /)
!ALLOCATE(HDF5RARR(1))
!HDF5RARR=flex_flag
!CALL h5screate_simple_f(1, dimscl, space, hdferr)
!CALL h5dcreate_f(file, 'Flexibility', H5T_IEEE_F32LE, space, dset, hdferr)
!CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
!CALL h5dclose_f(dset , hdferr)
!CALL h5sclose_f(space, hdferr)
!DEALLOCATE(HDF5RARR)

IF (IAEROSOL==-99) THEN
dimscl=(/ 19 /)
ALLOCATE(HDF5RARR(1))
!ALLOCATE(INPUTS(19))
HDF5RARR=inputs
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Inputs', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)
ENDIF 



!write(*,*)'PHMXMIE_ARSL_ANG',PHMXMIE_ARSL(1,1:NUM_SCAT_ANG,0)
write(*,*)'NUM_SCAT_ANG=',NUM_SCAT_ANG
dimscl = (/ NUM_SCAT_ANG /)
ALLOCATE(HDF5RARR(NUM_SCAT_ANG))
HDF5RARR=PHMXMIE_ARSL(NWV_BAND_START,1:NUM_SCAT_ANG,0)
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_Phmxmie_Scatang', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)

!OCI
!write(*,*) PHMXMIE_ARSL(1,1:25,0)

dimscl=(/(NWV_BAND_SEG1+NWV_BAND_SEG2)/)
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'WaveLength_OCI', H5T_IEEE_F32LE, space, dset, hdferr)
ALLOCATE(HDF5RARR(NWV_BAND_SEG1+NWV_BAND_SEG2))
HDF5RARR=WV_BAND(1:(NWV_BAND_SEG1+NWV_BAND_SEG2))
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
DEALLOCATE(HDF5RARR)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)

dimscl=(/ (NWV_BAND_SEG1+NWV_BAND_SEG2) /)
ALLOCATE(HDF5RARR(NWV_BAND_SEG1+NWV_BAND_SEG2))
HDF5RARR(1:(NWV_BAND_SEG1+NWV_BAND_SEG2))=MRR1_Save(IMIE,1:(NWV_BAND_SEG1+NWV_BAND_SEG2))
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_Mrf_OCI', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)

dimscl=(/(NWV_BAND_SEG1+NWV_BAND_SEG2) /)
ALLOCATE(HDF5RARR(NWV_BAND_SEG1+NWV_BAND_SEG2))
HDF5RARR(1:(NWV_BAND_SEG1+NWV_BAND_SEG2))=MRI1_Save(IMIE,1:(NWV_BAND_SEG1+NWV_BAND_SEG2))
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_Mif_OCI', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)


dimscl=(/ (NWV_BAND_SEG1+NWV_BAND_SEG2) /)
ALLOCATE(HDF5RARR(NWV_BAND_SEG1+NWV_BAND_SEG2))
HDF5RARR(1:(NWV_BAND_SEG1+NWV_BAND_SEG2))=MRR2_Save(IMIE,1:(NWV_BAND_SEG1+NWV_BAND_SEG2))
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_Mrc_OCI', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)

dimscl=(/(NWV_BAND_SEG1+NWV_BAND_SEG2)/)
ALLOCATE(HDF5RARR(NWV_BAND_SEG1+NWV_BAND_SEG2))
HDF5RARR(1:(NWV_BAND_SEG1+NWV_BAND_SEG2))=MRI2_Save(IMIE,1:(NWV_BAND_SEG1+NWV_BAND_SEG2))
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_Mic_OCI', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)

dimscl=(/ (NWV_BAND_SEG1+NWV_BAND_SEG2) /)
ALLOCATE(HDF5RARR(NWV_BAND_SEG1+NWV_BAND_SEG2))
IF(IAEROSOL==-99 .AND. NMODE==3)THEN
   HDF5RARR(1:(NWV_BAND_SEG1+NWV_BAND_SEG2)) = &
		 MRRD_save(IMIE,1:(NWV_BAND_SEG1+NWV_BAND_SEG2))
ELSE
   HDF5RARR=-999
ENDIF
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_MrD_OCI', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)

!needs correction
dimscl=(/(NWV_BAND_SEG1+NWV_BAND_SEG2)/)
ALLOCATE(HDF5RARR(NWV_BAND_SEG1+NWV_BAND_SEG2))
IF(IAEROSOL==-99 .AND. NMODE==3)THEN
  HDF5RARR(1:(NWV_BAND_SEG1+NWV_BAND_SEG2)) = &
		   MRID_save(IMIE,1:(NWV_BAND_SEG1+NWV_BAND_SEG2))
ELSE
  HDF5RARR=-999
ENDIF
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_MiD_OCI', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)




!write(*,*)'NUM_SCAT_ANG',NUM_SCAT_ANG

dims3 = (/(NWV_BAND_SEG1+NWV_BAND_SEG2),NUM_SCAT_ANG,6/)
ALLOCATE(HDF5RARR3DIM((NWV_BAND_SEG1+NWV_BAND_SEG2),NUM_SCAT_ANG,6))
HDF5RARR3DIM=PHMXMIE_ARSL(1:(NWV_BAND_SEG1+NWV_BAND_SEG2),1:NUM_SCAT_ANG,1:6)
CALL h5screate_simple_f(3, dims3, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_Phmxmie_OCI', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR3DIM(1,1,1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR3DIM)

!write(*,*) 'PHMX',PHMXMIE_ARSL(1:5,1:10,1)

dimscl=(/ (NWV_BAND_SEG1+NWV_BAND_SEG2)/)
ALLOCATE(HDF5RARR((NWV_BAND_SEG1+NWV_BAND_SEG2)))
HDF5RARR(1:(NWV_BAND_SEG1+NWV_BAND_SEG2))=CEXT_ARSL_BAND(1:(NWV_BAND_SEG1+NWV_BAND_SEG2))
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_Cext_OCI', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)

dimscl=(/ (NWV_BAND_SEG1+NWV_BAND_SEG2)/)
ALLOCATE(HDF5RARR((NWV_BAND_SEG1+NWV_BAND_SEG2)))
HDF5RARR(1:(NWV_BAND_SEG1+NWV_BAND_SEG2))=CSCAT_ARSL_BAND(1:(NWV_BAND_SEG1+NWV_BAND_SEG2))
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_Cscat_OCI', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)


!SPEX
NWVOS = NWV_BAND_SEG1+NWV_BAND_SEG2

dimscl=(/(NWV_BAND_SEG3)/)
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'WaveLength_SPEX', H5T_IEEE_F32LE, space, dset, hdferr)
ALLOCATE(HDF5RARR(NWV_BAND_SEG3))
HDF5RARR=WV_BAND((NWVOS+1):(NWVOS+NWV_BAND_SEG3))
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
DEALLOCATE(HDF5RARR)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)

dimscl=(/ (NWV_BAND_SEG3) /)
ALLOCATE(HDF5RARR(NWV_BAND_SEG3))
HDF5RARR= MRR1_Save(IMIE,(NWVOS+1):(NWVOS+NWV_BAND_SEG3))
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_Mrf_SPEX', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)

dimscl=(/ (NWV_BAND_SEG3) /)
ALLOCATE(HDF5RARR(NWV_BAND_SEG3))
HDF5RARR= MRI1_Save(IMIE,(NWVOS+1):(NWVOS+NWV_BAND_SEG3))
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_Mif_SPEX', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)

dimscl=(/ (NWV_BAND_SEG3) /)
ALLOCATE(HDF5RARR(NWV_BAND_SEG3))
HDF5RARR= MRR2_Save(IMIE,(NWVOS+1):(NWVOS+NWV_BAND_SEG3))
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_Mrc_SPEX', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)
 
dimscl=(/ (NWV_BAND_SEG3) /)
ALLOCATE(HDF5RARR(NWV_BAND_SEG3))
HDF5RARR= MRI2_Save(IMIE,(NWVOS+1):(NWVOS+NWV_BAND_SEG3))
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_Mic_SPEX', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)


   dimscl=(/ (NWV_BAND_SEG3) /)
   ALLOCATE(HDF5RARR(NWV_BAND_SEG3))
   IF(IAEROSOL==-99 .AND. NMODE==3)THEN
      HDF5RARR= MRRD_save(IMIE,(NWVOS+1):(NWVOS+NWV_BAND_SEG3))
   ELSE
      HDF5RARR=-999
   ENDIF
   CALL h5screate_simple_f(1, dimscl, space, hdferr)
   CALL h5dcreate_f(file, 'Aerosol_MrD_SPEX', H5T_IEEE_F32LE, space, dset, hdferr)
   CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
   CALL h5dclose_f(dset , hdferr)
   CALL h5sclose_f(space, hdferr)
   DEALLOCATE(HDF5RARR)

   dimscl=(/ (NWV_BAND_SEG3) /)
   ALLOCATE(HDF5RARR(NWV_BAND_SEG3))
   IF(IAEROSOL==-99 .AND. NMODE==3)THEN
      HDF5RARR= MRID_save(IMIE,(NWVOS+1):(NWVOS+NWV_BAND_SEG3))
   ELSE
	  HDF5RARR=-999
   ENDIF

   CALL h5screate_simple_f(1, dimscl, space, hdferr)
   CALL h5dcreate_f(file, 'Aerosol_MiD_SPEX', H5T_IEEE_F32LE, space, dset, hdferr)
   CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
   CALL h5dclose_f(dset , hdferr)
   CALL h5sclose_f(space, hdferr)
   DEALLOCATE(HDF5RARR)



!write(*,*)'PHMXMIE_ARSL_at output writing',PHMXMIE_ARSL((NWVOS+1):(NWVOS+6),1,1)
!write(*,*) 'PHMXMIE_ARSL',PHMXMIE_ARSL(:5,1,1)

dims3 = (/NWV_BAND_SEG3,NUM_SCAT_ANG,6/)
ALLOCATE(HDF5RARR3DIM(NWV_BAND_SEG3,NUM_SCAT_ANG,6))
HDF5RARR3DIM=PHMXMIE_ARSL((NWVOS+1):(NWVOS+NWV_BAND_SEG3),1:NUM_SCAT_ANG,1:6)
CALL h5screate_simple_f(3, dims3, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_Phmxmie_SPEX', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR3DIM(1,1,1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR3DIM)

dimscl=(/ NWV_BAND_SEG3/)
ALLOCATE(HDF5RARR(NWV_BAND_SEG3))
HDF5RARR=CEXT_ARSL_BAND((NWVOS+1):(NWVOS+NWV_BAND_SEG3))
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_Cext_SPEX', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)

dimscl=(/ NWV_BAND_SEG3/)
ALLOCATE(HDF5RARR(NWV_BAND_SEG3))
HDF5RARR=CSCAT_ARSL_BAND((NWVOS+1):(NWVOS+NWV_BAND_SEG3))
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_Cscat_SPEX', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)

!HARP

NWVOS  = NWV_BAND_SEG1+NWV_BAND_SEG2+NWV_BAND_SEG3

dimscl=(/NWV_BAND_SEG4/)
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'WaveLength_HARP', H5T_IEEE_F32LE, space, dset, hdferr)
ALLOCATE(HDF5RARR(NWV_BAND_SEG4))
HDF5RARR=WV_BAND((NWVOS+1):(NWVOS+NWV_BAND_SEG4))
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
DEALLOCATE(HDF5RARR)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)

dimscl=(/ (NWV_BAND_SEG4) /)
ALLOCATE(HDF5RARR(NWV_BAND_SEG4))
HDF5RARR= MRR1_Save(IMIE,(NWVOS+1):(NWVOS+NWV_BAND_SEG4))
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_Mrf_HARP', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)

dimscl=(/ (NWV_BAND_SEG4) /)
ALLOCATE(HDF5RARR(NWV_BAND_SEG4))
HDF5RARR= MRI1_Save(IMIE,(NWVOS+1):(NWVOS+NWV_BAND_SEG4))
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_Mif_HARP', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)

!needs correction  

dimscl=(/ (NWV_BAND_SEG4) /)
ALLOCATE(HDF5RARR(NWV_BAND_SEG4))
HDF5RARR=  MRR2_Save(IMIE,(NWVOS+1):(NWVOS+NWV_BAND_SEG4))
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_Mrc_HARP', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)

!needs correction  
dimscl=(/ (NWV_BAND_SEG4) /)
ALLOCATE(HDF5RARR(NWV_BAND_SEG4))
HDF5RARR= MRI2_Save(IMIE,(NWVOS+1):(NWVOS+NWV_BAND_SEG4))
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_Mic_HARP', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)

   dimscl=(/ (NWV_BAND_SEG4) /)
   ALLOCATE(HDF5RARR(NWV_BAND_SEG4))
   IF(IAEROSOL==-99 .AND. NMODE==3)THEN
      HDF5RARR=  MRRD_save(IMIE,(NWVOS+1):(NWVOS+NWV_BAND_SEG4))
   ELSE
      HDF5RARR=-999
   ENDIF

   CALL h5screate_simple_f(1, dimscl, space, hdferr)
   CALL h5dcreate_f(file, 'Aerosol_MrD_HARP', H5T_IEEE_F32LE, space, dset, hdferr)
   CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
   CALL h5dclose_f(dset , hdferr)
   CALL h5sclose_f(space, hdferr)
   DEALLOCATE(HDF5RARR)

   !needs correction
   dimscl=(/ (NWV_BAND_SEG4) /)
   ALLOCATE(HDF5RARR(NWV_BAND_SEG4))
   IF(IAEROSOL==-99 .AND. NMODE==3)THEN
      HDF5RARR= MRID_save(IMIE,(NWVOS+1):(NWVOS+NWV_BAND_SEG4))
   ELSE
      HDF5RARR=-999
   ENDIF
   CALL h5screate_simple_f(1, dimscl, space, hdferr)
   CALL h5dcreate_f(file, 'Aerosol_MiD_HARP', H5T_IEEE_F32LE, space, dset, hdferr)
   CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
   CALL h5dclose_f(dset , hdferr)
   CALL h5sclose_f(space, hdferr)
   DEALLOCATE(HDF5RARR)



dims3 = (/NWV_BAND_SEG4,NUM_SCAT_ANG,6/)
ALLOCATE(HDF5RARR3DIM(NWV_BAND_SEG4,NUM_SCAT_ANG,6))
HDF5RARR3DIM=PHMXMIE_ARSL((NWVOS+1):(NWVOS+NWV_BAND_SEG4),1:NUM_SCAT_ANG,1:6)
CALL h5screate_simple_f(3, dims3, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_Phmxmie_HARP', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR3DIM(1,1,1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR3DIM)

dimscl=(/ NWV_BAND_SEG4/)
ALLOCATE(HDF5RARR(NWV_BAND_SEG4))
HDF5RARR(1:NWV_BAND_SEG4)=CEXT_ARSL_BAND((NWVOS+1):(NWVOS+NWV_BAND_SEG4))
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_Cext_HARP', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)

dimscl=(/ NWV_BAND_SEG4/)
ALLOCATE(HDF5RARR(NWV_BAND_SEG4))
HDF5RARR(1:NWV_BAND_SEG4)=CSCAT_ARSL_BAND((NWVOS+1):(NWVOS+NWV_BAND_SEG4))
CALL h5screate_simple_f(1, dimscl, space, hdferr)
CALL h5dcreate_f(file, 'Aerosol_Cscat_HARP', H5T_IEEE_F32LE, space, dset, hdferr)
CALL h5dwrite_f(dset, H5T_NATIVE_REAL,C_LOC(HDF5RARR(1)), hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
DEALLOCATE(HDF5RARR)



call h5fclose_f(file, hdferr)
call h5close_f(hdferr)


write(*,*) 'Finished writing output'
END SUBROUTINE  PHMX_OUTPUT




SUBROUTINE Particle_PHMX_Assign_StandAlone(aux_dir,NUMMIEUSE,NWV_PHMX,NWV_BAND_START,NWV_BAND_END,&
      IAEROSOL,IRH,rf1, rf2, rf3,FRACS, FMFRAC, IREFF, IVAR,R0F,R0C,RHI, &
      R0DL,R0WS,R0BC,R0S,R0SS,MIX_FLAG,sigf,sigc,nmode,dfrac,dsfrac,REFF1_Save,&
      REFF2_Save,REFFDS,VEFF1_Save,VEFF2_Save,VEFFDS,Reff_Cloud,Veff_Cloud, &
      MRR1_Cloud,MRI1_Cloud,MRR1_Save,MRI1_Save,MRR2_Save,&
	  MRI2_Save,MRRD_save,MRID_save,ARSLND1_Save,ARSLND2_Save,ARSLNDDS)
USE MIE_PHMX_CAL
IMPLICIT NONE
CHARACTER(LEN=360),intent(in) :: aux_dir
INTEGER, INTENT(IN)::NUMMIEUSE,NWV_PHMX,NWV_BAND_START,NWV_BAND_END,IAEROSOL,  &
                     IRH, IREFF, IVAR, MIX_FLAG,NMODE
REAL*8, INTENT(IN) :: rf1, rf2, rf3,FRACS, FMFRAC, R0F,R0C,R0DL,R0WS,R0BC, &
                      R0S,R0SS,sigf,sigc,DFRAC,DSFRAC,Reff_Cloud,Veff_Cloud,MRR1_Cloud,MRI1_Cloud
REAL*8, INTENT(INOUT) :: RHI
REAL*8,DIMENSION(NUMMIEUSE),INTENT(OUT) :: REFF1_Save,REFF2_Save,VEFF1_Save,VEFF2_Save,&
                                           ARSLND1_Save,ARSLND2_Save,ARSLNDDS,REFFDS,VEFFDS
REAL*8,DIMENSION(NUMMIEUSE,NWV_PHMX),INTENT(OUT) ::MRR1_Save,MRI1_Save,MRR2_Save,MRI2_Save,MRRD_save,MRID_save

REAL*8::REFF1_LOCAL,VEFF1_LOCAL,REFF2_LOCAL,VEFF2_LOCAL,ARSLND1_LOCAL,ARSLND2_LOCAL,REFFD,VEFFD,arslndd
REAL*8,DIMENSION(:),ALLOCATABLE::MRR1_LOCAL,MRI1_LOCAL,MRR2_LOCAL,MRI2_LOCAL,MRRDL,MRIDL
INTEGER :: FREEFORMFLAG
FREEFORMFLAG=1

IF(NWV_PHMX .NE. NWV_BAND)STOP 'CHECK NWV_PHMX'
ALLOCATE(MRR1_LOCAL(NWV_PHMX),MRI1_LOCAL(NWV_PHMX),MRR2_LOCAL(NWV_PHMX),MRI2_LOCAL(NWV_PHMX),&
     MRRDL(NWV_PHMX),MRIDL(NWV_PHMX))

IF(FREEFORMFLAG==0)THEN
    REFF1_LOCAL=0.1D0
    REFF2_LOCAL=0.1D0
    VEFF1_LOCAL=1.D0
    VEFF2_LOCAL=0.5D0
    MRR1_LOCAL=1.45D0
    MRI1_LOCAL=0.0D0
    MRR2_LOCAL=1.45D0
    MRI2_LOCAL=0.0D0
    ARSLND1_LOCAL=0.99d0
    ARSLND2_LOCAL=0.01d0
ENDIF

IF(IAEROSOL==-98 .or. IAEROSOL==-96)THEN
	REFF1_LOCAL=Reff_Cloud
	REFF2_LOCAL=Reff_Cloud
	VEFF1_LOCAL=Veff_Cloud
	VEFF2_LOCAL=Reff_Cloud
	MRR1_LOCAL=MRR1_Cloud
	MRI1_LOCAL=MRI1_Cloud
	MRR2_LOCAL=MRR1_Cloud
	MRI2_LOCAL=MRI1_Cloud
	ARSLND1_LOCAL=1.0d0
	ARSLND2_LOCAL=0.0d0
ENDIF

CALL PHMXMIE_ALLO

CALL PHMXMIE_Instrument_INIT(aux_dir,FREEFORMFLAG,NWV_BAND_START,NWV_BAND_END,    &
     IAEROSOL,IRH, rf1, rf2,rf3, FRACS,FMFRAC, IREFF, IVAR,R0F,R0C,RHI,&
     R0DL,R0WS,R0BC,R0S,R0SS,MIX_FLAG,sigf,sigc,NMODE,DFRAC,DSFRAC,REFF1_LOCAL,VEFF1_LOCAL,      &
	 REFF2_LOCAL,VEFF2_LOCAL,reffd,veffd,MRR1_LOCAL,MRI1_LOCAL,MRR2_LOCAL,MRI2_LOCAL,MRRDL,MRIDL, &
	 ARSLND1_LOCAL,ARSLND2_LOCAL,arslndd)
REFF1_Save=REFF1_LOCAL
REFF2_Save=REFF2_LOCAL
REFFDS=REFFD
VEFF1_Save=VEFF1_LOCAL
VEFF2_Save=VEFF2_LOCAL
VEFFDS=VEFFD
ARSLND1_Save=ARSLND1_LOCAL
ARSLND2_Save=ARSLND2_LOCAL
ARSLNDDS=ARSLNDD

MRR1_Save(1,:)=MRR1_LOCAL
MRI1_Save(1,:)=MRI1_LOCAL
MRR2_Save(1,:)=MRR2_LOCAL
MRI2_Save(1,:)=MRI2_LOCAL
MRRD_save(1,:)=MRRDL
MRID_save(1,:)=MRIDL

DEALLOCATE(MRR1_LOCAL,MRI1_LOCAL,MRR2_LOCAL,MRI2_LOCAL,MRRDL,MRIDL)

END SUBROUTINE Particle_PHMX_Assign_StandAlone


