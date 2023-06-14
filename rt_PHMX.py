import xarray as xr

from .kit import cli, ZhaiRT
from .parameters import Parameters as P


def main(argv: str = None) -> None:
    # values to write, in the order below, to the RT input file
    # nb. not all parameters are used, but the order remains correct and
    # leaving any out could break custom inputs
    params = {
        P.Aerosol_Model_Number: -98,
        P.IRH: 4,
        P.Reff_Cloud: 6.0,
        P.Veff_Cloud: 0.1,
        P.nmode: 2,
        P.fmfrac: 1.0,
        P.dust_frac: 1.0,
        P.ds_frac: 1.0,
        P.cmsfracs: 0.0,
        P.rf1: 0.0,
        P.rf2: 0.0,
        P.rf3: 1.0,
        P.Aerosol_Mixing_Flag: 2,
        P.dust_ivar: 2,
        P.dust_ireff: 15,
        P.Relative_Humidity: 0.6,
        P.r0f: 0.15,
        P.r0c: 2.0194,
        P.sigf: 0.806,
        P.sigc: 0.672,
        P.r0_dl: 0.2,
        P.r0_ws: 0.15,
        P.r0_bc: 0.3,
        P.r0_s: 0.05,
        P.r0_ss: 2.0194,
        P.WAVEBAND_SEG_FLAG: 0,
    }

    # create a dataset to hold the inputs as coordinates
    dataset = P.make_dataset(params)
    aersol_model = dataset[P.Aerosol_Model_Number.__name__]
    if aersol_model > 0:
        unused_params = (
            P.Reff_Cloud,
            P.Veff_Cloud,
            P.nmode,
            P.fmfrac,
            P.dust_frac,
            P.ds_frac,
            P.cmsfracs,
            P.rf1,
            P.rf2,
            P.rf3,
            P.Aerosol_Mixing_Flag,
            P.dust_ivar,
            P.dust_ireff,
            P.Relative_Humidity,
            P.r0f,
            P.r0c,
            P.sigf,
            P.sigc,
            P.r0_dl,
            P.r0_ws,
            P.r0_bc,
            P.r0_s,
            P.r0_ss,
        )
    elif aersol_model == -98:
        unused_params = (
            P.IRH,
            P.nmode,
            P.fmfrac,
            P.dust_frac,
            P.ds_frac,
            P.cmsfracs,
            P.rf1,
            P.rf2,
            P.rf3,
            P.Aerosol_Mixing_Flag,
            P.dust_ivar,
            P.dust_ireff,
            P.Relative_Humidity,
            P.r0f,
            P.r0c,
            P.sigf,
            P.sigc,
            P.r0_dl,
            P.r0_ws,
            P.r0_bc,
            P.r0_s,
            P.r0_ss,
        )
    else:  # aersol_model == -99
        nmode = dataset[P.nmode.__name__]
        if nmode == 2:
            unused_params = (
                P.IRH,
                P.Reff_Cloud,
                P.Veff_Cloud,
                P.dust_frac,
                P.ds_frac,
            )
        else:  # nmode == 3
            unused_params = (
                P.IRH,
                P.Reff_Cloud,
                P.Veff_Cloud,
                P.cmsfracs,
                P.rf1,
            )
    dataset = dataset.drop_vars(tuple(i.__name__ for i in unused_params))

    # the callable object that runs the given program
    ac_pm = ZhaiRT(
        program="rtsos_Aerosol_Phmx_Cal.exe",
        params=tuple(params),
        defaults=dataset,
    )

    # parse arguments from command line interface and run as instructed
    args = cli.parse_args(argv)
    ac_pm(args)
