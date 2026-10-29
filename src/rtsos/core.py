# ===============================================================
#  RTSOS – Radiative Transfer model based on Successive Orders of Scattering
#  Copyright (C) 2025  Pengwang Zhai

#  Licensed under the Creative Commons Attribution–NonCommercial 4.0
#  International License (CC BY-NC 4.0).
#  You may use, modify, and share this code for research and
#  educational purposes with proper attribution.
#  Commercial use requires written permission from the author.

#  Full license: https://creativecommons.org/licenses/by-nc/4.0/
#  Contact: Pengwang Zhai  |  [pwzhai@gmail.com]
# ===============================================================

import subprocess
from argparse import Namespace
from collections.abc import Iterable
from functools import reduce
from pathlib import Path
from platform import system
from shutil import copy
from tempfile import TemporaryDirectory

import dask.config
import numpy as np
import xarray as xr
from dask.tokenize import tokenize

from .parameters import Parameters as P

expect_exe = system() == "Windows"
# TODO Slurm, threading, and https://github.com/pydata/xarray/issues/7549
dask.config.set(scheduler="synchronous")


def groupby(dataset: xr.Dataset, groups: xr.DataArray) -> Iterable[tuple]:
    """Return subsets selected from `dataset` at the coordinates of each unique
    value present in `groups`.
    """
    if groups.dims:
        # yield from the iterable created by xr.DataArray.groupby
        for key, value in groups.groupby(groups):
            subset = dataset.sel(value.unstack().indexes)
            yield key, subset
    else:
        # compensate for xr.DataArray.groupby's inability to handle no dims
        yield groups.item(), dataset


def split_list_arg(arg: str) -> dict:
    """Split the comma separated elements of `arg`, which are key, value
    pairs for the returned dictionary, parsing the value for later use
    in xr.Dataset indexing.
    """
    split = {}
    for item in arg.split(","):
        key, *value = item.split(":")
        if value:
            start, *stop = value[0].split("-")
            start = int(start)
            if stop:
                stop = int(stop[0])
            else:
                stop = start
            stop = stop + 1
        else:
            start = stop = None
        split[key] = slice(start, stop)
    return split


def paths_by_coords(current: xr.DataArray, next: tuple[(str, slice)]) -> xr.DataArray:
    """Create an array of Path objects with nesting subdirectories
    for the given dimensions and ranges.
    """
    # use xr.DataArray for broadcasting by named dimensions
    # TODO path construction, or maybe division, is oddly slow
    dim = next[0]
    start = next[1].start or 0
    stop = next[1].stop or current[dim].size + start
    idx = xr.DataArray(
        [Path(str(i)) for i in range(start, stop)],  # TODO padding is unknown
        dims=dim,
    )
    # note that Path objects represent concatenation by division
    subdir = dim / idx
    return current / subdir


def reduce_by_coords(
    coords: dict,
    inputs: xr.Dataset,
    outdirs: Path,
) -> tuple[xr.Dataset, xr.DataArray]:
    """A reduce operation that iterates over slices along xarray.DataArray.coords."""
    try:
        _inputs = inputs.isel(coords)
    except KeyError as cause:
        exception = Exception(
            "`--split` and `--combine` value(s) must reference dimensions of inputs"
        )
        raise exception from cause
    _outdirs, _ = xr.broadcast(xr.DataArray(outdirs), _inputs)
    _outdirs = reduce(paths_by_coords, coords.items(), _outdirs)
    return _inputs, _outdirs


class Program:
    def __init__(
        self,
        defaults: xr.Dataset,
        params: tuple = (),
    ) -> None:
        self.program = self.program + (".exe" if expect_exe else "")
        self.defaults = defaults
        # initialize the params @property
        self._params = tuple(i.__name__ for i in params)

    def __call__(self, args: Namespace) -> None:
        # with the `--pre` argument, write inputs and return
        if args.pre or not args.inputs.exists():
            # build coordinates dataset and write it to netCDF
            path = args.inputs
            path.parent.mkdir(parents=True, exist_ok=True)
            self.defaults.to_netcdf(path=path)
            if args.pre:
                return
        # read existing inputs
        inputs = xr.load_dataset(args.inputs)
        self.params = inputs
        # begin construction of output path(s) relative to args.outputs.parent
        outdirs = xr.DataArray(Path())
        prefix = Path(args.outputs.stem)
        # with the `--split` argument, prepare to process a subset of inputs
        # in subdirectories, defined by the dimension(s) given as the split
        if args.split:
            coordinates = split_list_arg(args.split)
            inputs, outdirs = reduce_by_coords(coordinates, inputs, prefix)
            prefix = Path()
        # with the `--combine` argument, combine split outputs and return
        if args.combine and not args.dry:
            coordinates = split_list_arg(args.combine)
            for key, value in groupby(dataset=inputs, groups=outdirs):
                _, outdirs = reduce_by_coords(coordinates, value, key)
                outdirs = np.unique(outdirs)
                paths = args.outputs.parent / prefix / outdirs / args.outputs.name
                dataset = xr.open_mfdataset(paths=paths.tolist(), data_vars="different")
                try:
                    dataset = self.post(dataset)
                except NotImplementedError:
                    pass
                dataset.to_netcdf(args.outputs.parent / key / args.outputs.name)
            return
        # execute the program in a temp directory then copy to outputs
        for key, value in groupby(dataset=inputs, groups=outdirs):
            path = args.outputs.parent / key / args.outputs.name
            self.run(value, path, args.tmp, args.dry)

    def run(self, inputs: xr.Dataset, outputs: Path, tmp: Path, dry: bool) -> None:
        # within a temporary directory, write the input files and store
        # outputs from each program execution, run as a subprocess
        with TemporaryDirectory(dir=tmp) as tmpdir:
            tmpdir = Path(tmpdir)
            outdir = outputs.parent
            outdir.mkdir(parents=True, exist_ok=True)
            # iterate over all coordinate combinations
            datasets = []
            shape = tuple(inputs.sizes.values())
            each_input = xr.DataArray(
                # FIXME dtype should be int (the default), but see https://github.com/pydata/xarray/issues/7423
                data=np.arange(np.prod(shape), dtype=float).reshape(shape),
                coords=inputs.coords,
            )
            for _, one_input in groupby(dataset=inputs, groups=each_input):
                # convert a zero-dimensional dataset to a parameter file
                # that gets copied to the folder with the combined outputs
                infile, outfile = self.infile(tmpdir, one_input.squeeze())
                copy(tmpdir / infile, outdir)
                if dry:
                    continue
                # run RTSOS as subprocess
                # TODO wrap Fortran to call the program directly
                subprocess.run(args=[self.program, str(tmpdir / infile)], check=True)
                # expect no output if instructed to only calculate Mie tables
                mie_table_cal = P.MIE_TABLE_CAL.__name__
                if mie_table_cal in one_input and one_input[mie_table_cal] == 1:
                    continue
                # lazy read for outfile metadata
                one_output = xr.open_dataset(tmpdir / outfile)
                # expect non-mergeable output with any phony dims
                if "phony_dim_0" in one_output.dims:
                    datasets.append(one_output)
                    continue
                # drop parameters duplicated in rt outputs
                for item in one_input.coords:
                    if item not in one_output:
                        continue
                    if one_input[item] == one_output[item]:
                        # keep item as coordinate
                        one_output = one_output.drop_vars(item)
                    elif np.isnan(one_input[item]):
                        one_input = one_input.drop_vars(item)
                    else:
                        # TODO issue zhai-rt#2
                        if item in [
                            "MONOCHROMATIC_FLAG",
                            "OCEAN_RAMAN_FLAG",
                            "OCEAN_FCHLA_FLAG",
                            "OCEAN_FCDOM_FLAG",
                        ]:
                            raise Exception("zhai-rt#2")
                        raise ValueError("Inputs/outputs are not as expected.")
                # combine coords from one_input with variables and coords
                # from one_output, and store for concatenation across each_input
                one_output = xr.merge((one_input, one_output))
                datasets.append(one_output)
            if datasets:
                # concatenate datasets
                ds = xr.combine_by_coords(
                    datasets, data_vars="different", compat="equals"
                )
                # write the concatenated datasets to the outputs directory, with
                # length one coordinates returned to scalars
                ds.to_netcdf(path=outputs)

    def infile(self, path: Path, dataset: xr.Dataset) -> tuple[Path, Path]:
        """Write parameters to a text file, and return its path."""
        lines = []
        for item in self.params:
            if item not in dataset:
                continue
            param = dataset[item]
            name = param.attrs.get("long_name", item)
            value = param.item()
            lines.append(f"{value:<24} # {name}")
        outfile = tokenize(dataset, ensure_deterministic=True)
        outfile = Path(outfile).with_suffix(".outfile")
        lines += [str(path / outfile), ""]
        infile = outfile.with_suffix(".infile.txt")
        with (path / infile).open("w") as stream:
            stream.write("\n".join(lines))
        return infile, outfile.with_suffix(".outfile.h5")

    def post(self, dataset: xr.Dataset) -> xr.Dataset:
        raise NotImplementedError

    @property
    def params(self) -> tuple:
        return self._params

    @params.setter
    def params(self, dataset: xr.Dataset) -> None:
        pass
