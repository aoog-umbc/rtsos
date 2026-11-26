# Input and Output Files of the RTSOS Code

Pengwang Zhai · Physics Department, UMBC · pwzhai@gmail.com

This guide describes the input and output files of the monochromatic RTSOS executable. It was converted from [SOS_io.tex](Describtion_of_input_files/SOS_io.tex) and updated to match the current [monochromatic main program](../src/main_program_monochromatic/main.f90) and [RTSOS core](../src/core/rtsos_rao_dg.f90), including the optional wind-direction input.

## Package directories and running the executable

In this guide, `SOSDIR` means the repository root, the directory containing `README.md`. The main directories are:

| Directory | Contents |
| --- | --- |
| `src/` | Fortran source code, including the monochromatic core `core/rtsos_rao_dg.f90`. |
| `compile/` | Legacy Makefiles. |
| `test/monochromatic/` | Monochromatic input files and example outputs. |
| `validation/benchmark/` | Benchmark cases. |

See the [README installation instructions](../README.md#1-installation) for the current CMake build procedure. The legacy Makefile workflow is:

```sh
SOSDIR=/absolute/path/to/SOS_Callable
cd "$SOSDIR/compile"
make
cp rtsos_rao_dg.exe ../test/monochromatic/
cd ../test/monochromatic/
./rtsos_rao_dg.exe sosi.example vSOS.example_run
```

The two command-line arguments are the system input filename and the output filename. The system input is called `sosi.dat` generically in this guide; its actual filename is your choice. The legacy executable is named `rtsos_rao_dg.exe`; CMake builds use `rtsos_rao_dg` on macOS/Linux.

The executable also reads `sosi.amu` and the specified phase-matrix files. Relative paths are resolved from the **current working directory**, which need not be the directory containing the executable. Optional surface data and solar irradiance data are described below.

## Angle file: `sosi.amu`

This file specifies the incident and outgoing directions. All input angles are in degrees. For example:

```text
1
120
10 4
0.0
20.
40.
60.
80.
100.
120.
140.
160.
180.
0.
60.
120.
180.
```

Read the file in this order:

1. The number of incident directions, `NTHETAIN`.
2. `NTHETAIN` incident zenith angles, one per line.
3. Two integers: the number of outgoing zenith angles, `NTHETAOUT`, and the number of outgoing azimuth angles, `NPHIOUT`.
4. `NTHETAOUT` outgoing zenith angles, one per line.
5. `NPHIOUT` outgoing azimuth angles, one per line.

The example requests one incident direction, ten outgoing zenith angles from 0° to 180° in 20° increments, and four outgoing azimuths: 0°, 60°, 120°, and 180°.

### Direction convention

Positive $z$ points upward. Zenith angles describe **photon propagation directions**: the code uses $\mu=\cos\theta$. Downward incident sunlight therefore has a negative incident cosine. An incident angle of 120° in `sosi.amu` corresponds to a conventional solar zenith angle of 60°.

Outgoing zenith angles below 90° describe upward propagation; angles above 90° describe downward propagation. Azimuth zero lies on the specular-glint side of the solar principal plane. Azimuth increases counterclockwise when viewed from above. The optional wind direction uses this same horizontal coordinate system.

## System input file: `sosi.dat`

### Record order and example

The file contains:

1. Seven-column configuration records, ordered from the top of the atmosphere to the bottom boundary.
2. A line containing `NCOL NQUADA NQUADO`.
3. A line containing `NUMMIE MAXLORD MAXMORD`.
4. `NUMMIE` phase-matrix filenames, one per line.
5. A required snow-data directory line if `IPT=-202` is used.
6. An optional wind-direction line if `IPT=-100`, `-101`, or `-102` is used. If a snow-data directory is also required, the wind line follows that directory line.

Here is a complete coupled atmosphere–ocean example without an optional wind line:

```text
-1000 0.0 0.0 0.0 0.0 0.0 0.0
1     0.1 1.0 0.412 215.0 0.0 0.0
-1000 0.0 0.0 0.0 0.0 0.0 0.0
-100  7.0 1.34 0.0 0.0 0.0 0.0
-1000 0.0 0.0 0.0 0.0 0.0 0.0
2     0.1 1.0 0.412 215.0 0.0 0.0
-1000 0.0 0.0 0.0 0.0 0.0 0.0
-200  1.0 1.0 1.5 0.0 0.0 0.0
40 30 60
2 30 10
RayDepol0.pmtx
gamma_aa_0.03bb_0.33wv0.35.pmtx
```

The first **eight** lines are seven-column configuration records. Column 1 is `IPT`, identifying the record type. The example specifies:

| Line | Meaning |
| --- | --- |
| 1 | A detector at the top of the atmosphere. |
| 2 | An atmospheric layer using phase matrix 1, with optical thickness 0.1, single-scattering albedo 1, wavelength 0.412 µm (412 nm), and temperature 215 K. |
| 3 | A detector at the bottom of the atmosphere, just above the ocean interface. |
| 4 | An air–water interface with wind speed 7 m/s, water refractive index $1.34+0i$, and sun glint included. |
| 5 | A detector just below the ocean interface. |
| 6 | An ocean layer using phase matrix 2, with optical thickness 0.1 and single-scattering albedo 1. |
| 7 | A detector at the bottom of the ocean layer. |
| 8 | A Lambertian ocean bottom with albedo 1. |
| 9 | 40 scattering orders, with atmosphere and ocean quadrature settings 30 and 60. |
| 10 | Two phase matrices, maximum Wigner expansion order 30, and maximum Fourier order 10. |
| 11–12 | Phase-matrix filenames associated with `IPT=1` and `IPT=2`, respectively. |

**Wavelengths in the configuration records are in micrometers.** Use `0.412` for 412 nm. The original LaTeX example used `412.0`, which the current code interprets as 412 µm.

To use wind direction in this example, append:

```text
0.5 0.8660254
```

This specifies wind blowing toward azimuth 60° at the speed already given in column 2 of the water-surface record.

### `IPT` values and seven-column fields

Every configuration record contains seven numbers, including `IPT`. `BN` below means an unused numeric placeholder: supply a number such as `0.0`, rather than leaving the field empty.

| `IPT` | Record type |
| --- | --- |
| `-1000` | Detector. |
| Positive integer | Atmospheric or ocean scattering layer; the integer selects a phase-matrix file. |
| `-100` | Air–water interface with an explicitly modeled ocean below it. |
| `-101` | Water surface as the lower boundary, without an explicitly modeled ocean water column. |
| `-102` | Water surface as the lower boundary for infrared calculations, with temperature and emissivity. |
| `-200` | Lambertian/flat Fresnel reflection boundary. |
| `-201` | Polarized BRDF boundary. |
| `-202` | Snow BRDF boundary. |
| `-203` | Ross–Li boundary with a polarized reflection term. |

| Column 1 | Column 2 | Column 3 | Column 4 | Column 5 | Column 6 | Column 7 |
| --- | --- | --- | --- | --- | --- | --- |
| `-1000` | BN | BN | BN | BN | BN | BN |
| `IPT>0` | `TAU` | `LBDOM` | Wavelength (µm) | Temperature (K) | `EFLRSC` | `ALH` |
| `-100` | Wind speed (m/s) | Real water refractive index | Imaginary water refractive index | Glint flag | `RSR0P` | `FWC` |
| `-101` | Wind speed (m/s) | Real water refractive index | Imaginary water refractive index | Glint flag | `RSR0P` | `FWC` |
| `-102` | Wind speed (m/s) | Real water refractive index | Imaginary water refractive index | Glint flag | Temperature (K) | Emissivity |
| `-200` | Albedo | `flam` | Real bottom refractive index | Imaginary bottom refractive index | Temperature (K) | Emissivity field; see below |
| `-201` | `pBRDFa` | `pBRDFk` | `pBRDFb` | `pBRDFe` | Real bottom refractive index | Imaginary bottom refractive index |
| `-202` | Albedo | BN | BN | BN | BN | BN |
| `-203` | `fiso` | `fvol` | `fgeo` | `Bpol` | Real bottom refractive index | Imaginary bottom refractive index |

`TAU` is the optical thickness of the individual layer, not the cumulative optical depth. `LBDOM` is its single-scattering albedo. `EFLRSC` controls ocean inelastic-scattering sources and should be zero in ordinary monochromatic inputs; ocean inelastic calculations require a dedicated main program. `ALH` is the atmospheric layer top height, in kilometers, used by the pseudospherical-shell treatment.

For pseudospherical calculations, set the atmospheric heights consistently and enable the option in the main program, for example:

```fortran
USE RTUTILITY, ONLY : PSEUDO_SPHERICAL_SHELL
! ... executable statements ...
PSEUDO_SPHERICAL_SHELL = .TRUE.
```

Layers before the `-100` interface are atmospheric layers, and layers below it are ocean layers. The records `-101`, `-102`, `-200`, `-201`, `-202`, and `-203` terminate the configuration. No further detector or layer records follow a terminating boundary; the next line contains the numerical controls. A `-100` interface does not terminate the configuration: supply the ocean records and a bottom boundary after it.

### Numerical controls and phase-matrix filenames

The line immediately after the terminating boundary contains:

```text
NCOL NQUADA NQUADO
```

`NCOL` is the number of scattering orders. `NQUADA` and `NQUADO` control the atmospheric and ocean quadratures used in source-function integration. The single-quadrature implementation ignores the separate ocean setting. Choose sufficient scattering orders and quadrature resolution for the accuracy required; check convergence for your case.

The next line contains:

```text
NUMMIE MAXLORD MAXMORD
```

`NUMMIE` is the number of phase-matrix files. `MAXLORD` is the maximum order of the Wigner-function expansion of the scattering matrix. `MAXMORD` is the maximum Fourier order. The next `NUMMIE` lines contain filenames: the first is selected by `IPT=1`, the second by `IPT=2`, and so on. Multiple layers may share the same phase matrix.

### Water-surface parameters

The wind speed in column 2 is in m/s. Columns 3 and 4 contain the real and imaginary parts of the water refractive index. A glint flag of `0` includes sun glint; `1` excludes it.

For `-100` and `-101`, `RSR0P` and `FWC` control prescribed water-leaving reflectance or surface coverage. Normally both are zero. `RSR0P` denotes just-above-water remote-sensing reflectance. For prescribed whitecaps or other floating debris, supply their equivalent Lambertian reflectance `WCLBDO` through:

$$
\mathrm{RSR0P}=\frac{\mathrm{WCLBDO}}{\pi}.
$$

`FWC` is the covered surface fraction, with $0<\mathrm{FWC}\leq1$ for prescribed coverage.

| Configuration | Interpretation |
| --- | --- |
| `IPT=-101`, `RSR0P>0`, `FWC=0` | Prescribed water-leaving remote-sensing reflectance; no explicit ocean-water radiative transfer. |
| `IPT=-101`, `RSR0P>0`, `FWC>0` | Prescribed Lambertian whitecap/debris reflectance and coverage; no explicit ocean-water radiative transfer. |
| `IPT=-100`, `RSR0P>0`, `FWC>0` | Coupled atmosphere–ocean radiative transfer with prescribed whitecap/debris reflectance and coverage. |
| `IPT=-100`, `RSR0P=0`, `FWC=0` | Coupled atmosphere–ocean radiative transfer. Wind-speed-dependent whitecaps are included only if the whitecap option is enabled. |

The current monochromatic main program sets `WCFLG_INPUT=.FALSE.`, so default zero coverage does not enable parameterized whitecaps. A prescribed nonzero `FWC` in a `-100` or `-101` record enables the surface-coverage calculation internally. For this case, the core raises a wind speed below 0.5 m/s to 0.5 m/s to avoid a conflict between flat-water and coverage treatments.

For `-102`, columns 6 and 7 instead specify surface temperature and emissivity. Do not put `RSR0P` or `FWC` in these columns.

### Optional wind direction for `IPT=-100`, `-101`, and `-102`

Supply two real numbers on one optional line **after the last phase-matrix filename**:

```text
wind_x wind_y
```

If a snow-data directory is required, it is read before this optional wind line. All configuration records retain their original seven columns. Existing files ending after the phase-matrix filenames continue to work.

The components are dimensionless direction cosines:

$$
\mathrm{wind\_x}=\cos\theta_w,\qquad
\mathrm{wind\_y}=\sin\theta_w.
$$

The positive $x$-axis points toward viewing azimuth 0°, on the specular-glint side of the solar principal plane. Positive $y$ points toward viewing azimuth 90°. The angle $\theta_w$ increases counterclockwise when viewed from above, in the same sense as viewing azimuth, and specifies the direction **toward which the wind blows**. Convert meteorological wind directions, which usually specify where the wind comes from, before constructing these components.

| Wind blows toward | `wind_x wind_y` |
| --- | --- |
| 0° | `1.0 0.0` |
| 60° | `0.5 0.8660254` |
| 90° | `0.0 1.0` |
| 180° | `-1.0 0.0` |
| 270° | `0.0 -1.0` |

Wind speed remains in column 2 of the water-surface record. Do not multiply these direction cosines by the wind speed.

#### Optional-line parsing and validation

The monochromatic main program handles the trailer as follows:

| Optional input | Behavior |
| --- | --- |
| End of file immediately after the last required line | No wind direction is supplied; the isotropic surface treatment is retained. |
| Empty lines, spaces, tabs, or comment-only lines | Skipped while looking for a wind-direction line. Reaching end of file retains the isotropic treatment. |
| Two finite real numbers with unit norm within tolerance | Accepted and normalized to remove small rounding errors; `WIND_VECTOR_PRESENT=.TRUE.`. |
| Two finite real numbers whose norm differs from 1 by more than `1.0e-6` | A warning reports the norm and components; the vector is ignored and the isotropic treatment is used. |
| A nonnumeric line that cannot be read as two real numbers | A message reports that no optional wind direction was found; the isotropic treatment is used. Later lines are not searched. |
| Parsed nonfinite components, such as `NaN` or `Inf`, or a nonfinite norm | The program stops with an error. |
| A file-read error other than end of file | The program stops with an error. |

The norm test is:

$$
\left|\sqrt{\mathrm{wind\_x}^2+\mathrm{wind\_y}^2}-1\right|\leq10^{-6}.
$$

For example, `0.5 0.8660254` is accepted, while `0.5 0.5`, `0.0 0.0`, and `3.0 4.0` produce a warning and fall back to isotropic behavior. Supply both components explicitly; list-directed null fields or slash termination can leave a component unset and trigger the finite-value check.

The optional wind line supports `#` and `!` comments, including trailing comments:

```text
# Direction toward which the wind blows
0.5 0.8660254  ! 60 degrees counterclockwise from viewing azimuth zero
```

This optional-line reader belongs to the monochromatic `main.f90`. Other front ends or applications calling `RTSOS` must configure the wind variables themselves; the callable seven-column `RECDATASTREAM` interface has not gained additional columns.

#### Directional Cox–Munk model and its present scope

For rough water with `I_SURFACE_ROUGHNESS_PARA=1` (the current monochromatic default), an accepted wind direction selects `BRDM_OCEAN_nonGAUSSIAN` for **direct solar reflection**. The routine uses the directional slope statistics and Gram–Charlier correction in Cox and Munk (1954), Eq. (18), including skewness and peakedness coefficients.

For wind speed $W$ in m/s, the current coefficients are:

$$
\sigma_c^2=0.003+0.00192W,\qquad
\sigma_u^2=0.00316W,
$$

$$
c_{21}=0.01-0.0086W,\qquad
c_{03}=0.04-0.033W,
$$

$$
c_{40}=0.40,\qquad c_{22}=0.12,\qquad c_{04}=0.23.
$$

Here $c$ and $u$ denote crosswind and upwind slopes. The input vector points downwind, so the routine reverses its direction when projecting onto the paper's positive upwind axis. See [Facet slopes and wind coordinates](BRDM_OCEAN_nonGAUSSIAN.md) for the geometric derivation. Negative values of the truncated Gram–Charlier distribution are clipped to zero, with no renormalization after clipping.

**The present wind dependence applies to direct solar reflection and air-to-water transmission.** Diffuse interface reflection/transmission and the Smith shadowing approximation retain their isotropic treatments. Supplying a wind vector does not make the entire coupled atmosphere–ocean calculation anisotropic or change the prescribed thermal emissivity. If sun glint is disabled, the direct reflected/transmitted radiance contributions are excluded.

Direct radiance and multiple scattering have different flat-surface thresholds:

- `WNDSPD < 1e-6` m/s: the direct reflected and transmitted beams use flat Fresnel optics.
- `1e-6 <= WNDSPD < 0.5` m/s: direct glint uses rough-surface kernels while multiple scattering retains `FLATO=.TRUE.`.
- `WNDSPD >= 0.5` m/s: multiple scattering uses the isotropic rough interface, and direct glint uses rough-surface kernels.

An accepted vector with Cox-Munk roughness makes the rough direct kernels wind dependent; without a vector, or with `I_SURFACE_ROUGHNESS_PARA=2`, those kernels remain isotropic. Direct-beam irradiances and scattering-source illumination follow the `FLATO` treatment, so they need not match an angular integral of the rough direct-radiance pattern in the hybrid interval. Prescribed coverage can still raise the core wind speed to 0.5 m/s as described above. The `1e-6` cutoff does not regularize the very narrow directional glint at near-zero wind speeds.

The PACE HDF5 output records the direct and multiple-scattering surface models separately; see [wind metadata in HDF5 output](pace_ocean_optics.md#wind-metadata-in-hdf5-output).

### Other lower boundaries and snow data

For `IPT=-200`, `albedo` is the Lambertian reflectance and `flam` is the Lambertian surface fraction. The remaining fraction, $1-\mathrm{flam}$, uses flat Fresnel reflection with the supplied complex refractive index. The current core does not support this Lambertian/specular mixture at an ocean bottom; use `flam=1` there. Although column 7 occupies an emissivity field, the current `-200` implementation sets emissivity internally to `1-albedo` and ignores the supplied column-7 value.

For `IPT=-201`, the four `pBRDF` values configure the polarized BRDF model. For `IPT=-203`, supply the Ross–Li coefficients `fiso`, `fvol`, and `fgeo`, followed by `Bpol` and the real and imaginary refractive index. The last three fields of a `-203` record are used by the current implementation.

For `IPT=-202`, the line after the last phase-matrix filename must contain the directory holding the snow BRDF data, for example:

```text
/absolute/path/to/snow_brdf_data
```

The reader accepts the directory as a full line and removes a trailing `#` comment. The snow data follow Hudson et al. (2006), listed in the references.

## Solar irradiance data and `auxiliary_directory`

Infrared calculations and calculations with Raman or fluorescence sources require the solar irradiance dataset. The core calls `FSUNCAL` for these cases; the first call initializes the spectrum through `SUNLREADIN` in [Save_Ocean_Rad.f90](../src/core/Save_Ocean_Rad.f90). The commented preload call in the monochromatic main program is not required for this initialization.

For automatic loading, place a file named `auxiliary_directory` in the **current working directory from which you run the executable**. Its first line must contain the directory holding the solar spectrum files. The loader first tries `tsis1_hsrs_binned_fs.csv` and falls back to `f0.txt`. The supported files have different native units; the loader converts them to its internal wavelength and spectral-irradiance units. Keep the dataset's original file format.

The data archive is described in the [README auxiliary-data instructions](../README.md#12-auxiliary-data) and is available from [Zenodo](https://doi.org/10.5281/zenodo.17410093). The archive is named `RTSOS_data_v1.0_20251022.tar.gz`. For example:

```sh
SOSDIR=/absolute/path/to/SOS_Callable
PACEDATADIR=/absolute/path/to/downloaded_data
cd "$PACEDATADIR"
tar -xf RTSOS_data_v1.0_20251022.tar.gz
cd "$PACEDATADIR/Data"
pwd > "$SOSDIR/test/monochromatic/auxiliary_directory"
```

The archive provides `Gas_Absorption_Coefficients/` and `Data/`; the solar irradiance files belong in `Data/`. The command above prepares the pointer file for runs whose working directory is `test/monochromatic/`. Create the pointer in your own run directory if you run elsewhere.

For ordinary elastic visible-wavelength simulations, `FSUNCAL` is not needed. In the current core, a first atmospheric-layer wavelength greater than 3 µm triggers the absolute solar-irradiance calculation. This is another reason to enter wavelengths in micrometers.

## Phase-matrix files and examples

Supply a phase-matrix file for every distinct scattering type selected by a positive `IPT`. These files are often called Mie input files even when they describe Rayleigh scattering or another scattering medium. The package includes `RayDepol0.pmtx` and other examples.

For the scattering-matrix definitions and expansion conventions, see Zhai et al. (2009), particularly Appendix A. Example inputs are in [test/monochromatic](../test/monochromatic/), and benchmark cases are in [validation/benchmark](../validation/benchmark/). Keep phase-matrix filenames and their ordering consistent with the positive `IPT` values in your configuration.

## Output file

The output begins with the configuration and numerical settings. For each detector and incident direction, it then gives the downward and upward irradiances and the Stokes components $I$, $Q$, $U$, and $V$ as functions of outgoing zenith angle `THETA` and azimuth `PHI`. The radiance column is Stokes $I$. The code can also write `COS(THETA)` when its output cosine option is selected.

Detectors are numbered in the order of their `-1000` records. Their optical depths follow from the cumulative layer optical thicknesses; internally, atmospheric and ocean detector depths are stored in `TAUDETA` and `TAUDETO`.

### Wind-information footer

For configurations containing a water-surface record, the monochromatic main program appends a `WIND VECTOR INFORMATION` block at the **end** of the output file. For a valid wind direction and rough Cox–Munk surface, an example is:

```text
WIND VECTOR INFORMATION
WIND_VECTOR_PRESENT=T
WIND SPEED USED (M/S)=  7.00000000E+00
WIND_X,WIND_Y (DIRECTION COSINES)=   5.00000002E-01   8.66025403E-01
THETA_W (DEG, BLOWS TOWARD, CCW FROM PHI=0)=   60.000000
DIRECT SOLAR R/T=DIRECTIONAL COX-MUNK
MULTIPLE SCATTERING SURFACE=ISOTROPIC GAUSSIAN
```

`THETA_W` is reported in the range $[0,360)$ degrees. The components printed here are the accepted, normalized direction cosines. `WIND SPEED USED` is the speed used by the core, including any adjustment for prescribed surface coverage.

At 7 m/s, if the direction is absent or rejected by the norm check, the footer instead reports:

```text
WIND_VECTOR_PRESENT=F
WIND DIRECTION=UNSPECIFIED
DIRECT SOLAR R/T=ISOTROPIC GAUSSIAN
MULTIPLE SCATTERING SURFACE=ISOTROPIC GAUSSIAN
```

The speed line is still present. The two model lines describe the selected kernels; `R/T` means reflection/transmission. Direct sunlight reports `FLAT` below `1e-6` m/s, and otherwise reports `DIRECTIONAL COX-MUNK` with an accepted vector and Cox-Munk roughness, or `ISOTROPIC GAUSSIAN`. Multiple scattering reports `FLAT` below 0.5 m/s and `ISOTROPIC GAUSSIAN` otherwise. Thus, at 0.4 m/s with an accepted vector:

```text
DIRECT SOLAR R/T=DIRECTIONAL COX-MUNK
MULTIPLE SCATTERING SURFACE=FLAT
```

These labels identify the selected models even when the input glint switch disables the direct contributions. Norm-rejection warnings remain in the console.

## Important variables in the source code

These settings are source-level or callable-interface controls, rather than extra columns in `sosi.dat`. Rebuild the executable after changing main-program defaults.

| Variable | Meaning and current behavior |
| --- | --- |
| `DELTATAUA`, `DELTATAUO` | Dimensionless optical-depth integration steps in the atmosphere and ocean. The monochromatic main supplies `0.01` for both. Use steps no larger than half the optical thickness of a homogeneous layer, and check convergence for the desired accuracy. |
| `ESUN(1:4)` | Incident solar irradiance Stokes vector. The module default is $(\pi,0,0,0)$. Select the intensity normalization consistently with your application. Absolute solar-irradiance calculations replace the intensity using the solar dataset. |
| `WLR_FLAG` | `.TRUE.` selects water-leaving radiance for atmospheric detectors; `.FALSE.` selects total radiance. The monochromatic main supplies `.FALSE.`. |
| `WCFLG` | Enables wind-speed-dependent whitecap parameterization. The monochromatic main supplies `.FALSE.` through `WCFLG_INPUT`; prescribed nonzero coverage can enable the calculation internally. |
| `TRUC_FLAG` | Enables phase-matrix truncation and the associated rescaling of optical thickness and single-scattering albedo. The module default is `.TRUE.`; `DELTAM` selects the truncation method. |
| `DELTAM` | `0`: delta-M; `1`: delta-M+; `2`: delta-fit. The monochromatic main supplies `1`. |
| `LINEXP` | `.TRUE.` selects the linear-exponential source approximation; `.FALSE.` selects the linear approximation. The module default is `.TRUE.`. |
| `GEOSR` | Enables the geometric-series approximation. The module default is `.TRUE.`. |
| `SCL` | `.TRUE.` selects scalar radiance calculations; `.FALSE.` selects vector calculations. The module default is `.FALSE.`. |
| `I_SURFACE_ROUGHNESS_PARA` | `1`: Cox–Munk slope parameterization; `2`: Gordon–Wang isotropic parameterization. The monochromatic main sets `1`. |
| `WIND_VECTOR_PRESENT`, `WIND_X`, `WIND_Y` | Optional wind-direction state in `RTUTILITY`. The monochromatic reader validates and sets these variables before calling `RTSOS`. |

The original guide also described a `Mishchenko_Sign` switch for choosing between phase-matrix conventions. That switch is not present in the current monochromatic/core source. For the historical convention discussion, consult Mishchenko et al. (2002), Siewert (1982), and Eq. (A-12) of Zhai et al. (2009); do not assume the old switch remains available.

## References

- Cox, C., and W. Munk (1954). Measurement of the roughness of the sea surface from photographs of the sun's glitter. *Journal of the Optical Society of America*, **44**, 838–850. Eq. (18) gives the non-Gaussian slope expansion used by the directional direct-reflection routine.
- Hudson, S. R., S. G. Warren, R. E. Brandt, T. C. Grenfell, and D. Six (2006). Spectral bidirectional reflectance of Antarctic snow: Measurements and parameterization. *Journal of Geophysical Research*, **111**, D18106. [doi:10.1029/2006JD007290](https://doi.org/10.1029/2006JD007290).
- Mishchenko, M. I., L. D. Travis, and A. A. Lacis (2002). *Scattering, Absorption, and Emission of Light by Small Particles*. Cambridge University Press, pp. 103–104.
- Siewert, C. E. (1982). On the phase matrix basic to the scattering of polarized light. *Astronomy and Astrophysics*, **109**, 195–200.
- Zhai, P.-W., Y. Hu, C. R. Trepte, and P. L. Lucker (2009). A vector radiative transfer model for coupled atmosphere and ocean systems based on successive order of scattering method. *Optics Express*, **17**, 2057–2079. [doi:10.1364/OE.17.002057](https://doi.org/10.1364/OE.17.002057).
