from pytest import fixture
import xarray as xr

from zhai_rt import rt_PHMX


@fixture(scope="module")
def cache_dir(pytestconfig):
    return pytestconfig.cache.mkdir("phmx")


@fixture(scope="module")
def cache_input(cache_dir):
    path = cache_dir / "input.nc"
    if not path.exists():
        rt_PHMX.main(["--pre", str(path)])
    return path


@fixture(scope="module")
def cache_output(cache_input):
    path = cache_input.parent / "output.nc"
    if not path.exists():
        rt_PHMX.main(
            [
                str(cache_input),
                str(path),
            ],
        )
    return path


def test_default(cache_input):
    ds = xr.open_dataset(cache_input)
    assert len(ds.data_vars) == 0


def test_output(cache_output):
    ds = xr.open_dataset(cache_output)
    assert len(ds.coords) == 0
