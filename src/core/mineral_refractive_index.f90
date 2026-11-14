! Zhang et al. (2024), DOI:10.1029/2023JD040181.
! Dataset version 1.3: https://zenodo.org/records/14171144
! Reads the absolute (not water-relative) coarse-mode refractive indices.
! Table layout: (wavelength row, regional sample column), 127 x 27.
! Wavelengths are in micrometres. k is the nonnegative absorption index.
module mineral_refractive_index
  implicit none
  private
  integer, parameter, public :: ri_dp = selected_real_kind(15, 307)
  integer, parameter, public :: ri_nwave = 127, ri_nsample = 27
  public :: read_mineral_ri, interpolate_mineral_ri

  ! Exact concatenation of GroupRefInd/swav.txt then GroupRefInd/lwav.txt.
  ! Independently checked against column 1 of GroupRefInd/coarseMode127.dat.
  real(ri_dp), parameter :: source_wavelength(ri_nwave) = (/ &
    0.2_ri_dp, 0.22_ri_dp, 0.25_ri_dp, 0.28_ri_dp, 0.3_ri_dp, &
    0.32_ri_dp, 0.34_ri_dp, 0.35_ri_dp, 0.355_ri_dp, 0.375_ri_dp, &
    0.4_ri_dp, 0.423_ri_dp, 0.44_ri_dp, 0.46_ri_dp, 0.48_ri_dp, &
    0.5_ri_dp, 0.52_ri_dp, 0.532_ri_dp, 0.535_ri_dp, 0.55_ri_dp, &
    0.58_ri_dp, 0.6_ri_dp, 0.62_ri_dp, 0.635_ri_dp, 0.65_ri_dp, &
    0.67_ri_dp, 0.69_ri_dp, 0.71_ri_dp, 0.73_ri_dp, 0.755_ri_dp, &
    0.78_ri_dp, 0.8_ri_dp, 0.83_ri_dp, 0.85_ri_dp, 0.873_ri_dp, &
    0.9_ri_dp, 0.92_ri_dp, 0.95_ri_dp, 0.98_ri_dp, 1.015_ri_dp, &
    1.04_ri_dp, 1.064_ri_dp, 1.1_ri_dp, 1.15_ri_dp, 1.2_ri_dp, &
    1.25_ri_dp, 1.3_ri_dp, 1.35_ri_dp, 1.4_ri_dp, 1.449_ri_dp, &
    1.504_ri_dp, 1.555_ri_dp, 1.615_ri_dp, 1.68_ri_dp, 1.73_ri_dp, &
    1.79_ri_dp, 1.85_ri_dp, 1.905_ri_dp, 1.95_ri_dp, 2.0_ri_dp, &
    2.08_ri_dp, 2.19_ri_dp, 2.25_ri_dp, 2.32_ri_dp, 2.4_ri_dp, &
    2.5_ri_dp, 2.6_ri_dp, 2.7_ri_dp, 2.8_ri_dp, 2.9_ri_dp, &
    3.077_ri_dp, 3.2_ri_dp, 3.413_ri_dp, 3.5_ri_dp, 3.7_ri_dp, &
    3.85_ri_dp, 4.01_ri_dp, 4.25_ri_dp, 4.5_ri_dp, 4.75_ri_dp, &
    5.0_ri_dp, 5.25_ri_dp, 5.5_ri_dp, 5.75_ri_dp, 6.0_ri_dp, &
    6.2_ri_dp, 6.5_ri_dp, 6.8_ri_dp, 7.2_ri_dp, 7.5_ri_dp, &
    7.9_ri_dp, 8.2_ri_dp, 8.5_ri_dp, 8.7_ri_dp, 9.0_ri_dp, &
    9.2_ri_dp, 9.5_ri_dp, 9.8_ri_dp, 10.0_ri_dp, 10.2_ri_dp, &
    10.5_ri_dp, 11.0_ri_dp, 11.5_ri_dp, 12.0_ri_dp, 12.5_ri_dp, &
    13.0_ri_dp, 13.5_ri_dp, 14.0_ri_dp, 14.4_ri_dp, 14.8_ri_dp, &
    15.0_ri_dp, 15.6_ri_dp, 16.4_ri_dp, 17.2_ri_dp, 18.0_ri_dp, &
    18.5_ri_dp, 19.2_ri_dp, 20.0_ri_dp, 21.3_ri_dp, 22.5_ri_dp, &
    25.0_ri_dp, 27.9_ri_dp, 30.0_ri_dp, 35.0_ri_dp, 40.0_ri_dp, &
    45.0_ri_dp, 50.0_ri_dp /)
  real(ri_dp), save :: saved_n(ri_nwave, ri_nsample)
  real(ri_dp), save :: saved_k(ri_nwave, ri_nsample)
  logical, save :: loaded = .false.

contains

  subroutine read_mineral_ri(data_directory, ierr, message)
    character(len=*), intent(in) :: data_directory
    real(ri_dp) :: n_table(ri_nwave, ri_nsample)
    real(ri_dp) :: k_table(ri_nwave, ri_nsample)
    integer, optional, intent(out) :: ierr
    character(len=*), optional, intent(out) :: message
    character(len=len_trim(data_directory)+32) :: n_path, k_path
    character(len=512) :: detail
    integer :: status, length

    loaded = .false.
    n_table = 0.0_ri_dp
    k_table = 0.0_ri_dp
    call report_status(0, '', ierr, message)
    length = len_trim(data_directory)
    if (length == 0) then
      n_path = 'nall27_coarse.dat'
      k_path = 'kall27_coarse.dat'
    else if (data_directory(length:length) == '/') then
      n_path = trim(data_directory)//'nall27_coarse.dat'
      k_path = trim(data_directory)//'kall27_coarse.dat'
    else
      n_path = trim(data_directory)//'/nall27_coarse.dat'
      k_path = trim(data_directory)//'/kall27_coarse.dat'
    end if

    call read_matrix(trim(n_path), n_table, status, detail)
    if (status == 0) call read_matrix(trim(k_path), k_table, status, detail)
    if (status == 0) then
      if (.not. all(n_table > 0.0_ri_dp .and. n_table <= huge(1.0_ri_dp))) then
        status = 3
        detail = 'The real-index table must contain finite, positive values.'
      else if (.not. all(k_table >= 0.0_ri_dp .and. k_table <= huge(1.0_ri_dp))) then
        status = 3
        detail = 'The imaginary-index table must contain finite, nonnegative values.'
      end if
    end if
    if (status /= 0) then
      n_table = 0.0_ri_dp
      k_table = 0.0_ri_dp
      call report_status(status, detail, ierr, message)
      return
    end if
    saved_n = n_table
    saved_k = k_table
    loaded = .true.
  end subroutine read_mineral_ri

  subroutine interpolate_mineral_ri(wavelength_um, sample_number, n_real, k_imag, ierr, message)
    real(ri_dp), intent(in) :: wavelength_um
    integer, intent(in) :: sample_number
    real(ri_dp), intent(out) :: n_real, k_imag
    integer, optional, intent(out) :: ierr
    character(len=*), optional, intent(out) :: message
    integer :: lower, upper, middle
    real(ri_dp) :: weight

    n_real = 0.0_ri_dp
    k_imag = 0.0_ri_dp
    call report_status(0, '', ierr, message)
    if (.not. loaded) then
      call report_status(4, 'Call read_mineral_ri successfully before interpolation.', ierr, message)
      return
    end if
    if (sample_number < 1 .or. sample_number > ri_nsample) then
      call report_status(5, 'Sample number must be between 1 and 27.', ierr, message)
      return
    end if
    ! Written this way to reject NaN and infinite wavelengths as well.
    if (.not. (wavelength_um >= source_wavelength(1) .and. &
               wavelength_um <= source_wavelength(ri_nwave))) then
      call report_status(6, 'Wavelength must be within 0.2 to 50 micrometres; no extrapolation.', ierr, message)
      return
    end if
    lower = 1
    upper = ri_nwave
    do while (upper-lower > 1)
      middle = (lower+upper)/2
      if (wavelength_um < source_wavelength(middle)) then
        upper = middle
      else
        lower = middle
      end if
    end do
    if (wavelength_um == source_wavelength(lower)) then
      n_real = saved_n(lower, sample_number)
      k_imag = saved_k(lower, sample_number)
    else if (wavelength_um == source_wavelength(upper)) then
      n_real = saved_n(upper, sample_number)
      k_imag = saved_k(upper, sample_number)
    else
      weight = (wavelength_um-source_wavelength(lower)) / &
               (source_wavelength(upper)-source_wavelength(lower))
      n_real = (1.0_ri_dp-weight)*saved_n(lower,sample_number) + weight*saved_n(upper,sample_number)
      k_imag = (1.0_ri_dp-weight)*saved_k(lower,sample_number) + weight*saved_k(upper,sample_number)
    end if
  end subroutine interpolate_mineral_ri

  subroutine read_matrix(path, values, status, detail)
    character(len=*), intent(in) :: path
    real(ri_dp), intent(out) :: values(ri_nwave,ri_nsample)
    integer, intent(out) :: status
    character(len=*), intent(out) :: detail
    character(len=8192) :: line
    character(len=32) :: row_string
    integer :: unit_number, candidate, ios, row
    real(ri_dp) :: row_values(ri_nsample)
    logical :: opened

    values = 0.0_ri_dp
    status = 1
    detail = 'No free Fortran I/O unit in the range 10 to 99.'
    unit_number = -1
    do candidate = 10, 99
      opened = .true.
      inquire(unit=candidate, opened=opened, iostat=ios)
      if (ios == 0 .and. .not. opened) then
        unit_number = candidate
        exit
      end if
    end do
    if (unit_number < 0) return
    open(unit=unit_number, file=path, status='old', action='read', iostat=ios)
    if (ios /= 0) then
      detail = 'Cannot open '//trim(path)
      return
    end if
    row = 0
    do
      read(unit_number,'(A)',iostat=ios) line
      if (ios < 0) exit
      if (ios > 0) then
        detail = 'I/O error while reading '//trim(path)
        close(unit_number)
        return
      end if
      if (len_trim(line) == 0) cycle
      row = row+1
      if (row > ri_nwave) then
        status = 2
        detail = 'Expected exactly 127 nonblank rows in '//trim(path)
        close(unit_number)
        return
      end if
      call parse_row(line, row_values, ios)
      if (ios /= 0) then
        status = 2
        write(row_string,'(I8)') row
        detail = 'Expected 27 numeric fields at row '//trim(adjustl(row_string))//' in '//trim(path)
        close(unit_number)
        return
      end if
      values(row,:) = row_values
    end do
    close(unit_number)
    if (row /= ri_nwave) then
      status = 2
      detail = 'Expected exactly 127 nonblank rows in '//trim(path)
      return
    end if
    status = 0
    detail = ''
  end subroutine read_matrix

  ! Accept comma-separated or whitespace-separated numbers, but reject missing
  ! fields and extra columns. Read each physical row independently: no spillover.
  subroutine parse_row(line, values, status)
    character(len=*), intent(in) :: line
    real(ri_dp), intent(out) :: values(ri_nsample)
    integer, intent(out) :: status
    integer :: pos, finish, first, count, ios
    logical :: needs_value
    values = 0.0_ri_dp
    status = 1
    finish = len_trim(line)
    pos = 1
    count = 0
    needs_value = .true.
    do while (pos <= finish)
      if (line(pos:pos) == ' ' .or. line(pos:pos) == achar(9) .or. line(pos:pos) == achar(13)) then
        pos = pos+1
      else if (line(pos:pos) == ',') then
        if (needs_value) return
        needs_value = .true.
        pos = pos+1
      else
        first = pos
        do while (pos <= finish)
          if (index(' ,'//achar(9)//achar(13), line(pos:pos)) /= 0) exit
          pos = pos+1
        end do
        count = count+1
        if (count > ri_nsample) return
        ! Disallow list-directed repetition/null/termination syntax in raw CSV.
        if (index(line(first:pos-1),'*') /= 0 .or. index(line(first:pos-1),'/') /= 0) return
        read(line(first:pos-1),*,iostat=ios) values(count)
        if (ios /= 0) return
        needs_value = .false.
      end if
    end do
    if (count /= ri_nsample .or. needs_value) return
    status = 0
  end subroutine parse_row

  ! With ierr present, return an error code and optional explanation. Without
  ! ierr, fail loudly rather than allow invalid optical data into the simulator.
  subroutine report_status(status, detail, ierr, message)
    integer, intent(in) :: status
    character(len=*), intent(in) :: detail
    integer, optional, intent(out) :: ierr
    character(len=*), optional, intent(out) :: message
    if (present(message)) message = detail
    if (present(ierr)) then
      ierr = status
    else if (status /= 0) then
      write(*,'(A)') 'mineral_refractive_index: '//trim(detail)
      stop 1
    end if
  end subroutine report_status

end module mineral_refractive_index
