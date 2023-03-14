import numpy as np
import xarray as xr

from .kit import cli, ZhaiRT
from .parameters import Parameters as P


def lstsq(a, b):
    return np.linalg.lstsq(a, b, rcond=None)[0]


class AC_LUT(ZhaiRT):

    def post(self, dataset):
        # drop unneeded coordinates
        dataset = dataset.where(dataset['ThetaV'] < 90.0, drop=True)
        # restore the coordinates stacked in am
        dataset = dataset.squeeze('am').drop_vars('am')
        # unstack the sza-dt dimension into separate datasets
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
        # calculate aggregrates, ignoring dimensions known to have no effect
        # TODO this na thing suggests prior unnecessary broadcasting
        na = {
            P.Wind_Speed.__name__: 0,
            P.Solar_Zenith_Angle.__name__: 0,
            'ThetaV': 0,
            }
        sza['aot'] = sza['Tau_Aerosol_Extinction'][na].sum('NTLYERA')
        sza['rot'] = sza['Tau_Rayleigh_Extinction'][na].sum('NTLYERA')
        sza['depol'] = sza['Rayleigh_Depolarization_Ratio'][na].mean('NTLYERA')
        # finish calculations on the sza dataset
        sza = sza[list(renamed.values()) + ['aot', 'rot', 'depol']]
        # merge the sza and dt datasets back together
        dataset = xr.merge((dt, sza))
        # calculate LUTs
        # select aot == 0 which means Rayleigh only atmosphere
        ds = dataset.loc[{'Tau_NIR': 0}]
        # calculate rhot with TOA glint removed
        rhot = np.pi * ds['Lt'] / ds['diff_irrad']
        Trhog = np.pi * ds['TLg'] / ds['diff_irrad']
        rhor = rhot - Trhog
        # TODO comment on this part
        ds = dataset[{'Tau_NIR': dataset['Tau_NIR'] > 0}]
        rhot_all = np.pi * ds['Lt'] / ds['diff_irrad']
        Trhog_all = np.pi * ds['TLg'] / ds['diff_irrad']
        rhoa = rhot_all - rhor - Trhog_all
        rhoa = rhoa.loc[{'Wind_Speed': 0}]
        # for each wavelength and for each geometry, fit least squares
        # for rhoa over Tau_NIR
        a = xr.DataArray(np.arange(5, dtype=np.float32), dims='N')
        a = np.log(ds['aot']) ** a
        a = a.where(np.logical_or(a['WaveLength'] < 0.8, a['N'] < 3), 0.0)
        a.load() # TODO dask='allowed'
        b = np.log(rhoa.stack({'K': ['ThetaV', 'PhiV', 'Solar_Zenith_Angle']}))
        b.load() # TODO dask='allowed'
        x = xr.apply_ufunc(
            lstsq, # solves b = a @ x for x
            a,     # a.dims == ('Tau_NIR', 'WaveLength', 'N')
            b,     # b.dims == ('Tau_NIR', 'WaveLength', 'K')
            input_core_dims=[['Tau_NIR', 'N'], ['Tau_NIR', 'K']],
            output_core_dims=[['N', 'K']],
            vectorize=True,
            # TODO dask='allowed'
            )
        rhoa_coef = (
            x.unstack()
            .assign_coords({'N': [f'{i}ms_all' for i in 'abcde']})
            .to_dataset('N')
            )
        # arbitrary choice of PhiV index (no effect on td)
        ds = dataset[{'Wind_Speed': 0, 'PhiV': 10}]
        td = ds['LT_TOA'] / ds['LT_BOA']
        a = ds['aot'] ** xr.DataArray(np.arange(2, dtype=np.float32), dims='N')
        a.load()
        b = np.log(td)
        b.load()
        x = xr.apply_ufunc(
            lstsq, # solves b = a @ x for x
            a,     # a.dims == ('Tau_NIR', 'WaveLength', 'N')
            b,     # b.dims == ('Tau_NIR', 'ThetaV', 'WaveLength')
            input_core_dims=[['Tau_NIR', 'N'], ['Tau_NIR', 'ThetaV']],
            output_core_dims=[['N', 'ThetaV']],
            vectorize=True,
            )
        td_coef = (
            x.assign_coords({'N': ['dtran_a', 'dtran_b']})
            .to_dataset(dim='N')
        )
        td_coef['dtran_a'] = np.exp(td_coef['dtran_a'])
        td_coef['dtran_b'] = -td_coef['dtran_b']
        # TODO comment next section
        ds = dataset[{'Tau_NIR': 1}]
        ref = ds['WAVELENGTH_MICRON_REF']
        # FIXME ref is not in WaveLength?
        extc = ds['aot'] / ds['aot'].sel({'WaveLength': ref}, method='nearest')
        # FIXME dtype float32
        ds = (
            xr.merge((rhoa_coef, td_coef, extc))
            .rename({
                'WaveLength': 'wave',
                'Solar_Zenith_Angle': 'solz',
                'PhiV': 'phi',
                'ThetaV': 'senz',
                })
            .transpose('wave', 'solz', 'phi', 'senz')
            )
        return ds
            # FIXME add these metadata
            # attrs={
            #     'AerosolFMF': int(fmf[imdl]),     # ?
            #     'Size Distribution': sd[imdl],    # ?
            #     }


def main(argv=None):

    # parse command line arguments
    args = cli.parse_args(argv)

    # values to write, in the order below, to the RT input file
    values = {
        # the default parameterization is for PACE-OCI
        P.NWV: 239,
        P.WAVELENGTH_MICRON_REF: 0.870,
        P.CFILE_INSTRUMENT: 'coeff_abs.dat',
        P.Aux_Dir: 'data/RT/bfranz/afrt/oci/inp',
        P.Atmos_Dir: 'data/RT/pwzrt/Gas_Absorption_Coefficients',
        P.Mie_Database_Dir: 'data/oci/mie',
        P.MIE_TABLE_CAL: 2,
        P.Aerosol_Model_Number: range(11, 21),
        P.AerosolFineModeFraction: np.nan,
        P.Relative_Humidity: [0.3, 0.5, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95],
        # wind speed will be calculated
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
        P.CFILE_AP: 'afglus.dat', # FIXME change the file name
        }

    # calculate compound coordinate wndspd
    sigma = np.array(
        [0, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4],
        dtype=np.float32
        )
    surface = values[P.I_SURFACE_ROUGHNESS_PARA]
    if surface == 1:
        wndspd = (np.square(sigma) - 0.003) / 0.00512
    elif surface == 2:
        wndspd = np.square(sigma) / 0.00534
    wndspd[wndspd<0.0] = 0.0
    values[P.Wind_Speed] = wndspd

    # create a dataset to hold the inputs as coordinates
    params = P()
    dataset = params.to_dataset(values)

    # replace independent sza and dt dimensions with a single index, so we
    # only run simulations over sza for dt == 0.
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

    # run RT model over parameters as specified in command line arguments
    ac_lut = AC_LUT(
        program='rtsos_GSFC_AC_LUT.exe',
        params=tuple(values),
        defaults=dataset,
        )
    ac_lut(args)
