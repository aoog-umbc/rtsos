import pytest
import xarray as xr

from zhai_rt import rt_PHMX


@pytest.fixture
def param_path(tmp_path):
    path = tmp_path / "defaults.nc"
    rt_PHMX.main(["--pre", str(path)])
    return path


@pytest.fixture
def output_path(param_path):
    inputs = param_path.parent / "inputs.nc"
    outputs = param_path.parent / "outputs.nc"
    rt_PHMX.main([str(inputs), str(outputs)])
    return outputs


def test_parameters(param_path):
    dataset = xr.open_dataset(param_path)
    assert list(dataset.coords)


# def test_infile(output_path):
#     infile_parent = output_path.parent
#     assert infile_parent.exists()


# def test_run(output_path):
#     inputs = output_path.parent / 'inputs.nc'
#     outputs = output_path.parent / 'outputs.nc'
#     rt_PHMX.main([str(inputs), str(outputs)])
#     dataset = xr.open_dataset(outputs)
#     assert list(dataset.data_vars)
