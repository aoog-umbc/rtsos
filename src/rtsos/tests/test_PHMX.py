import xarray as xr


def test_default(phmx_tmp_default):
    ds = xr.open_dataset(phmx_tmp_default)
    assert len(ds.data_vars) == 0


def test_output(phmx_cache_output):
    ds = xr.open_dataset(phmx_cache_output)
    assert len(ds.coords) == 0
