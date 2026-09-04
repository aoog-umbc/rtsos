import numpy as np
import xarray as xr

from .core import cli, ZhaiRT
from .parameters import Parameters as P


def main(argv: str = None) -> None:
    # values to write to the default input file
    # nb. not all parameters are used and the order is set by PHMX.params
    values = {
        P.Aerosol_Model: -96,
        P.IRH: 4,
        P.Reff_Cloud: 0.2 * np.exp(2.5 * 0.47**2),
        P.Veff_Cloud: np.exp(0.47**2) - 1.0,
        P.Mr_Cloud: 1.45,
        P.Mi_Cloud: 0.0,
        P.nmode: 2,
        P.fmfrac: 1.0,
        P.dustfrac: 1.0,
        P.dsfrac: 1.0,
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
        P.Aux_Dir: "Auxiliary_Files",
    }

    # create a dataset to hold the inputs as coordinates
    params = P()
    dataset = params.make_dataset(values)

    # the callable object that runs the given program
    prog = PHMX(
        program="rtsos_Aerosol_Phmx_Cal",
        defaults=dataset,
    )

    # parse arguments from command line interface and run as instructed
    args = cli.parse_args(argv)
    prog(args)


class PHMX(ZhaiRT):
    """Class that drives rt-PHMX, having a `params.setter` method that takes aerosol
    model and number of modes into account
    """

    @ZhaiRT.params.setter
    def params(self, dataset: xr.DataArray) -> None:
        nmode = dataset[P.nmode.__name__].item()
        aerosol_model_number = dataset[P.Aerosol_Model.__name__]
        if aerosol_model_number > 0 and aerosol_model_number <= 20:
            _params = (
                P.Aerosol_Model,
                P.IRH,
                P.WAVEBAND_SEG_FLAG,
                P.Aux_Dir,
            )
        elif aerosol_model_number == -96:
            _params = (
                P.Aerosol_Model,
                P.Reff_Cloud,
                P.Veff_Cloud,
                P.Mr_Cloud,
                P.Mi_Cloud,
                P.WAVEBAND_SEG_FLAG,
                P.Aux_Dir,
            )
        elif aerosol_model_number == -98:
            _params = (
                P.Aerosol_Model,
                P.Reff_Cloud,
                P.Veff_Cloud,
                P.WAVEBAND_SEG_FLAG,
                P.Aux_Dir,
            )
        elif aerosol_model_number == -99:
            if nmode == 2:
                _params = (
                    P.Aerosol_Model,
                    P.nmode,
                    P.fmfrac,
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
                    P.WAVEBAND_SEG_FLAG,
                    P.Aux_Dir,
                )
            elif nmode == 3:
                _params = (
                    P.Aerosol_Model,
                    P.nmode,
                    P.fmfrac,
                    P.dustfrac,
                    P.dsfrac,
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
                    P.WAVEBAND_SEG_FLAG,
                    P.Aux_Dir,
                )
        self._params = (i.__name__ for i in _params)
