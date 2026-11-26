"""Kernel checks requiring gfortran, without HDF5 or auxiliary data.

Compile the actual RTSOS modules, transmission routines, Fresnel routine, and
polarization rotations. Known facets are refracted using vector Snell's law
before checking the slope-PDF dependence and the existing Gaussian limit.
"""

import itertools
from pathlib import Path
import re
import shutil
import subprocess

import numpy as np
import pytest


def extract_unit(source, kind, name):
    start = re.search(
        rf"(?im)^\s*(?:DOUBLE PRECISION\s+)?{kind}\s+{name}\s*\(", source,
    )
    assert start, name
    end = re.search(rf"(?im)^\s*END\s*{kind}\s+{name}\b", source[start.start():])
    assert end, name
    return source[start.start():start.start() + end.end()] + "\n"


@pytest.fixture(scope="module")
def transmission_executable(tmp_path_factory):
    compiler = shutil.which("gfortran")
    if compiler is None:
        pytest.skip("gfortran is required for the transmission kernel checks")
    src = Path(__file__).resolve().parents[1]
    directory = tmp_path_factory.mktemp("transmission_kernels")
    modules = (src / "core/rttype_sos_rao_dg.f90").read_text()
    modules = modules[:modules.index("END MODULE RTUTILITY") + len("END MODULE RTUTILITY")]
    kernels = (src / "core/rtsos_rao_dg.f90").read_text()
    fresnel = (src / "core/rtspecfunc.f90").read_text()
    selected = "\n".join([
        modules,
        *(extract_unit(kernels, "SUBROUTINE", name) for name in [
            "BTDM_AT_OCEAN", "BTDM_AT_OCEAN_nonGaussian", "RADOCMDRCT",
        ]),
        extract_unit(kernels, "FUNCTION", "SHADOW"),
        extract_unit(fresnel, "SUBROUTINE", "FRSNL_T2"),
        extract_unit(fresnel, "SUBROUTINE", "RMATRIX"),
    ])
    (directory / "kernels.f90").write_text(selected)
    executable = directory / "transmission.exe"
    result = subprocess.run([
        compiler, "-O0", "-g", "-fcheck=all", "-fbacktrace",
        "-ffpe-trap=invalid,zero,overflow", "-ffree-line-length-none",
        str(directory / "kernels.f90"),
        str(src / "checks/ocean_transmission_driver.f90"),
        "-o", str(executable),
    ], cwd=directory, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    return executable


def run_cases(executable, cases, *, check=True):
    def literal(value):
        if isinstance(value, (bool, np.bool_)):
            return ".true." if value else ".false."
        if isinstance(value, str):
            return f"'{value}'"
        return format(value, ".17g")

    text = "\n".join(
        "&transmission_case " + ", ".join(
            f"{name}={literal(value)}" for name, value in case.items()
        ) + " /"
        for case in cases
    ) + "\n"
    result = subprocess.run(
        [str(executable)], input=text, capture_output=True, text=True, timeout=30,
    )
    if not check:
        return result
    assert result.returncode == 0, result.stdout + result.stderr
    # Fortran emits each 4x4 matrix in column-major order.
    rows = np.loadtxt(result.stdout.splitlines(), ndmin=2)
    return rows.reshape(len(cases), 4, 4).transpose(0, 2, 1)


def refract_facet(slope, *, theta=45.0, phi=0.0, n=1.34):
    theta, phi = np.radians([theta, phi])
    incident = np.array([np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), -np.cos(theta)])
    normal = np.array([-slope[0], -slope[1], 1.0])
    normal /= np.linalg.norm(normal)
    incident_normal = np.dot(incident, normal)
    assert incident_normal < 0
    transmitted = incident / n - (
        incident_normal / n + np.sqrt(1 - (1 - incident_normal**2) / n**2)
    ) * normal
    assert transmitted[2] < 0
    return dict(cost1=incident[2], phi1=phi, cost2=transmitted[2],
                phi2=np.arctan2(transmitted[1], transmitted[0]), nwre=n)


def wind_parameters(angle):
    angle = np.radians(angle)
    return dict(wind_x=np.cos(angle), wind_y=np.sin(angle))


def test_isotropic_gaussian_limit(transmission_executable):
    cases = []
    for n, theta, slope, scalar, shadow in itertools.product(
        [1.2, 1.34, 1.5], [0.0, 30.0, 65.0],
        [(0.0, 0.0), (0.04, -0.03), (-0.06, 0.02)], [False, True], [False, True],
    ):
        geometry = refract_facet(slope, theta=theta, phi=27.0, n=n)
        common = dict(geometry, sigmasq=0.04, sigmacsq=0.02, sigmausq=0.02,
                      surf_c21=0, surf_c03=0, surf_c40=0, surf_c22=0, surf_c04=0,
                      nwim=1e-4, scl=scalar, shdwflg=shadow, **wind_parameters(73.0))
        cases.extend([dict(common, kernel="isotropic"), dict(common, kernel="directional")])
    results = run_cases(transmission_executable, cases)
    np.testing.assert_allclose(results[1::2], results[::2], rtol=2e-11, atol=1e-11)


@pytest.mark.parametrize("slope", [(0.0, 0.0), (0.05, -0.03), (-0.04, 0.06)])
def test_known_facet_pdf_and_upwind_sign(transmission_executable, slope):
    geometry = refract_facet(slope, theta=47.0, phi=13.0)
    angles = np.array([0.0, 60.0, 180.0, 300.0])
    cases = [dict(geometry, kernel="isotropic")]
    cases.extend(dict(geometry, **wind_parameters(a)) for a in angles)
    results = run_cases(transmission_executable, cases)
    wx, wy = np.cos(np.radians(angles)), np.sin(np.radians(angles))
    vc, vu, total = 0.003 + 0.00192 * 7, 0.00316 * 7, 0.003 + 0.00512 * 7
    xi = (-wy * slope[0] + wx * slope[1]) / np.sqrt(vc)
    eta = -(wx * slope[0] + wy * slope[1]) / np.sqrt(vu)
    c21, c03 = 0.01 - 0.0086 * 7, 0.04 - 0.033 * 7
    gc = (1 - c21 / 2 * (xi**2 - 1) * eta - c03 / 6 * (eta**3 - 3 * eta)
          + 0.4 / 24 * (xi**4 - 6 * xi**2 + 3)
          + 0.12 / 4 * (xi**2 - 1) * (eta**2 - 1)
          + 0.23 / 24 * (eta**4 - 6 * eta**2 + 3))
    directional = np.maximum(gc, 0) * np.exp(-(xi**2 + eta**2) / 2) / (2 * np.pi * np.sqrt(vc * vu))
    isotropic = np.exp(-np.dot(slope, slope) / total) / (np.pi * total)
    expected = results[0] * (directional / isotropic)[:, None, None]
    np.testing.assert_allclose(results[1:], expected, rtol=2e-11, atol=1e-11)
    np.testing.assert_array_equal(results[:, 3, 0], 0)  # Unpolarized sunlight does not generate V.


def test_rotation_mirror_and_periodicity(transmission_executable):
    geometry = refract_facet((0.06, -0.04), theta=50, phi=20)
    base = dict(geometry, **wind_parameters(60))
    cases = [base]
    for turn in [np.radians(81), 2 * np.pi, -2 * np.pi]:
        cases.append(dict(geometry, phi1=geometry["phi1"] + turn,
                          phi2=geometry["phi2"] + turn,
                          **wind_parameters(60 + np.degrees(turn))))
    cases.append(dict(geometry, phi1=-geometry["phi1"], phi2=-geometry["phi2"],
                      **wind_parameters(-60)))
    cases.append(dict(base, wind_x=3 * base["wind_x"], wind_y=3 * base["wind_y"]))
    result = run_cases(transmission_executable, cases)
    np.testing.assert_allclose(result[1:4], np.broadcast_to(result[0], (3, 4, 4)), rtol=2e-11, atol=1e-11)
    signs = np.diag([1, 1, -1, -1])
    np.testing.assert_allclose(result[4], signs @ result[0] @ signs, rtol=2e-11, atol=1e-11)
    np.testing.assert_allclose(result[5], result[0], rtol=2e-11, atol=1e-11)


def test_negative_gram_charlier_factor_is_clipped(transmission_executable):
    # ETA=2 with a deliberately large skewness coefficient gives a negative PDF.
    geometry = refract_facet((-2 * np.sqrt(0.00316 * 7), 0), theta=30)
    case = dict(geometry, surf_c21=0, surf_c03=10, surf_c40=0, surf_c22=0, surf_c04=0)
    result = run_cases(transmission_executable, [case, dict(case, kernel="isotropic")])
    np.testing.assert_array_equal(result[0], 0)
    assert result[1, 0, 0] > 0


@pytest.mark.parametrize("geometry", [
    dict(cost1=0.5), dict(cost2=0.5), dict(cost2=0),
    dict(cost1=-0.5, cost2=-0.5 / 1.34), dict(cost1=-0.7, cost2=-0.1),
])
def test_invalid_transmission_geometry_returns_zero(transmission_executable, geometry):
    result = run_cases(transmission_executable, [geometry])
    np.testing.assert_array_equal(result, 0)


@pytest.mark.parametrize("invalid", [dict(wind_x=0, wind_y=0), dict(sigmacsq=0), dict(sigmausq=-1)])
def test_invalid_wind_statistics_stop(transmission_executable, invalid):
    result = run_cases(transmission_executable, [invalid], check=False)
    assert result.returncode != 0
    assert "Cox-Munk transmission requires" in result.stderr


def test_direct_caller_selects_directional_or_legacy_kernel(transmission_executable):
    geometry = refract_facet((0.04, 0), phi=0)
    cases = [dict(geometry, kernel="isotropic"), geometry,
             dict(geometry, kernel="direct"),
             dict(geometry, kernel="direct", wind_vector_present=False,
                  wind_x=0, wind_y=0, sigmacsq=0, sigmausq=0),
             dict(geometry, kernel="direct", i_surface_roughness_para=2,
                  wind_x=0, wind_y=0, sigmacsq=0, sigmausq=0)]
    result = run_cases(transmission_executable, cases)
    np.testing.assert_allclose(result[2, :, 0], result[1, :, 0], rtol=1e-14, atol=1e-14)
    for k in [3, 4]:
        np.testing.assert_allclose(result[k, :, 0], result[0, :, 0], rtol=1e-14, atol=1e-14)
    assert not np.allclose(result[0, :, 0], result[1, :, 0])
