# Contributing Guide

This guide is in early development. Sections that are not started, outdated, or
incomplete have `<!-- COMMENTS -->`.

## Repository Orientation

The repository has the following key components:

1. Fortran (i.e. ".f" and ".f90") files within the [src/](./src) folder are the main
   programs and shared modules.
1. The [python_script](./test/PACE_Simulator/python_script) folder contains a helper
   scripts for using the PACE simulator without the Python wrapper.
1. The "CMakeLists.txt" files tell CMake how to build the Fortran programs and shared
   modules.
1. The [src/rtsos](./src/rtsos) folder and the [pyproject.toml](./pyproject.toml) files
   provide the Python wrapper for the Fortran modules.

## Development Setup

<!--
Some of the development install information from the README could move here.
-->

<!--
To compile and install from source for development, create a conda environment
(using a `python` executable meeting the version constraints) and install the
package with the `dev` group in editable mode. The `rtsos` Python packaging uses
`scikit-build-core` to implement a `pip install` that calls `cmake` to compile the
Fortran sources.

```shell
$ conda create -p ./.venv python==3.12 hdf5 liblapack
$ conda run -p ./.venv python -m venv .venv
```

Thence either

```shell
$ conda run -p .venv uv sync
```

or (requires `pip>=25.1` and ignores `uv.lock`)

```shell
$ conda run -p .venv pip install --group dev -e .
```

If the install does not succeed with `Could NOT find HDF5`, try calling with
the `HDF5_ROOT` variable as described in the [Installation](#installation)
section above.

To compile the Fortran code without using scikit-build-core, open a terminal and
change to the project root directory, which contains "CMakeLists.txt". If using conda
to obtain the non-Python dependencies, activate the conda environment. Thence
...

```shell
$ cmake -B build
$ cd build
$ cmake --build .
```

If `cmake -B build` does not succeed with `Could NOT find HDF5`, try calling
with the `HDF5_ROOT` variable as described in the [Installation](#installation)
section above.

-->

## Running Tests

<!--
Check the [latest package release][latest] for a link to download `tests.tar.gz`
and extract it into your project folder.
In addition to the folders `Auxiliary_Files` and `Gas_Absorption_Coefficients`, the archive includes files for testing your `zhai-rt` installation (see [Tests](#tests)).


Run the tests with `--cache-clear` and, assuming they pass, ensure no extraneous
data exists in `.pytest_cache/d` or data folders. Thence

```shell
$ cd tests
$ tar --no-xattrs --disable-copyfile -czvf tests.tar.gz .pytest_cache/d Auxiliary_Files Gas_Absorption_Coefficients *.py
```

Create a release on the repository host and include the link to `tests.tar.gz` on the OEL fileshare.
Use hardlinking when creating a versioned filename and update the URL on the previous release.


Before running tests, download the data and cache (see [Auxilliary Data](#auxiliary-data)).
For development testing, extract the archive within the "tests" subfolder.
For testing `zhai-rt` after installation without a clone, extract the archive within in your project.

```shell
$ tar -kxzf path/to/tests.tar.gz
```

Then check the cache and run the tests.

```shell
$ pytest --cache-show
$ pytest
```

The test cache includes outputs from long-running tests. Call `pytest` with
`--cache-clear` in order to execute those long-running tests.
-->

## Updating Documentation

<!--
- changelog when there is one
- README until there is a docs site
-->

## Releasing

Release of a new version happens whenever the project maintainers have a bundle of
changes to make available via non-development installs. There is no changelog or docs
site yet, so releasing takes only one maintainer action: creating the release on GitHub.

### Create a GitHub Release

Decide on the SemVer version number (denoted "<v>") and a corresponding title like
"Release Version <v>", "Pre-release Version <v>", or "Release Candidate <v>". [Create a
new release on GitHub](../../releases/new) from the "main" branch and create a tag like
`v#.#.#` for the major, minor, and patch version numbers. For a pre-release, include a
well-known suffix and use an upcoming version number (e.g. `v2.0.0-alpha2`,
`v2.0.0-beta1`, or `v2.0.0-rc3`). Publishing the release on GitHub triggers the
following automations via [.github/workflows](.github/workflows).

### Publish to PyPI ([publish-to-pypi.yml](.github/workflows/publish-to-pypi.yml))

Automatic publishing to the Python Package Index (PyPI) has been configured according to
the Python Packaging Authority's [guide][pypa-guide]. The GitHub workflow creates a
corresponing PyPI release for each GitHub release. Authentication with PyPI is by the
"trusted publishing" mechanism available under project [settings][pypi-settings].

[pypi-settings]: https://pypi.org/manage/project/rtsos/settings/publishing/
[pypa-guide]: https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/
