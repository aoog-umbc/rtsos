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
        P.aux_dir: 'data/RT/pwzrt/Data',
        P.gas_abs_coef_dir: 'data/RT/pwzrt/Gas_Absorption_Coefficients',
        P.mie_database_dir: 'data/RT/pwzrt/Mie_Database/OCI_Mie_Database',
        P.MIE_TABLE_CAL: 3,
        P.aerosol: range(11, 21),
        # intentionly set bizarre aerofms as we don't need it in this work
        P.AerosolFineModeFraction: -1.0E12,
        P.Relative_Humidity: [0.3, 0.5, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95],
        # wndspd will be calculated
        P.wndspd: None,
        # theta0 will be set to vary only when `df == 0`
        P.theta0: np.arange(0, 90, 2),
        P.tau865: [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5],
        P.Pressure_Surface_mb: 1013,
        P.H2O_COLUMN: 1.4387,
        P.OZONE_COLUMN_DobsonUnit: 345.66,
        P.iwhitecap: 0,
        P.I_SURFACE_ROUGHNESS_PARA: 2,
        P.df: [0, 1],
        P.I_SPHERICAL_SHELL_CORRECTION: 0,
        P.atmos_profile: 'afglus.dat',
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
    values[P.wndspd] = wndspd

    # create a dataset to hold the inputs as coordinates
    params = P()
    dataset = params.to_dataset(values)

    # replace independent theta0 and df dimensions with a compound
    # dimension and coordinates
    dataset = dataset.stack({'theta0-df': ('theta0', 'df')})
    dataset = (
        dataset.where(
            # TODO confirm theta0 value for diffuse transmission
            ~np.logical_and(dataset['df']==1, dataset['theta0']!=0.),
            drop=True,
            )
        .reset_index('theta0-df')
        )

    # run command line tool
    rt = ZhaiRT(
        'rtsos_GSFC_AC_LUT.exe',
        params=tuple(values),
        defaults=dataset,
        )
    return rt.execute(args)
