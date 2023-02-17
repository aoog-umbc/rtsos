import numpy as np
import xarray as xr

from .kit import cli, ZhaiRT
from .parameters import Parameters as P


class AC_LUT(ZhaiRT):

    def post(self, dataset):
        # drop unneeded coordinates
        dataset = dataset.where(dataset['ThetaV'] < 90.0, drop=True)
        # "unstack" the sza-dt dimension into separate datasets
        idx = dataset[P.Diffuse_Transmittance_Flag.__name__] == 1
        renamed = {
            'Radiance_TOA': 'LT_TOA',
            'Radiance_BOA': 'LT_BOA',
            }
        dt = (
            dataset
            .sel({'sza-dt': idx})
            .squeeze('sza-dt')
            .rename(renamed)
            .drop_vars([P.Diffuse_Transmittance_Flag.__name__, 'sza-dt'])
            )
        dt = dt[list(renamed.values())]
        renamed = {
            'Radiance_TOA': 'Lt',
            'Q_TOA': 'LQ',
            'U_TOA': 'LU',
            'Radiance_TOA_Glint': 'TLg',
            'Q_TOA_Glint': 'TQg',
            'U_TOA_Glint': 'TUg',
            'Irrad_Down_TOA': 'diff_irrad',
            }
        sza = (
            dataset
            .sel({'sza-dt': ~idx})
            .swap_dims({'sza-dt': P.Solar_Zenith_Angle.__name__})
            .rename(renamed)
            .drop_vars([P.Diffuse_Transmittance_Flag.__name__, 'sza-dt'])
            )
        # calculate aggregrates
        noeffect = {P.Wind_Speed.__name__: 0, P.Solar_Zenith_Angle.__name__: 0}
        sza['aot'] = (
            sza['Tau_Aerosol_Extinction']
            .isel(noeffect)
            .sum(dim='NTLYERA')
            )
        sza['rot'] = (
            sza['Tau_Rayleigh_Extinction']
            .isel(noeffect)
            .sum(dim='NTLYERA')
            )
        sza['depol'] = (
            sza['Rayleigh_Depolarization_Ratio']
            .isel(noeffect)
            .mean(dim='NTLYERA')
            )
        # finish creating sza
        sza = sza[list(renamed.values()) + ['aot', 'rot', 'depol']]
        # return the two datasets merged back together
        return xr.merge((dt, sza))


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
        P.Mie_Database_Dir: 'Mie_Database',
        P.MIE_TABLE_CAL: 2,
        P.Aerosol_Model_Number: range(11, 21),
        P.AerosolFineModeFraction: np.nan,
        P.Relative_Humidity: [0.3, 0.5, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95],
        # wndspd will be calculated
        P.Wind_Speed: None,
        # SZA will be set to vary only when `Diffuse_Transmittance_Flag == 0`
        P.Solar_Zenith_Angle: range(0, 90, 2),
        P.Tau_NIR: [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5],
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

    # replace independent sza and dt dimensions with a new index
    dim = {
        'sza-dt': (
            P.Solar_Zenith_Angle.__name__,
            P.Diffuse_Transmittance_Flag.__name__,
            ),
    }
    dataset = dataset.stack(dimensions=dim, create_index=False)
    dataset = (
        dataset.where(
            ~np.logical_and(
                dataset[P.Diffuse_Transmittance_Flag.__name__] == 1,
                dataset[P.Solar_Zenith_Angle.__name__] != 0.0,
                ),
            drop=True,
            )
        )
    dataset['sza-dt'] = dataset.get_index('sza-dt')

    # combine Aerosol_Model_Number and Relative_Humidity into one index
    dim = {
        'am': (
            P.Aerosol_Model_Number.__name__,
            P.Relative_Humidity.__name__,
            )
    }
    dataset = dataset.stack(dimensions=dim, create_index=False)
    dataset['am'] = dataset.get_index('am')

    # run command line tool
    ac_lut = AC_LUT(
        program='rtsos_GSFC_AC_LUT.exe',
        params=tuple(values),
        defaults=dataset,
        )
    ac_lut(args)
