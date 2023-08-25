from pytest import fixture
import xarray as xr

from zhai_rt import rt_AC_LUT


@fixture(scope="module")
def cache_dir(pytestconfig):
    return pytestconfig.cache.mkdir("ac_lut")


@fixture(scope="module")
def cache_default(cache_dir):
    path = cache_dir / "default.nc"
    if not path.exists():
        rt_AC_LUT.main(["--pre", str(path)])
    return path


@fixture(scope="module")
def cache_input(cache_default):
    path = cache_default.parent / "input.nc"
    if not path.exists():
        ds = xr.load_dataset(cache_default)
        ds["NWV"][...] = 6
        ds = ds.isel(
            {
                "Wind_Speed": slice(0, 1),
                "sza-dt": slice(0, 3),  # three sza-dt folders for each am
                "Tau_NIR": slice(0, 2),  # two parameter files in each sza-dt folder
            },
        )
        ds.to_netcdf(path)
    return path


@fixture(scope="module")
def cache_output(cache_input):
    path = cache_input.parent / "output.nc"
    if not any((path.parent / "output").glob("am/**/output.nc")):
        rt_AC_LUT.main(
            [
                "--cluster=am:42,sza-dt",  # run only am 42, run for each sza-dt
                str(cache_input),
                str(path),
            ],
        )
    return path


@fixture
def tmp_cluster_post(cache_input, cache_output):
    rt_AC_LUT.main(
        [
            "--cluster=am:42",  # for am index 42
            "--post=sza-dt",  # aggregate sza-dt
            str(cache_input),
            str(cache_output),
        ],
    )
    yield cache_output
    path = cache_output.parent / "output"
    for item in path.glob("am/*/output.nc"):
        item.unlink()


@fixture
def tmp_post(cache_input, cache_output):
    rt_AC_LUT.main(
        [
            "--post=am:42,sza-dt",
            str(cache_input),
            str(cache_output),
        ],
    )
    yield cache_output
    cache_output.unlink()


def test_default(cache_default):
    ds = xr.open_dataset(cache_default)
    assert len(ds.data_vars) == 0


def test_infile(cache_output):
    path = cache_output.parent / "output"
    assert len(tuple(path.glob("**/*.infile.txt"))) == 6


def test_output(cache_output):
    path = cache_output.parent / "output"
    output = tuple(path.glob("am/42/**/output.nc"))
    assert len(output) == 3
    for item in output:
        dataset = xr.open_dataset(item)
        assert dataset.sizes["Tau_NIR"] == 2


def test_cluster_post(tmp_cluster_post):
    path = tmp_cluster_post.parent / "output"
    output = tuple(path.glob("am/*/output.nc"))
    assert len(output) == 1
    for item in output:
        dataset = xr.open_dataset(item)
        assert dataset.sizes["Tau_NIR"] == 2
        assert dataset.sizes["Solar_Zenith_Angle"] == 2


def test_post(tmp_post):
    dataset = xr.open_dataset(tmp_post)
    assert dataset.sizes["Tau_NIR"] == 2
    assert dataset.sizes["Solar_Zenith_Angle"] == 2
