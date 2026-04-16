MODULE hdf5_utils
USE hdf5
USE h5ds
USE iso_c_binding
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
  call h5dcreate_f(file, name, H5T_NATIVE_REAL, space, dset_id, hdferr)

  ! Write data
  call h5dwrite_f(dset_id, H5T_NATIVE_REAL, values, dims, hdferr)

  ! Mark as dimension scale
  CALL h5dsset_scale_f(dset_id, hdferr)

  ! Close space
  call h5sclose_f(space, hdferr)

end subroutine create_dim_scale

SUBROUTINE write_scalar_real(file, name, value)
  USE HDF5
  IMPLICIT NONE

  INTEGER(HID_T), INTENT(IN) :: file
  CHARACTER(*), INTENT(IN)   :: name
  REAL, INTENT(IN)           :: value

  INTEGER(HID_T) :: space, dset
  INTEGER :: hdferr
  ! We declare a dummy array of size 0 or 1 for the interface
  INTEGER(HSIZE_T), DIMENSION(1) :: dims

  ! 1. Scalar dataspace (True scalar, rank 0)
  CALL h5screate_f(H5S_SCALAR_F, space, hdferr)

  ! 2. Create dataset
  CALL h5dcreate_f(file, name, H5T_NATIVE_REAL, space, dset, hdferr)

  ! 3. Write scalar value
  ! Pass 'dims' even though it's a scalar; HDF5 ignores its content
  ! for H5S_SCALAR_F but requires the argument to match the generic interface.
  CALL h5dwrite_f(dset, H5T_NATIVE_REAL, value, dims, hdferr)

  ! 4. Clean up
  CALL h5dclose_f(dset, hdferr)
  CALL h5sclose_f(space, hdferr)
END SUBROUTINE

SUBROUTINE write_scalar_int(file, name, value)
  USE HDF5
  IMPLICIT NONE

  INTEGER(HID_T), INTENT(IN) :: file
  CHARACTER(*), INTENT(IN)   :: name
  INTEGER, INTENT(IN)        :: value

  INTEGER(HID_T) :: space, dset
  INTEGER :: hdferr
  INTEGER(HSIZE_T), DIMENSION(1) :: dims

  ! 1. Create scalar dataspace
  CALL h5screate_f(H5S_SCALAR_F, space, hdferr)

  ! 2. Create dataset
  CALL h5dcreate_f(file, name, H5T_NATIVE_INTEGER, space, dset, hdferr)

  ! 3. Write scalar value
  CALL h5dwrite_f(dset, H5T_NATIVE_INTEGER, value, dims, hdferr)

  ! 4. Clean up
  CALL h5dclose_f(dset, hdferr)
  CALL h5sclose_f(space, hdferr)
END SUBROUTINE


subroutine write_1d_int(file, name, values, c_dim_1)
  use hdf5
  implicit none

  ! Inputs
  integer(hid_t), intent(in)        :: file
  character(len=*), intent(in)      :: name
  integer, dimension(:), intent(in) :: values
  integer(hid_t), intent(in), optional :: c_dim_1

  ! Locals
  integer(hid_t) :: space, dset
  integer(hsize_t), dimension(1) :: dims
  integer :: hdferr

  ! Define dimensions
  dims(1) = size(values)

  ! Create dataspace
  call h5screate_simple_f(1, dims, space, hdferr)

  ! Create dataset
  call h5dcreate_f(file, name, H5T_NATIVE_INTEGER, space, dset, hdferr)

  ! Write data (IMPORTANT: pass dims to avoid interface ambiguity)
  call h5dwrite_f(dset, H5T_NATIVE_INTEGER, values, dims, hdferr)

  ! Attach dimension scale if provided
  if (present(c_dim_1)) then
	call h5dsattach_scale_f(dset, c_dim_1, 1, hdferr)
  end if

  ! Close resources
  call h5dclose_f(dset, hdferr)
  call h5sclose_f(space, hdferr)

end subroutine write_1d_int

! ==========================================
! Subroutine to write a 1D Real Array
! ==========================================
SUBROUTINE write_1d_real(file_id, dataset_name, data_array, c_dim_1)
	USE HDF5
	USE H5DS
	IMPLICIT NONE

	INTEGER(HID_T), INTENT(IN) :: file_id
	CHARACTER(LEN=*), INTENT(IN) :: dataset_name
	REAL, DIMENSION(:), INTENT(IN) :: data_array
	INTEGER(HID_T), INTENT(IN) :: c_dim_1  ! Pre-existing scale ID

	INTEGER(HID_T) :: dset_id, dspace_id
	INTEGER(HSIZE_T), DIMENSION(1) :: dims
	INTEGER :: hdferr
	INTEGER :: rank = 1

	dims(1) = SIZE(data_array, 1)

	CALL h5screate_simple_f(rank, dims, dspace_id, hdferr)
	CALL h5dcreate_f(file_id, dataset_name, H5T_NATIVE_REAL, dspace_id, dset_id, hdferr)
	CALL h5dwrite_f(dset_id, H5T_NATIVE_REAL, data_array, dims, hdferr)

	! Attach the single dimension scale
	CALL h5dsattach_scale_f(dset_id, c_dim_1, 1, hdferr)

	CALL h5dclose_f(dset_id, hdferr)
	CALL h5sclose_f(dspace_id, hdferr)
END SUBROUTINE write_1d_real

! ==========================================
! Subroutine to write a 2D Real Array
! ==========================================
SUBROUTINE write_2d_real(file_id, dataset_name, data_array, c_dim_1, c_dim_2)
	USE HDF5
	USE H5DS
	IMPLICIT NONE

	INTEGER(HID_T), INTENT(IN) :: file_id
	CHARACTER(LEN=*), INTENT(IN) :: dataset_name
	REAL, DIMENSION(:,:), INTENT(IN) :: data_array
	INTEGER(HID_T), INTENT(IN) :: c_dim_1, c_dim_2 ! Pre-existing scale IDs

	INTEGER(HID_T) :: dset_id, dspace_id
	INTEGER(HSIZE_T), DIMENSION(2) :: dims
	INTEGER :: hdferr
	INTEGER :: rank = 2

	dims(1) = SIZE(data_array, 1)
	dims(2) = SIZE(data_array, 2)

	CALL h5screate_simple_f(rank, dims, dspace_id, hdferr)
	CALL h5dcreate_f(file_id, dataset_name, H5T_NATIVE_REAL, dspace_id, dset_id, hdferr)
	CALL h5dwrite_f(dset_id, H5T_NATIVE_REAL, data_array, dims, hdferr)

	! Attach scales to both dimensions
	CALL h5dsattach_scale_f(dset_id, c_dim_1, 2, hdferr)
	CALL h5dsattach_scale_f(dset_id, c_dim_2, 1, hdferr)

	CALL h5dclose_f(dset_id, hdferr)
	CALL h5sclose_f(dspace_id, hdferr)
END SUBROUTINE write_2d_real


SUBROUTINE write_4d_real(file_id, dataset_name, data_array, &
						 c_dim_1, c_dim_2, c_dim_3, c_dim_4)
	USE HDF5
	USE H5DS ! Required for Dimension Scale operations
	IMPLICIT NONE

	! Input Arguments
	INTEGER(HID_T), INTENT(IN) :: file_id      ! File identifier
	CHARACTER(LEN=*), INTENT(IN) :: dataset_name
	REAL, DIMENSION(:,:,:,:), INTENT(IN) :: data_array
	
	! These are the identifiers for the coordinate datasets (e.g., 'WV_BAND')
	INTEGER(HID_T), INTENT(IN) :: c_dim_1, c_dim_2, c_dim_3, c_dim_4

	! Local HDF5 Variables
	INTEGER(HID_T) :: dset_id, dspace_id
	INTEGER(HSIZE_T), DIMENSION(4) :: dims
	INTEGER :: hdferr
	INTEGER :: rank = 4

	! 1. Get dimensions from the actual data array
	dims(1) = SIZE(data_array, 1)
	dims(2) = SIZE(data_array, 2)
	dims(3) = SIZE(data_array, 3)
	dims(4) = SIZE(data_array, 4)

	! 2. Create the dataspace for the 4D array
	CALL h5screate_simple_f(rank, dims, dspace_id, hdferr)

	! 3. Create the main dataset
	! Using H5T_NATIVE_REAL ensures it matches the Fortran REAL precision
	CALL h5dcreate_f(file_id, dataset_name, H5T_NATIVE_REAL, dspace_id, dset_id, hdferr)

	! 4. Write the data
	CALL h5dwrite_f(dset_id, H5T_NATIVE_REAL, data_array, dims, hdferr)

	! 5. Attach the pre-existing Dimension Scales
	! The third argument is the index of the dimension (1-based in Fortran)
	CALL h5dsattach_scale_f(dset_id, c_dim_1, 4, hdferr)
	CALL h5dsattach_scale_f(dset_id, c_dim_2, 3, hdferr)
	CALL h5dsattach_scale_f(dset_id, c_dim_3, 2, hdferr)
	CALL h5dsattach_scale_f(dset_id, c_dim_4, 1, hdferr)

	! 6. Clean up the 4D dataset and its space (does not close the scales)
	CALL h5dclose_f(dset_id, hdferr)
	CALL h5sclose_f(dspace_id, hdferr)

END SUBROUTINE write_4d_real

END MODULE hdf5_utils

