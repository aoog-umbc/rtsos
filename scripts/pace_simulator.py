from .kit import cli, ZhaiRT
from .parameters import Parameters as P


def main(argv=None):
    # parse command line arguments
    args = cli.parse_args(argv)

    # values to write, in the order below, to the RT input file
    values = {
        P.aux_dir: 'data/RT/pwzrt/Data',
        P.gas_abs_coef_dir: 'data/RT/pwzrt/Gas_Absorption_Coefficients',
        P.mie_database_dir: 'data/RT/pwzrt/Mie_Database/OCI_Mie_Database',
        P.wndspd: 5.0,
        P.theta0: [45.0, 85.0],
        P.wv_pace_ref: 873.0,
        P.tau_ref: [0.1, 0.4],
        P.height_particle: 3.0,
        P.aerosol: [-1, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
        P.aerofmf: 0.3,
        P.RH: [0.30, 0.50, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95],
        P.ocean_case_select: 0,
        P.albedo_ground: 0.3,
        P.water_depth_max: 200.0,
        P.chla: [0.01, 0.03, 0.1, 0.3, 1.0, 3, 10, 30],
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
        P.MAXMORDINPUT: 20,
        P.NTHETAV: 36,
        P.NPHIV: 19,
        P.chla_homogeneity: 1,
        P.ocean_raman_flag: 1,
        P.ocean_fchla_flag: 1,
        P.ocean_fcdom_flag: 1,
        P.ap_select: 1,
        P.monochromatic_flag: 0,
        P.hyspectral_flag: 0,
        P.npq_flag: 0,
        P.ocean_phmx_one: 1,
        P.atmos_zero: 0,
        P.SUNGLINT_INPUT: 0,
        P.gas_abs_flag: 1,
        P.OZONE_COLUMN: 345.66,
        P.H2O_COLUMN: 1.4387,
        P.NO2_COLUMN: 0.2075,
        P.pressure_surface: 1013.0,
        P.wv_seg_flag: 0,
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
        phony_dims={
            # TODO confirm 'Wavelength_Simulation' over 'Wavelength_PACE'
            'phony_dim_1': 'Wavelength_Simulation',
            'phony_dim_4': 'PhiV',
            'phony_dim_6': 'Stokes_Vector',
            'phony_dim_7': 'ThetaV',
            },
        )
    return rt.execute(args)
    # TODO
    # phony_dim_1 wavelength
    # phony_dim_2 atmospheric levels
    # phony_dim_3 water dept levels
    # phony_dim_5
    # phony_dim_6 stokes components
