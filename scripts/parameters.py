from dataclasses import dataclass, asdict

import numpy as np
import numpy.typing as npt
import xarray as xr


@dataclass
class Attributes:
    '''metadata associated with a model parameter'''

    name: str = None
    description: str = None
    dtype: npt.DTypeLike = None
    units: str = None
    range: str = None
    source: str = None


@dataclass(slots=True)
class Parameters:
    '''Names and other documentation for parameters in RT codes'''
    # The type hints are not to be interpreted as Numpy dtypes, which is instead
    # a member of `Attributes`; it's better to think of Parameters as the
    # metadata about parameters used in RT calculations. That means the defaults
    # below are almost always used, and essentially serve as documentation.
    # The purpose of `slots=True` is to produce Class attributes that are
    # visible to IDEs which provide tab completion, i.e. `Parameters.<tab>`.
    # TODO clean up metadata

    adg440: Attributes = Attributes(
        units='1/m',
        range='0.0:2.5',
        dtype=np.float32,
        )
    aerofmf: Attributes = Attributes(
        name='Aerosol Fine Mode Fraction',
        description='only used when Aerosol Model is set to "-1"',
        dtype=np.float32,
        )
    aerosol: Attributes = Attributes(
        name='Aerosol Model',
        description=(
            '-99 read aerosol pmhx in from file, '
            '-98 read water cloud phmx from file, '
            '-1 Ahmad model with flexbile RH and FMF, '
            '1-10 is Shettle and Fenn, '
            '11-20 is Ahmad model, '
            '21 dust aerosol model'
            ),
        dtype=np.int16,
        )
    aerosol_phasematrix_file: Attributes = Attributes(
        )
    AirSensor_Height: Attributes = Attributes(
        units='km',
        dtype=np.float32,
        )
    albedo_ground: Attributes = Attributes(
        dtype=np.float32,
        )
    ap_select: Attributes = Attributes(
        description=(
            '1 Bricaud LUT, '
            '2 Mixure of pico and micron cells in Ciott et al. 2002'
            ),
        dtype=np.int16,
        )
    atmos_profile: Attributes = Attributes(
        description=(
            'valid atmosphere profiles are: afglus.dat, '
            'afglsw.dat, afglss.dat, or afglmw.dat'
            ),
        )
    atmos_zero: Attributes = Attributes(
        dtype=np.int16,
        )
    aux_dir: Attributes = Attributes(
        description=(
            'path to directory containing auxiliary data files '
            '(e.g. afrt_input_oci.txt)'
            )
        )
    bbp660_BackscatterCoeff: Attributes = Attributes(
        units='1/m',
        range='0.0:0.1',
        dtype=np.float32,
        )
    Bp660_BackscatterFraction: Attributes = Attributes(
        range='0.0:0.05',
        dtype=np.float32,
        )
    chla: Attributes = Attributes(
        dtype=np.float32,
        )
    chla_homogeneity: Attributes = Attributes(
        dtype=np.int16,
        )
    df: Attributes = Attributes(
        description=(
            'calculate regular reflectance (0) or '
            'diffuse transmittance (1)'
            ),
        dtype=np.int16,
        )
    gas_abs_flag: Attributes = Attributes(
        dtype=np.int16,
        )
    gas_abs_coef_dir: Attributes = Attributes(
        description='path to directory containing gas absorbption data'
        )
    H2O_COLUMN: Attributes = Attributes(
        description='water vapor in the whole column',
        units='cm',
        source='US standard atmosphere 1976',
        dtype=np.float32,
        )
    height_particle: Attributes = Attributes(
        description='scatteror height',
        dtype=np.float32,
        )
    hyspectral_flag: Attributes = Attributes(
        dtype=np.int16,
        )
    I_SURFACE_ROUGHNESS_PARA: Attributes = Attributes(
        dtype=np.int16,
        )
    I_SPHERICAL_SHELL_CORRECTION: Attributes = Attributes(
        description=(
            'turn spherical shell correction off (0) or on (1)'
            ),
        dtype=np.int16,
        )
    # TODO replace instrument with additional parameters
    instrument: Attributes = Attributes(
        description='numeric identifier of the instrument',
        dtype=np.int16,
        )
    iwhitecap: Attributes = Attributes(
        description='turn white cap calculation off (0) or on (1)',
        dtype=np.int16,
        )
    MAXMORDINPUT: Attributes = Attributes(
        dtype=np.int16,
        )
    mie_database_dir: Attributes = Attributes(
        description='path to directory containing Mie database'
        )
    monochromatic_flag: Attributes = Attributes(
        dtype=np.int16,
        )
    ncolinput: Attributes = Attributes(
        dtype=np.int16,
        )
    NO2_COLUMN: Attributes = Attributes(
        description='no2 column amount',
        units='Dobson Unit',
        dtype=np.float32,
        )
    npq_flag: Attributes = Attributes(
        dtype=np.int16,
        )
    nquadainput: Attributes = Attributes(
        dtype=np.int16,
        )
    nquadoinput: Attributes = Attributes(
        dtype=np.int16,
        )
    NPHIV: Attributes = Attributes(
        dtype=np.int16,
        )
    NTHETAV: Attributes = Attributes(
        dtype=np.int16,
        )
    ocean_case_select: Attributes = Attributes(
        description=(
            '-1 land, '
            '0 atmosphere only, '
            '1 [Chla] parameterization, '
            '2 [Chla]+Sediment, '
            '3 seven parameter model'
            ),
        dtype=np.int16,
        )
    ocean_fcdom_flag: Attributes = Attributes(
        dtype=np.int16,
        )
    ocean_fchla_flag: Attributes = Attributes(
        dtype=np.int16,
        )
    ocean_phmx_one: Attributes = Attributes(
        dtype=np.int16,
        )
    ocean_raman_flag: Attributes = Attributes(
        dtype=np.int16,
        )
    OZONE_COLUMN: Attributes = Attributes(
        description='ozone in the whole column',
        units='Dobson Unit',
        source='US standard atmosphere 1976',
        dtype=np.float32,
        )
    phytoplankton_index_refraction: Attributes = Attributes(
        dtype=np.float32,
        )
    phytoplankton_spectral_slope: Attributes = Attributes(
        dtype=np.float32,
        )
    pressure_surface: Attributes = Attributes(
        name='surface pressure',
        units='mb',
        dtype=np.float32,
        )
    pss_flag: Attributes = Attributes(
        description='pseudospherical flag',
        dtype=np.int16,
        )
    RH: Attributes = Attributes(
        name='Relative Humidity',
        dtype=np.float32,
        )
    S_Bp: Attributes = Attributes(
        description='power spectral slope of backscattering fraction',
        units='1/m',
        range='-0.2:0.2',
        dtype=np.float32,
        )
    Sbp: Attributes = Attributes(
        description='power spectral slope of backscattering coefficient',
        units='1/m',
        range='0.0:0.5',
        dtype=np.float32,
        )
    Sdg: Attributes = Attributes(
        description='exponential spectral slope of dg absorption',
        units='1/m',
        range='0.01:0.02',
        dtype=np.float32,
        )
    sediment_concentration: Attributes = Attributes(
        dtype=np.float32,
        )
    sediment_index_refraction: Attributes = Attributes(
        dtype=np.float32,
        )
    sediment_spectral_slope: Attributes = Attributes(
        dtype=np.float32,
        )
    SUNGLINT_INPUT: Attributes = Attributes(
        description=(
            '0 include sun glint, '
            '1 no sun glint '
            ),
        dtype=np.int16,
        )
    theta0: Attributes = Attributes(
        units='degrees',
        dtype=np.float32,
        )
    tau865: Attributes = Attributes(
        dtype=np.float32,
        )
    tau_ref: Attributes = Attributes(
        dtype=np.float32,
        )
    wndspd: Attributes = Attributes(
        name='Wind Speed',
        description=(
            'if `I_SURFACE_ROUGHNESS_PARA == 1`, inverse wind speed '
            'from SIGMA^2=0.003D0+0.00512D0*WNDSPD Cox & Munk 1954, '
            'else if `I_SURFACE_ROUGHNESS_PARA == 2` from Gordon & '
            'Wang 1992'
            ),
        dtype=np.float32,
        )
    water_depth_max: Attributes = Attributes(
        dtype=np.float32,
        )
    wv_pace_ref: Attributes = Attributes(
        dtype=np.float32,
        )
    wv_seg_flag: Attributes = Attributes(
        description=(
            '0: all; '
            '1: seg1+3only; '
            '2: seg2only; '
            '3 seg1+2+3; '
            '4: seg4only'
            ),
        dtype=np.int16,
        )

    def to_dataset(self, data: dict) -> xr.Dataset:
        '''Cast native dataclass to XArray Dataset with parameter attributes
        from the dataclass and values from `data`.
        '''
        dataset = xr.Dataset()
        for key, value in data.items():
            key = key.__name__
            attributes = asdict(getattr(self, key))
            value = np.array(value, dtype=attributes.pop('dtype', None))
            dim = key if value.shape else ()
            attributes = {k: v for k, v in attributes.items() if v}
            dataset = dataset.assign_coords({key: (dim, value, attributes)})
        return dataset
