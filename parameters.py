from dataclasses import dataclass, field, fields
from typing import Any

import numpy as np
import xarray as xr


@dataclass(slots=True)
class Parameters:
    """names and other documentation for parameters in RTM codes"""

    # This dataclass stores parameter metadata, but does NOT store the
    # parameter values used in RT calculations. The class's `make_dataset` method
    # returns an XArray.Dataset that combines the values provided to the method
    # with the metadata defined here. The purpose of `slots=True` is to produce Class
    # attributes that are visible to IDEs which provide tab completion and refactoring.

    # To add a new parameter that must be written to an input file for the RT
    # simulations, first add its unique short-name in alphabetical order below, and
    # include as many of `long_name`, `comments`, `units`, `valid_range`, and `dtype`
    # as are helpful. Second, find the dictionary of parameters defined in the `main`
    # function of each `scripts/rt_*.py` wrapper that needs the new parameter. Add
    # the parameter and a default value (or list of values), in the order that
    # parameters must be written to RT simulation input files.

    adg440: Any = field(
        default=None,
        metadata=dict(
            comment="used when ocean_case_select == 3",
            units="1/m",
            valid_range=np.array((0, 2.5), dtype=np.float32),
            dtype=np.float32,
        ),
    )

    Aerosol_FMF: Any = field(
        default=None,
        metadata=dict(
            long_name="aerosol fine mode fraction",
            comment="used in RT sims only when Aerosol_Model is set to `-1`",
            valid_range=np.array((0, 1), dtype=np.float32),
            dtype=np.float32,
        ),
    )

    Aerosol_Mixing_Flag: Any = field(
        default=None,
        metadata=dict(
            long_name="mixing of fine mode aerosols",
            flag_values=np.array((0, 1, 2), np.int32),
            flag_meanings="internal_with_zia internal external",
            dtype=np.int32,
        ),
    )

    Aerosol_Model: Any = field(
        default=None,
        metadata=dict(
            long_name="aerosol model number",
            flag_values=np.array(
                (-99, -98, -97, -96, -1) + tuple(range(1, 22)),
                dtype=np.int32,
            ),
            flag_meanings=(
                (
                    "aerosol_pmhx_in_from_file"  # -99
                    " water_cloud_phmx_from_file"  # -98
                    " two_layer_scattorer_phmx_from_file"  # -97
                    " mono_modal"  # -96
                    " Ahmad_model_with_flexbile_RH_and_FMF"  # -1
                )
                + "".join((" Shettle_and_Fenn",) * 10)
                + "".join((" Ahmad",) * 10)
                + " dust_aerosol_model"
            ),
            flag_meanings_fmf=np.array(
                [np.nan] * 15 + [0, 1, 2, 5, 10, 20, 30, 50, 80, 95, np.nan],
                dtype=np.float32,
            ),
            flag_meanings_sd=np.array(
                [np.nan] * 15 + [25, 24, 23, 22, 21, 20, 19, 18, 17, 16, np.nan],
                dtype=np.float32,
            ),
            dtype=np.int32,
        ),
    )

    Aerosol_Phasematrix_File_Hi: Any = field(
        default=None,
        metadata=dict(
            long_name="top layer scattor aerosol phase matrix file",
            comment="used for Aerosol_Model -99, -98, -97 only",
        ),
    )

    Aerosol_Phasematrix_File_Low: Any = field(
        default=None,
        metadata=dict(
            long_name="lower layer scattor aerosol phase matrix file",
            comment="used for Aerosol_Model -97 only",
        ),
    )

    AirSensor_Height: Any = field(
        default=None,
        metadata=dict(
            units="km",
            dtype=np.float32,
        ),
    )

    albedo_ground: Any = field(
        default=None,
        metadata=dict(
            dtype=np.float32,
        ),
    )

    ap_select: Any = field(
        default=None,
        metadata=dict(
            flag_values=np.array((1, 2), np.int32),
            flag_meanings=(
                "Bricaud_LUT" " Mixure_of_pico_and_micron_cells_in_Ciott_et_al._2002"
            ),
            dtype=np.int32,
        ),
    )

    Atmos_Dir: Any = field(
        default=None,
        metadata=dict(
            long_name="path to directory containing gas absorbption data",
        ),
    )

    ATMOS_ZERO: Any = field(
        default=None,
        metadata=dict(
            flag_values=np.array((0, 1), np.int32),
            flag_meanings="false true",
            dtype=np.int32,
        ),
    )

    Aux_Dir: Any = field(
        default=None,
        metadata=dict(
            long_name="path to directory containing auxiliary data files",
        ),
    )

    bbp660_BackscatterCoeff: Any = field(
        default=None,
        metadata=dict(
            comment="used when ocean_case_select == 3",
            units="1/m",
            valid_range=np.array((0, 0.1), dtype=np.float32),
            dtype=np.float32,
        ),
    )

    Bp660_BackscatterFraction: Any = field(
        default=None,
        metadata=dict(
            comment="used when ocean_case_select == 3",
            valid_range=np.array((0, 0.05), dtype=np.float32),
            dtype=np.float32,
        ),
    )

    CFILE_AP: Any = field(
        default=None,
        metadata=dict(
            long_name="filename for atmospheric profile data",
            comment=(
                "valid atmosphere profiles are: afglus.dat, "
                "afglsw.dat, afglss.dat, or afglmw.dat"
            ),
        ),
    )

    CFILE_INSTRUMENT: Any = field(
        default=None,
        metadata=dict(
            long_name="filename for AFRT",
        ),
    )

    chla: Any = field(
        default=None,
        metadata=dict(
            comment="used when ocean_case_select in (1, 2, 3)",
            valid_range=np.array((0.04, 50.0), dtype=np.float32),
            units="mg/m3",
            dtype=np.float32,
        ),
    )

    CHLA_HOMOGENEITY: Any = field(
        default=None,
        metadata=dict(
            dtype=np.int32,
            flag_values=np.array((0, 1), np.int32),
            flag_meanings="false true",
        ),
    )

    cmsfracs: Any = field(
        default=None,
        metadata=dict(
            long_name="spherical fraction in coarse mode: by volume",
            dtype=np.float32,
        ),
    )

    Diffuse_Transmittance_Flag: Any = field(
        default=None,
        metadata=dict(
            flag_values=np.array((0, 1), np.int32),
            flag_meanings="calculate_regular_reflectance diffuse_transmittance",
            dtype=np.int32,
        ),
    )

    dustfrac: Any = field(
        default=None,
        metadata=dict(
            long_name="dust fraction",
            dtype=np.float32,
        ),
    )

    dust_ireff: Any = field(
        default=None,
        metadata=dict(
            long_name="dust effective radius selection from database",
            flag_values=np.arange(1, 16, 1, np.int32),
            flag_meanings=" ".join([f"{i:0.1f}" for i in np.arange(0.2, 3.1, 0.2)]),
            dtype=np.int32,
        ),
    )

    dust_ivar: Any = field(
        default=None,
        metadata=dict(
            long_name="dust variance selection from data base",
            flag_values=np.arange(1, 6, 1, np.int32),
            flag_meanings="1.2 1.5 2.0 2.5 3.0",
            dtype=np.int32,
        ),
    )

    dsfrac: Any = field(
        default=None,
        metadata=dict(
            long_name="spherical fraction in dust mode",
            dtype=np.float32,
        ),
    )

    fmfrac: Any = field(
        default=None,
        metadata=dict(
            long_name="fine mode fraction: by volume",
            dtype=np.float32,
        ),
    )

    gas_abs_flag: Any = field(
        default=None,
        metadata=dict(
            flag_values=np.array((0, 1), np.int32),
            flag_meanings="false true",
            dtype=np.int32,
        ),
    )

    H2O_COLUMN: Any = field(
        default=None,
        metadata=dict(
            long_name="water vapor in the whole column",
            units="cm",
            source="US standard atmosphere 1976",
            valid_range=np.array((0.01, 15), dtype=np.float32),
            dtype=np.float32,
        ),
    )

    height_particle_hi: Any = field(
        default=None,
        metadata=dict(
            long_name="top layer scatteror centroid height",
            valid_max=np.float32(120),
            dtype=np.float32,
        ),
    )

    height_particle_low: Any = field(
        default=None,
        metadata=dict(
            long_name="lower layer scatteror centroid height",
            comment="set to a negative number for one aerosol layer",
            valid_min=np.float32(-100),
            dtype=np.float32,
        ),
    )

    hyspectral_flag: Any = field(
        default=None,
        metadata=dict(
            flag_values=np.array((0, 1), np.int32),
            flag_meanings="false true",
            dtype=np.int32,
        ),
    )

    IRH: Any = field(
        default=None,
        metadata=dict(
            long_name="relative humidity lookup position",
            flag_values=np.arange(1, 6, 1, np.int32),
            flag_meanings=(0.50, 0.70, 0.80, 0.90, 0.95),
            dtype=np.int32,
        ),
    )

    I_SURFACE_ROUGHNESS_PARA: Any = field(
        default=None,
        metadata=dict(
            dtype=np.int32,
        ),
    )

    I_SPHERICAL_SHELL_CORRECTION: Any = field(
        default=None,
        metadata=dict(
            long_name="spherical shell correction",
            flag_values=np.array((0, 1), np.int32),
            flag_meanings="off on",
            dtype=np.int32,
        ),
    )

    iwhitecap: Any = field(
        default=None,
        metadata=dict(
            long_name="white cap calculation",
            flag_values=np.array((0, 1), np.int32),
            flag_meanings="off on",
            dtype=np.int32,
        ),
    )

    MAXMORDINPUT: Any = field(
        default=None,
        metadata=dict(
            dtype=np.int32,
        ),
    )

    Wave_Mean_Square_Slope: Any = field(
        default=None,
        metadata=dict(
            long_name="mean square slope of waves",
            dim="Wind_Speed",
            dtype=np.float32,
        ),
    )

    Mie_Database_Dir: Any = field(
        default=None,
        metadata=dict(long_name="path to directory containing Mie database"),
    )

    MIE_TABLE_CAL: Any = field(
        default=None,
        metadata=dict(
            long_name="Mie database calculation",
            flag_values=np.arange(1, 4, 1, np.int32),
            flag_meanings=(
                "only_calculate_and_store_Mie_scattering_matrix"
                " calculate_and_use_(w/out_storing)_Mie_scattering_matrix"
                " read_(w/out_calculating)_stored_Mie_scattering_matrix"
            ),
            dtype=np.int32,
        ),
    )

    MONOCHROMATIC_FLAG: Any = field(
        default=None,
        metadata=dict(
            flag_values=np.array((0, 1), np.int32),
            flag_meanings="false true",
            dtype=np.int32,
        ),
    )

    Mr_Cloud: Any = field(
        default=None,
        metadata=dict(
            long_name="Real Refractive Index",
            dtype=np.float32,
        ),
    )

    Mi_Cloud: Any = field(
        default=None,
        metadata=dict(
            long_name="Imaginary Refractive Index",
            dtype=np.float32,
        ),
    )

    ncolinput: Any = field(
        default=None,
        metadata=dict(
            dtype=np.int32,
        ),
    )

    nmode: Any = field(
        default=None,
        metadata=dict(
            long_name="number of aerosol modes",
            flag_values=np.array((2, 3), np.int32),
            flag_meanings="bi-modal tri-modal",
            dtype=np.int32,
        ),
    )

    NO2_COLUMN_DobsonUnit: Any = field(
        default=None,
        metadata=dict(
            long_name="NO_2 column amount",
            units="Dobson Unit",
            dtype=np.float32,
        ),
    )

    NonPhotochemicalQuenching_FLAG: Any = field(
        default=None,
        metadata=dict(
            flag_values=np.array((0, 1), np.int32),
            flag_meanings="false true",
            dtype=np.int32,
        ),
    )

    NPHIV: Any = field(
        default=None,
        metadata=dict(
            dtype=np.int32,
        ),
    )

    nquadainput: Any = field(
        default=None,
        metadata=dict(
            dtype=np.int32,
        ),
    )

    nquadoinput: Any = field(
        default=None,
        metadata=dict(
            dtype=np.int32,
        ),
    )

    NTHETAV: Any = field(
        default=None,
        metadata=dict(
            dtype=np.int32,
        ),
    )

    NWV: Any = field(
        default=None,
        metadata=dict(
            long_name="number of wavelegnths",
            comment="typically equal to the length of the CFILE_INSTRUMENT array",
            dtype=np.int32,
        ),
    )

    OCEAN_CASE_SELECT: Any = field(
        default=None,
        metadata=dict(
            flag_values=(-1, 0, 1, 2, 3),
            flag_meanings=(
                "land"
                " atmosphere_only"
                " [Chla]_parameterization"
                " [Chla]+Sediment"
                " seven_parameter_model"
            ),
            dtype=np.int32,
        ),
    )

    OCEAN_FCDOM_FLAG: Any = field(
        default=None,
        metadata=dict(
            flag_values=np.array((0, 1), np.int32),
            flag_meanings="false true",
            dtype=np.int32,
        ),
    )

    OCEAN_FCHLA_FLAG: Any = field(
        default=None,
        metadata=dict(
            flag_values=np.array((0, 1), np.int32),
            flag_meanings="false true",
            dtype=np.int32,
        ),
    )

    OCEAN_PHMX_ONE: Any = field(
        default=None,
        metadata=dict(
            flag_values=np.array((0, 1), np.int32),
            flag_meanings="false true",
            dtype=np.int32,
        ),
    )

    OCEAN_RAMAN_FLAG: Any = field(
        default=None,
        metadata=dict(
            flag_values=np.array((0, 1), np.int32),
            flag_meanings="false true",
            dtype=np.int32,
        ),
    )

    OZONE_COLUMN_DobsonUnit: Any = field(
        default=None,
        metadata=dict(
            comment="ozone in the whole column",
            units="Dobson Unit",
            source="US standard atmosphere 1976",
            valid_range=np.array((250, 500), dtype=np.float32),
            dtype=np.float32,
        ),
    )

    phytoplankton_index_refraction: Any = field(
        default=None,
        metadata=dict(
            comment="used when ocean_case_select == 2",
            dtype=np.float32,
        ),
    )

    phytoplankton_spectral_slope: Any = field(
        default=None,
        metadata=dict(
            comment="used when ocean_case_select == 2",
            dtype=np.float32,
        ),
    )

    Pressure_Surface_mb: Any = field(
        default=None,
        metadata=dict(
            long_name="surface pressure",
            units="mb",
            valid_range=np.array((850, 1050), dtype=np.float32),
            dtype=np.float32,
        ),
    )

    pss_flag: Any = field(
        default=None,
        metadata=dict(
            long_name="pseudospherical flag",
            flag_values=np.array((0, 1), np.int32),
            flag_meanings="off on",
            dtype=np.int32,
        ),
    )

    Relative_Humidity: Any = field(
        default=None,
        metadata=dict(
            long_name="relative humidity",
            valid_range=np.array((0.3, 0.95), dtype=np.float32),
            dtype=np.float32,
        ),
    )

    Reff_Cloud: Any = field(
        default=None,
        metadata=dict(
            long_name="effective radius",
            dtype=np.float32,
        ),
    )

    rf1: Any = field(
        default=None,
        metadata=dict(
            long_name="dust like contribution in fine mode: by volume",
            dtype=np.float32,
        ),
    )

    rf2: Any = field(
        default=None,
        metadata=dict(
            long_name="water soluble contribution in fine mode: by volume",
            dtype=np.float32,
        ),
    )

    rf3: Any = field(
        default=None,
        metadata=dict(
            long_name="brown carbon contribution in fine mode: by volume",
            dtype=np.float32,
        ),
    )

    r0c: Any = field(
        default=None,
        metadata=dict(
            long_name="dry radius coarse mode spherical (sea salt) by volume",
            dtype=np.float32,
        ),
    )

    r0f: Any = field(
        default=None,
        metadata=dict(
            long_name="dry radius fine mode spherical - internal mixing by volume",
            dtype=np.float32,
        ),
    )

    r0_bc: Any = field(
        default=None,
        metadata=dict(
            long_name="dry radius brown carbon (fine mode) by volume",
            dtype=np.float32,
        ),
    )

    r0_dl: Any = field(
        default=None,
        metadata=dict(
            long_name="dry radius dust like (fine mode) by volume",
            dtype=np.float32,
        ),
    )

    r0_ws: Any = field(
        default=None,
        metadata=dict(
            long_name="dry radius water soluble (fine mode) by volume",
            dtype=np.float32,
        ),
    )

    r0_s: Any = field(
        default=None,
        metadata=dict(
            long_name="dry radius soot (fine mode) by volume",
            dtype=np.float32,
        ),
    )

    r0_ss: Any = field(
        default=None,
        metadata=dict(
            long_name="dry radius sea salt (coarse mode) by volume",
            dtype=np.float32,
        ),
    )

    S_Bp: Any = field(
        default=None,
        metadata=dict(
            long_name="power spectral slope of backscattering fraction",
            comment="used when ocean_case_select == 3",
            units="1/nm",
            valid_range=np.array((-0.2, 0.2), dtype=np.float32),
            dtype=np.float32,
        ),
    )

    Sbp: Any = field(
        default=None,
        metadata=dict(
            long_name="power spectral slope of backscattering coefficient",
            comment="used when ocean_case_select == 3",
            units="1/nm",
            valid_range=np.array((0, 0.5), dtype=np.float32),
            dtype=np.float32,
        ),
    )

    Sdg: Any = field(
        default=None,
        metadata=dict(
            long_name="exponential spectral slope of dg absorption",
            comment="used when ocean_case_select == 3",
            units="1/nm",
            valid_range=np.array((0.01, 0.02), dtype=np.float32),
            dtype=np.float32,
        ),
    )

    sediment_concentration: Any = field(
        default=None,
        metadata=dict(
            comment="used when ocean_case_select == 2",
            valid_range=np.array((0, 30), dtype=np.float32),
            dtype=np.float32,
        ),
    )

    sediment_index_refraction: Any = field(
        default=None,
        metadata=dict(
            comment="used when ocean_case_select == 2",
            dtype=np.float32,
        ),
    )

    sediment_spectral_slope: Any = field(
        default=None,
        metadata=dict(
            comment="used when ocean_case_select == 2",
            dtype=np.float32,
        ),
    )

    sigc: Any = field(
        default=None,
        metadata=dict(
            long_name="standard deviation coarse mode",
            dtype=np.float32,
        ),
    )

    sigf: Any = field(
        default=None,
        metadata=dict(
            long_name="standard deviation fine mode",
            dtype=np.float32,
        ),
    )

    SUN_GLINT_FLAG: Any = field(
        default=None,
        metadata=dict(
            flag_values=np.array((0, 1), np.int32),
            flag_meanings="include_sun_glint no_sun_glint",
            dtype=np.int32,
        ),
    )

    Solar_Zenith_Angle: Any = field(
        default=None,
        metadata=dict(
            units="degrees",
            valid_range=np.array((0, 80), dtype=np.float32),
            dtype=np.float32,
        ),
    )

    Tau_NIR: Any = field(
        default=None,
        metadata=dict(
            long_name="optical depth at NIR wavelength",
            valid_range=np.array((0, 100), dtype=np.float32),
            dtype=np.float32,
        ),
    )

    tau_ref_hi: Any = field(
        default=None,
        metadata=dict(
            long_name="top layer optical depth at reference wavelength",
            valid_range=np.array((0, 100), dtype=np.float32),
            dtype=np.float32,
        ),
    )

    tau_ref_low: Any = field(
        default=None,
        metadata=dict(
            long_name="bottom layer optical depth at reference wavelength",
            comment="set to 0.0 for one aerosol layer",
            valid_range=np.array((0, 100), dtype=np.float32),
            dtype=np.float32,
        ),
    )

    Wind_Speed: Any = field(
        default=None,
        metadata=dict(
            long_name="Wind Speed",
            comment=(
                "if `I_SURFACE_ROUGHNESS_PARA == 1`, inverse wind speed "
                "from SIGMA^2=0.003D0+0.00512D0*WNDSPD Cox & Munk 1954, "
                "else if `I_SURFACE_ROUGHNESS_PARA == 2` from Gordon & "
                "Wang 1992"
            ),
            valid_range=np.array((0.1, 15), dtype=np.float32),
            dtype=np.float32,
        ),
    )
    # NB use of "Wind_Speed" in Parameters.Mean_Square_Slope

    water_depth_max: Any = field(
        default=None,
        metadata=dict(
            dtype=np.float32,
        ),
    )

    WAVELENGTH_MICRON_REF: Any = field(
        default=None,
        metadata=dict(
            dtype=np.float32,
        ),
    )

    wv_pace_ref: Any = field(
        default=None,
        metadata=dict(
            long_name="reference wavelength for optical depth assignment",
            dtype=np.float32,
        ),
    )

    WAVEBAND_SEG_FLAG: Any = field(
        default=None,
        metadata=dict(
            flag_values=np.arange(0, 5, 1, np.int32),
            flag_meanings="all seg1+3only seg2only seg1+2+3 seg4only",
            dtype=np.int32,
        ),
    )

    Veff_Cloud: Any = field(
        default=None,
        metadata=dict(
            long_name="effective variance",
            dtype=np.float32,
        ),
    )

    @classmethod
    def make_dataset(cls, data: dict) -> xr.Dataset:
        """Cast native dataclass to XArray Dataset with attributes
        from the dataclass fields and values from `data`.
        """
        dataset = xr.Dataset()
        metadata = {i.name: i.metadata for i in fields(cls)}
        for key, value in data.items():
            coord = key.__name__
            attrs = metadata[coord].copy()
            array = np.array(value, dtype=attrs.pop("dtype", None))
            dim = attrs.pop("dim", False) or coord if array.shape else ()
            dataset = dataset.assign_coords({coord: (dim, array, attrs)})
        return dataset


# aliases
AM = Parameters.Aerosol_Model.__name__
RH = Parameters.Relative_Humidity.__name__
WI = Parameters.Wind_Speed.__name__
TN = Parameters.Tau_NIR.__name__
SZ = Parameters.Solar_Zenith_Angle.__name__
DT = Parameters.Diffuse_Transmittance_Flag.__name__
WA = Parameters.Wave_Mean_Square_Slope.__name__
REF = Parameters.WAVELENGTH_MICRON_REF.__name__
