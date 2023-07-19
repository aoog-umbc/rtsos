from pathlib import Path

import pytest
import xarray as xr

from zhai_rt import rt_AC_LUT


@pytest.fixture(scope="module")
def param_path(tmpdir_factory):
    path = Path(tmpdir_factory.mktemp("data")) / "defaults.nc"
    rt_AC_LUT.main(["--pre", str(path)])
    return path


# FIXME does not cache
@pytest.fixture(scope="module")
def output_path(param_path):
    ds = xr.open_dataset(param_path)
    ds["CFILE_INSTRUMENT"] = "afrt_input_demo.txt"
    ds["Aux_Dir"] = "data/RT"
    ds["Atmos_Dir"] = "data/RT/pwzrt/Gas_Absorption_Coefficients"
    ds["MIE_TABLE_CAL"][...] = 2
    ds["NWV"][...] = 3
    ds = ds.isel(
        {
            "Wind_Speed": slice(0, 2),
            "sza-dt": slice(0, 3),
            "Tau_NIR": slice(0, 2),
        },
    )
    inputs = param_path.parent / "inputs.nc"
    ds.to_netcdf(inputs)
    outputs = param_path.parent / "outputs.nc"
    rt_AC_LUT.main(
        [
            "--cluster=am:42,sza-dt",
            str(inputs),
            str(outputs),
        ],
    )
    return outputs


def test_parameters(param_path):
    dataset = xr.open_dataset(param_path)
    assert len(dataset.coords) == 23
    assert len(dataset.data_vars) == 0


def test_infile(output_path):
    cluster_parent = output_path.parent / "outputs" / "am" / "42"
    assert len(tuple(cluster_parent.glob("**/*.infile.txt"))) == 12


def test_outputs(output_path):
    inputs = output_path.parent / "inputs.nc"
    outputs = output_path
    rt_AC_LUT.main(
        [
            "--post=am:42,sza-dt:8",
            "--cluster=am",
            str(inputs),
            str(outputs),
        ],
    )
    dataset = xr.open_dataset(outputs / "am" / "0" / "outputs.nc")
    assert list(dataset.data_vars)


def test_tmp(param_path):
    import os

    os.chdir("../../ac-luts-pca")
    inst = "demo"
    rt_AC_LUT.main(
        [
            "--post=Tau_NIR,sza-dt",
            "--cluster=am:0",
            f"data/{inst}/inputs.nc",
            f"data/{inst}/outputs.nc",
        ]
    )
