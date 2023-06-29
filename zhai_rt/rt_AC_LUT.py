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


def main(argv=None):
    """Entry point for rt-AC-LUT command line tool"""

    # values to write, in the order below, to the RT input file
    # NWV should come from CFILE_INSTRUMENT (but is not enforced to allow a fast path)
    # Wind_Speed will be calculated from Mean_Square_Slope (which becomes an aux coord)
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

    # calculate rt coordinate Wind_Speed, taking its ordering from Mean_Square_Slope
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

    # combine Aerosol_Model and Relative_Humidity into one index
    # TODO could be unncessary with --rename
    dim = {
        "am": (
            P.Aerosol_Model.__name__,
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
    """Class that drives rt-AC-LUT and includes post-processing to calculate
    coeficients appearing in the atmospheric correction look-up-tables.
    """

    def post(self, dataset: xr.Dataset, rename: str) -> xr.Dataset:
        # aliases
        AM = "Aerosol_Model_Number"  # DEBUG
        # AM = P.Aerosol_Model.__name__
        WS = P.Wind_Speed.__name__
        TAU_NIR = P.Tau_NIR.__name__
        SOLZ = P.Solar_Zenith_Angle.__name__
        # prepare for LUT calcultions
        dataset = self.unpack_outputs(dataset)
        # calculate aerosol LUT coefficients and return
        if rename.startswith("aerosol"):
            # no wind speed consideration for aerosol LUTs
            dataset = dataset.sel({WS: 0})
            # calculate rho with direct glint at TOA removed
            rhot = np.pi * (dataset["Lt"] - dataset["TLg"]) / dataset["diff_irrad"]
            # calculate rhoa with Rayleigh removed (Tau_NIR==0 is Rayleigh only atmosphere)
            rhoa = rhot.isel({TAU_NIR: slice(1, None)}) - rhot.isel({TAU_NIR: 0})
            # coefficient inference by polynomial least squares for each wavelength
            # predict rhoa(tau) from (log aot(tau)) ** n
            ds = dataset.isel({TAU_NIR: slice(1, None)})
            a = np.log(ds["aot"]) ** xr.DataArray(np.arange(5), dims="N")
            a = a.where(np.logical_or(a["WaveLength"] <= 0.8, a["N"] <= 2), 0.0)
            b = np.log(rhoa).stack({"M": ["PhiV", "ThetaV", SOLZ]})
            x = xr.apply_ufunc(
                lstsq,  # solves a @ x = b for x
                a.load(),  # a.dims are Tau_NIR, WaveLength, N
                b.load(),  # b.dims are Tau_NIR, WaveLength, M
                input_core_dims=[(TAU_NIR, "N"), (TAU_NIR, "M")],
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
                input_core_dims=[(TAU_NIR, "N"), (TAU_NIR, "ThetaV")],
                output_core_dims=[("N", "ThetaV")],
                vectorize=True,
            )
            td_coef = x.assign_coords({"N": ["dtran_a", "dtran_b"]}).to_dataset(dim="N")
            td_coef["dtran_a"] = np.exp(td_coef["dtran_a"])
            td_coef["dtran_b"] = -td_coef["dtran_b"]
            base_band = dataset[P.WAVELENGTH_MICRON_REF.__name__].item()
            ds = dataset.isel({TAU_NIR: 1}, drop=True)
            extc = ds["aot"] / ds["aot"].sel(
                {"WaveLength": base_band}, method="nearest"
            )
            extc.name = "extc"
            # combine coef arrays
            dataset = (
                xr.merge((rhoa_coef, td_coef, extc))
                .rename(
                    {
                        "WaveLength": "wave",
                        SOLZ: "solz",
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
            # metadata to OBPG conventions
            dataset = self.to_obpg_input(dataset)
            try:
                coords = {i: dataset.attrs[i] for i in findall(r"{([^:]*).*?}", rename)}
                rh = coords["relative_humidity"]
                coords["relative_humidity"] = int(np.round(rh * 100))
            except KeyError as error:
                error.add_note(
                    f"\tThe model output does not have an attribute named {error}."
                )
                raise
            return {rename.format(**coords): dataset}
        # calculate rayleigh LUT coefficients and return
        if rename.startswith("rayleigh"):
            # calculate rho_ (Tau_NIR==0 is Rayleigh only atmosphere)
            dataset = dataset.isel({TAU_NIR: 0})
            # conversion for rho to radiance for F0=1: rho = pi*L/cos(solz)
            # the rayleigh luts need radiance as an input for F0=1
            conversion = np.cos(np.deg2rad(dataset[SOLZ])) / np.pi
            # azimuth angles used in lstsq prediction
            phi = np.deg2rad(dataset["PhiV"]) * xr.DataArray(np.arange(3), dims="N")
            kdim = {"K": ["WaveLength", "ThetaV", SOLZ, WS]}
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
                        SOLZ: "solz",
                        "ThetaV": "senz",
                        "WaveLength": "wave",
                    }
                )
                .rename_dims(
                    {
                        "wave": "nlambda",
                        "solz": "nsun_ray",
                        "senz": "nrad_ray",
                        WS: "nwind_ray",
                        "N": "norder_ray",
                    }
                )
                .transpose("nwind_ray", "nsun_ray", "norder_ray", "nrad_ray", ...)
            )
            return {  # TODO rounding
                rename.format(wave=int(np.round(k * 1e3))): self.to_obpg_input(v, True)
                for k, v in ds.groupby("wave")
            }

    def to_obpg_input(self, dataset: xr.Dataset, rayleigh=False) -> xr.Dataset:
        dataset.attrs.update(
            {
                "version": version(__name__.split(".", 1)[0]),
                "comment": "coefficients for MSEPS tables",
                "date_created": datetime.now(timezone.utc).isoformat(),
                "history": ",".join(
                    (
                        "rt-AC-LUT --cluster=<cluster> <inputs> <outputs>",
                        "rt-AC-LUT --post=<cluster> --cluster=am <inputs> <outputs>",
                    )  # TODO make history precise
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
                "references": "",  # FIXME add PZ citation
            },
        )
        if rayleigh:
            wave = int(np.round(dataset["wave"].item() * 1e3))
            dataset.attrs.update(
                {
                    "title": f"Atmospheric Rayleigh radiance table for OCIS at {wave:d} nm",
                }
            )
        else:
            # am = dataset[P.Aerosol_Model.__name__] # DEBUG
            am = dataset["Aerosol_Model_Number"]  # DEBUG
            rh = dataset[P.Relative_Humidity.__name__]
            ws = dataset[P.Mean_Square_Slope.__name__]  # DEBUG
            # am_flag_index = np.argwhere(am.attrs["flag_values"] == am.values)[0][0] # DEBUG
            # am_flag_meaning_fmf = am.attrs["flag_meanings_fmf"][am_flag_index] # DEBUG
            am_flag_meaning_fmf = {  # DEBUG
                11: 0,
                12: 1,
                13: 2,
                14: 5,
                15: 10,
                16: 20,
                17: 30,
                18: 50,
                19: 80,
                20: 95,
            }[am.values.item()]
            # am_flag_meaning_sd = am.attrs["flag_meanings_sd"][am_flag_index] # DEBUG
            am_flag_meaning_sd = {  # DEBUG
                11: 25,
                12: 24,
                13: 23,
                14: 22,
                15: 21,
                16: 20,
                17: 19,
                18: 18,
                19: 17,
                20: 16,
            }[am.values.item()]
            dataset.attrs.update(
                {
                    "title": "MSEPS Aerosol Model Data for OCIS",
                    "aerosol_model_number": str(am.values[()]),
                    "fine_mode_fraction": np.int16(am_flag_meaning_fmf),
                    "relative_humidity": rh.values[()],
                    "size_distribution": np.int16(am_flag_meaning_sd),
                    "wave_mean_square_slope": ws.values[()],
                },
            )
        dataset = dataset.drop_vars(
            (
                P.NWV.__name__,
                P.WAVELENGTH_MICRON_REF.__name__,
                P.CFILE_INSTRUMENT.__name__,
                P.Aux_Dir.__name__,
                P.Atmos_Dir.__name__,
                P.Relative_Humidity.__name__,
                P.Mie_Database_Dir.__name__,
                P.MIE_TABLE_CAL.__name__,
                "Aerosol_Model_Number",  # P.Aerosol_Model.__name__, # DEBUG
                P.Aerosol_FMF.__name__,
                P.Wind_Speed.__name__,
                P.Wave_Mean_Square_Slope.__name__,
                P.Tau_NIR.__name__,
                P.Pressure_Surface_mb.__name__,
                P.H2O_COLUMN.__name__,
                P.OZONE_COLUMN_DobsonUnit.__name__,
                P.iwhitecap.__name__,
                P.I_SURFACE_ROUGHNESS_PARA.__name__,
                P.I_SPHERICAL_SHELL_CORRECTION.__name__,
                P.CFILE_AP.__name__,
            ),
            errors="ignore",
        )
        return dataset

    def unpack_outputs(self, dataset: xr.Dataset) -> xr.Dataset:
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
