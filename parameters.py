from dataclasses import dataclass, asdict

import numpy as np
import numpy.typing as npt
import xarray as xr


@dataclass
class Attributes:
    '''metadata associated with a model parameter'''

    name: str = None
    description: str = None
    units: str = None
    range: str = None
    source: str = None
    dtype: npt.DTypeLike = str


@dataclass(slots=True)
class Parameters:
    '''names and other documentation for parameters in RTM codes'''
    # This dataclass is for parameter metadata, not the parameter values,
    # used in RT calculations. That means the defaults below are almost always
    # used and essentially serve as built-in model documentation.
    # The purpose of `slots=True` is to produce Class attributes that are
    # visible to IDEs which provide tab completion, i.e. `Parameters.<tab>`.
    # TODO clean up metadata

    adg440: Attributes = Attributes(
        description='used when ocean_case_select == 3',
        units='1/m',
        range='0.0:2.5',
        dtype=np.float32,
        )
    AerosolFineModeFraction: Attributes = Attributes(
        name='Aerosol Fine Mode Fraction',
        description='only used when Aerosol Model Number is set to "-1"',
        range='0:1',
        dtype=np.float32,
        )
    Aerosol_Model_Number: Attributes = Attributes(
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
    Aerosol_Phasematrix_File: Attributes = Attributes(
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
    Atmos_Dir: Attributes = Attributes(
        description='path to directory containing gas absorbption data'
        )
    ATMOS_ZERO: Attributes = Attributes(
        description='1=True, 0=False',
        dtype=np.int16,
        )
    Aux_Dir: Attributes = Attributes(
        description=(
            'path to directory containing auxiliary data files '
            '(e.g. afrt_input_oci.txt)'
            )
        )
    bbp660_BackscatterCoeff: Attributes = Attributes(
        description='used when ocean_case_select == 3',
        units='1/m',
        range='0.0:0.1',
        dtype=np.float32,
        )
    Bp660_BackscatterFraction: Attributes = Attributes(
        description='used when ocean_case_select == 3',
        range='0.0:0.05',
        dtype=np.float32,
        )
    CFILE_AP: Attributes = Attributes(
        name='filename for atmospheric profile data',
        description=(
            'valid atmosphere profiles are: afglus.dat, '
            'afglsw.dat, afglss.dat, or afglmw.dat'
            ),
        )
    CFILE_INSTRUMENT: Attributes = Attributes(
        description='name of AFRT file to use',
    )
    chla: Attributes = Attributes(
        description='used when ocean_case_select in (1, 2, 3)',
        range='0.04:50',
        units='mg/m3',
        dtype=np.float32,
        )
    CHLA_HOMOGENEITY: Attributes = Attributes(
        dtype=np.int16,
        description='1=True, 0=False',
        )
    Diffuse_Transmittance_Flag: Attributes = Attributes(
        description=(
            'calculate regular reflectance (0) or '
            'diffuse transmittance (1)'
            ),
        dtype=np.int16,
        )
    gas_abs_flag: Attributes = Attributes(
        description='1=True, 0=False',
        dtype=np.int16,
        )
    H2O_COLUMN: Attributes = Attributes(
        description='water vapor in the whole column',
        units='cm',
        source='US standard atmosphere 1976',
        range='0.01:15',
        dtype=np.float32,
        )
    height_particle: Attributes = Attributes(
        description='scatteror height',
        range='1:10',
        dtype=np.float32,
        )
    hyspectral_flag: Attributes = Attributes(
        description='1=True, 0=False',
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
    iwhitecap: Attributes = Attributes(
        description='turn white cap calculation off (0) or on (1)',
        dtype=np.int16,
        )
    MAXMORDINPUT: Attributes = Attributes(
        dtype=np.int16,
        )
    Mie_Database_Dir: Attributes = Attributes(
        description='path to directory containing Mie database'
        )
    MIE_TABLE_CAL: Attributes = Attributes(
        description=(
            'Set behavior for Mie table calculations to '
            '1 = calculate and store Mie scattering matrix, then exit, '
            '2 = calculate and use (w/out storing) Mie scattering matrix, '
            '3 = use existing Mie scattering matrix'
        ),
        dtype=np.int16,
    )
    MONOCHROMATIC_FLAG: Attributes = Attributes(
        description='1=True, 0=False',
        dtype=np.int16,
        )
    ncolinput: Attributes = Attributes(
        dtype=np.int16,
        )
    NO2_COLUMN_DobsonUnit: Attributes = Attributes(
        description='no2 column amount',
        units='Dobson Unit',
        dtype=np.float32,
        )
    NonPhotochemicalQuenching_FLAG: Attributes = Attributes(
        description='1=True, 0=False',
        dtype=np.int16,
        )
    NPHIV: Attributes = Attributes(
        dtype=np.int16,
        )
    nquadainput: Attributes = Attributes(
        dtype=np.int16,
        )
    nquadoinput: Attributes = Attributes(
        dtype=np.int16,
        )
    NTHETAV: Attributes = Attributes(
        dtype=np.int16,
        )
    NWV: Attributes = Attributes(
        name='number of wavelegnths',
        dtype=np.int16,
    )
    OCEAN_CASE_SELECT: Attributes = Attributes(
        description=(
            '-1 land, '
            '0 atmosphere only, '
            '1 [Chla] parameterization, '
            '2 [Chla]+Sediment, '
            '3 seven parameter model'
            ),
        dtype=np.int16,
        )
    OCEAN_FCDOM_FLAG: Attributes = Attributes(
        description='1=True, 0=False',
        dtype=np.int16,
        )
    OCEAN_FCHLA_FLAG: Attributes = Attributes(
        description='1=True, 0=False',
        dtype=np.int16,
        )
    OCEAN_PHMX_ONE: Attributes = Attributes(
        description='1=True, 0=False',
        dtype=np.int16,
        )
    OCEAN_RAMAN_FLAG: Attributes = Attributes(
        description='1=True, 0=False',
        dtype=np.int16,
        )
    OZONE_COLUMN_DobsonUnit: Attributes = Attributes(
        description='ozone in the whole column',
        units='Dobson Unit',
        source='US standard atmosphere 1976',
        range='250:500',
        dtype=np.float32,
        )
    phytoplankton_index_refraction: Attributes = Attributes(
        description='used when ocean_case_select == 2',
        dtype=np.float32,
        )
    phytoplankton_spectral_slope: Attributes = Attributes(
        description='used when ocean_case_select == 2',
        dtype=np.float32,
        )
    Pressure_Surface_mb: Attributes = Attributes(
        name='surface pressure',
        units='mb',
        range='850:1050',
        dtype=np.float32,
        )
    pss_flag: Attributes = Attributes(
        name='pseudospherical flag',
        description='1: turn on, 0: turn off',
        dtype=np.int16,
        )
    Relative_Humidity: Attributes = Attributes(
        name='Relative Humidity',
        range='0.3:0.95',
        dtype=np.float32,
        )
    S_Bp: Attributes = Attributes(
        description=(
            'power spectral slope of backscattering fraction, '
            'used when ocean_case_select == 3'
            ),
        units='1/nm',
        range='-0.2:0.2',
        dtype=np.float32,
        )
    Sbp: Attributes = Attributes(
        description=(
            'power spectral slope of backscattering coefficient, '
            'used when ocean_case_select == 3'
            ),
        units='1/nm',
        range='0.0:0.5',
        dtype=np.float32,
        )
    Sdg: Attributes = Attributes(
        description=(
            'exponential spectral slope of dg absorption, '
            'used when ocean_case_select == 3'
            ),
        units='1/nm',
        range='0.01:0.02',
        dtype=np.float32,
        )
    sediment_concentration: Attributes = Attributes(
        description='used when ocean_case_select == 2',
        range='0:30',
        dtype=np.float32,
        )
    sediment_index_refraction: Attributes = Attributes(
        description='used when ocean_case_select == 2',
        dtype=np.float32,
        )
    sediment_spectral_slope: Attributes = Attributes(
        description='used when ocean_case_select == 2',
        dtype=np.float32,
        )
    SUN_GLINT_FLAG: Attributes = Attributes(
        description=(
            '0 include sun glint, '
            '1 no sun glint'
            ),
        dtype=np.int16,
        )
    Solar_Zenith_Angle: Attributes = Attributes(
        units='degrees',
        range='0:80',
        dtype=np.float32,
        )
    Tau_NIR: Attributes = Attributes(
        # TODO duplicates tau_ref?
        dtype=np.float32,
        )
    tau_ref: Attributes = Attributes(
        range='0.01:0.4',
        dtype=np.float32,
        )
    Wind_Speed: Attributes = Attributes(
        name='Wind Speed',
        description=(
            'if `I_SURFACE_ROUGHNESS_PARA == 1`, inverse wind speed '
            'from SIGMA^2=0.003D0+0.00512D0*WNDSPD Cox & Munk 1954, '
            'else if `I_SURFACE_ROUGHNESS_PARA == 2` from Gordon & '
            'Wang 1992'
            ),
        range='0.1:15',
        dtype=np.float32,
        )
    water_depth_max: Attributes = Attributes(
        dtype=np.float32,
        )
    WAVELENGTH_MICRON_REF: Attributes = Attributes(
        dtype=np.float32,
    )
    wv_pace_ref: Attributes = Attributes(
        dtype=np.float32,
        )
    WAVEBAND_SEG_FLAG: Attributes = Attributes(
        description=(
            '0: all; '
            '1: seg1+3only; '
            '2: seg2only; '
            '3: seg1+2+3; '
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
