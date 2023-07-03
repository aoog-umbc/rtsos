from datetime import datetime, timezone
from importlib.metadata import version
from re import findall

import numpy as np
import xarray as xr

from .kit import cli, ZhaiRT
from .parameters import Parameters as P


cli.add_argument(
    "--rename",
    type=str,
    default="",
    help="name for the post-processes outputs",
)
AM = P.Aerosol_Model.__name__
RH = P.Relative_Humidity.__name__
WI = P.Wind_Speed.__name__
TN = P.Tau_NIR.__name__
SZ = P.Solar_Zenith_Angle.__name__
DT = P.Diffuse_Transmittance_Flag.__name__
WA = P.Wave_Mean_Square_Slope.__name__


def main(argv=None):
    """Entry point for rt-AC-LUT command line tool"""

    # values to write, in the order below, to the RT input file
    # NWV should come from CFILE_INSTRUMENT (but is not enforced to allow a fast path)
    # Wind_Speed will be calculated from Wave_Mean_Square_Slope (which becomes an aux coord)
    # SZA will be set to vary only when `Diffuse_Transmittance_Flag == 0`
    values = {
        P.NWV: 0,
        P.WAVELENGTH_MICRON_REF: 0.870,
        P.CFILE_INSTRUMENT: "",
        P.Aux_Dir: "",
        P.Atmos_Dir: "",
        P.Mie_Database_Dir: "",
        P.MIE_TABLE_CAL: 2,
        P.Aerosol_Model: range(11, 21),
        P.Aerosol_FMF: None,
        P.Relative_Humidity: [0.3, 0.5, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95],
        P.Wave_Mean_Square_Slope: [0, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4],
        P.Solar_Zenith_Angle: range(0, 90, 2),
        P.Tau_NIR: [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5],
        P.Pressure_Surface_mb: 1013.0,
        P.H2O_COLUMN: 1.4387,
        P.OZONE_COLUMN_DobsonUnit: 345.66,
        P.iwhitecap: 0,
        P.I_SURFACE_ROUGHNESS_PARA: 2,
        P.Diffuse_Transmittance_Flag: [0, 1],
        P.I_SPHERICAL_SHELL_CORRECTION: 0,
        P.CFILE_AP: "afglus.dat",  # FIXME change the file name
    }

    # calculate rt coordinate Wind_Speed, taking the position of Wave_Mean_Square_Slope
    surface = values[P.I_SURFACE_ROUGHNESS_PARA]
    mss = values[P.Wave_Mean_Square_Slope]
    if surface == 1:
        wndspd = (np.square(mss) - 0.003) / 0.00512
    elif surface == 2:
        wndspd = np.square(mss) / 0.00534
    wndspd[wndspd < 0.0] = 0.0
    values = {
        P.Wind_Speed if k == P.Wave_Mean_Square_Slope else k: v
        for k, v in values.items()
    }
    values[P.Wind_Speed] = wndspd
    values[P.Wave_Mean_Square_Slope] = mss

    # create a dataset to hold the inputs as coordinates
    params = P()
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

    # combine Aerosol_Model and Relative_Humidity into one index
    # TODO could be unncessary with --rename
    dim = {"am": (AM, RH)}
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
    """Class that drives rt-AC-LUT and includes post-processing to calculate
    coeficients appearing in the atmospheric correction look-up-tables.
    """

    def post(self, dataset: xr.Dataset, rename: str) -> xr.Dataset:
        # instrument string from --rename argument
        inst = rename.split("_", 2)[1]
        # prepare for LUT calcultions
        dataset = unpack_outputs(dataset)
        # calculate aerosol LUT coefficients and return
        if rename.startswith("aerosol"):
            dataset = aerosol_mseps(dataset)
            # metadata to l2gen conventions
            dataset = for_l2gen(dataset, inst)
            try:
                coords = {i: dataset.attrs[i] for i in findall(r"{([^:]*).*?}", rename)}
                rh = coords["relative_humidity"]
                coords["relative_humidity"] = int(np.round(rh * 100))
            except KeyError as error:
                error.add_note(
                    f"\tThe model output does not have an attribute named {error}."
                )
                raise
            outputs = {rename.format(**coords): dataset}
        # calculate rayleigh LUT coefficients and return
        if rename.startswith("rayleigh"):
            dataset = rayleigh_mseps(dataset)
            # metadata to l2gen conventions
            outputs = {
                rename.format(wave=int(np.round(k * 1e3))): for_l2gen(v, inst, True)
                for k, v in dataset.groupby("wave")
            }
        return outputs


def aerosol_mseps(dataset: xr.Dataset) -> xr.Dataset:
    # no wind speed consideration for aerosol LUTs
    dataset = dataset.sel({WI: 0})

    # calculate rho with direct glint at TOA removed
    rhot = np.pi * (dataset["Lt"] - dataset["TLg"]) / dataset["diff_irrad"]
    # calculate rhoa with Rayleigh removed (Tau_NIR==0 is Rayleigh only atmosphere)
    rhoa = rhot.isel({TN: slice(1, None)}) - rhot.isel({TN: 0})
    # coefficient inference by polynomial least squares for each wavelength
    # predict rhoa(tau) from (log aot(tau)) ** n
    ds = dataset.isel({TN: slice(1, None)})
    a = np.log(ds["aot"]) ** xr.DataArray(np.arange(5), dims="N")
    a = a.where(np.logical_or(a["WaveLength"] <= 0.8, a["N"] <= 2), 0.0)
    b = np.log(rhoa).stack({"M": ["PhiV", "ThetaV", SZ]})
    x = xr.apply_ufunc(
        lstsq,  # solves a @ x = b for x
        a.load(),  # a.dims are Tau_NIR, WaveLength, N
        b.load(),  # b.dims are Tau_NIR, WaveLength, M
        input_core_dims=[(TN, "N"), (TN, "M")],
        output_core_dims=[("N", "M")],
        vectorize=True,  # over 'WaveLength' dimension
        # TODO dask='allowed'
    )
    # TODO xarray bug skipping attrs?
    x[AM].attrs.update(b[AM].attrs)
    rhoa_coef = (
        x.unstack()
        .assign_coords({"N": [f"{i}ms_all" for i in "abcde"]})
        .to_dataset("N")
    )

    # predict td(tau) from aot(tau) ** n
    # arbitrary choice of PhiV index (no effect on td)
    ds = dataset.isel({"PhiV": 10})
    a = ds["aot"] ** xr.DataArray(np.arange(2), dims="N")
    b = np.log(ds["LT_TOA"] / ds["LT_BOA"])
    x = xr.apply_ufunc(
        lstsq,  # solves b = a @ x for x
        a.load(),  # a.dims are Tau_NIR, WaveLength, N
        b.load(),  # b.dims are Tau_NIR, ThetaV, WaveLength
        input_core_dims=[(TN, "N"), (TN, "ThetaV")],
        output_core_dims=[("N", "ThetaV")],
        vectorize=True,
    )
    td_coef = x.assign_coords({"N": ["dtran_a", "dtran_b"]}).to_dataset(dim="N")
    td_coef["dtran_a"] = np.exp(td_coef["dtran_a"])
    td_coef["dtran_b"] = -td_coef["dtran_b"]
    base_band = dataset[P.WAVELENGTH_MICRON_REF.__name__].item()
    ds = dataset.isel({TN: 1}, drop=True)
    extc = ds["aot"] / ds["aot"].sel({"WaveLength": base_band}, method="nearest")
    extc.name = "extc"

    # combine coef arrays
    ds = (
        xr.merge((rhoa_coef, td_coef, extc))
        .rename(
            {
                "WaveLength": "wave",
                SZ: "solz",
                "PhiV": "phi",
                "ThetaV": "senz",
            }
        )
        .rename_dims(
            {
                "wave": "nwave",
                "solz": "nsolz",
                "phi": "nphi",
                "senz": "nsenz",
            }
        )
        .transpose("nwave", "nsolz", "nphi", "nsenz")
    )
    return ds


def rayleigh_mseps(dataset: xr.Dataset) -> xr.Dataset:
    # calculate rho_ (Tau_NIR==0 is Rayleigh only atmosphere)
    dataset = dataset.isel({TN: 0})
    # conversion for rho to radiance for F0=1: rho = pi*L/cos(solz)
    # the rayleigh luts need radiance as an input for F0=1
    conversion = np.cos(np.deg2rad(dataset[SZ])) / np.pi
    # azimuth angles used in lstsq prediction
    phi = np.deg2rad(dataset["PhiV"]) * xr.DataArray(np.arange(3), dims="N")
    kdim = {"K": ["WaveLength", "ThetaV", SZ, WI]}

    # TODO vectorize over iqu component
    # i_ray calculation
    # convert radiance in outputs to reflectance, removing direct sun glint
    rho = np.pi * (dataset["Lt"] - dataset["TLg"]) / dataset["diff_irrad"]
    a = np.cos(phi)
    b = (rho * conversion).stack(kdim)
    x = xr.apply_ufunc(
        lstsq,
        a.load(),
        b.load(),
        input_core_dims=[a.dims, b.dims],
        output_core_dims=[("N", "K")],
    )
    dataset["i_ray"] = x.unstack()
    dataset["i_ray"].attrs.update(
        {
            "long_name": "Rayleigh radiance coefficients for I-component",
            "units": "unitless",
        }
    )
    # q_ray calculation
    rho = np.pi * (dataset["LQ"] - dataset["TQg"]) / dataset["diff_irrad"]
    b = (rho * conversion).stack(kdim)
    x = xr.apply_ufunc(
        lstsq,
        a.load(),
        b.load(),
        input_core_dims=[a.dims, b.dims],
        output_core_dims=[("N", "K")],
    )
    dataset["q_ray"] = x.unstack()
    dataset["q_ray"].attrs.update(
        {
            "long_name": "Rayleigh radiance coefficients for Q-component",
            "units": "unitless",
        }
    )
    # u_ray calculation
    rho = np.pi * (dataset["LU"] - dataset["TUg"]) / dataset["diff_irrad"]
    a = np.sin(phi)
    b = (rho * conversion).stack(kdim)
    x = xr.apply_ufunc(
        lstsq,
        a.load(),
        b.load(),
        input_core_dims=[a.dims, b.dims],
        output_core_dims=[("N", "K")],
    )
    dataset["u_ray"] = x.unstack()
    dataset["u_ray"].attrs.update(
        {
            "long_name": "Rayleigh radiance coefficients for U-component",
            "units": "unitless",
        }
    )

    # select and rename outputs
    ds = (
        dataset[["rot", "depol", "i_ray", "q_ray", "u_ray"]]
        .rename(
            {
                "rot": "taur",
                SZ: "solz",
                "ThetaV": "senz",
                "WaveLength": "wave",
                WA: "wave_mean_square_slope",
            }
        )
        .rename_dims(
            {
                "wave": "nlambda",
                "solz": "nsun_ray",
                "senz": "nrad_ray",
                WI: "nwind_ray",
                "N": "norder_ray",
            }
        )
        .drop_vars([WI])
        .transpose("nwind_ray", "nsun_ray", "norder_ray", "nrad_ray", ...)
    )
    return ds


def for_l2gen(dataset: xr.Dataset, inst: str, rayleigh=False) -> xr.Dataset:
    dataset.attrs.update(
        {
            "title": "MSEPS Aerosol Model Data for OCIS",
            "source": "https://oceandata.sci.gsfc.nasa.gov/rcs/rt/zhai_rt",
            "version": version(__name__.split(".", 1)[0]),
            "comment": "coefficients for MSEPS tables",
            "date_created": datetime.now(timezone.utc).isoformat(),
            "history": "\n".join(
                (
                    f"rt-AC-LUT data/{inst}/mie.nc data/{inst}/outputs.nc",
                    f"rt-AC-LUT data/{inst}/inputs.nc data/{inst}/outputs.nc",
                    f"rt-AC-LUT --rename=aerosol/aerosol_{inst}_r{{relative_humidity:02d}}f{{fine_mode_fraction:02d}}v01.nc data/{inst}/inputs.nc data/{inst}/outputs.nc",
                )
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
            "references": "\n".join(
                [
                    "Zhai, P., Hu, Y., Chowdhary, J., Trepte, C. R., Lucker, P. L., Josset, D. B. (2010). A vector radiative transfer model for coupled atmosphere and ocean systems with a rough interface. Journal of Quantitative Spectroscopy and Radiative Transfer, 111(7), 1025-1040.",
                    "Zhai, P., Gao, M., Franz, B. A., Werdell, P. J., Ibrahim, A., Hu, Y., Chowdhary, J. (2022). A Radiative Transfer Simulator for PACE: Theory and Applications. Frontiers in Remote Sensing, 3.",
                ]
            ),
        },
    )
    if rayleigh:
        wave = int(np.round(dataset["wave"].item() * 1e3))
        dataset.attrs.update(
            {
                "title": f"Atmospheric Rayleigh radiance table for OCIS at {wave:d} nm",
                "history": "\n".join(
                    (
                        f"rt-AC-LUT data/{inst}/mie.nc data/{inst}/outputs.nc",
                        f"rt-AC-LUT data/{inst}/inputs.nc data/{inst}/outputs.nc",
                        f"rt-AC-LUT --rename=rayleigh/rayleigh_{inst}_{{wave:d}}_iqu.nc data/{inst}/inputs.nc data/{inst}/outputs.nc",
                    )
                ),
            }
        )
    else:
        am = dataset[AM]
        rh = dataset[RH]
        wa = dataset[WA]
        am_flag_index = np.argwhere(am.attrs["flag_values"] == am.values)[0][0]
        am_flag_meaning_fmf = am.attrs["flag_meanings_fmf"][am_flag_index]
        am_flag_meaning_sd = am.attrs["flag_meanings_sd"][am_flag_index]
        dataset.attrs.update(
            {
                "aerosol_model_number": str(am.values[()]),
                "fine_mode_fraction": np.int16(am_flag_meaning_fmf),
                "relative_humidity": rh.values[()],
                "size_distribution": np.int16(am_flag_meaning_sd),
                "wave_mean_square_slope": wa.values[()],
            },
        )
    scalar_vars = [i for i in dataset.variables if not dataset[i].shape]
    dataset = dataset.drop_vars(scalar_vars)
    return dataset


def unpack_outputs(dataset: xr.Dataset) -> xr.Dataset:
    # drop unneeded coordinates
    dataset = dataset.where(dataset["ThetaV"] < 90.0, drop=True)
    # restore the coordinates stacked in am
    dataset = dataset.squeeze("am").drop_vars("am")
    # unstack the sza-dt dimension into separate datasets
    dt = dataset[P.Diffuse_Transmittance_Flag.__name__] == 1
    dt_dataset = (
        dataset.sel({"sza-dt": dt})
        .squeeze("sza-dt")
        .drop_vars([P.Diffuse_Transmittance_Flag.__name__, "sza-dt"])
    )
    rename = {
        "Radiance_TOA": "LT_TOA",
        "Radiance_BOA": "LT_BOA",
    }
    dt_dataset = dt_dataset.rename(rename)[list(rename.values())]
    sza_dataset = (
        dataset.sel({"sza-dt": ~dt})
        .swap_dims({"sza-dt": P.Solar_Zenith_Angle.__name__})
        .drop_vars([P.Diffuse_Transmittance_Flag.__name__, "sza-dt"])
    )
    # calculate aggregrates, ignoring dimensions known to have no effect
    # TODO this subsetting suggests prior unnecessary broadcasting,
    #      as does the dimension of e.g. Aerosol_Model_Number in raw output
    ds = sza_dataset[
        {
            P.Wind_Speed.__name__: 0,
            P.Solar_Zenith_Angle.__name__: 0,
            "ThetaV": 0,
        }
    ]
    sza_dataset["aot"] = ds["Tau_Aerosol_Extinction"].sum("NTLYERA")
    sza_dataset["aot"].attrs.update(
        {
            "long_name": "Optical Thickness",
            "units": "unitless",
        }
    )
    sza_dataset["rot"] = ds["Tau_Rayleigh_Extinction"].sum("NTLYERA")
    sza_dataset["rot"].attrs.update(
        {
            "long_name": "Optical Thickness",
            "units": "unitless",
        }
    )
    sza_dataset["depol"] = ds["Rayleigh_Depolarization_Ratio"].mean("NTLYERA")
    sza_dataset["depol"].attrs.update(
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
    sza_dataset = sza_dataset.rename(rename)
    sza_dataset = sza_dataset[list(rename.values()) + ["aot", "rot", "depol"]]
    # merge the sza and dt datasets back together
    return xr.merge((dt_dataset, sza_dataset))


def lstsq(a, b):
    return np.linalg.lstsq(a, b, rcond=None)[0]
