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
    parent = path.parent / "output"
    if not any(parent.glob("chla/**/output.nc")):
        # run for only chla 0 and each tau_ref_hi
        rt_PACE.main(
            [
                "--cluster=chla:0,tau_ref_hi",
                str(tmp_input),
                str(path),
            ],
        )
        for item in parent.glob("**/*.infile.txt"):
            item.unlink()
    return path


@fixture(scope="module")
def tmp_phmx_input(tmp_input):
    # TODO resolve cross module fixture: pace needs phmx
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
def cache_phmx_output(tmp_phmx_input):
    path = tmp_phmx_input.parent / "phmx-output.nc"
    if not path.exists():
        rt_PACE.main(
            [
                str(tmp_phmx_input),
                str(path),
            ],
        )
        for item in path.parent.glob("**/*.infile.txt"):
            item.unlink()
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


def test_infile(tmp_input):
    path = tmp_input.parent / "output.nc"
    # generate infiles for only chla 0 and each tau_ref_hi
    rt_PACE.main(
        [
            "--dry-run",
            "--cluster=chla:0,tau_ref_hi",
            str(tmp_input),
            str(path),
        ],
    )
    infile = tuple((path.parent / "output").glob("**/*.infile.txt"))
    for item in infile:
        item.unlink()
    assert len(infile) == 4


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


def test_phmx_output(cache_phmx_output):
    ds = xr.open_dataset(cache_phmx_output)
    assert ds.sizes["NUMMIEUSE"] == 2
