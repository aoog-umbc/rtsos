MODULE hdf5_utils
  USE HDF5
  USE H5DS
  IMPLICIT NONE
CONTAINS

subroutine create_dim_scale(file, name, values, dset_id)
  use hdf5
  implicit none

  ! Inputs
  integer(hid_t), intent(in)  :: file
  character(len=*), intent(in):: name
  real, dimension(:), intent(in) :: values

  ! Output
  integer(hid_t), intent(out) :: dset_id

  ! Locals
  integer(hid_t) :: space
  integer(hsize_t), dimension(1) :: dims
  integer :: hdferr

  ! Define dataspace
  dims(1) = size(values)
  call h5screate_simple_f(1, dims, space, hdferr)

  ! Create dataset
  call h5dcreate_f(file, name, H5T_IEEE_F32LE, space, dset_id, hdferr)

  ! Write data
  call h5dwrite_f(dset_id, H5T_NATIVE_REAL, values, dims, hdferr)

  ! Mark as dimension scale
  call h5dsset_scale_f(dset_id, hdferr)

  ! Close space
  call h5sclose_f(space, hdferr)

end subroutine create_dim_scale

subroutine write_scalar_real(file_id, name, value)
  use hdf5
  implicit none

  integer(HID_T), intent(in) :: file_id
  character(len=*), intent(in) :: name
  real, intent(in) :: value

  integer(HID_T) :: dspace_id, dset_id
  integer :: hdferr
  integer(HSIZE_T), dimension(1) :: dims

  ! Scalar dataspace (rank-1 with size 1)
  dims(1) = 1
  call h5screate_simple_f(1, dims, dspace_id, hdferr)

  ! Create dataset
  call h5dcreate_f(file_id, trim(name), H5T_NATIVE_REAL, dspace_id, dset_id, hdferr)

  ! Write data
  call h5dwrite_f(dset_id, H5T_NATIVE_REAL, value, dims, hdferr)

  ! Close
  call h5dclose_f(dset_id, hdferr)
  call h5sclose_f(dspace_id, hdferr)

end subroutine write_scalar_real

subroutine write_scalar_int(file_id, name, value)
  use hdf5
  implicit none

  integer(HID_T), intent(in) :: file_id
  character(len=*), intent(in) :: name
  integer, intent(in) :: value

  integer(HID_T) :: dspace_id, dset_id
  integer :: hdferr
  integer(HSIZE_T), dimension(1) :: dims

  ! Scalar dataspace (rank-1 with size 1)
  dims(1) = 1
  call h5screate_simple_f(1, dims, dspace_id, hdferr)

  ! Create dataset
  call h5dcreate_f(file_id, trim(name), H5T_NATIVE_INTEGER, dspace_id, dset_id, hdferr)

  ! Write data
  call h5dwrite_f(dset_id, H5T_NATIVE_INTEGER, value, dims, hdferr)

  ! Close
  call h5dclose_f(dset_id, hdferr)
  call h5sclose_f(dspace_id, hdferr)

end subroutine write_scalar_int


subroutine write_1d_int(file, name, values, dim1)
  use hdf5
  implicit none

  ! Inputs
  integer(hid_t), intent(in)        :: file
  character(len=*), intent(in)      :: name
  integer, dimension(:), intent(in) :: values
  integer(hid_t), intent(in), optional :: dim1

  ! Locals
  integer(hid_t) :: space, dset
  integer(hsize_t), dimension(1) :: dims
  integer :: hdferr

  ! Define dimensions
  dims(1) = size(values)

  ! Create dataspace
  call h5screate_simple_f(1, dims, space, hdferr)

  ! Create dataset
  call h5dcreate_f(file, name, H5T_STD_I32LE, space, dset, hdferr)

  ! Write data (IMPORTANT: pass dims to avoid interface ambiguity)
  call h5dwrite_f(dset, H5T_NATIVE_INTEGER, values, dims, hdferr)

  ! Attach dimension scale if provided
  if (present(dim1)) then
	call h5dsattach_scale_f(dset, dim1, 1, hdferr)
  end if

  ! Close resources
  call h5dclose_f(dset, hdferr)
  call h5sclose_f(space, hdferr)

end subroutine write_1d_int

SUBROUTINE write_1d_real(file, name, data, dim1)
  IMPLICIT NONE

  INTEGER(HID_T), INTENT(IN) :: file
  CHARACTER(*), INTENT(IN)   :: name
  REAL, DIMENSION(:), INTENT(IN) :: data
  INTEGER(HID_T), INTENT(IN), OPTIONAL :: dim1

  INTEGER(HID_T) :: space, dset
  INTEGER(HSIZE_T), DIMENSION(1) :: dims
  INTEGER :: hdferr

  dims(1) = SIZE(data,1)

  CALL h5screate_simple_f(1, dims, space, hdferr)
  CALL h5dcreate_f(file, name, H5T_IEEE_F32LE, space, dset, hdferr)

  CALL h5dwrite_f(dset, H5T_NATIVE_REAL, data, dims, hdferr)

  IF (PRESENT(dim1)) THEN
	CALL h5dsattach_scale_f(dset, dim1, 1, hdferr)
  ENDIF

  CALL h5dclose_f(dset, hdferr)
  CALL h5sclose_f(space, hdferr)
END SUBROUTINE

SUBROUTINE write_2d_real(file, name, data, dim1, dim2)
  IMPLICIT NONE

  INTEGER(HID_T), INTENT(IN) :: file
  CHARACTER(*), INTENT(IN)   :: name
  REAL, DIMENSION(:,:), INTENT(IN) :: data
  INTEGER(HID_T), INTENT(IN), OPTIONAL :: dim1, dim2

  INTEGER(HID_T) :: space, dset
  INTEGER(HSIZE_T), DIMENSION(2) :: dims
  INTEGER :: hdferr

  dims = SHAPE(data)

  CALL h5screate_simple_f(2, dims, space, hdferr)
  CALL h5dcreate_f(file, name, H5T_IEEE_F32LE, space, dset, hdferr)

  CALL h5dwrite_f(dset, H5T_NATIVE_REAL, data, dims, hdferr)

  IF (PRESENT(dim1)) CALL h5dsattach_scale_f(dset, dim1, 1, hdferr)
  IF (PRESENT(dim2)) CALL h5dsattach_scale_f(dset, dim2, 2, hdferr)

  CALL h5dclose_f(dset, hdferr)
  CALL h5sclose_f(space, hdferr)
END SUBROUTINE

SUBROUTINE write_3d_real(file, name, data, dim1, dim2, dim3)
  IMPLICIT NONE

  INTEGER(HID_T), INTENT(IN) :: file
  CHARACTER(*), INTENT(IN)   :: name
  REAL, DIMENSION(:,:,:), INTENT(IN) :: data
  INTEGER(HID_T), INTENT(IN), OPTIONAL :: dim1, dim2, dim3

  INTEGER(HID_T) :: space, dset
  INTEGER(HSIZE_T), DIMENSION(3) :: dims
  INTEGER :: hdferr

  dims = SHAPE(data)

  CALL h5screate_simple_f(3, dims, space, hdferr)
  CALL h5dcreate_f(file, name, H5T_IEEE_F32LE, space, dset, hdferr)

  CALL h5dwrite_f(dset, H5T_NATIVE_REAL, data, dims, hdferr)

  IF (PRESENT(dim1)) CALL h5dsattach_scale_f(dset, dim1, 1, hdferr)
  IF (PRESENT(dim2)) CALL h5dsattach_scale_f(dset, dim2, 2, hdferr)
  IF (PRESENT(dim3)) CALL h5dsattach_scale_f(dset, dim3, 3, hdferr)

  CALL h5dclose_f(dset, hdferr)
  CALL h5sclose_f(space, hdferr)
END SUBROUTINE

SUBROUTINE write_4d_real(file, name, data, dim1, dim2, dim3, dim4)
  IMPLICIT NONE

  INTEGER(HID_T), INTENT(IN) :: file
  CHARACTER(*), INTENT(IN)   :: name
  REAL, DIMENSION(:,:,:,:), INTENT(IN) :: data
  INTEGER(HID_T), INTENT(IN), OPTIONAL :: dim1, dim2, dim3, dim4

  INTEGER(HID_T) :: space, dset
  INTEGER(HSIZE_T), DIMENSION(4) :: dims
  INTEGER :: hdferr

  dims = SHAPE(data)

  CALL h5screate_simple_f(4, dims, space, hdferr)
  CALL h5dcreate_f(file, name, H5T_IEEE_F32LE, space, dset, hdferr)

  CALL h5dwrite_f(dset, H5T_NATIVE_REAL, data, dims, hdferr)

  IF (PRESENT(dim1)) CALL h5dsattach_scale_f(dset, dim1, 1, hdferr)
  IF (PRESENT(dim2)) CALL h5dsattach_scale_f(dset, dim2, 2, hdferr)
  IF (PRESENT(dim3)) CALL h5dsattach_scale_f(dset, dim3, 3, hdferr)
  IF (PRESENT(dim4)) CALL h5dsattach_scale_f(dset, dim4, 4, hdferr)

  CALL h5dclose_f(dset, hdferr)
  CALL h5sclose_f(space, hdferr)
END SUBROUTINE

END MODULE hdf5_utils

