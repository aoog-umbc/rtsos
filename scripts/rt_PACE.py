from .kit import cli, ZhaiRT
from .parameters import Parameters as P


def main(argv: str = None) -> None:
    # parse command line arguments
    args = cli.parse_args(argv)

    # values to write, in the order below, to the RT input file
    values = {
        P.aux_dir: 'data/RT/pwzrt/Data',
        P.gas_abs_coef_dir: 'data/RT/pwzrt/Gas_Absorption_Coefficients',
        P.mie_database_dir: 'data/RT/pwzrt/Mie_Database/OCI_Mie_Database',
        P.wndspd: 5.0,
        P.theta0: 45.0,
        P.wv_pace_ref: 873.0,
        P.tau_ref: 0.1,
        P.height_particle: 6.0,
        P.aerosol: -1,
        P.AerosolFineModeFraction: 0.3,
        P.Relative_Humidity: 0.3,
        P.OCEAN_CASE_SELECT: 1,
        P.albedo_ground: 0.3,
        P.water_depth_max: 200.0,
        P.chla: 0.01,
        P.phytoplankton_index_refraction: 1.02,
        P.phytoplankton_spectral_slope: 3.0,
        P.sediment_index_refraction: 1.2,
        P.sediment_spectral_slope: 4.0,
        P.sediment_concentration: 0.0,
        P.adg440: 1.0,
        P.bbp660_BackscatterCoeff: 0.05,
        P.Bp660_BackscatterFraction: 0.01,
        P.Sdg: 0.015,
        P.Sbp: 0.3,
        P.S_Bp: 0.01,
        P.ncolinput: 40,
        P.nquadainput: 40,
        P.nquadoinput: 60,
        P.MAXMORDINPUT: 40,
        P.NTHETAV: 36,
        P.NPHIV: 19,
        P.CHLA_HOMOGENEITY: 1,
        P.OCEAN_RAMAN_FLAG: 1,
        P.OCEAN_FCHLA_FLAG: 1,
        P.OCEAN_FCDOM_FLAG: 1,
        P.ap_select: 1,
        P.MONOCHROMATIC_FLAG: 0,
        P.hyspectral_flag: 0,
        P.NonPhotochemicalQuenching_FLAG: 0,
        P.OCEAN_PHMX_ONE: 1,
        P.ATMOS_ZERO: 0,
        P.SUN_GLINT_FLAG: 0,
        P.gas_abs_flag: 1,
        P.OZONE_COLUMN_DobsonUnit: 345.66,
        P.H2O_COLUMN: 1.4387,
        P.NO2_COLUMN_DobsonUnit: 0.2075,
        P.Pressure_Surface_mb: 1013.0,
        P.WAVEBAND_SEG_FLAG: 0,
        P.AirSensor_Height: 2.2,
        P.pss_flag: 0,
        P.atmos_profile: 'afglus.dat',
        # for Aerosol Model "-1", there is no aerosol_phasematrix_file
        P.aerosol_phasematrix_file: '',
        }

    # create a dataset to hold the inputs as coordinates
    params = P()
    dataset = params.to_dataset(values)

    # run command line tool
    rt = ZhaiRT(
        'rtsos_PACE_Simulator_DoubleK.exe',
        params=tuple(values),
        defaults=dataset,
        dims={
            # TODO confirm 'WaveLength_Simulation' over 'WaveLength_PACE'
            # TODO do these change with parameters?
            'phony_dim_1': 'WaveLength_Simulation',
            'phony_dim_2': 'Atmosphere_Layer_Altitudes',
            'phony_dim_3': 'WATER_DEPTH_LEVELS',
            'phony_dim_4': 'dim_4',
            'phony_dim_5': 'PhiV',
            'phony_dim_6': 'dim_6',
            'phony_dim_7': 'Stokes_Component',
            'phony_dim_8': 'ThetaV',
            },
        )
    rt.execute(args)
