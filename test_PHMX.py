from pytest import fixture
import xarray as xr

from zhai_rt import rt_PHMX


@fixture(scope="module")
def cache_dir(pytestconfig):
    return pytestconfig.cache.mkdir("phmx")


@fixture(scope="module")
def tmp_default(cache_dir):
    path = cache_dir / "default.nc"
    rt_PHMX.main(["--pre", str(path)])
    yield path
    path.unlink()


@fixture(scope="module")
def cache_output(tmp_default):
    path = tmp_default.parent / "output.nc"
    if not path.exists():
        rt_PHMX.main(
            [
                str(tmp_default),
                str(path),
            ],
        )
        for item in (path.parent / "output").glob("**/*.infile.txt"):
            item.unlink()
    return path


def test_default(tmp_default):
    ds = xr.open_dataset(tmp_default)
    assert len(ds.data_vars) == 0


def test_output(cache_output):
    ds = xr.open_dataset(cache_output)
    assert len(ds.coords) == 0
