import numpy as np
import pytest
import xarray as xr

from zhai_rt import rt_PACE


@pytest.fixture
def param_path(tmp_path):
    path = tmp_path / "defaults.nc"
    rt_PACE.main(["--pre", str(path)])
    return path


@pytest.fixture
def output_path(param_path):
    ds = xr.open_dataset(param_path)
    ds = ds.drop_dims("tau_ref_hi")
    ds = ds.assign_coords(
        {
            "tau_ref_hi": ((), np.array(0, dtype=np.float32)),
        },
    )
    inputs = param_path.parent / "inputs.nc"
    ds.to_netcdf(inputs)
    outputs = param_path.parent / "outputs.nc"
    rt_PACE.main(
        [
            "--cluster=chla:0",
            str(inputs),
            str(outputs),
        ],
    )
    return outputs


def test_parameters(param_path):
    dataset = xr.open_dataset(param_path)
    assert dataset["wv_pace_ref"].item() == np.float32(532.0)


def test_infile(output_path):
    cluster_parent = output_path.parent / "outputs" / "chla" / "0"
    infile = next(cluster_parent.glob("*.infile.txt"))
    assert infile.exists()


def test_run(output_path):
    inputs = output_path.parent / "inputs.nc"
    outputs = output_path.parent / "outputs.nc"
    rt_PACE.main(
        [
            "--post=chla:0",
            str(inputs),
            str(outputs),
        ],
    )
    dataset = xr.open_dataset(outputs)
    assert list(dataset.data_vars)
