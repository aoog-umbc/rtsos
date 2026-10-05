from .core import cli, ZhaiRT
from .parameters import Parameters as P


def main(argv: str = None) -> None:
    # values to write, in the order below, to the input file
    values = {
        P.Wind_Speed: 5.0,
        P.Solar_Zenith_Angle: [20.0, 60.0],
        P.wv_pace_ref: 532.0,
        P.tau_ref_hi: [0.1, 0.3],
        P.height_particle_hi: 15.0,
        P.height_particle_variance_hi: 2.0,
        P.tau_ref_low: 0.0,
        P.height_particle_low: -1,
        P.height_particle_variance_low: -1,
        P.Aerosol_Model: -1,
        P.Aerosol_FMF: 0.3,
        P.Relative_Humidity: 0.3,
        P.OCEAN_CASE_SELECT: 1,
        P.albedo_ground: 0.3,
        P.water_depth_max: 200.0,
        P.chla: [0.03, 0.3, 3, 10, 30],
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
        P.Aux_Dir: "Auxiliary_Files",
        P.Atmos_Dir: "Gas_Absorption_Coefficients",
        P.CFILE_AP: "afglus.dat",
        P.Aerosol_Phasematrix_File_Hi: "",
        P.Aerosol_Phasematrix_File_Low: "",
    }

    # create a dataset to hold the inputs as coordinates
    params = P()
    dataset = params.make_dataset(values)

    # the callable object that runs the given program
    prog = ZhaiRT(
        program="rtsos_PACE_Simulator_DoubleK",
        defaults=dataset,
        params=tuple(values),
    )

    # parse arguments from command line and run as instructed
    args = cli.parse_args(argv)
    prog(args)
