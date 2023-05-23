from dataclasses import dataclass, field, fields
from typing import Any

import numpy as np
import numpy.typing as npt
import xarray as xr


@dataclass(slots=True)
class Parameters:
    '''names and other documentation for parameters in RTM codes'''
    # This dataclass stores parameter metadata, but is never used to store the
    # parameter values used in RT calculations. The `make_dataset` method it
    # provides builds the dataset used in RT calculations from provided values
    # and these metadata. The purpose of `slots=True` is to produce Class
    # attributes that are visible to IDEs which provide tab completion.

    # To add a new parameter that must be written to an input file for the RT
    # simulations, first add its unique short-name in alphabetical order below, and
    # include as many of `name`, `description`, `units`, `range`, and `dtype`
    # as are helpful. Second, find the dictionary of parameters defined in the `main`
    # function of each `scripts/rt_*.py` wrapper that needs the new parameter. Add
    # the parameter and a default value (or list of values), in the order that
    # parameters must be written to RT simulation input files.

    # TODO clean up metadata

    adg440: Any = field(default=None, metadata=dict(
        comment='used when ocean_case_select == 3',
        units='1/m',
        valid_range=(0.0, 2.5),
        dtype=np.float32,
    ))

    AerosolFineModeFraction: Any = field(default=None, metadata=dict(
        long_name='Aerosol Fine Mode Fraction',
        comment='only used when Aerosol Model Number is set to "-1"',
        valid_range=(0.0, 1.0),
        dtype=np.float32,
    ))

    Aerosol_Mixing_Flag: Any = field(default=None, metadata=dict(
        long_name='mixing of fine mode aerosols',
        flag_values=(0, 1, 2),
        flag_meanings=('internal with zia', 'internal', 'external'),
        dtype=np.int16,
    ))

    Aerosol_Model_Number: Any = field(default=None, metadata=dict(
        long_name='Aerosol Model',
        flag_values=(-99, -98, -97, -1) + tuple(range(1, 22)),
        flag_meanings=(
            'aerosol pmhx in from file',
            'water cloud phmx from file',
            'two layer scattorer phmx from file',
            'Ahmad model with flexbile RH and FMF',
        ) +
            ('Shettle and Fenn',) * 10 +
            ('Ahmad model',) * 10 + (
            'dust aerosol model',
        ),
        dtype=np.int16,
    ))

    Aerosol_Phasematrix_File_Hi: Any = field(default=None, metadata=dict(
        long_name='top layer scattor aerosol phase matrix file',
    ))

    Aerosol_Phasematrix_File_Low: Any = field(default=None, metadata=dict(
        long_name='lower layer scattor aerosol phase matrix file',
    ))

    AirSensor_Height: Any = field(default=None, metadata=dict(
        units='km',
        dtype=np.float32,
    ))

    albedo_ground: Any = field(default=None, metadata=dict(
        dtype=np.float32,
    ))

    ap_select: Any = field(default=None, metadata=dict(
        flag_values=(1, 2),
        flag_meanings=('Bricaud LUT', 'Mixure of pico and micron cells in Ciott et al. 2002'),
        dtype=np.int16,
    ))

    Atmos_Dir: Any = field(default=None, metadata=dict(
        long_name='path to directory containing gas absorbption data'
    ))

    ATMOS_ZERO: Any = field(default=None, metadata=dict(
        flag_values=(0, 1),
        flag_meanings=('False', 'True'),
        dtype=np.int16,
    ))

    Aux_Dir: Any = field(default=None, metadata=dict(
        long_name='path to directory containing auxiliary data files',
    ))

    bbp660_BackscatterCoeff: Any = field(default=None, metadata=dict(
        comment='used when ocean_case_select == 3',
        units='1/m',
        valid_range=(0.0, 0.1),
        dtype=np.float32,
    ))

    Bp660_BackscatterFraction: Any = field(default=None, metadata=dict(
        comment='used when ocean_case_select == 3',
        valid_range=(0.0, 0.05),
        dtype=np.float32,
    ))

    CFILE_AP: Any = field(default=None, metadata=dict(
        long_name='filename for atmospheric profile data',
        comment=(
            'valid atmosphere profiles are: afglus.dat, '
            'afglsw.dat, afglss.dat, or afglmw.dat'
            ),
    ))

    CFILE_INSTRUMENT: Any = field(default=None, metadata=dict(
        long_name='filename for AFRT',
    ))

    chla: Any = field(default=None, metadata=dict(
        comment='used when ocean_case_select in (1, 2, 3)',
        valid_range=(0.04, 50.0),
        units='mg/m3',
        dtype=np.float32,
    ))

    CHLA_HOMOGENEITY: Any = field(default=None, metadata=dict(
        dtype=np.int16,
        flag_values=(0, 1),
        flag_meanings=('False', 'True'),
    ))

    cmsfracs: Any = field(default=None, metadata=dict(
        long_name='spherical fraction in coarse mode: by volume',
        dtype=np.float32,
    ))

    Diffuse_Transmittance_Flag: Any = field(default=None, metadata=dict(
        flag_values=(0, 1),
        flag_meanings=('calculate regular reflectance', 'diffuse transmittance'),
        dtype=np.int16,
    ))

    dust_frac: Any = field(default=None, metadata=dict(
        long_name='dust fraction',
        dtype=np.float32,
    ))

    dust_ireff: Any = field(default=None, metadata=dict(
        long_name='dust effective radius selection from database',
        flag_values=tuple(range(1, 15)),
        flag_meanings=(0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0),
        dtype=np.int16,
    ))

    dust_ivar: Any = field(default=None, metadata=dict(
        long_name='dust variance selection from data base',
        flag_values=tuple(range(1, 5)),
        flag_meanings=(1.2, 1.5, 2.0, 2.5, 3.0),
        dtype=np.int16,
    ))

    ds_frac: Any = field(default=None, metadata=dict(
        long_name='spherical fraction in dust mode',
        dtype=np.float32,
    ))

    fmfrac: Any = field(default=None, metadata=dict(
        long_name='fine mode fraction: by volume',
        dtype=np.float32,
    ))

    gas_abs_flag: Any = field(default=None, metadata=dict(
        flag_values=(0, 1),
        flag_meanings=('False', 'True'),
        dtype=np.int16,
    ))

    H2O_COLUMN: Any = field(default=None, metadata=dict(
        long_name='water vapor in the whole column',
        units='cm',
        source='US standard atmosphere 1976',
        valid_range=(0.01, 15),
        dtype=np.float32,
    ))

    height_particle_hi: Any = field(default=None, metadata=dict(
        long_name='top layer scatteror centroid height',
        valid_max=120.0,
        dtype=np.float32,
    ))

    height_particle_low: Any = field(default=None, metadata=dict(
        long_name='lower layer scatteror centroid height',
        comment='set to a negative number for one aerosol layer',
        valid_min=-100.0,
        dtype=np.float32,
    ))

    hyspectral_flag: Any = field(default=None, metadata=dict(
        flag_values=(0, 1),
        flag_meanings=('False', 'True'),
        dtype=np.int16,
    ))

    IRH: Any = field(default=None, metadata=dict(
        long_name='relative humidity lookup position',
        flag_values=tuple(range(1, 5)),
        flag_meanings=(0.50, 0.70, 0.80, 0.90, 0.95),
        dtype=np.int16,
    ))

    I_SURFACE_ROUGHNESS_PARA: Any = field(default=None, metadata=dict(
        dtype=np.int16,
    ))

    I_SPHERICAL_SHELL_CORRECTION: Any = field(default=None, metadata=dict(
        long_name='spherical shell correction',
        flag_values=(0, 1),
        flag_meanings=('Off', 'On'),
        dtype=np.int16,
    ))

    iwhitecap: Any = field(default=None, metadata=dict(
        long_name='white cap calculation',
        flag_values=(0, 1),
        flag_meanings=('Off', 'On'),
        dtype=np.int16,
    ))

    MAXMORDINPUT: Any = field(default=None, metadata=dict(
        dtype=np.int16,
    ))

    Mie_Database_Dir: Any = field(default=None, metadata=dict(
        long_name='path to directory containing Mie database'
    ))

    MIE_TABLE_CAL: Any = field(default=None, metadata=dict(
        long_name='Mie database calculation',
        flag_values=(1, 2, 3),
        flag_meanings=(
            'only calculate and store Mie scattering matrix',
            'calculate and use (w/out storing) Mie scattering matrix',
            'read (w/out calculating) stored Mie scattering matrix',
        ),
        dtype=np.int16,
    ))

    MONOCHROMATIC_FLAG: Any = field(default=None, metadata=dict(
        flag_values=(0, 1),
        flag_meanings=('False', 'True'),
        dtype=np.int16,
    ))

    ncolinput: Any = field(default=None, metadata=dict(
        dtype=np.int16,
    ))

    nmode: Any = field(default=None, metadata=dict(
        long_name='number of aerosol modes',
        flag_values=(2, 3),
        flag_meanings=('bi-modal', 'tri-modal'),
        dtype=np.int16,
    ))

    NO2_COLUMN_DobsonUnit: Any = field(default=None, metadata=dict(
        long_name='NO_2 column amount',
        units='Dobson Unit',
        dtype=np.float32,
    ))

    NonPhotochemicalQuenching_FLAG: Any = field(default=None, metadata=dict(
        flag_values=(0, 1),
        flag_meanings=('False', 'True'),
        dtype=np.int16,
    ))

    NPHIV: Any = field(default=None, metadata=dict(
        dtype=np.int16,
    ))

    nquadainput: Any = field(default=None, metadata=dict(
        dtype=np.int16,
    ))

    nquadoinput: Any = field(default=None, metadata=dict(
        dtype=np.int16,
    ))

    NTHETAV: Any = field(default=None, metadata=dict(
        dtype=np.int16,
    ))

    NWV: Any = field(default=None, metadata=dict(
        long_name='number of wavelegnths',
        dtype=np.int16,
    ))

    OCEAN_CASE_SELECT: Any = field(default=None, metadata=dict(
        flag_values=(-1, 0, 1, 2, 3),
        flag_meanings=(
            'land',
            'atmosphere only',
            '[Chla] parameterization',
            '[Chla]+Sediment',
            'seven parameter model',
        ),
        dtype=np.int16,
    ))

    OCEAN_FCDOM_FLAG: Any = field(default=None, metadata=dict(
        flag_values=(0, 1),
        flag_meanings=('False', 'True'),
        dtype=np.int16,
    ))

    OCEAN_FCHLA_FLAG: Any = field(default=None, metadata=dict(
        flag_values=(0, 1),
        flag_meanings=('False', 'True'),
        dtype=np.int16,
    ))

    OCEAN_PHMX_ONE: Any = field(default=None, metadata=dict(
        flag_values=(0, 1),
        flag_meanings=('False', 'True'),
        dtype=np.int16,
    ))

    OCEAN_RAMAN_FLAG: Any = field(default=None, metadata=dict(
        flag_values=(0, 1),
        flag_meanings=('False', 'True'),
        dtype=np.int16,
    ))

    OZONE_COLUMN_DobsonUnit: Any = field(default=None, metadata=dict(
        comment='ozone in the whole column',
        units='Dobson Unit',
        source='US standard atmosphere 1976',
        valid_range=(250.0, 500.0),
        dtype=np.float32,
    ))

    phytoplankton_index_refraction: Any = field(default=None, metadata=dict(
        comment='used when ocean_case_select == 2',
        dtype=np.float32,
    ))

    phytoplankton_spectral_slope: Any = field(default=None, metadata=dict(
        comment='used when ocean_case_select == 2',
        dtype=np.float32,
    ))

    Pressure_Surface_mb: Any = field(default=None, metadata=dict(
        long_name='surface pressure',
        units='mb',
        valid_range=(850.0, 1050.0),
        dtype=np.float32,
    ))

    pss_flag: Any = field(default=None, metadata=dict(
        long_name='pseudospherical flag',
        flag_values=(0, 1),
        flag_meanings=('Off', 'On'),
        dtype=np.int16,
    ))

    Relative_Humidity: Any = field(default=None, metadata=dict(
        long_name='relative humidity',
        valid_range=(0.3, 0.95),
        dtype=np.float32,
    ))

    Reff_Cloud: Any = field(default=None, metadata=dict(
        long_name='effective radius',
        dtype=np.float32,
    ))

    rf1: Any = field(default=None, metadata=dict(
        long_name='dust like contribution in fine mode: by volume',
        dtype=np.float32,
    ))

    rf2: Any = field(default=None, metadata=dict(
        long_name='water soluble contribution in fine mode: by volume',
        dtype=np.float32,
    ))

    rf3: Any = field(default=None, metadata=dict(
        long_name='brown carbon contribution in fine mode: by volume',
        dtype=np.float32,
    ))

    r0c: Any = field(default=None, metadata=dict(
        long_name='dry radius coarse mode spherical (sea salt) by volume',
        dtype=np.float32,
    ))

    r0f: Any = field(default=None, metadata=dict(
        long_name='dry radius fine mode spherical - internal mixing by volume',
        dtype=np.float32,
    ))

    r0_bc: Any = field(default=None, metadata=dict(
        long_name='dry radius brown carbon (fine mode) by volume',
        dtype=np.float32,
    ))

    r0_dl: Any = field(default=None, metadata=dict(
        long_name='dry radius dust like (fine mode) by volume',
        dtype=np.float32,
    ))

    r0_ws: Any = field(default=None, metadata=dict(
        long_name='dry radius water soluble (fine mode) by volume',
        dtype=np.float32,
    ))

    r0_s: Any = field(default=None, metadata=dict(
        long_name='dry radius soot (fine mode) by volume',
        dtype=np.float32,
    ))

    r0_ss: Any = field(default=None, metadata=dict(
        long_name='dry radius sea salt (coarse mode) by volume',
        dtype=np.float32,
    ))

    S_Bp: Any = field(default=None, metadata=dict(
        long_name='power spectral slope of backscattering fraction',
        comment='used when ocean_case_select == 3',
        units='1/nm',
        valid_range=(-0.2, 0.2),
        dtype=np.float32,
    ))

    Sbp: Any = field(default=None, metadata=dict(
        long_name='power spectral slope of backscattering coefficient',
        comment='used when ocean_case_select == 3',
        units='1/nm',
        valid_range=(0.0, 0.5),
        dtype=np.float32,
    ))

    Sdg: Any = field(default=None, metadata=dict(
        long_name='exponential spectral slope of dg absorption',
        comment='used when ocean_case_select == 3',
        units='1/nm',
        valid_range=(0.01, 0.02),
        dtype=np.float32,
    ))

    sediment_concentration: Any = field(default=None, metadata=dict(
        comment='used when ocean_case_select == 2',
        valid_range=(0.0, 30.0),
        dtype=np.float32,
    ))

    sediment_index_refraction: Any = field(default=None, metadata=dict(
        comment='used when ocean_case_select == 2',
        dtype=np.float32,
    ))

    sediment_spectral_slope: Any = field(default=None, metadata=dict(
        comment='used when ocean_case_select == 2',
        dtype=np.float32,
    ))

    sigc: Any = field(default=None, metadata=dict(
        long_name='standard deviation coarse mode',
        dtype=np.float32,
    ))

    sigf: Any = field(default=None, metadata=dict(
        long_name='standard deviation fine mode',
        dtype=np.float32,
    ))

    SUN_GLINT_FLAG: Any = field(default=None, metadata=dict(
        flag_values=(0, 1),
        flag_meanings=('include sun glint', 'no sun glint'),
        dtype=np.int16,
    ))

    Solar_Zenith_Angle: Any = field(default=None, metadata=dict(
        units='degrees',
        valid_range=(0.0, 80.0),
        dtype=np.float32,
    ))

    tau_ref_hi: Any = field(default=None, metadata=dict(
        long_name='top layer optical depth at reference wavelength',
        valid_range=(0.0, 100.0),
        dtype=np.float32,
    ))

    tau_ref_low: Any = field(default=None, metadata=dict(
        long_name='bottom layer optical depth at reference wavelength',
        comment='set to 0.0 for one aerosol layer',
        valid_range=(0.0, 100.0),
        dtype=np.float32,
    ))

    Wind_Speed: Any = field(default=None, metadata=dict(
        long_name='Wind Speed',
        comment=(
            'if `I_SURFACE_ROUGHNESS_PARA == 1`, inverse wind speed '
            'from SIGMA^2=0.003D0+0.00512D0*WNDSPD Cox & Munk 1954, '
            'else if `I_SURFACE_ROUGHNESS_PARA == 2` from Gordon & '
            'Wang 1992'
            ),
        valid_range=(0.1, 15.0),
        dtype=np.float32,
    ))

    water_depth_max: Any = field(default=None, metadata=dict(
        dtype=np.float32,
    ))

    WAVELENGTH_MICRON_REF: Any = field(default=None, metadata=dict(
        dtype=np.float32,
    ))

    wv_pace_ref: Any = field(default=None, metadata=dict(
        long_name='reference wavelength for optical depth assignment',
        dtype=np.float32,
    ))

    WAVEBAND_SEG_FLAG: Any = field(default=None, metadata=dict(
        flag_values=(0, 1, 2, 3, 4),
        flag_meanings=(
            'all',
            'seg1+3only',
            'seg2only',
            'seg1+2+3',
            'seg4only',
        ),
        dtype=np.int16,
    ))

    Veff_Cloud: Any = field(default=None, metadata=dict(
        long_name='effective variance',
        dtype=np.float32,
    ))

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
            array = np.array(value, dtype=attrs.pop('dtype', None))
            dim = coord if array.shape else ()
            dataset = dataset.assign_coords({coord: (dim, array, attrs)})
        return dataset
