import numpy as np
import xarray as xr

from .kit import cli, ZhaiRT
from .parameters import Parameters as P
from .parameters import AM, RH, WI, SZ, DT


def main(argv=None):
    """Entry point for rt-AC-LUT command line tool"""

    # values to write, in the order below, to the RT input file
    # NWV should come from CFILE_INSTRUMENT (but is not enforced to allow a fast path)
    # Wind_Speed will be calculated from Wave_Mean_Square_Slope (which becomes an aux coord)
    # SZA will be set to vary only when `Diffuse_Transmittance_Flag == 0`
    values = {
        P.NWV: 0,
        P.WAVELENGTH_MICRON_REF: 0.870,
        P.CFILE_INSTRUMENT: "afinp.txt",
        P.Aux_Dir: "aux",
        P.Atmos_Dir: "atmos",
        P.Mie_Database_Dir: "",
        P.MIE_TABLE_CAL: 2,
        P.Aerosol_Model: range(11, 21),
        P.Aerosol_FMF: None,
        P.Relative_Humidity: [0.3, 0.5, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95],
        P.Wave_Mean_Square_Slope: [0, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4],
        P.Solar_Zenith_Angle: range(0, 90, 2),
        P.Tau_NIR: [0, 0.01, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5],
        P.Pressure_Surface_mb: 1013.0,
        P.H2O_COLUMN: 1.4387,
        P.OZONE_COLUMN_DobsonUnit: 345.66,
        P.iwhitecap: 0,
        P.I_SURFACE_ROUGHNESS_PARA: 2,
        P.Diffuse_Transmittance_Flag: [0, 1],
        P.I_SPHERICAL_SHELL_CORRECTION: 1,
        P.CFILE_AP: "afglus.dat",
    }

    # calculate rt coordinate Wind_Speed, taking the position of Wave_Mean_Square_Slope
    surface = values[P.I_SURFACE_ROUGHNESS_PARA]
    wmss = values[P.Wave_Mean_Square_Slope]
    if surface == 1:
        wndspd = (np.square(wmss) - 0.003) / 0.00512
    elif surface == 2:
        wndspd = np.square(wmss) / 0.00534
    wndspd[wndspd < 0.0] = 0.0
    values = {
        P.Wind_Speed if k == P.Wave_Mean_Square_Slope else k: v
        for k, v in values.items()
    }
    values[P.Wind_Speed] = wndspd

    # create a dataset to hold the inputs as coordinates
    params = P()
    values[P.Wave_Mean_Square_Slope] = wmss
    dataset = params.make_dataset(values)
    values.pop(P.Wave_Mean_Square_Slope)

    # replace independent sza and dt dimensions with a single index, so we
    # only run simulations over sza for dt == 0.
    dim = {"sza-dt": (SZ, DT)}
    dataset = dataset.stack(dimensions=dim, create_index=False)
    dataset = dataset.where(
        ~np.logical_and(dataset[DT] == 1, dataset[SZ] != 0.0),
        drop=True,
    )
    dataset["sza-dt"] = dataset.get_index("sza-dt")

    # the callable object that runs the given program
    prog = AC_LUT(
        program="rtsos_GSFC_AC_LUT.exe",
        defaults=dataset,
        params=tuple(values),
    )

    # parse arguments from command line and run as instructed
    args = cli.parse_args(argv)
    prog(args)


class AC_LUT(ZhaiRT):
    """Class that drives rt-AC-LUT, having a `post` method to normalize the compound
    dimensions
    """

    def post(self, dataset: xr.Dataset) -> xr.Dataset:
        # replace am and sza-dt coordinates with model parameters
        # TODO move as much of the renaming/slicing to ac-luts as possible
        # drop unneeded coordinates
        dataset = dataset.sel({"ThetaV": slice(0, 90)})
        dataset = dataset.drop_dims("Altitude")
        # unstack the sza-dt dimension into separate datasets
        diffuse = dataset[DT] == 1
        dt = (
            dataset.sel({"sza-dt": diffuse}).squeeze("sza-dt").drop_vars([DT, "sza-dt"])
        )
        rename = {
            "Radiance_TOA": "LT_TOA",
            "Radiance_BOA": "LT_BOA",
        }
        dt = dt.rename(rename)[list(rename.values())]
        sza = (
            dataset.sel({"sza-dt": ~diffuse})
            .swap_dims({"sza-dt": SZ})
            .drop_vars([DT, "sza-dt"])
        )
        # calculate aggregrates, ignoring dimensions known to have no effect
        sza["aot"] = sza["Tau_Aerosol_Extinction"].sum("NTLYERA")
        sza["aot"].attrs.update(
            {
                "long_name": "Optical Thickness",
                "units": "unitless",
            }
        )
        # FIXME rot has Tau_NIR dim in Amir's code, but not here
        sza["rot"] = sza["Tau_Rayleigh_Extinction"].sum("NTLYERA")
        sza["rot"].attrs.update(
            {
                "long_name": "Optical Thickness",
                "units": "unitless",
            }
        )
        sza["depol"] = sza["Rayleigh_Depolarization_Ratio"].mean("NTLYERA")
        sza["depol"].attrs.update(
            {
                "long_name": "Depolarization Factor",
                "units": "unitless",
            }
        )
        rename = {
            "Radiance_TOA": "Lt",
            "Q_TOA": "LQ",
            "U_TOA": "LU",
            "Radiance_TOA_Glint": "TLg",
            "Q_TOA_Glint": "TQg",
            "U_TOA_Glint": "TUg",
            "Irrad_Down_TOA": "diff_irrad",
        }
        sza = sza.rename(rename)
        sza = sza[list(rename.values()) + ["aot", "rot", "depol"]]
        # merge the sza and dt datasets back together
        coords = dataset.drop_dims("sza-dt").coords
        dataset = xr.merge((coords, dt, sza))
        return dataset
