from datetime import datetime, timezone
import importlib

import numpy as np
import xarray as xr

from .kit import cli, ZhaiRT
from .parameters import Parameters as P


def main(argv=None):
    # values to write, in the order below, to the RT input file
    values = {
        # derive wavelength from CFILE_INSTRUMENT (nb.: not enforced to allow fast-path)
        P.NWV: 0,
        P.WAVELENGTH_MICRON_REF: 0.870,
        P.CFILE_INSTRUMENT: "",
        P.Aux_Dir: "",
        P.Atmos_Dir: "",
        P.Mie_Database_Dir: "",
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
        P.CFILE_AP: "afglus.dat",  # FIXME change the file name
    }

    # calculate compound coordinate wndspd
    sigma = np.array(
        [0, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4],
        dtype=np.float32,
    )
    surface = values[P.I_SURFACE_ROUGHNESS_PARA]
    if surface == 1:
        wndspd = (np.square(sigma) - 0.003) / 0.00512
    elif surface == 2:
        wndspd = np.square(sigma) / 0.00534
    wndspd[wndspd < 0.0] = 0.0
    values[P.Wind_Speed] = wndspd

    # create a dataset to hold the inputs as coordinates
    params = P()
    dataset = params.make_dataset(values)

    # replace independent sza and dt dimensions with a single index, so we
    # only run simulations over sza for dt == 0.
    dim = {
        "sza-dt": (
            P.Solar_Zenith_Angle.__name__,
            P.Diffuse_Transmittance_Flag.__name__,
        ),
    }
    dataset = dataset.stack(dimensions=dim, create_index=False)
    dataset = dataset.where(
        ~np.logical_and(
            dataset[P.Diffuse_Transmittance_Flag.__name__] == 1,
            dataset[P.Solar_Zenith_Angle.__name__] != 0.0,
        ),
        drop=True,
    )
    dataset["sza-dt"] = dataset.get_index("sza-dt")

    # combine Aerosol_Model_Number and Relative_Humidity into one index
    dim = {
        "am": (
            P.Aerosol_Model_Number.__name__,
            P.Relative_Humidity.__name__,
        )
    }
    dataset = dataset.stack(dimensions=dim, create_index=False)
    dataset["am"] = dataset.get_index("am")

    # the callable object that runs the given program
    ac_lut = AC_LUT(
        program="rtsos_GSFC_AC_LUT.exe",
        params=tuple(values),
        defaults=dataset,
    )

    # parse arguments from command line and run as instructed
    args = cli.parse_args(argv)
    ac_lut(args)


class AC_LUT(ZhaiRT):

    def obdaac_metadata(
        self, dataset: xr.Dataset, rayleigh=False
    ) -> xr.Dataset:  # FIXME one file is both
        dataset.attrs.update(
            {
                "title": "Atmospheric Rayleigh radiance table for OCIS at #### nm",  # FIXME
                "version": importlib.metadata.version(__name__.split(".", 1)[0]),
                "comment": "Coefficients for polynomial interpolation of TOA radiances.",  # FIXME
                "date_created": datetime.now(timezone.utc).isoformat(),
                "history": ",".join(
                    "rt-AC-LUT --cluster=<cluster> <inputs> <outputs>",
                    "rt-AC-LUT --post=<cluster> --cluster=am <inputs> <outputs>",
                ),
                "created_by": "NASA/GSFC/OBPG",
                "creator_name": "NASA/GSFC/OBPG",
                "creator_email": "data@oceancolor.gsfc.nasa.gov",
                "creator_url": "https://oceandata.sci.gsfc.nasa.gov",
                "project": "Ocean Biology Processing Group (NASA/GSFC/OBPG)",
                "publisher_name": "NASA/GSFC/OBPG",
                "publisher_url": "https://oceandata.sci.gsfc.nasa.gov",
                "publisher_email": "data@oceancolor.gsfc.nasa.gov",
                "institution": "NASA Goddard Space Flight Center, Ocean Ecology Laboratory, Ocean Biology Processing Group",
                "instrument": "OCI",
                "platform": "PACE",
                "license": "https://science.nasa.gov/earth-science/earth-science-data/data-information-policy/",
                "references": "",
            },
        )
        if not rayleigh:
            am = dataset["Aerosol_Model_Number"]
            am_flag_index = (am.attrs["flag_values"] == am).argsort()[-1]
            am_flag_meaning = am.attrs["flag_meanings"][am_flag_index.item()]
            dataset.attrs.update(
                {
                    "title": "Aerosol model data for OCIS",
                    "aerosol_model_number": str(am.item()),
                    "fine_mode_fraction": str(am_flag_meaning.split("_")[-1]),
                    "relative_humidity": dataset["Relative_Humidity"].values[0],
                    "size_distribution": str(),  # FIXME
                    "wind_sigma": float(),  # FIXME this one may need a better name...just not sure what that should be...or even if it is needed, since it's always zero...
                },
            )
        return dataset

    def restructure_outputs(self, dataset: xr.Dataset) -> xr.Dataset:
        # drop unneeded coordinates
        dataset = dataset.where(dataset["ThetaV"] < 90.0, drop=True)
        # restore the coordinates stacked in am
        dataset = dataset.squeeze("am").drop_vars("am")
        # unstack the sza-dt dimension into separate datasets
        idx = dataset[P.Diffuse_Transmittance_Flag.__name__] == 1
        renamed = {
            "Radiance_TOA": "LT_TOA",
            "Radiance_BOA": "LT_BOA",
        }
        dt = (
            dataset.sel({"sza-dt": idx})
            .squeeze("sza-dt")
            .rename(renamed)
            .drop_vars([P.Diffuse_Transmittance_Flag.__name__, "sza-dt"])
        )
        dt = dt[list(renamed.values())]
        renamed = {
            "Radiance_TOA": "Lt",
            "Q_TOA": "LQ",
            "U_TOA": "LU",
            "Radiance_TOA_Glint": "TLg",
            "Q_TOA_Glint": "TQg",
            "U_TOA_Glint": "TUg",
            "Irrad_Down_TOA": "diff_irrad",
        }
        sza = (
            dataset.sel({"sza-dt": ~idx})
            .swap_dims({"sza-dt": P.Solar_Zenith_Angle.__name__})
            .rename(renamed)
            .drop_vars([P.Diffuse_Transmittance_Flag.__name__, "sza-dt"])
        )
        # calculate aggregrates, ignoring dimensions known to have no effect
        # TODO this na thing suggests prior unnecessary broadcasting
        na = {
            P.Wind_Speed.__name__: 0,
            P.Solar_Zenith_Angle.__name__: 0,
            "ThetaV": 0,
        }
        sza["aot"] = sza["Tau_Aerosol_Extinction"][na].sum("NTLYERA")
        sza["rot"] = sza["Tau_Rayleigh_Extinction"][na].sum("NTLYERA")
        sza["depol"] = sza["Rayleigh_Depolarization_Ratio"][na].mean("NTLYERA")
        # finish calculations on the sza dataset
        sza = sza[list(renamed.values()) + ["aot", "rot", "depol"]]
        # merge the sza and dt datasets back together
        return xr.merge((dt, sza))


def lstsq(a, b):
    return np.linalg.lstsq(a, b, rcond=None)[0]
