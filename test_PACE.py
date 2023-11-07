from pathlib import Path

from pytest import fixture
import numpy as np
import xarray as xr

from zhai_rt import rt_PACE


@fixture(scope="module")
def cache_dir(pytestconfig):
    return pytestconfig.cache.mkdir("pace")


@fixture(scope="module")
def tmp_default(cache_dir):
    path = cache_dir / "default.nc"
    rt_PACE.main(["--pre", str(path)])
    yield path
    path.unlink()


@fixture(scope="module")
def tmp_input(tmp_default):
    path = tmp_default.parent / "input.nc"
    ds = xr.load_dataset(tmp_default)
    ds["ncolinput"][()] = 10
    ds["nquadainput"][()] = 20
    ds["nquadoinput"][()] = 40
    ds["MAXMORDINPUT"][()] = 3
    ds["NTHETAV"][()] = 1
    ds["NPHIV"][()] = 1
    ds["OCEAN_RAMAN_FLAG"][()] = 0
    ds["OCEAN_FCHLA_FLAG"][()] = 0
    ds["OCEAN_FCDOM_FLAG"][()] = 0
    ds.to_netcdf(path)
    yield path
    path.unlink()


@fixture(scope="module")
def cache_output(tmp_input):
    path = tmp_input.parent / "output.nc"
    if not any((path.parent / "output").glob("chla/**/output.nc")):
        rt_PACE.main(
            [
                "--cluster=chla:0,tau_ref_hi",  # run only chla 0, run for each tau_ref_hi
                str(tmp_input),
                str(path),
            ],
        )
    return path


@fixture(scope="module")
def tmp_two_layer_input(tmp_input):
    # TODO resolve cross module fixture
    phmx = tmp_input.parent.parent / "phmx" / "output.nc"
    path = tmp_input.parent / "phmx-input.nc"
    ds = xr.load_dataset(tmp_input)
    ds = ds.isel({"Solar_Zenith_Angle": 0, "tau_ref_hi": 0, "chla": 0})
    ds["Aerosol_Model"][()] = -97
    ds["tau_ref_hi"][()] = 0.05
    ds["tau_ref_low"][()] = 0.1
    ds["height_particle_hi"] = 12.0
    ds["height_particle_low"] = 4.0
    ds["Aerosol_Phasematrix_File_Hi"] = str(phmx)
    ds["Aerosol_Phasematrix_File_Low"] = str(phmx)
    ds.to_netcdf(path)
    yield path
    path.unlink()


@fixture(scope="module")
def cache_two_layer_output(tmp_two_layer_input):
    path = tmp_two_layer_input.parent / "phmx-output.nc"
    if not path.exists():
        rt_PACE.main(
            [
                str(tmp_two_layer_input),
                str(path),
            ],
        )
    return path


@fixture
def tmp_post(tmp_input, cache_output):
    rt_PACE.main(
        [
            "--post=chla:0,tau_ref_hi",
            str(tmp_input),
            str(cache_output),
        ],
    )
    yield cache_output
    cache_output.unlink()


def test_default(tmp_default):
    ds = xr.open_dataset(tmp_default)
    assert len(ds.data_vars) == 0
    assert ds["wv_pace_ref"].item() == np.float32(532.0)


def test_infile(cache_output):
    path = cache_output.parent / "output"
    assert len(tuple(path.glob("**/*.infile.txt"))) == 4


def test_output(cache_output):
    path = cache_output.parent / "output"
    output = tuple(path.glob("chla/0/**/output.nc"))
    assert len(output) == 2
    for item in output:
        ds = xr.open_dataset(item)
        assert ds.sizes["tau_ref_hi"] == 1


def test_post(tmp_post):
    ds = xr.open_dataset(tmp_post)
    assert ds.sizes["tau_ref_hi"] == 2
    assert ds.sizes["Solar_Zenith_Angle"] == 2


def test_two_layer_output(cache_two_layer_output):
    ds = xr.open_dataset(cache_two_layer_output)
    assert ds.sizes["NUMMIEUSE"] == 2
