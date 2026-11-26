"""PACE wind input, wrapper, and optional executable regression checks.

Run with PYTHONPATH=src python -m pytest src/checks/test_pace_wind.py.
Set RTSOS_PACE_EXECUTABLE to a rebuilt executable for the Fortran/HDF5 checks,
and RTSOS_DATA_DIR to the extracted Data directory. RTSOS_GAS_DIR can specify
the gas/profile directory. RTSOS_PACE_BASELINE enables comparison to an older
executable. These checks write all inputs and outputs into pytest's temp directory.
"""

import ast
import math
import os
from pathlib import Path
import subprocess

import numpy as np
import pytest

from rtsos.PACE_Simulator_DoubleK import init


@pytest.fixture(scope="module")
def one_case():
    program = init()
    dataset = program.defaults.isel({name: 0 for name in program.defaults.dims})
    return program, dataset


@pytest.mark.parametrize("legacy", [False, True])
def test_omitted_direction_preserves_input_layout(tmp_path, one_case, legacy):
    program, dataset = one_case
    if legacy:
        dataset = dataset.drop_vars("Wind_Direction")
    infile, outfile = program.infile(tmp_path, dataset)
    lines = (tmp_path / infile).read_text().splitlines()
    assert len(lines) == len(program.params) + 1
    assert lines[-1] == str(tmp_path / outfile.with_suffix(""))
    assert float(lines[0].split()[0]) == dataset.Wind_Speed.item()


@pytest.mark.parametrize("angle", [0.0, 60.0, 90.0, 180.0, 270.0, -90.0, 420.0])
def test_direction_is_a_unit_vector_after_outfile(tmp_path, one_case, angle):
    program, dataset = one_case
    infile, outfile = program.infile(tmp_path, dataset.assign_coords(Wind_Direction=angle))
    lines = (tmp_path / infile).read_text().splitlines()
    assert len(lines) == len(program.params) + 2
    assert lines[-2] == str(tmp_path / outfile.with_suffix(""))
    vector = np.fromstring(lines[-1].split("#")[0], sep=" ")
    assert vector.size == 2
    assert np.linalg.norm(vector) == pytest.approx(1.0, abs=1e-15)
    used_angle = math.degrees(math.atan2(vector[1], vector[0])) % 360.0
    assert used_angle == pytest.approx(angle % 360.0, abs=1e-12)


def test_direction_changes_run_identity(tmp_path, one_case):
    program, dataset = one_case
    runs = [program.infile(tmp_path, dataset.assign_coords(Wind_Direction=a)) for a in [0.0, 60.0]]
    assert runs[0] != runs[1]


def test_nonfinite_angle_is_rejected_before_writing(tmp_path, one_case):
    program, dataset = one_case
    with pytest.raises(ValueError, match="must be finite"):
        program.infile(tmp_path, dataset.assign_coords(Wind_Direction=float("inf")))
    assert not tuple(tmp_path.iterdir())


def test_land_omits_wind_trailer(tmp_path, one_case):
    program, dataset = one_case
    dataset = dataset.assign_coords(Wind_Direction=60.0, OCEAN_CASE_SELECT=-200)
    infile, outfile = program.infile(tmp_path, dataset)
    assert (tmp_path / infile).read_text().splitlines()[-1] == str(
        tmp_path / outfile.with_suffix("")
    )


def test_direction_coordinate_roundtrip_and_sweep(tmp_path, one_case):
    import xarray as xr

    program, dataset = one_case
    direction = xr.DataArray(
        [0.0, 60.0, 270.0], dims="Wind_Direction",
        attrs=dataset.Wind_Direction.attrs,
    )
    dataset = dataset.assign_coords(Wind_Direction=direction)
    path = tmp_path / "wind-input.nc"
    dataset.to_netcdf(path)
    loaded = xr.load_dataset(path)
    runs = [program.infile(tmp_path, loaded.isel(Wind_Direction=i)) for i in range(3)]
    assert len(set(runs)) == 3
    assert loaded.Wind_Direction.attrs["units"] == "degrees"


@pytest.mark.parametrize("filename, writer", [
    ("pace_simulator_twolayer_inputfile_ocean.py", "ocean_input_writer"),
    ("synthetic_Holton_sequence_inputfiles.py", "input_writer"),
])
def test_standalone_generators_append_vector(tmp_path, monkeypatch, filename, writer):
    scripts = Path(os.environ.get(
        "RTSOS_PACE_GENERATOR_DIR",
        Path(__file__).resolve().parents[2] / "test/PACE_Simulator/python_script",
    ))
    source = (scripts / filename).read_text()
    # Load settings and the writer without generating its example/batch runs.
    tree = ast.parse(source)
    tree.body = [
        node for node in tree.body
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.Assign))
        and not (
            isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "hs"
                for target in node.targets
            )
        )
    ]
    namespace = {}
    exec(compile(tree, str(scripts / filename), "exec"), namespace)
    monkeypatch.chdir(tmp_path)
    args = ("wind_check", namespace["ipss"], namespace["iocean"]) if writer == "ocean_input_writer" else (
        "wind_check", 0.3, 4, 0, 60.0, 0.1,
    )
    namespace["wind_vector"] = None
    namespace[writer](*args)
    legacy = (tmp_path / "input_ps_wind_check").read_text().splitlines()
    namespace["wind_vector"] = (0.5, 0.8660254)
    namespace[writer](*args)
    directional = (
        next(tmp_path.glob("input_ps_wind_check_wind_*")).read_text().splitlines()
    )
    assert directional[:-2] == legacy[:-1]
    assert len(directional) == len(legacy) + 1
    assert directional[-2].startswith("output_ps_wind_check_wind_")
    np.testing.assert_allclose(
        np.fromstring(directional[-1].split("#")[0], sep=" "), [0.5, 0.8660254]
    )


@pytest.fixture(scope="module")
def pace_case(one_case):
    executable = os.environ.get("RTSOS_PACE_EXECUTABLE")
    data = os.environ.get("RTSOS_DATA_DIR")
    if not executable or not data:
        pytest.skip("Set RTSOS_PACE_EXECUTABLE and RTSOS_DATA_DIR for executable checks")
    program, dataset = one_case
    gas = os.environ.get("RTSOS_GAS_DIR", data)
    dataset = dataset.assign_coords(
        Aux_Dir=str(Path(data).resolve()) + "/",
        Atmos_Dir=str(Path(gas).resolve()) + "/",
        OCEAN_CASE_SELECT=0,
        Wind_Speed=7.0,
        Solar_Zenith_Angle=60.0,
        Aerosol_Model=10,
        tau_ref_hi=0.05,
        ncolinput=8,
        nquadainput=12,
        nquadoinput=16,
        MAXMORDINPUT=3,
        NTHETAV=6,
        NPHIV=3,
        OCEAN_RAMAN_FLAG=0,
        OCEAN_FCHLA_FLAG=0,
        OCEAN_FCDOM_FLAG=0,
        MONOCHROMATIC_FLAG=1,
        gas_abs_flag=0,
        WAVEBAND_SEG_FLAG=4,
        pss_flag=0,
    )
    return program, dataset, str(Path(executable).resolve())


def run_pace(directory, pace_case, trailer=None, changes=None, executable=None):
    import h5py

    program, dataset, default_exe = pace_case
    directory.mkdir()
    if changes:
        dataset = dataset.assign_coords(**changes)
    infile, outfile = program.infile(directory, dataset)
    if trailer is not None:
        with (directory / infile).open("a") as stream:
            stream.write(trailer)
    with (directory / "run.log").open("w") as log:
        result = subprocess.run(
            [executable or default_exe, str(directory / infile)],
            cwd=directory, stdout=log, stderr=subprocess.STDOUT, timeout=180,
        )
    output = directory / outfile
    assert result.returncode == 0 and output.exists(), (directory / "run.log").read_text()[-5000:]
    with h5py.File(output) as handle:
        values = {
            name: value[()] for name, value in handle.items()
            if isinstance(value, h5py.Dataset)
        }
        descriptions = (
            dict(handle["Water_Surface_Model"].attrs)
            if "Water_Surface_Model" in handle else {}
        )
        if "Multiple_Scattering_Surface_Model" in handle:
            descriptions["multiple_scattering"] = dict(
                handle["Multiple_Scattering_Surface_Model"].attrs
            )
    return values, descriptions


@pytest.fixture(scope="module")
def isotropic(tmp_path_factory, pace_case):
    directory = tmp_path_factory.mktemp("pace_reference") / "isotropic"
    return run_pace(directory, pace_case)[0]


@pytest.mark.parametrize("trailer", ["\n\t\n# no wind\n", "not_a_vector\n1 0\n", "0 0\n", "0.5 0.5\n"])
def test_optional_fallback_matches_isotropic(tmp_path, pace_case, isotropic, trailer):
    values, _ = run_pace(tmp_path / "fallback", pace_case, trailer=trailer)
    assert values["Wind_Vector_Present"] == 0
    assert values["Wind_Direction_Active"] == 0
    assert values["Water_Surface_Model"] == 1
    for name in isotropic:
        np.testing.assert_array_equal(values[name], isotropic[name], err_msg=name)


def test_direction_changes_radiance_and_records_used_vector(tmp_path, pace_case, isotropic):
    values, descriptions = run_pace(
        tmp_path / "directional", pace_case,
        trailer="\n# wind\n0.5 0.8660254 ! sixty degrees\n",
    )
    assert values["Wind_Vector_Present"] == 1
    assert values["Wind_Direction_Active"] == 1
    assert values["Water_Surface_Model"] == 2
    assert values["Wind_X"] == pytest.approx(0.5, abs=1e-6)
    assert values["Wind_Y"] == pytest.approx(math.sqrt(3) / 2, abs=1e-6)
    assert values["Wind_Direction_Used"] == pytest.approx(60.0, abs=1e-4)
    assert "scope" in descriptions
    nphi = 2 * int(pace_case[1].NPHIV.item())
    np.testing.assert_allclose(values["PhiV"], np.arange(nphi) * 360.0 / nphi, atol=1e-5)
    radiances = [name for name in values if np.ndim(values[name]) == 4]
    assert radiances
    reference_phi, wind_phi = np.where(np.isclose(
        isotropic["PhiV"][:, None], values["PhiV"][None, :], rtol=0, atol=1e-4,
    ))
    assert reference_phi.size > 0
    assert any(
        not np.array_equal(values[name][:, wind_phi], isotropic[name][:, reference_phi])
        for name in radiances if name != "Stokes_Vector_TOO"
    )
    for name in radiances:
        assert values[name].shape[1] == nphi, name
        assert np.all(np.isfinite(values[name])), name
    for name in values:
        if name.startswith("Irradiance_"):
            np.testing.assert_array_equal(values[name], isotropic[name], err_msg=name)


@pytest.mark.parametrize("changes, model", [({"Wind_Speed": 0.5e-6}, 0), ({"SUN_GLINT_FLAG": 1}, 2)])
def test_inactive_direction_matches_legacy_surface(tmp_path, pace_case, changes, model):
    old, _ = run_pace(tmp_path / "without", pace_case, changes=changes)
    values, _ = run_pace(
        tmp_path / "with", pace_case,
        changes=dict(changes, Wind_Direction=60.0),
    )
    assert values["Wind_Vector_Present"] == 1
    assert values["Wind_Direction_Active"] == 0
    assert values["Water_Surface_Model"] == model
    # An accepted vector expands the grid even when directional glint is inactive.
    # Compare radiances at common physical angles rather than matching indices.
    old_phi, new_phi = np.where(np.isclose(
        old["PhiV"][:, None], values["PhiV"][None, :], rtol=0, atol=1e-4,
    ))
    assert old_phi.size > 0
    for name in old:
        if name == "PhiV":
            continue
        if name.startswith("Stokes_Vector_"):
            np.testing.assert_array_equal(
                values[name][:, new_phi], old[name][:, old_phi], err_msg=name,
            )
        elif np.ndim(old[name]) >= 1:
            np.testing.assert_array_equal(values[name], old[name], err_msg=name)


@pytest.mark.parametrize("speed,direction,glint_switch,direct_model,ms_model,active", [
    (0.0, None, 0, 0, 0, 0),
    (0.0, 60.0, 0, 0, 0, 0),
    (0.5e-6, 60.0, 0, 0, 0, 0),
    (1e-6, None, 0, 1, 0, 0),
    (1e-6, 60.0, 0, 2, 0, 1),
    (0.4, None, 0, 1, 0, 0),
    (0.4, 60.0, 0, 2, 0, 1),
    (0.5, 60.0, 0, 2, 1, 1),
    (0.4, 60.0, 1, 2, 0, 0),
])
def test_direct_and_multiple_scattering_surface_metadata(
    tmp_path, pace_case, speed, direction, glint_switch, direct_model, ms_model, active,
):
    values, attributes = run_pace(
        tmp_path / "surface_metadata", pace_case,
        changes={"Wind_Speed": speed, "Wind_Direction": np.nan if direction is None else direction,
                 "SUN_GLINT_FLAG": glint_switch},
    )
    assert values["Water_Surface_Model"] == direct_model
    assert values["Multiple_Scattering_Surface_Model"] == ms_model
    assert values["Wind_Direction_Active"] == active
    assert values["Wind_Vector_Present"] == int(direction is not None)
    assert "direct" in str(attributes["scope"]).lower()
    assert "FLATO" in str(attributes["multiple_scattering"]["codes"])
    assert "irradiances" in str(attributes["multiple_scattering"]["scope"])


@pytest.mark.parametrize("nphi", [1, 19])
def test_directional_azimuth_count_and_spacing(tmp_path, pace_case, nphi):
    values, _ = run_pace(
        tmp_path / "azimuth_grid", pace_case,
        changes={"Wind_Direction": 60.0, "NPHIV": nphi},
    )
    expected = np.arange(2 * nphi) * 180.0 / nphi
    np.testing.assert_allclose(values["PhiV"], expected, rtol=0, atol=2e-5)
    assert values["PhiV"][0] == 0
    assert values["PhiV"][-1] < 360
    for name in values:
        if name.startswith("Stokes_Vector_"):
            assert values[name].shape[1] == 2 * nphi, name


def test_legacy_results_match_previous_executable(tmp_path, pace_case, isotropic):
    baseline = os.environ.get("RTSOS_PACE_BASELINE")
    if not baseline:
        pytest.skip("Set RTSOS_PACE_BASELINE to compare existing output datasets")
    old, _ = run_pace(tmp_path / "baseline", pace_case, executable=str(Path(baseline).resolve()))
    for name in old:
        np.testing.assert_array_equal(isotropic[name], old[name], err_msg=name)


@pytest.mark.parametrize("trailer", ["NaN 0\n", "Inf 0\n"])
def test_nonfinite_vector_stops_before_simulation(tmp_path, pace_case, trailer):
    program, dataset, executable = pace_case
    infile, outfile = program.infile(tmp_path, dataset)
    with (tmp_path / infile).open("a") as stream:
        stream.write(trailer)
    result = subprocess.run(
        [executable, str(tmp_path / infile)], cwd=tmp_path,
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode != 0
    assert "Wind-direction components must be finite numbers" in result.stdout + result.stderr
    assert not (tmp_path / outfile).exists()


def test_wrapper_executes_direction_sweep(tmp_path, pace_case):
    import xarray as xr

    program, dataset, executable = pace_case
    dataset = dataset.assign_coords(Wind_Direction=[0.0, 60.0, 270.0])
    original_program = program.program
    program.program = executable
    try:
        program.run(dataset, tmp_path / "sweep.nc", tmp_path, dry=False)
    finally:
        program.program = original_program
    result = xr.load_dataset(tmp_path / "sweep.nc")
    np.testing.assert_allclose(result.Wind_Direction_Used, [0.0, 60.0, 270.0], atol=1e-4)
    np.testing.assert_array_equal(result.Wind_Vector_Present, [1, 1, 1])
    np.testing.assert_array_equal(result.Wind_Direction_Active, [1, 1, 1])


def test_directional_coupled_ocean(tmp_path, pace_case):
    values, _ = run_pace(
        tmp_path / "coupled", pace_case,
        changes={"OCEAN_CASE_SELECT": 1, "water_depth_max": 1.0, "Wind_Direction": 60.0},
    )
    assert values["Wind_Vector_Present"] == 1
    assert values["Wind_Direction_Active"] == 1
    assert values["Water_Surface_Model"] == 2
    assert values["Wind_Direction_Used"] == pytest.approx(60.0, abs=1e-4)
    radiances = [value for value in values.values() if np.ndim(value) == 4]
    assert radiances
    assert all(np.all(np.isfinite(value)) for value in radiances)


def test_directional_transmission_changes_downward_underwater_radiance(tmp_path, pace_case):
    changes = {"OCEAN_CASE_SELECT": 1, "water_depth_max": 1.0, "NTHETAV": 36}
    isotropic, _ = run_pace(tmp_path / "isotropic_water", pace_case, changes=changes)
    directional, attributes = run_pace(
        tmp_path / "directional_water", pace_case,
        changes=dict(changes, Wind_Direction=60.0),
    )
    old_phi, new_phi = np.where(np.isclose(
        isotropic["PhiV"][:, None], directional["PhiV"][None, :], rtol=0, atol=1e-4,
    ))
    assert old_phi.size > 0
    reference = isotropic["Stokes_Vector_TOO"][:, old_phi]
    result = directional["Stokes_Vector_TOO"][:, new_phi]
    downward = directional["ThetaV"] > 90
    assert np.any(result[0, :, downward] != reference[0, :, downward])
    np.testing.assert_array_equal(result[:, :, ~downward], reference[:, :, ~downward])
    np.testing.assert_array_equal(result[3], reference[3])
    for name in directional:
        if name.startswith("Irradiance_"):
            np.testing.assert_array_equal(directional[name], isotropic[name], err_msg=name)
    assert "transmission" in str(attributes["scope"])
