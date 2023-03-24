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
    # TODO clean up metadata

    adg440: Any = field(default=None, metadata=dict(
        description='used when ocean_case_select == 3',
        units='1/m',
        range='0.0:2.5',
        dtype=np.float32,
        ))
    AerosolFineModeFraction: Any = field(default=None, metadata=dict(
        name='Aerosol Fine Mode Fraction',
        description='only used when Aerosol Model Number is set to "-1"',
        range='0:1',
        dtype=np.float32,
        ))
    Aerosol_Model_Number: Any = field(default=None, metadata=dict(
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
        ))
    Aerosol_Phasematrix_File: Any = field(default=None, metadata=dict(
        ))
    AirSensor_Height: Any = field(default=None, metadata=dict(
        units='km',
        dtype=np.float32,
        ))
    albedo_ground: Any = field(default=None, metadata=dict(
        dtype=np.float32,
        ))
    ap_select: Any = field(default=None, metadata=dict(
        description=(
            '1 Bricaud LUT, '
            '2 Mixure of pico and micron cells in Ciott et al. 2002'
            ),
        dtype=np.int16,
        ))
    Atmos_Dir: Any = field(default=None, metadata=dict(
        description='path to directory containing gas absorbption data'
        ))
    ATMOS_ZERO: Any = field(default=None, metadata=dict(
        description='1=True, 0=False',
        dtype=np.int16,
        ))
    Aux_Dir: Any = field(default=None, metadata=dict(
        description=(
            'path to directory containing auxiliary data files '
            '(e.g. afrt_input_oci.txt)'
            )
        ))
    bbp660_BackscatterCoeff: Any = field(default=None, metadata=dict(
        description='used when ocean_case_select == 3',
        units='1/m',
        range='0.0:0.1',
        dtype=np.float32,
        ))
    Bp660_BackscatterFraction: Any = field(default=None, metadata=dict(
        description='used when ocean_case_select == 3',
        range='0.0:0.05',
        dtype=np.float32,
        ))
    CFILE_AP: Any = field(default=None, metadata=dict(
        name='filename for atmospheric profile data',
        description=(
            'valid atmosphere profiles are: afglus.dat, '
            'afglsw.dat, afglss.dat, or afglmw.dat'
            ),
        ))
    CFILE_INSTRUMENT: Any = field(default=None, metadata=dict(
        description='name of AFRT file to use',
        ))
    chla: Any = field(default=None, metadata=dict(
        description='used when ocean_case_select in (1, 2, 3)',
        range='0.04:50',
        units='mg/m3',
        dtype=np.float32,
        ))
    CHLA_HOMOGENEITY: Any = field(default=None, metadata=dict(
        dtype=np.int16,
        description='1=True, 0=False',
        ))
    Diffuse_Transmittance_Flag: Any = field(default=None, metadata=dict(
        description=(
            'calculate regular reflectance (0) or '
            'diffuse transmittance (1)'
            ),
        dtype=np.int16,
        ))
    gas_abs_flag: Any = field(default=None, metadata=dict(
        description='1=True, 0=False',
        dtype=np.int16,
        ))
    H2O_COLUMN: Any = field(default=None, metadata=dict(
        description='water vapor in the whole column',
        units='cm',
        source='US standard atmosphere 1976',
        range='0.01:15',
        dtype=np.float32,
        ))
    height_particle: Any = field(default=None, metadata=dict(
        description='scatteror height',
        range='1:10',
        dtype=np.float32,
        ))
    hyspectral_flag: Any = field(default=None, metadata=dict(
        description='1=True, 0=False',
        dtype=np.int16,
        ))
    I_SURFACE_ROUGHNESS_PARA: Any = field(default=None, metadata=dict(
        dtype=np.int16,
        ))
    I_SPHERICAL_SHELL_CORRECTION: Any = field(default=None, metadata=dict(
        description=(
            'turn spherical shell correction off (0) or on (1)'
            ),
        dtype=np.int16,
        ))
    iwhitecap: Any = field(default=None, metadata=dict(
        description='turn white cap calculation off (0) or on (1)',
        dtype=np.int16,
        ))
    MAXMORDINPUT: Any = field(default=None, metadata=dict(
        dtype=np.int16,
        ))
    Mie_Database_Dir: Any = field(default=None, metadata=dict(
        description='path to directory containing Mie database'
        ))
    MIE_TABLE_CAL: Any = field(default=None, metadata=dict(
        description=(
            'Set behavior for Mie table calculations to '
            '1 = calculate and store Mie scattering matrix, then exit, '
            '2 = calculate and use (w/out storing) Mie scattering matrix, '
            '3 = use existing Mie scattering matrix'
        ),
        dtype=np.int16,
        ))
    MONOCHROMATIC_FLAG: Any = field(default=None, metadata=dict(
        description='1=True, 0=False',
        dtype=np.int16,
        ))
    ncolinput: Any = field(default=None, metadata=dict(
        dtype=np.int16,
        ))
    NO2_COLUMN_DobsonUnit: Any = field(default=None, metadata=dict(
        description='no2 column amount',
        units='Dobson Unit',
        dtype=np.float32,
        ))
    NonPhotochemicalQuenching_FLAG: Any = field(default=None, metadata=dict(
        description='1=True, 0=False',
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
        name='number of wavelegnths',
        dtype=np.int16,
        ))
    OCEAN_CASE_SELECT: Any = field(default=None, metadata=dict(
        description=(
            '-1 land, '
            '0 atmosphere only, '
            '1 [Chla] parameterization, '
            '2 [Chla]+Sediment, '
            '3 seven parameter model'
            ),
        dtype=np.int16,
        ))
    OCEAN_FCDOM_FLAG: Any = field(default=None, metadata=dict(
        description='1=True, 0=False',
        dtype=np.int16,
        ))
    OCEAN_FCHLA_FLAG: Any = field(default=None, metadata=dict(
        description='1=True, 0=False',
        dtype=np.int16,
        ))
    OCEAN_PHMX_ONE: Any = field(default=None, metadata=dict(
        description='1=True, 0=False',
        dtype=np.int16,
        ))
    OCEAN_RAMAN_FLAG: Any = field(default=None, metadata=dict(
        description='1=True, 0=False',
        dtype=np.int16,
        ))
    OZONE_COLUMN_DobsonUnit: Any = field(default=None, metadata=dict(
        description='ozone in the whole column',
        units='Dobson Unit',
        source='US standard atmosphere 1976',
        range='250:500',
        dtype=np.float32,
        ))
    phytoplankton_index_refraction: Any = field(default=None, metadata=dict(
        description='used when ocean_case_select == 2',
        dtype=np.float32,
        ))
    phytoplankton_spectral_slope: Any = field(default=None, metadata=dict(
        description='used when ocean_case_select == 2',
        dtype=np.float32,
        ))
    Pressure_Surface_mb: Any = field(default=None, metadata=dict(
        name='surface pressure',
        units='mb',
        range='850:1050',
        dtype=np.float32,
        ))
    pss_flag: Any = field(default=None, metadata=dict(
        name='pseudospherical flag',
        description='1: turn on, 0: turn off',
        dtype=np.int16,
        ))
    Relative_Humidity: Any = field(default=None, metadata=dict(
        name='Relative Humidity',
        range='0.3:0.95',
        dtype=np.float32,
        ))
    S_Bp: Any = field(default=None, metadata=dict(
        description=(
            'power spectral slope of backscattering fraction, '
            'used when ocean_case_select == 3'
            ),
        units='1/nm',
        range='-0.2:0.2',
        dtype=np.float32,
        ))
    Sbp: Any = field(default=None, metadata=dict(
        description=(
            'power spectral slope of backscattering coefficient, '
            'used when ocean_case_select == 3'
            ),
        units='1/nm',
        range='0.0:0.5',
        dtype=np.float32,
        ))
    Sdg: Any = field(default=None, metadata=dict(
        description=(
            'exponential spectral slope of dg absorption, '
            'used when ocean_case_select == 3'
            ),
        units='1/nm',
        range='0.01:0.02',
        dtype=np.float32,
        ))
    sediment_concentration: Any = field(default=None, metadata=dict(
        description='used when ocean_case_select == 2',
        range='0:30',
        dtype=np.float32,
        ))
    sediment_index_refraction: Any = field(default=None, metadata=dict(
        description='used when ocean_case_select == 2',
        dtype=np.float32,
        ))
    sediment_spectral_slope: Any = field(default=None, metadata=dict(
        description='used when ocean_case_select == 2',
        dtype=np.float32,
        ))
    SUN_GLINT_FLAG: Any = field(default=None, metadata=dict(
        description=(
            '0 include sun glint, '
            '1 no sun glint'
            ),
        dtype=np.int16,
        ))
    Solar_Zenith_Angle: Any = field(default=None, metadata=dict(
        units='degrees',
        range='0:80',
        dtype=np.float32,
        ))
    Tau_NIR: Any = field(default=None, metadata=dict(
        # TODO duplicates tau_ref?
        dtype=np.float32,
        ))
    tau_ref: Any = field(default=None, metadata=dict(
        range='0.01:0.4',
        dtype=np.float32,
        ))
    Wind_Speed: Any = field(default=None, metadata=dict(
        name='Wind Speed',
        description=(
            'if `I_SURFACE_ROUGHNESS_PARA == 1`, inverse wind speed '
            'from SIGMA^2=0.003D0+0.00512D0*WNDSPD Cox & Munk 1954, '
            'else if `I_SURFACE_ROUGHNESS_PARA == 2` from Gordon & '
            'Wang 1992'
            ),
        range='0.1:15',
        dtype=np.float32,
        ))
    water_depth_max: Any = field(default=None, metadata=dict(
        dtype=np.float32,
        ))
    WAVELENGTH_MICRON_REF: Any = field(default=None, metadata=dict(
        dtype=np.float32,
        ))
    wv_pace_ref: Any = field(default=None, metadata=dict(
        dtype=np.float32,
        ))
    WAVEBAND_SEG_FLAG: Any = field(default=None, metadata=dict(
        description=(
            '0: all; '
            '1: seg1+3only; '
            '2: seg2only; '
            '3: seg1+2+3; '
            '4: seg4only'
            ),
        dtype=np.int16,
        ))

    def make_dataset(self, data: dict) -> xr.Dataset:
        '''Cast native dataclass to XArray Dataset with attributes
        from the dataclass fields and values from `data`.
        '''
        dataset = xr.Dataset()
        metadata = {i.name: i.metadata for i in fields(self)}
        for key, value in data.items():
            coord = key.__name__
            attrs = metadata[coord].copy()
            array = np.array(value, dtype=attrs.pop('dtype', None))
            dim = coord if array.shape else ()
            dataset = dataset.assign_coords({coord: (dim, array, attrs)})
        return dataset
