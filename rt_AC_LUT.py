import numpy as np
import xarray as xr

from .kit import cli, ZhaiRT
from .parameters import Parameters as P
from .parameters import SZ, DT


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
    values[P.Wave_Mean_Square_Slope] = wmss

    # create a dataset to hold the inputs as coordinates
    params = P()
    dataset = params.make_dataset(values)

    # replace independent sza and dt dimensions with a single index, so we
    # only run simulations over sza for dt == 0.
    dim = {"sza-dt": (SZ, DT)}
    dataset = dataset.stack(dim=dim, create_index=False)
    dataset = dataset.where(
        np.logical_or(dataset[DT] == 0, dataset[SZ] == 0.0),
        drop=True,
    )
    dataset["sza-dt"] = dataset.get_index("sza-dt")

    # the callable object that runs the given program
    values.pop(P.Wave_Mean_Square_Slope)
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
    dimension and limit outputs
    """

    def post(self, dataset: xr.Dataset) -> xr.Dataset:
        # replace am and sza-dt coordinates with model parameters
        # TODO drop unneeded coordinates range in FORTRAN
        dataset = dataset.sel({"ThetaV": slice(0, 90)})
        # TODO drop unneeded dimension in FORTRAN
        dataset = dataset.drop_dims("Altitude")
        # split the flag for diffuse transmittance into separate datasets
        dataset = dataset.set_index({"sza-dt": [SZ, DT]})
        td = dataset.sel({DT: 1}).squeeze(SZ).reset_coords(drop=True)
        dataset = dataset.sel({DT: 0}).drop_vars(DT)
        # calculate ratios and aggregrates
        variable = []
        variable.append("diffuse_transmittance")
        dataset[variable[-1]] = td["Radiance_TOA"] / td["Radiance_BOA"]
        dataset[variable[-1]].attrs.update(
            {
                "long_name": "Diffuse Transmittance",
            }
        )
        variable.append("aerosol_optical_thickness")
        dataset[variable[-1]] = dataset["Tau_Aerosol_Extinction"].sum("NTLYERA")
        dataset[variable[-1]].attrs.update(
            {
                "long_name": "Aerosol Optical Thickness",
                "units": "unitless",
            }
        )
        # FIXME rot has Tau_NIR dim in Amir's code, but not here
        variable.append("rayleigh_optical_thickness")
        dataset[variable[-1]] = dataset["Tau_Rayleigh_Extinction"].sum("NTLYERA")
        dataset[variable[-1]].attrs.update(
            {
                "long_name": "Rayleigh Optical Thickness",
                "units": "unitless",
            }
        )
        variable.append("depolarization")
        dataset[variable[-1]] = dataset["Rayleigh_Depolarization_Ratio"].mean("NTLYERA")
        dataset[variable[-1]].attrs.update(
            {
                "long_name": "Rayleigh Depolarization Factor",
                "units": "unitless",
            }
        )
        # limit the outputs
        variable = [
            "Radiance_TOA",
            "Radiance_TOA_Glint",
            "Q_TOA",
            "Q_TOA_Glint",
            "U_TOA",
            "U_TOA_Glint",
            "Irrad_Down_TOA",
            *variable,
            *dataset.coords,
        ]
        return dataset[variable]
