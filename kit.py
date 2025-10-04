from argparse import ArgumentParser, Namespace
from functools import reduce
from pathlib import Path
from shutil import copy
from tempfile import gettempdir, TemporaryDirectory
from typing import Iterable
import subprocess

import dask
import numpy as np
import xarray as xr

from .parameters import Parameters as P


# TODO Slurm, threading, and https://github.com/pydata/xarray/issues/7549
dask.config.set(scheduler="synchronous")


cli = ArgumentParser()
cli.add_argument(
    "--pre",
    action="store_true",
    help="write radiative transfer model (RTM) defaults to inputs",
)
cli.add_argument(
    "--cluster",
    type=str,
    help=(
        "comma-separated list of dimensions by which inputs are split into "
        "nested subdirectories, with optional positions or inclusive ranges as "
        "`dim:index` or `dim:start-stop` respectively."
    ),
)
cli.add_argument(
    "--post",
    type=str,
    help="dimensions by which cluster outputs (i.e. a previous call with "
    "`--cluster`) are combined, formatted as for `--cluster`",
)
cli.add_argument(
    "--tmp",
    type=Path,
    default=gettempdir(),
    help="path where temporary directories will be created",
)
cli.add_argument(
    "inputs",
    type=Path,
    help=(
        "path for RTM input file, a NetCDF whose coordinates are parameters "
        "over which the model will generate outputs"
    ),
)
cli.add_argument(
    "outputs",
    nargs="?",
    type=Path,
    help=("path for RTM output files (ignored, if given, with `--pre`)"),
)


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
    cluster = {}
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
        cluster[key] = slice(start, stop)
    return cluster


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
) -> tuple[(xr.Dataset, xr.DataArray)]:
    """A reduce operation that iterates over slices along xarray.DataArray.coords."""
    try:
        inputs = inputs.isel(coords)
    except KeyError as cause:
        exception = Exception(
            "`--cluster` and `--post` value(s) must be dimensions of inputs"
        )
        raise exception from cause
    outdirs, _ = xr.broadcast(xr.DataArray(outdirs), inputs)
    outdirs = reduce(paths_by_coords, coords.items(), outdirs)
    return inputs, outdirs


class ZhaiRT:
    def __init__(
        self,
        program: str,
        defaults: xr.Dataset,
        params: tuple = (),
    ) -> None:
        self.program = program
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
        # with the `--cluster` argument, prepare to process a subset of inputs
        # in subdirectories, defined by the dimension(s) given with cluster
        if args.cluster:
            coordinates = split_list_arg(args.cluster)
            inputs, outdirs = reduce_by_coords(coordinates, inputs, prefix)
            prefix = Path()
        # with the `--post` argument, combine RT outputs (after --cluster) and return
        if args.post:
            coordinates = split_list_arg(args.post)
            for key, value in groupby(dataset=inputs, groups=outdirs):
                _, postdirs = reduce_by_coords(coordinates, value, key)
                postdirs = np.unique(postdirs)
                paths = args.outputs.parent / prefix / postdirs / args.outputs.name
                dataset = xr.open_mfdataset(paths=paths.tolist(), data_vars="different")
                if hasattr(self, "post"):
                    dataset = self.post(dataset)
                dataset.to_netcdf(args.outputs.parent / key / args.outputs.name)
            return
        # execute the RT simulations in a temp directory then copy to outputs
        for key, value in groupby(dataset=inputs, groups=outdirs):
            self.rtsos(args.tmp, value, args.outputs.parent / key / args.outputs.name)

    def rtsos(self, tmp: Path, inputs: xr.Dataset, outputs: Path) -> None:
        # within a temporary directory, write the rtsos input files and store
        # outputs from each rtsos calculation, run as a subprocess
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
                # run RT as subprocess
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
                ds = xr.combine_by_coords(datasets, data_vars="different")
                # write the concatenated datasets to the outputs directory, with
                # length one coordinates returned to scalars
                return ds.to_netcdf(path=outputs)

    def infile(self, path: Path, dataset: xr.Dataset) -> Path:
        """Write parameters to a text file, and return its path."""
        lines = []
        for item in self.params:
            if item not in dataset:
                continue
            param = dataset[item]
            name = param.attrs.get("long_name", item)
            value = param.item()
            lines.append(f"{value:<24} # {name}")
        outfile = Path(dask.base.tokenize(dataset)).with_suffix(".outfile")
        lines += [str(path / outfile), ""]
        infile = outfile.with_suffix(".infile.txt")
        with (path / infile).open("w") as stream:
            stream.write("\n".join(lines))
        return infile, outfile.with_suffix(".outfile.h5")

    @property
    def params(self) -> tuple:
        return self._params

    @params.setter
    def params(self, dataset: xr.Dataset) -> None:
        pass
