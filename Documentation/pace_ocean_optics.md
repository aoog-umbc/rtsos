# Ocean and surface model options

This guide describes the implemented PACE simulator surface choices and ocean-optics
updates introduced in November 2026. The selector controls both land surfaces and
ocean water models despite its name, `OCEAN_CASE_SELECT`. The mineral tables described
later are used only for the Case 2 suspended-sediment calculation. Their dust-derived
optical constants feed the simulator's spherical Mie solver; this integration does
not replace atmospheric aerosol models or load the dataset's dust phase matrices.

## Supported OCEAN_CASE_SELECT values

The implemented choices are `0`, `1`, `2`, `3`, `-200`, `-201`, `-202`, and `-203`.
Use these specific values. The generic `-1` entry in the current Python parameter
metadata is not an implemented land-surface selector in the PACE Fortran program.

| Value | Lower boundary / water model | Main inputs | Extra data beyond the standard auxiliary bundle |
| --- | --- | --- | --- |
| `0` | Ocean interface, black water body | Wind speed and interface flags | None |
| `1` | Chlorophyll-based Case 1 water | `chla`, `ap_select`, depth/profile and inelastic settings | None |
| `2` | Chlorophyll-associated particles and mineral sediment | Case 1 absorption/profile inputs, phytoplankton Mie inputs, sediment sample/slope/concentration | `nall27_coarse.dat`, `kall27_coarse.dat` |
| `3` | Seven-parameter water model | `chla`, `adg440`, `bbp660_BackscatterCoeff`, `Bp660_BackscatterFraction`, `Sdg`, `Sbp`, `S_Bp` | None |
| `-200` | Lambertian–Fresnel land surface | Albedo, Lambertian fraction, real and imaginary index | User land spectral file |
| `-201` | mRPV land surface | `pBRDFa`, `pBRDFk`, `pBRDFb`, `pBRDFe`, real and imaginary index | User land spectral file |
| `-202` | Snow surface | Spectral snow albedo | User land spectral file and snow BRDF tables |
| `-203` | Ross–Li surface with polarized reflection | `fiso`, `fvol`, `fgeo`, `Bpol`, real and imaginary index | User land spectral file |

These descriptions follow `main_PACE_Simulator_DoubleK.f90`, especially its input
reader, `RTSOSINIT`, and `HYDRSL_PARA_INIT`. The generic parameter metadata and some
older script comments are less specific than these implemented branches.

### Case 0: black water body beneath the ocean interface

This option suppresses the water-leaving contribution and sets the lower water
boundary to black. The ocean interface remains, so surface reflection, including sun
glint when enabled, can still contribute to the observed signal. It is not equivalent
to removing the ocean interface. The code disables Raman scattering, chlorophyll and
CDOM fluorescence, and hyperspectral water-source calculations for this case.

Supply the complete non-land positional input layout, including unused ocean
parameters. Use a valid integer placeholder such as `sediment_sample_num=1`. The
mineral tables are not loaded for this case.

### Case 1: chlorophyll-based water

This option combines pure seawater, chlorophyll-associated particle absorption and
scattering, and a chlorophyll-dependent CDOM absorption model. `chla` is in mg m^-3;
`ap_select=1` uses the Bricaud absorption lookup table and `ap_select=2` uses the
Ciotti pico/micro mixture. The UV absorption is joined to the selected visible model
at 400 nm. Water depth, chlorophyll profile, Raman scattering, and fluorescence flags
control the corresponding water-column calculations.

The current source fixes `BIOCASE1_SELECT=2` inside `HYDRSL_PARA_INIT`. Its active
attenuation parameterization is:

```text
cp550 = 0.33 * chla**0.57
gamma = -0.4 + 2.2 / (1 + sqrt(chla))
cp(lambda) = cp550 * (550 / lambda_nm)**gamma
bp(lambda) = cp(lambda) - ap(lambda)
```

These are the current deterministic values: the local random-number vector is reset
to 0.5 before evaluating this branch. The alternative `BIOCASE1_SELECT=1` scattering
law remains in the source but is not selected by a parameter-file option. The
Case 2 Morel (2009) attenuation law described below does not replace this Case 1 law.

Case 1 uses an empirical backscattering fraction and a Fournier–Forand particle phase
function mixed with seawater scattering. It does not use the new sediment mineral
model, sediment concentration, or phytoplankton Mie index/slope inputs. These unused
fields must still occupy their positions in a text input file.

### Case 2: chlorophyll-associated particles plus mineral sediment

This option uses the selected `ap_select` absorption model, a chlorophyll-associated
attenuation model, and separate Mie optical properties for phytoplankton and minerals.
The current chlorophyll-associated attenuation is
`cp(lambda) = 0.377 * chla**0.53 * (488 / lambda_nm)` in m^-1.
The sediment contribution depends on `sediment_sample_num`,
`sediment_spectral_slope`, and `sediment_concentration`; the phytoplankton phase matrix
depends on its own relative index and size-distribution exponent.

The full mineral data, units, input migration, and calculation details are given in
[the following data section](#required-data-and-provenance) and
[the Case 2 calculation notes](#changes-to-the-optical-calculations).
The two mineral tables are required even for a zero sediment concentration.

### Case 3: seven-parameter water model

This option uses chlorophyll for particle absorption, with six additional parameters
that control combined dissolved/nonalgal absorption and particle backscattering:

| Python/input-generator name | Meaning | Units |
| --- | --- | --- |
| `chla` | Chlorophyll-a concentration used for absorption | mg m^-3 |
| `adg440` | Combined dissolved/nonalgal absorption at 440 nm | m^-1 |
| `bbp660_BackscatterCoeff` | Particle backscattering coefficient at 660 nm | m^-1 |
| `Bp660_BackscatterFraction` | Particle backscattering fraction at 660 nm | Dimensionless |
| `Sdg` | Exponential absorption slope | nm^-1 |
| `Sbp` | Power-law exponent of particle backscattering | Dimensionless |
| `S_Bp` | Power-law exponent of the backscattering fraction | Dimensionless |

For wavelength `lambda_nm` in nanometres, the code evaluates:

```text
adg(lambda) = adg440 * exp(-Sdg * (lambda_nm - 440))
bbp(lambda) = bbp660_BackscatterCoeff * (lambda_nm / 660)**(-Sbp)
Bbp(lambda) = Bp660_BackscatterFraction * (lambda_nm / 660)**(-S_Bp)
bp(lambda) = bbp(lambda) / Bbp(lambda)
```

Use a positive backscattering fraction no larger than one over the simulated range.
The power-law exponents `Sbp` and `S_Bp` are dimensionless, although current Python
metadata and some generator comments label them as `1/nm`. Only `Sdg` has inverse-nm
units. `adg` is assigned to `ACDMLOCAL` in the implementation; a separate sediment
absorption/scattering component is not added in this option.

The program forces `AP_SELECT=1` for Case 3, so Bricaud absorption is used even if the
input requests Ciotti. As in Case 1, the phase matrix is assembled using the empirical
particle representation and seawater scattering rather than the new mineral Mie
component. The mineral data files are not required.

### Land cases -200 through -203

These options replace the atmosphere–ocean system with an atmosphere–land system.
Water-column inputs and ocean inelastic flags are omitted from the land text-input
layout; the code disables ocean Raman and fluorescence calculations. A land spectral
filename is inserted after the two aerosol phase-matrix filenames and before the
output filename.

Use `test/PACE_Simulator/python_script/pace_simulator_twolayer_inputfile_land.py`.
Set `bottom_case_select` and its index `icase`, and edit the surface spectra and
auxiliary paths. For example, to generate mRPV inputs:

```python
bottom_case_select = np.array([-201])
icase = 0
```

The generator creates both the simulator parameter file and its land spectral file.
The latter has one header line, a line containing the number of wavelength rows, and
then **seven numeric columns per row**, with these model-specific meanings:

| Case | Column 1 | Column 2 | Column 3 | Column 4 | Column 5 | Column 6 | Column 7 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `-200` | Wavelength, nm | Lambertian albedo | Lambertian fraction | Unused | Unused | Real index | Imaginary index |
| `-201` | Wavelength, nm | `pBRDFa` | `pBRDFk` | `pBRDFb` | `pBRDFe` | Real index | Imaginary index |
| `-202` | Wavelength, nm | Snow albedo | Unused | Unused | Unused | Unused | Unused |
| `-203` | Wavelength, nm | `fiso` | `fvol` | `fgeo` | `Bpol` | Real index | Imaginary index |

Retain numeric placeholders for unused columns. Cover the wavelengths used in the
simulation; the reader interpolates each input column to the requested wavelengths.
The common storage names `fiso_input`, `fvol_input`, `fgeo_input`, and `Bpol_input`
therefore have different physical meanings for different surface cases.

- **`-200`, Lambertian–Fresnel:** the Lambertian fraction ranges from zero to one.
  One selects a purely Lambertian surface; reducing it introduces the weighted
  Fresnel specular contribution. The real and imaginary indices specify the Fresnel
  material. For a pure Lambertian example at 550 nm, a row could be
  `550 0.2 1.0 0 0 1.5 0`.
- **`-201`, mRPV:** supply the four mRPV parameters and the complex surface index.
  This is a directional land-reflection model, not an ocean IOP selection. The
  generator's example row at 550 nm is `550 0.155 1.5 -0.5 0 1.5 0`.
- **`-202`, snow:** the supplied spectral albedo sets the brightness; the angular
  BRDF shape uses the snow auxiliary tables. The current path construction requires
  a trailing slash on `aux_dir`, for example `/absolute/path/to/Data/`, followed by
  the existing subdirectory `SnowBRDF_Data/brdfPaperMaterial/`. It reads `albedo.txt`
  and `eof_A.txt` through `eof_F.txt` from that subdirectory. The mineral refractive-index
  tables are not used. A surface-file row could be `550 0.98 0 0 0 0 0`.
- **`-203`, Ross–Li:** provide isotropic, volumetric, and geometric kernel weights
  (`fiso`, `fvol`, `fgeo`), the polarized term parameter `Bpol`, and the complex
  surface index. These are surface-reflectance parameters, not water absorption or
  scattering coefficients. An example row is `550 0.05 0.005 0.025 1 1.5 0`.

### Choosing the input interface

The ocean generator writes the ocean-format record sequence and should be restricted
to choices `0`–`3`. The land generator writes the shorter land-format sequence and
surface filename for `-200`–`-203`. Changing only the selector in an existing ocean
text file does not convert it to a land input.

The current `rtsos PACE_Simulator_DoubleK` Python wrapper also has a fixed ocean-format
parameter list and no land spectral filename parameter. Use it for ocean options
`0`–`3`; use the land text generator and binary executable for land options. Merely
setting a negative selector in a wrapper NetCDF dataset does not supply the required
land input layout. This guide documents the current interface without changing it.

All choices still require the main RTSOS auxiliary files, atmosphere profile, and
instrument data; the program loads some water tables during common initialization
even for land runs. The mineral pair is an additional requirement only for Case 2.
For ocean cases, `SUN_GLINT_FLAG=0` includes glint and `1` disables it. For all cases,
`ATMOS_ZERO=1` removes the atmospheric contribution, whereas the default `0` retains it.

## Optional wind direction

PACE ocean cases `0`, `1`, `2`, and `3` accept an optional line after the output
filename, at the end of the positional text input:

```text
output_scene.h5
0.5 0.8660254  # wind direction cosines
```

The first input line still specifies wind speed in m/s. The optional pair is
`wind_x = cos(theta_w)`, `wind_y = sin(theta_w)`, with a unit norm. `theta_w` is the
direction **toward which** the wind blows, in degrees counterclockwise viewed from
above, measured from viewing azimuth zero on the solar-glint side of the principal
plane. These are dimensionless direction cosines, not east/north velocity components.

The reader follows the monochromatic executable's behavior: EOF retains isotropy;
blank and comment-only lines are skipped; `#` and `!` start comments. A nonnumeric
first meaningful line retains isotropy and ends the search. A finite vector whose
norm differs from 1 by more than `1e-6` is reported and ignored. Accepted vectors
are normalized to remove rounding errors. Parsed NaN/Inf components and read errors
other than EOF stop the program. Land cases ignore the optional wind trailer.

The direction is initialized once and reused across excitation wavelengths and all
output-wavelength calls. With the default Cox-Munk roughness parameterization, it
selects the existing non-Gaussian **direct solar reflection** routine. Diffuse
reflection, interface transmission, Smith shadowing, and water-column source
calculations retain their isotropic treatments. Wind speeds below 0.5 m/s select
flat water, and disabling sun glint disables the directional reflected contribution.

The viewing-azimuth grid remains 0-180 degrees for compatibility. For arbitrary
wind directions, do not reconstruct the other half-plane by the usual fixed-wind
mirror symmetry.

### Standalone input generators

In `test/PACE_Simulator/python_script/`, both
`pace_simulator_twolayer_inputfile_ocean.py` and
`synthetic_Holton_sequence_inputfiles.py` now provide:

```python
wind_vector = None  # e.g. (0.5, 0.8660254)
```

`None` preserves the existing input layout and filenames. Set a two-component tuple
to append the wind line. Directional filenames include `_wind_<x>_<y>` so they are
distinct from the corresponding isotropic run. The Halton sequence still samples
its original five parameters; `wind_vector` is a configurable setting shared by
that generated batch.

### Python wrapper

The `rtsos PACE_Simulator_DoubleK` wrapper starts from a NetCDF input dataset, writes
a text input for each parameter combination, runs the executable, and combines the
HDF5 results. It exposes wind direction as a single coordinate, `Wind_Direction`,
in degrees, and converts it into the required cosine/sine pair after `OUTFILE`.
The default is NaN, which omits the wind line. Existing NetCDF inputs without this
coordinate are also supported. Infinite angles are rejected; finite angles are
wrapped into `[0,360)`. Land runs omit the wind trailer.

For example, create defaults, then enable a single wind direction:

```sh
rtsos PACE_Simulator_DoubleK --pre pace_defaults.nc
```

```python
import xarray as xr

ds = xr.load_dataset("pace_defaults.nc")
ds["Wind_Direction"][()] = 60.0
# Configure Aux_Dir, Atmos_Dir, and other simulation settings as usual.
ds.to_netcdf("pace_wind.nc")
```

```sh
rtsos PACE_Simulator_DoubleK pace_wind.nc pace_output.nc
```

To sweep several directions, replace the scalar coordinate with:

```python
direction_attrs = ds["Wind_Direction"].attrs.copy()
ds = ds.assign_coords(Wind_Direction=xr.DataArray(
    [0.0, 60.0, 270.0], dims="Wind_Direction", attrs=direction_attrs,
))
```

The wrapper writes a separate valid unit vector and a distinct temporary output
name for each direction. Avoid treating the x and y components as independent
sweep coordinates, which would create non-unit combinations. The Fortran output
uses `Wind_Direction_Used` for the accepted angle, so input/output comparisons do
not confuse the requested angle with its wrapped or normalized representation.

### Wind metadata in HDF5 output

The existing `Wind_Speed` dataset is retained. New scalar datasets are:

| Dataset | Meaning |
| --- | --- |
| `Wind_Vector_Present` | `1` if the direction was accepted; otherwise `0`. |
| `Wind_X`, `Wind_Y` | Accepted, normalized direction cosines; both zero when unspecified. |
| `Wind_Direction_Used` | Accepted angle in `[0,360)` degrees; `-999` when unspecified. |
| `Wind_Direction_Active` | `1` if directional direct solar reflection is enabled; `0` for isotropic, flat, land, or glint-disabled cases. |
| `Water_Surface_Model` | `-1`: non-ocean; `0`: flat; `1`: isotropic Gaussian; `2`: directional Cox-Munk direct solar reflection. |

Descriptions, angle units, model codes, and the direct-reflection scope are attached
as HDF5 attributes. An accepted vector may be present while inactive, for example
with flat water or sun glint disabled.

### Regression checks

From the repository root, run the wrapper and input-generator checks with:

```sh
PYTHONPATH=src python -m pytest src/checks/test_pace_wind.py
```

For executable/HDF5 checks, also set `RTSOS_PACE_EXECUTABLE` to the rebuilt PACE
executable, `RTSOS_DATA_DIR` to the extracted Data directory, and `RTSOS_GAS_DIR`
to the gas/profile directory. Optionally set `RTSOS_PACE_BASELINE` to an older
executable to check that existing output datasets are unchanged when wind direction
is omitted. All simulation inputs and outputs are generated in temporary directories.

## Required data and provenance

First obtain the main RTSOS auxiliary data as described in the
[README](../README.md#12-auxiliary-data). Then follow the
[mineral-table download instructions](../README.md#additional-mineral-data-for-case-2).
The additional dataset is:

- Zhang, Y., Saito, M., Yang, P., Schuster, G. L., and Trepte, C. R. (2024),
  *Sensitivities of Spectral Optical Properties of Dust Aerosols to their
  Mineralogical and Microphysical Properties*.
  [Paper DOI](https://doi.org/10.1029/2023JD040181).
- [Dataset version 1.3, pinned record](https://doi.org/10.5281/zenodo.14171144).
  Its [readme](https://zenodo.org/records/14171144/files/readme_v1.3.txt?download=1)
  describes the different files and versions.

The runtime files are `nall27_coarse.dat` and `kall27_coarse.dat`. Place them directly
in the directory specified by `aux_dir` / `Aux_Dir`, alongside the existing water,
plankton, and instrument files. For example:

```text
/path/to/auxiliary/Data/
    nall27_coarse.dat
    kall27_coarse.dat
    ap_PicoMicro.txt
    ap_UV_biosope.dat
    ...other RTSOS auxiliary files...
```

The simulator reads both tables during Case 2 Mie initialization, including runs with
zero sediment concentration. Case 1 and Case 3 do not initialize this mineral model.

For reproducibility, the v1.3 file MD5 values published by Zenodo are:

| File | MD5 |
| --- | --- |
| `nall27_coarse.dat` | `4fea222a6b423518f9a67440c5438bea` |
| `kall27_coarse.dat` | `c72aafff7b0999da1d93b0e4758405a7` |

On macOS, run `md5 /path/to/auxiliary/Data/nall27_coarse.dat` and the corresponding
command for `kall27_coarse.dat`. On Linux, use `md5sum` with the same paths.

### Which files and sample should I choose?

Use the coarse-mode n and k pair together. The current reader expects these exact
filenames; fine-mode files are not selected through an input flag. The word *coarse*
identifies the source optical-constant dataset. The simulator's particle size
distribution is still controlled by its own sediment model parameters.

`sediment_sample_num` selects a column, numbered **1 through 27 in the original
order**. Consult
[NewRegionalSamples.xlsx](https://zenodo.org/records/14171144/files/NewRegionalSamples.xlsx?download=1)
for regional composition information when choosing a representative sample. The
Python default is column 1; it is a default selection, not an automatic geographic
match or a universal sediment composition. The 27 columns represent regional mineral
mixtures, not 27 individual mineral species.

The files `GroupRefInd.tar.gz`, `DustSamples.tar.gz`, `BulkProperties.tar.gz`, and
`PhaseMatrices.tar.gz` are not required by this runtime reader. The simulator computes
its own Mie optical properties. `GroupRefInd.tar.gz` is useful for inspecting the
original wavelength grid and individual mineral-group optical constants.

### Wavelengths and table format

Each runtime table contains **127 rows by 27 columns**. The parser accepts comma- or
whitespace-separated numeric fields. Do not add a header or a wavelength column.
The real and imaginary tables must retain the same row and column ordering.

The 127-point wavelength grid spans **0.2 to 50 micrometres**. It is the concatenation
of `GroupRefInd/swav.txt` followed by `GroupRefInd/lwav.txt`, and is embedded in
`src/core/mineral_refractive_index.f90`. Neither `wavelength_um.dat` nor an extracted
`GroupRefInd` directory is needed at runtime. The module linearly interpolates n and k
separately and rejects extrapolation outside this grid.

The tables contain absolute refractive indices. Supply them unchanged: the simulator
converts n and k to indices relative to water and uses the wavelength in water when
calling the Mie solver. The tabulated absorption index k is nonnegative.

## Case 2 inputs and units

| Input | Meaning | Units or allowed values |
| --- | --- | --- |
| `OCEAN_CASE_SELECT` | Selects the Case 2 ocean implementation | `2` |
| `chla` | Chlorophyll-a concentration | mg m^-3 |
| `phytoplankton_index_refraction` | Existing real phytoplankton index relative to water | Dimensionless, e.g. `1.02` |
| `sediment_sample_num` | Column of the paired mineral tables | Integer 1–27 |
| `sediment_spectral_slope` | Junge exponent used in the sediment particle size distribution | Dimensionless |
| `sediment_concentration` | Sediment mass concentration | g m^-3; nonnegative |
| `aux_dir` / `Aux_Dir` | Directory containing both new tables and existing auxiliary data | Directory path |
| `ap_select` | Chlorophyll-associated absorption model | `1`: Bricaud; `2`: Ciotti mixture |

The concentration unit g m^-3 is numerically equivalent to mg L^-1. The sediment
size-distribution exponent is no longer applied as an additional power law to a
665 nm sediment scattering coefficient; its effect enters through the Mie calculation.

### Text input generators

In `test/PACE_Simulator/python_script/pace_simulator_twolayer_inputfile_ocean.py`
or `synthetic_Holton_sequence_inputfiles.py`, select a Case 2 run and set:

```python
sediment_sample_num = 1
sediment_spectral_slope = 4.0
sediment_concentration = 1.0  # g m^-3; illustrative, not a recommended concentration
aux_dir = "/absolute/path/to/auxiliary/Data/"
```

Retain the other required inputs and regenerate the text parameter file. In its
positional ocean-input block, the relevant lines are now:

```text
1.02       # PHYTOPLANKTON_INDEX_REFRACTION
3.0        # PHYTOPLANKTON_SPECTRAL_SLOPE
1          # SEDIMENT_SAMPLE_NUM: integer column number, 1-27
4.0        # SEDIMENT_SPECTRAL_SLOPE
1.0        # SEDIMENT_CONCENTRATION, g m^-3
```

### Python wrapper and NetCDF inputs

Generate a new template using the updated installation:

```shell
rtsos PACE_Simulator_DoubleK --pre defaults.nc
```

For a scalar Case 2 selection, update the template with Python:

```python
import numpy as np
import xarray as xr

with xr.open_dataset("defaults.nc") as source:
    inputs = source.load()
inputs["OCEAN_CASE_SELECT"] = np.int32(2)
inputs["sediment_sample_num"] = np.int32(1)
inputs["sediment_concentration"] = np.float32(1.0)  # g m^-3
inputs["Aux_Dir"] = "/absolute/path/to/auxiliary/Data"
inputs["Atmos_Dir"] = "/absolute/path/to/Gas_Absorption_Coefficients"
inputs.to_netcdf("inputs.nc")
```

The template contains arrays for several other parameters. Select their values or
subsets as needed before running. Preview generated text inputs without running the
radiative-transfer calculation:

```shell
rtsos PACE_Simulator_DoubleK --dry-run inputs.nc preview.nc
```

Run the actual simulations with:

```shell
rtsos PACE_Simulator_DoubleK inputs.nc outputs.nc
```

### Migrating existing inputs

The former floating-point `sediment_index_refraction` / `SEDIMENT_INDEX_REFRACTION`
parameter has been replaced by the integer `sediment_sample_num` /
`SEDIMENT_SAMPLE_NUM`, in the same text-input position. An old value such as `1.2`
is not a valid sample number. There is no unique conversion from a constant index to
a regional mixture; select a sample from the dataset and regenerate the inputs.

This position is read for all non-land input cases (`OCEAN_CASE_SELECT >= 0`), even
though the mineral optical model is used only for Case 2. Use an integer placeholder
such as `1` for the other ocean cases.

For existing NetCDF inputs, the preferred approach is to generate a fresh template and
transfer the desired settings, choosing an integer `sediment_sample_num`. Remove the
obsolete `sediment_index_refraction` coordinate. Do not simply rename that coordinate
while keeping its old refractive-index value. The wrapper can skip missing fields
when writing positional text inputs, so a dataset missing the new parameter can shift
subsequent parameters into incorrect positions.

## Changes to the optical calculations

The following describe the implemented choices, rather than a claim that one empirical
model applies universally to all water types.

- **Mineral absorption and scattering:** sediment scattering uses Mie `Csca`, and
  absorption uses `Cext - Csca`, with the same particle distribution and mass
  normalization. The previous 665 nm extrapolation with an empirical absorption
  subtraction is no longer active. Sediment absorption is therefore not additionally
  added from the old Babin exponential parameterization.
- **Sediment density:** the current approximation evaluates the selected sample's real
  index at 0.55 micrometres, divides it by 1.34, and uses
  `rho = 6.779e6 * n_relative - 5.232e6` in g m^-3. Density is constant with wavelength
  for a selected sample. This empirical estimate is not a measured sample density.
- **Chlorophyll-associated attenuation, Case 2:** the code uses
  `cp(488) = 0.377 * chla**0.53` in m^-1, from
  [Morel (2009), Eq. 17](https://doi.org/10.1029/2008JC004803), and
  `cp(lambda) = cp(488) * (488 / lambda_nm)**gamma_cp`, with `gamma_cp = 1` currently
  fixed in the source. The spectral choice is informed by
  [Boss et al. (2013)](https://doi.org/10.1016/j.mio.2013.11.002).
  Scattering is calculated as `bp = cp - ap`. This is the chlorophyll-associated
  component; the separately computed sediment coefficients are added to it.
- **Backscattering:** Case 2 uses Mie-derived backscattering fractions consistently
  when calculating and reporting the plankton and mineral backscattering coefficients.
  Nearest-band lookups in these coefficient routines are restricted to initialized bands.
- **Absorption normalization:** the UV absorption spectrum is matched to the selected
  visible absorption model at 400 nm for both `ap_select=1` and `ap_select=2`.
  The Ciotti pico basis is anchored at 676 nm and the micro basis at 674 nm, following
  [Ciotti et al. (2002), Table 3](https://doi.org/10.4319/lo.2002.47.2.0404).
- **Inelastic calculations:** enabling Raman scattering or either fluorescence source
  causes initialization over the full existing instrument-band grid. Aerosol phase
  matrices loaded from files must cover the corresponding required bands.

The 0.2–50 micrometre refractive-index grid does not establish the validity range of
the empirical chlorophyll model or extend the simulator's Mie band grid. Its existing
lack of bands below approximately 314.6 nm remains a separate limitation; shorter
wavelength coefficient lookups may use the nearest initialized band. Evaluate UV and
infrared applications separately. Dust-derived mineral mixtures and spherical Mie
particles are also modeling assumptions when representing natural aquatic sediments.

## Fortran interface and rebuilding

`src/core/mineral_refractive_index.f90` stores the tables privately in double
precision. Its public calls are:

```fortran
use mineral_refractive_index, only: ri_dp, read_mineral_ri, interpolate_mineral_ri
integer :: ierr
character(len=512) :: message
real(ri_dp) :: n_real, k_imag

call read_mineral_ri('/absolute/path/to/auxiliary/Data', ierr, message)
if (ierr /= 0) error stop trim(message)
call interpolate_mineral_ri(0.55_ri_dp, 1, n_real, k_imag, ierr, message)
if (ierr /= 0) error stop trim(message)
```

`read_mineral_ri` takes the directory containing the two files and does not return the
tables or wavelength grid. `interpolate_mineral_ri` takes wavelength in micrometres
and a one-based sample number. Both routines accept optional error-code and message
outputs. Without an error-code argument, invalid input terminates the program. The
PACE simulator performs this initialization itself; users do not add these calls to
its parameter files.

Both the PACE Makefile and the core CMake library must include the new module.
After updating sources, use a fresh build directory to avoid stale module files:

```shell
cmake -S . -B build/ocean-optics
cmake --build build/ocean-optics --target rtsos_PACE_Simulator_DoubleK -j 2
```

Configure `HDF5_ROOT` as described in the README if needed. This CMake target produces
`build/ocean-optics/src/rtsos_PACE_Simulator_DoubleK` on macOS/Linux. The legacy Makefile
build produces `rtsos_PACE_Simulator_DoubleK.exe` in its build directory. Rebuild the
executable used by your scripts, or reinstall the updated Python package so its bundled
executable is rebuilt.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| Cannot open `nall27_coarse.dat` or `kall27_coarse.dat` | Both files must be directly inside the configured auxiliary directory; check the path, filenames, and read permissions. |
| Reader expects 127 rows or 27 fields | Download the original coarse-mode pair, retain its layout, and check the file checksums. A saved HTML download page is not a data table. |
| Invalid integer while reading the input | Replace the old refractive-index value with an integer sample number and regenerate the positional input. |
| Sample number outside 1–27 | Select a valid original column; do not use zero-based numbering. |
| Wavelength outside 0.2–50 micrometres | Pass micrometres to the interpolation routine; it does not extrapolate. |
| `CPTCLOCAL<APTCLOCAL` | The chosen absorption and attenuation models imply negative `bp`; inspect the wavelength, chlorophyll concentration, and model choices. The code stops rather than accepting that result. |
| No initialized bands available | Check the Mie initialization sequence and the selected band/inelastic settings. |
| Cannot open `mineral_refractive_index.mod` | Ensure the build configuration includes the new module and rebuild in a fresh directory. |
