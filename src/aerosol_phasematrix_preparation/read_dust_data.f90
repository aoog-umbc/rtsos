MODULE DUST_DATA
USE HDF5
!USE auxiliary_dir_readin

INTEGER, PARAMETER :: NASPR=12, NWV_D=18, nsigma=5, nreff=15, &
     NSCATANG=500, nscatangs=498
REAL*8 :: asp_r(naspr), reff(nreff), sigma(nsigma),  wvl(nwv_d), mrd(nwv_d), mid(nwv_d)
REAL*8, DIMENSION(:), ALLOCATABLE :: scat_ang, scat_angs

REAL*8, DIMENSION(:,:,:,:), ALLOCATABLE :: p11s, p12s, p22s, p33s, p34s, p44s
REAL*8, DIMENSION(:,:,:), ALLOCATABLE :: gs, qes, vints, ssas

REAL*8, DIMENSION(:,:,:,:), ALLOCATABLE :: p11o, p12o, p22o, p33o, p34o, p44o
REAL*8, DIMENSION(:,:,:), ALLOCATABLE :: go, qeo, vinto, ssao, areao

REAL*8, DIMENSION(:,:,:,:), ALLOCATABLE :: p11p, p12p, p22p, p33p, p34p, p44p
REAL*8, DIMENSION(:,:,:), ALLOCATABLE :: gp, qep, vintp, ssap, areap


CONTAINS
  
SUBROUTINE READ_DUST_DATA(aux_dir,shape,aspr_in)
IMPLICIT NONE

CHARACTER(LEN=360) ::aux_dir,dust_filename, aspr_str
REAL*8 :: read_string
INTEGER(HID_T)  :: file, space, dset, attr ! Handles
INTEGER :: hdferr
TYPE(C_PTR) :: f_ptr
REAL*4,DIMENSION(:),TARGET,ALLOCATABLE :: HDF5RARRD1
REAL*4,DIMENSION(:,:,:),TARGET,ALLOCATABLE :: HDF5RARR3DIM
REAL*4,DIMENSION(:,:,:,:),TARGET,ALLOCATABLE :: HDF5RARR4DIM
CHARACTER(LEN=65) :: aspr_in
INTEGER,INTENT(IN) :: shape
logical :: file_e
INTEGER :: iaspr

ALLOCATE(p11s(nscatangs,nreff,nsigma,nwv_d),p12s(nscatangs,nreff,nsigma,nwv_d),&
     p22s(nscatangs,nreff,nsigma,nwv_d),p33s(nscatangs,nreff,nsigma,nwv_d),&
     p34s(nscatangs,nreff,nsigma,nwv_d),p44s(nscatangs,nreff,nsigma,nwv_d),gs(nreff,nsigma,nwv_d),&
     qes(nreff,nsigma,nwv_d), vints(nreff,nsigma,nwv_d), ssas(nreff,nsigma,nwv_d),&
     scat_ang(nscatang),scat_angs(nscatangs))

ALLOCATE(p11o(nscatang,nreff,nsigma,nwv_d),p12o(nscatang,nreff,nsigma,nwv_d),&
     p22o(nscatang,nreff,nsigma,nwv_d),p33o(nscatang,nreff,nsigma,nwv_d),&
     p34o(nscatang,nreff,nsigma,nwv_d),p44o(nscatang,nreff,nsigma,nwv_d),go(nreff,nsigma,nwv_d),&
     qeo(nreff,nsigma,nwv_d), vinto(nreff,nsigma,nwv_d), ssao(nreff,nsigma,nwv_d), &
     areao(nreff,nsigma,nwv_d))

ALLOCATE(p11p(nscatang,nreff,nsigma,nwv_d),p12p(nscatang,nreff,nsigma,nwv_d),&
     p22p(nscatang,nreff,nsigma,nwv_d),p33p(nscatang,nreff,nsigma,nwv_d),&
     p34p(nscatang,nreff,nsigma,nwv_d),p44p(nscatang,nreff,nsigma,nwv_d),gp(nreff,nsigma,nwv_d),&
     qep(nreff,nsigma,nwv_d), vintp(nreff,nsigma,nwv_d), ssap(nreff,nsigma,nwv_d), &
     areap(nreff,nsigma,nwv_d))

!call aux_dir_readin
dust_filename=trim(aux_dir)//'Dust.h5'

inquire(file=dust_filename, exist=file_e)
if(file_e) then
   !print *, dust_filename
else
   write(*,*) dust_filename,'do not exist'
   stop
endif

CALL h5open_f(hdferr)
call h5fopen_f(dust_filename, h5f_acc_rdwr_f, file, hdferr)


ALLOCATE(HDF5RARRD1(naspr))
CALL h5dopen_f (file, 'Aspect_ratio', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARRD1(1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
asp_r(1:naspr)=HDF5RARRD1(1:naspr)
DEALLOCATE(HDF5RARRD1)

!WRITE(*,*)'aspect ratio', asp_r(:)

ALLOCATE(HDF5RARRD1(nreff))
CALL h5dopen_f (file, 'Effective_radius', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARRD1(1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
reff(1:nreff)=HDF5RARRD1(1:nreff)
DEALLOCATE(HDF5RARRD1)

!write(*,*) 'reff',reff

ALLOCATE(HDF5RARRD1(nwv_d))
CALL h5dopen_f (file, 'Refractive_index_imaginary', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARRD1(1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
mid(1:nwv_d)=HDF5RARRD1(1:nwv_d)

!write(*,*)'mi',mid

CALL h5dopen_f (file, 'Refractive_index_real', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARRD1(1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
mrd(1:nwv_d)=HDF5RARRD1(1:nwv_d)

!write(*,*)'mr',mrd

CALL h5dopen_f (file, 'Wavelength', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARRD1(1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
wvl(1:nwv_d)=HDF5RARRD1(1:nwv_d)
DEALLOCATE(HDF5RARRD1)

!write(*,*)'wv',wvl

ALLOCATE(HDF5RARRD1(nscatang))
CALL h5dopen_f (file, 'Scatering_angle', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARRD1(1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
scat_ang(1:nscatang)=HDF5RARRD1(1:nscatang)
DEALLOCATE(HDF5RARRD1)

!write(*,*)'scat_ang',scat_ang

ALLOCATE(HDF5RARRD1(nsigma))
CALL h5dopen_f (file, 'Variance', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARRD1(1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
sigma(1:nsigma)=HDF5RARRD1(1:nsigma)
DEALLOCATE(HDF5RARRD1)

!write(*,*)'variance',sigma


IF (shape==1) THEN

ALLOCATE(HDF5RARR4DIM(nscatangs,nreff,nsigma,nwv_d))

CALL h5dopen_f (file, 'Sphere/P11', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR4DIM(1,1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
p11s(1:nscatangs,1:nreff,1:nsigma,1:nwv_d)=HDF5RARR4DIM(1:nscatangs,1:nreff,1:nsigma,1:nwv_d)

!write(*,*)'P11 sphere',p11s(1,1,1,1)

CALL h5dopen_f (file, 'Sphere/P12', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR4DIM(1,1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
p12s(1:nscatangs,1:nreff,1:nsigma,1:nwv_d)=HDF5RARR4DIM(1:nscatangs,1:nreff,1:nsigma,1:nwv_d)

!write(*,*)'P12 sphere',p12s(1,1,1,1)

CALL h5dopen_f (file, 'Sphere/P22', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR4DIM(1,1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
p22s(1:nscatangs,1:nreff,1:nsigma,1:nwv_d)=HDF5RARR4DIM(1:nscatangs,1:nreff,1:nsigma,1:nwv_d)

CALL h5dopen_f (file, 'Sphere/P33', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR4DIM(1,1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
p33s(1:nscatangs,1:nreff,1:nsigma,1:nwv_d)=HDF5RARR4DIM(1:nscatangs,1:nreff,1:nsigma,1:nwv_d)

CALL h5dopen_f (file, 'Sphere/P34', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR4DIM(1,1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
p34s(1:nscatangs,1:nreff,1:nsigma,1:nwv_d)=HDF5RARR4DIM(1:nscatangs,1:nreff,1:nsigma,1:nwv_d)

CALL h5dopen_f (file, 'Sphere/P44', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR4DIM(1,1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
p44s(1:nscatangs,1:nreff,1:nsigma,1:nwv_d)=HDF5RARR4DIM(1:nscatangs,1:nreff,1:nsigma,1:nwv_d)
DEALLOCATE(HDF5RARR4DIM)

ALLOCATE(HDF5RARRD1(nscatangs))
CALL h5dopen_f (file, 'Sphere/Scattering_angle', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARRD1(1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
scat_angs(1:nscatangs)=HDF5RARRD1(1:nscatangs)
DEALLOCATE(HDF5RARRD1)

!write(*,*)'scatang',scat_angs(490:)

ALLOCATE(HDF5RARR3DIM(nreff,nsigma,nwv_d))
CALL h5dopen_f (file, 'Sphere/Asymmetry_factor', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR3DIM(1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
gs(1:nreff,1:nsigma,1:nwv_d)=HDF5RARR3DIM(1:nreff,1:nsigma,1:nwv_d)

!write(*,*)'g',gs(1,1,1)

CALL h5dopen_f (file, 'Sphere/Extinction_efficiency', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR3DIM(1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
qes(1:nreff,1:nsigma,1:nwv_d)=HDF5RARR3DIM(1:nreff,1:nsigma,1:nwv_d)

CALL h5dopen_f (file, 'Sphere/Integrated_volume', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR3DIM(1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
vints(1:nreff,1:nsigma,1:nwv_d)=HDF5RARR3DIM(1:nreff,1:nsigma,1:nwv_d)

CALL h5dopen_f (file, 'Sphere/Single-scattering_albedo', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR3DIM(1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
ssas(1:nreff,1:nsigma,1:nwv_d)=HDF5RARR3DIM(1:nreff,1:nsigma,1:nwv_d)
DEALLOCATE(HDF5RARR3DIM)

END IF

IF (shape==2) THEN  ! oblate

!write(*,*) 'Aspect ratio of dust (oblate) = ', aspr_in

ALLOCATE(HDF5RARR4DIM(nscatang,nreff,nsigma,nwv_d))
CALL h5dopen_f (file, 'Oblate/Aspect_ratio_'//TRIM(aspr_in)//'/P11', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR4DIM(1,1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
p11o(1:nscatang,1:nreff,1:nsigma,1:nwv_d)=HDF5RARR4DIM(1:nscatang,1:nreff,1:nsigma,1:nwv_d)

CALL h5dopen_f (file, 'Oblate/Aspect_ratio_'//TRIM(aspr_in)//'/P12', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR4DIM(1,1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
p12o(1:nscatang,1:nreff,1:nsigma,1:nwv_d)=HDF5RARR4DIM(1:nscatang,1:nreff,1:nsigma,1:nwv_d)

CALL h5dopen_f (file, 'Oblate/Aspect_ratio_'//TRIM(aspr_in)//'/P22', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR4DIM(1,1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
p22o(1:nscatang,1:nreff,1:nsigma,1:nwv_d)=HDF5RARR4DIM(1:nscatang,1:nreff,1:nsigma,1:nwv_d)

CALL h5dopen_f (file, 'Oblate/Aspect_ratio_'//TRIM(aspr_in)//'/P33', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR4DIM(1,1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
p33o(1:nscatang,1:nreff,1:nsigma,1:nwv_d)=HDF5RARR4DIM(1:nscatang,1:nreff,1:nsigma,1:nwv_d)

CALL h5dopen_f (file, 'Oblate/Aspect_ratio_'//TRIM(aspr_in)//'/P34', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR4DIM(1,1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
p34o(1:nscatang,1:nreff,1:nsigma,1:nwv_d)=HDF5RARR4DIM(1:nscatang,1:nreff,1:nsigma,1:nwv_d)

CALL h5dopen_f (file, 'Oblate/Aspect_ratio_'//TRIM(aspr_in)//'/P44', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR4DIM(1,1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
p44o(1:nscatang,1:nreff,1:nsigma,1:nwv_d)=HDF5RARR4DIM(1:nscatang,1:nreff,1:nsigma,1:nwv_d)
DEALLOCATE(HDF5RARR4DIM)

ALLOCATE(HDF5RARR3DIM(nreff,nsigma,nwv_d))
CALL h5dopen_f (file, 'Oblate/Aspect_ratio_'//TRIM(aspr_in)//'/Asymmetry_factor', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR3DIM(1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
go(1:nreff,1:nsigma,1:nwv_d)=HDF5RARR3DIM(1:nreff,1:nsigma,1:nwv_d)

CALL h5dopen_f (file, 'Oblate/Aspect_ratio_'//TRIM(aspr_in)//'/Extinction_efficiency', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR3DIM(1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
qeo(1:nreff,1:nsigma,1:nwv_d)=HDF5RARR3DIM(1:nreff,1:nsigma,1:nwv_d)

CALL h5dopen_f (file, 'Oblate/Aspect_ratio_'//TRIM(aspr_in)//'/Integrated_volume', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR3DIM(1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
vinto(1:nreff,1:nsigma,1:nwv_d)=HDF5RARR3DIM(1:nreff,1:nsigma,1:nwv_d)

CALL h5dopen_f (file, 'Oblate/Aspect_ratio_'//TRIM(aspr_in)//'/Single-scattering_albedo', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR3DIM(1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
ssao(1:nreff,1:nsigma,1:nwv_d)=HDF5RARR3DIM(1:nreff,1:nsigma,1:nwv_d)

CALL h5dopen_f (file, 'Oblate/Aspect_ratio_'//TRIM(aspr_in)//'/Area_projected', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR3DIM(1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
areao(1:nreff,1:nsigma,1:nwv_d)=HDF5RARR3DIM(1:nreff,1:nsigma,1:nwv_d)

DEALLOCATE(HDF5RARR3DIM)

!write(*,*) areao(2,3,5)

END IF

IF (shape==3) THEN  ! prolate

!write(*,*) 'Aspect ratio of dust (Prolate) = ', aspr_in
!write(*,*)'Prolate/Aspect_ratio_'//TRIM(aspr_in)//'/P11'


ALLOCATE(HDF5RARR4DIM(nscatang,nreff,nsigma,nwv_d))
CALL h5dopen_f (file, 'Prolate/Aspect_ratio_'//TRIM(aspr_in)//'/P11', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR4DIM(1,1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
p11p(1:nscatang,1:nreff,1:nsigma,1:nwv_d)=HDF5RARR4DIM(1:nscatang,1:nreff,1:nsigma,1:nwv_d)

!write(*,*) 'P11', p11p(:2,3,5,:2)

CALL h5dopen_f (file, 'Prolate/Aspect_ratio_'//TRIM(aspr_in)//'/P12', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR4DIM(1,1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
p12p(1:nscatang,1:nreff,1:nsigma,1:nwv_d)=HDF5RARR4DIM(1:nscatang,1:nreff,1:nsigma,1:nwv_d)

!write(*,*) 'P12', p12p(:2,3,5,:2)

CALL h5dopen_f (file, 'Prolate/Aspect_ratio_'//TRIM(aspr_in)//'/P22', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR4DIM(1,1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
p22p(1:nscatang,1:nreff,1:nsigma,1:nwv_d)=HDF5RARR4DIM(1:nscatang,1:nreff,1:nsigma,1:nwv_d)

!write(*,*) 'P22', p22p(:2,3,5,:2)

CALL h5dopen_f (file, 'Prolate/Aspect_ratio_'//TRIM(aspr_in)//'/P33', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR4DIM(1,1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
p33p(1:nscatang,1:nreff,1:nsigma,1:nwv_d)=HDF5RARR4DIM(1:nscatang,1:nreff,1:nsigma,1:nwv_d)

!write(*,*) 'P33', p33p(:2,3,5,:2)

CALL h5dopen_f (file, 'Prolate/Aspect_ratio_'//TRIM(aspr_in)//'/P34', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR4DIM(1,1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
p34p(1:nscatang,1:nreff,1:nsigma,1:nwv_d)=HDF5RARR4DIM(1:nscatang,1:nreff,1:nsigma,1:nwv_d)

!write(*,*) 'P34', p34p(:2,3,5,:2)

CALL h5dopen_f (file, 'Prolate/Aspect_ratio_'//TRIM(aspr_in)//'/P44', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR4DIM(1,1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
p44p(1:nscatang,1:nreff,1:nsigma,1:nwv_d)=HDF5RARR4DIM(1:nscatang,1:nreff,1:nsigma,1:nwv_d)
DEALLOCATE(HDF5RARR4DIM)

!write(*,*) 'P44', p44p(:2,3,5,:2)

ALLOCATE(HDF5RARR3DIM(nreff,nsigma,nwv_d))
CALL h5dopen_f (file, 'Prolate/Aspect_ratio_'//TRIM(aspr_in)//'/Asymmetry_factor', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR3DIM(1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
gp(1:nreff,1:nsigma,1:nwv_d)=HDF5RARR3DIM(1:nreff,1:nsigma,1:nwv_d)

!write(*,*) 'g', gp(3,5,:2)

CALL h5dopen_f (file, 'Prolate/Aspect_ratio_'//TRIM(aspr_in)//'/Extinction_efficiency', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR3DIM(1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
qep(1:nreff,1:nsigma,1:nwv_d)=HDF5RARR3DIM(1:nreff,1:nsigma,1:nwv_d)

!write(*,*) 'Qe', qep(3,5,:2)

CALL h5dopen_f (file, 'Prolate/Aspect_ratio_'//TRIM(aspr_in)//'/Integrated_volume', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR3DIM(1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
vintp(1:nreff,1:nsigma,1:nwv_d)=HDF5RARR3DIM(1:nreff,1:nsigma,1:nwv_d)

!write(*,*) 'V', vintp(3,5,:2)

CALL h5dopen_f (file, 'Prolate/Aspect_ratio_'//TRIM(aspr_in)//'/Single-scattering_albedo', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR3DIM(1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
ssap(1:nreff,1:nsigma,1:nwv_d)=HDF5RARR3DIM(1:nreff,1:nsigma,1:nwv_d)

!write(*,*) 'SSA',ssap(3,5,:2)

CALL h5dopen_f (file, 'Prolate/Aspect_ratio_'//TRIM(aspr_in)//'/Area_projected', dset, hdferr)
CALL h5dget_space_f(dset,space, hdferr)
f_ptr = C_LOC(HDF5RARR3DIM(1,1,1))
CALL h5dread_f( dset, H5T_NATIVE_REAL,f_ptr, hdferr)
CALL h5dclose_f(dset , hdferr)
CALL h5sclose_f(space, hdferr)
areap(1:nreff,1:nsigma,1:nwv_d)=HDF5RARR3DIM(1:nreff,1:nsigma,1:nwv_d)

DEALLOCATE(HDF5RARR3DIM)

!write(*,*) 'area',areap(2,3,5)

END IF

   
CALL h5fclose_f(file , hdferr)
CALL h5close_f(hdferr)


!DEALLOCATE(p11s,p12s,p22s,p33s,p34s,p44s,gs,qes, vints, ssas,scat_ang,scat_angs)
!DEALLOCATE(p11o,p12o,p22o,p33o,p34o,p44o,go,qeo, vinto,ssao,areao)
!DEALLOCATE(p11p,p12p,p22p,p33p,p34p,p44p,gp,qep, vintp, ssap,areap)

END SUBROUTINE READ_DUST_DATA

END MODULE DUST_DATA





SUBROUTINE DUST_SCAT_PROP_INIT(aux_dir,IREFF,IVAR,PHMX_DUST,CEXT_DUST,CSCAT_DUST,SCATANG)

USE DUST_DATA
CHARACTER(LEN=360),intent(in) :: aux_dir
INTEGER, INTENT(IN) :: IREFF, IVAR
REAL*8,DIMENSION(24)::ASPR=(/0.3 , 0.37, 0.42, 0.48, 0.56, 0.67, 0.83, 0.86, 0.88, 0.91, 0.95,0.98, &
     1.02, 1.05, 1.1 , 1.13, 1.16, 1.2 , 1.5 , 1.8 , 2.1 , 2.4 , 2.7 ,3.3/)
INTEGER::IASPR,shape
REAL*8, DIMENSION(NASPR*2,NSCATANG,NWV_D):: P11_DUST_TMP,P12_DUST_TMP,P22_DUST_TMP,P33_DUST_TMP, &
    P34_DUST_TMP,P44_DUST_TMP
REAL*8, DIMENSION(6,NASPR*2,NSCATANG,NWV_D) :: PHMX_DUST_TMP1
REAL*8, DIMENSION(NASPR*2,NWV_D,NSCATANG,6) :: PHMX_DUST_TMP
REAL*8, DIMENSION(NASPR*2,NWV_D) :: QEXT_DUST_TMP, SSA_DUST_TMP, AREA_DUST_TMP

CHARACTER(LEN=65):: aspr_n
INTEGER :: IWV, IANG, IPHMX
CHARACTER(LEN=65) :: a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11,a12
CHARACTER(LEN=65) :: b1,b2,b3,b4,b5,b6,b7,b8,b9,b10,b11,b12
CHARACTER (LEN=65), DIMENSION(12) :: ASPR_P, ASPR_PR
INTEGER :: N_ASPR_DIS_F

REAL*8, DIMENSION(:) :: QE_DUST(NWV_D), A_INT(NWV_D),SSA_DUST(NWV_D),QS_DUST(NWV_D)
REAL*8, DIMENSION(:) ::N_ASPR_D(NASPR*2)
REAL*8, DIMENSION(:),INTENT(OUT) :: CSCAT_DUST(NWV_D),CEXT_DUST(NWV_D),SCATANG(NSCATANG)
REAL*8, DIMENSION(:,:,:),INTENT(OUT) :: PHMX_DUST(NWV_D,NSCATANG,6)
REAL*8, DIMENSION(:) :: QE_INT_TMP(NWV_D), A_INT_TMP(NWV_D),SSA_INT_TMP(NWV_D)
REAL*8:: AREA, N_ASPR
REAL*8 :: RTMP,RTMP1,TRAPZOID
REAL*8, DIMENSION(:,:,:) ::PHMX_INT_TMP(NWV_D,NSCATANG,6)
REAL*8, DIMENSIOn(24) :: ASPR_BIN

a1='1.02'
a2='1.05'
a3='1.1'
a4='1.13'
a5='1.16'
a6='1.2'
a7='1.5'
a8='1.8'
a9='2.1'
a10='2.4'
a11='2.7'
a12='3.3'

b1='3.3'
b2='2.7'
b3='2.4'
b4='2.1'
b5='1.8'
b6='1.5'
b7='1.2'
b8='1.16'
b9='1.13'
b10='1.1'
b11='1.05'
b12='1.02'

ASPR_P=(/a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11,a12/)
ASPR_PR=(/b1,b2,b3,b4,b5,b6,b7,b8,b9,b10,b11,b12/)


SHAPE=3
DO IASPR=1,NASPR
   aspr_n= ASPR_PR(IASPR)
  ! write(*,*) aspr_n
   CALL READ_DUST_DATA(aux_dir,shape,aspr_n)
   P11_DUST_TMP(IASPR,:,:)=p11p(:,IREFF,IVAR,:)
   P12_DUST_TMP(IASPR,:,:)=p12p(:,IREFF,IVAR,:)
   P22_DUST_TMP(IASPR,:,:)=p22p(:,IREFF,IVAR,:)
   P33_DUST_TMP(IASPR,:,:)=p33p(:,IREFF,IVAR,:)
   P34_DUST_TMP(IASPR,:,:)=p34p(:,IREFF,IVAR,:)
   P44_DUST_TMP(IASPR,:,:)=p44p(:,IREFF,IVAR,:)
   QEXT_DUST_TMP(IASPR,:)=qep(IREFF,IVAR,:)
   SSA_DUST_TMP(IASPR,:)=ssap(IREFF,IVAR,:)
   AREA_DUST_TMP(IASPR,:)=areap(IREFF,IVAR,:)
   DEALLOCATE(p11s,p12s,p22s,p33s,p34s,p44s,gs,qes, vints, ssas,scat_ang,scat_angs)
   DEALLOCATE(p11o,p12o,p22o,p33o,p34o,p44o,go,qeo, vinto,ssao,areao)
   DEALLOCATE(p11p,p12p,p22p,p33p,p34p,p44p,gp,qep, vintp, ssap,areap)
END DO

SHAPE=2
DO IASPR=NASPR+1,2*NASPR
   aspr_n=ASPR_P(IASPR-NASPR)
   CALL READ_DUST_DATA(aux_dir,shape,aspr_n)
   P11_DUST_TMP(IASPR,:,:)=p11o(:,IREFF,IVAR,:)
   P12_DUST_TMP(IASPR,:,:)=p12o(:,IREFF,IVAR,:)
   P22_DUST_TMP(IASPR,:,:)=p22o(:,IREFF,IVAR,:)
   P33_DUST_TMP(IASPR,:,:)=p33o(:,IREFF,IVAR,:)
   P34_DUST_TMP(IASPR,:,:)=p34o(:,IREFF,IVAR,:)
   P44_DUST_TMP(IASPR,:,:)=p44o(:,IREFF,IVAR,:)
   QEXT_DUST_TMP(IASPR,:)=qeo(IREFF,IVAR,:)
   SSA_DUST_TMP(IASPR,:)=ssao(IREFF,IVAR,:)
   AREA_DUST_TMP(IASPR,:)=areao(IREFF,IVAR,:)
   DEALLOCATE(p11s,p12s,p22s,p33s,p34s,p44s,gs,qes, vints, ssas,scat_ang,scat_angs)
   DEALLOCATE(p11o,p12o,p22o,p33o,p34o,p44o,go,qeo, vinto,ssao,areao)
   DEALLOCATE(p11p,p12p,p22p,p33p,p34p,p44p,gp,qep, vintp, ssap,areap)
END DO

CALL READ_DUST_DATA(aux_dir,3,ASPR_P(1))
SCATANG(:)=SCAT_ANG(:)
DEALLOCATE(p11s,p12s,p22s,p33s,p34s,p44s,gs,qes, vints, ssas,scat_ang,scat_angs)
DEALLOCATE(p11o,p12o,p22o,p33o,p34o,p44o,go,qeo, vinto,ssao,areao)
DEALLOCATE(p11p,p12p,p22p,p33p,p34p,p44p,gp,qep, vintp, ssap,areap)


!PHMX_DUST_TMP1(1,:,:,:)=P11_DUST_TMP(:,:,:)
!PHMX_DUST_TMP1(2,:,:,:)=P12_DUST_TMP(:,:,:)
!PHMX_DUST_TMP1(3,:,:,:)=P22_DUST_TMP(:,:,:)
!PHMX_DUST_TMP1(4,:,:,:)=P33_DUST_TMP(:,:,:)
!PHMX_DUST_TMP1(5,:,:,:)=P34_DUST_TMP(:,:,:)
!PHMX_DUST_TMP1(6,:,:,:)=P44_DUST_TMP(:,:,:)

PHMX_DUST_TMP1(1,:,:,:)=P11_DUST_TMP(:,:,:)
PHMX_DUST_TMP1(2,:,:,:)=P22_DUST_TMP(:,:,:)
PHMX_DUST_TMP1(3,:,:,:)=P33_DUST_TMP(:,:,:)
PHMX_DUST_TMP1(4,:,:,:)=P44_DUST_TMP(:,:,:)
PHMX_DUST_TMP1(5,:,:,:)=P12_DUST_TMP(:,:,:)
PHMX_DUST_TMP1(6,:,:,:)=P34_DUST_TMP(:,:,:)


DO IASPR=1,NASPR*2
   DO IWV=1,18
      DO IANG=1,500
         DO IPHMX=1,6
            PHMX_DUST_TMP(IASPR,IWV,IANG,IPHMX)=PHMX_DUST_TMP1(IPHMX,IASPR,IANG,IWV) 
         END DO
      END DO
   END DO
END DO


!Trapzoidal integration (Assume equal-probable distribution)

N_ASPR_DIS_F=1

IF (N_ASPR_DIS_F==1) THEN !equal probable distribution
   ASPR_BIN = (/0.3d0 , 0.07d0, 0.05d0, 0.06d0, 0.08d0, 0.11d0, 0.16d0, 0.03d0,&
        0.02d0, 0.03d0, 0.04d0, 0.03d0, 0.04d0, 0.03d0, 0.05d0, 0.03d0, 0.03d0,&
        0.04d0, 0.3d0 , 0.3d0 , 0.3d0 , 0.3d0 ,0.3d0 , 0.6d0/)
   !equiprobable assumption n(de)=1 for de=0.1
   !log scale
   ASPR_BIN=LOG(ASPR_BIN)
   DO IASPR=1,NASPR*2
      N_ASPR_D(IASPR)=ASPR_BIN(IASPR)/LOG(0.1)
   END DO
END IF

!IF (N_ASPR_DIS_F==2) THEN !Power law distribution (Merilkallio et al., 2011)
!   N_ASPR_D= ABS(1-ASPR)**1.5
!END IF (incomplete)

ASPR=LOG(ASPR)

DO IWV=1,NWV_D
   A_INT_TMP(IWV)=TRAPZOID(NASPR*2,ASPR,N_ASPR_D(1:NASPR*2)*AREA_DUST_TMP(1:NASPR*2,IWV))
   QE_INT_TMP(IWV)=TRAPZOID(NASPR*2,ASPR,N_ASPR_D(1:NASPR*2)*AREA_DUST_TMP(1:NASPR*2,IWV)* &
        QEXT_DUST_TMP(1:NASPR*2,IWV))
   SSA_INT_TMP(IWV)=TRAPZOID(NASPR*2,ASPR,N_ASPR_D(1:NASPR*2)*AREA_DUST_TMP(1:NASPR*2,IWV)* &
        QEXT_DUST_TMP(1:NASPR*2,IWV) *SSA_DUST_TMP(1:NASPR*2,IWV))
END DO

N_ASPR=TRAPZOID(NASPR,ASPR,N_ASPR_D)

A_INT=A_INT_TMP/N_ASPR
AREA=SUM(A_INT)/NWV_D

QE_DUST=QE_INT_TMP/A_INT_TMP
SSA_DUST=SSA_INT_TMP/QE_INT_TMP

!write(*,*) 'QE_DUST',QE_DUST

DO IWV=1,NWV_D
   DO IANG=1,NSCATANG
      DO IPHMX=1,6
         PHMX_INT_TMP(IWV,IANG,IPHMX)=TRAPZOID(NASPR*2,ASPR,N_ASPR_D(1:NASPR*2)*AREA_DUST_TMP(1:NASPR*2,IWV)* &
              QEXT_DUST_TMP(1:NASPR*2,IWV)*SSA_DUST_TMP(1:NASPR*2,IWV)*PHMX_DUST_TMP(1:NASPR*2,IWV,IANG,IPHMX))
      END DO
   END DO
END DO

DO IWV=1,NWV_D
   DO IANG=1,NSCATANG
            DO IPHMX=1,6
               PHMX_DUST(IWV,IANG,IPHMX)=PHMX_INT_TMP(IWV,IANG,IPHMX)/SSA_INT_TMP(IWV)
            END DO
         END DO
      END DO
      
      
QS_DUST=QE_DUST*SSA_DUST
CSCAT_DUST=QS_DUST*AREA
CEXT_DUST=QE_DUST*AREA


!write(*,*) 'PHMX_DUST_at reading', phmx_dust(1,1,1)
!write(*,*) 'PHMX_DUST after reading', PHMX_DUST(:10,:10,1)

END SUBROUTINE DUST_SCAT_PROP_INIT
