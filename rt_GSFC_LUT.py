import numpy as np

from .kit import cli, ZhaiRT
from .parameters import Parameters as P


def main(argv=None):
    # parse command line arguments
    args = cli.parse_args(argv)

    # values to write, in the order below, to the RT input file
    values = {
        # the default parameterization is for PACE-OCI
        P.NWV: 239,
        P.WAVELENGTH_MICRON_REF: 0.870,
        P.CFILE_INSTRUMENT: 'afrt_input_oci.txt',
        P.Aux_Dir: 'data/RT/pwzrt/Data',
        P.Atmos_Dir: 'data/RT/pwzrt/Gas_Absorption_Coefficients',
        P.Mie_Database_Dir: 'data/Mie',
        P.MIE_TABLE_CAL: 2,
        P.Aerosol_Model_Number: range(11, 21),
        P.AerosolFineModeFraction: np.nan,
        P.Relative_Humidity: [0.3, 0.5, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95],
        # wndspd will be calculated
        P.Wind_Speed: None,
        # SZA will be set to vary only when `Diffuse_Transmittance_Flag == 0`
        P.Solar_Zenith_Angle: range(0, 90, 2),
        P.tau865: [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5],
        P.Pressure_Surface_mb: 1013,
        P.H2O_COLUMN: 1.4387,
        P.OZONE_COLUMN_DobsonUnit: 345.66,
        P.iwhitecap: 0,
        P.I_SURFACE_ROUGHNESS_PARA: 2,
        P.Diffuse_Transmittance_Flag: [0, 1],
        P.I_SPHERICAL_SHELL_CORRECTION: 0,
        P.CFILE_AP: 'afglus.dat',
        }

    # calculate compound coordinate wndspd
    sigma = np.array(
        [0, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4],
        dtype=np.float32
        )
    surface = values[P.I_SURFACE_ROUGHNESS_PARA]
    if surface == 1:
        wndspd = (np.square(sigma)-0.003)/0.00512
    elif surface == 2:
        wndspd = (np.square(sigma))/0.00534
    wndspd[wndspd<0.0] = 0.0
    values[P.Wind_Speed] = wndspd

    # create a dataset to hold the inputs as coordinates
    params = P()
    dataset = params.to_dataset(values)

    # replace independent sza and dt dimensions with a compound
    # dimension and coordinates
    dataset = dataset.stack({
        'sza-dt': ('Solar_Zenith_Angle', 'Diffuse_Transmittance_Flag'),
        })
    dataset = (
        dataset.where(
            # TODO confirm sza value for diffuse transmission
            ~np.logical_and(
                dataset['Diffuse_Transmittance_Flag'] == 1,
                dataset['Solar_Zenith_Angle'] != 0.0,
                ),
            drop=True,
            )
        .reset_index('sza-dt')
        )
    dataset['Solar_Zenith_Angle'] = (
        dataset['Solar_Zenith_Angle']
        .astype(dataset['Solar_Zenith_Angle'].dtype)
        )

    # run command line tool
    rt = ZhaiRT(
        'rtsos_GSFC_AC_LUT.exe',
        params=tuple(values),
        defaults=dataset,
        dims={
            'phony_dim_1': 'Optical_Depth',
            'phony_dim_2': 'Atmosphere_Layer_Altitudes',
            'phony_dim_3': 'WaveLength',
            'phony_dim_4': 'PhiV',
            'phony_dim_5': 'ThetaV',
            },
        )
    return rt.execute(args)
