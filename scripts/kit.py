from argparse import ArgumentParser, Namespace
from functools import reduce
from pathlib import Path
from shutil import copy
from tempfile import TemporaryDirectory
from typing import Iterable
import subprocess

from dask.base import tokenize
import xarray as xr
import numpy as np

from .parameters import Parameters as P


cli = ArgumentParser()
cli.add_argument(
    '--pre',
    action='store_true',
    help='write radiative transfer model (RTM) defaults to inputs',
    )
cli.add_argument(
    '--post',
    action='store_true',
    help='combine existing RTM outputs (e.g. created with `--cluster`)',
    )
cli.add_argument(
    '--cluster',
    type=str,
    help=(
        'comma-separated list of dimensions by which inputs are split into '
        'nested subdirectories, with optional positions or slices as '
        '`dim:index` or `dim:start:stop` respectively.'
        ),
    )
cli.add_argument(
    'inputs',
    type=Path,
    help=(
        'path for RTM input files (to read and/or write), or with `--post` '
        'the RTM output files to be post-processed'
        ),
    )
cli.add_argument(
    'outputs',
    nargs="?",
    type=Path,
    help=(
        'path for RTM output files (not required with `--pre`), or '
        'with `--post` the path for combined outputs'
        ),
    )


def groupby(dataset: xr.Dataset, groups: xr.DataArray) -> Iterable[tuple]:
    '''Return subsets selected from `dataset` at the coordinates of each unique
    value present in `groups`.'''
    if groups.dims:
        # yield from the iterable created by xr.DataArray.groupby
        for key, value in groups.groupby(groups):
            subset = dataset.sel(value.unstack().indexes)
            yield key, subset
    else:
        # compensate for xr.DataArray.groupby's inability to handle no dims
        return ((groups.item(), dataset), )


def split_cluster(arg: str) -> dict:
    ''''Split the comma separated elements of `arg`, which are key, value
    pairs for the returned dictionary, parsing the value for later use
    in xr.Dataset indexing.'''
    cluster = {}
    for item in arg.split(','):
        key, *value = item.split(':')
        value = tuple(int(i) for i in value)
        if value:
            if len(value) == 1:
                value = value[0]
                cluster[key] = slice(value, value + 1)
            else:
                cluster[key] = slice(*value)
        else:
            cluster[key] = slice(None)
    return cluster


def paths_by_cluster(current: xr.DataArray, next: str) -> xr.DataArray:
    '''Create an array of Path objects with nesting subdirectories
    for the given dimensions and ranges.'''
    # use xr.DataArray for broadcasting by named dimensions
    # TODO path construction, or maybe division, is oddly slow
    idx = xr.DataArray(
        [Path(str(i)) for i in range(current[next].size)],
        dims=next,
        )
    # note that Path objects represent concatenation by division
    subdir = next / idx
    return current / subdir


class ZhaiRT:

    def __init__(
            self,
            program: str,
            params: tuple,
            defaults: xr.Dataset,
            ) -> None:
        self.program = program
        self.params = tuple(i.__name__ for i in params)
        self.defaults = defaults

    def execute(self, args: Namespace) -> None:
        # with the `--pre` argument, write inputs and return
        if args.pre or not args.inputs.exists():
            # build coordinates dataset and write it to netCDF
            path = args.inputs
            path.parent.mkdir(parents=True, exist_ok=True)
            self.defaults.to_netcdf(path=path)
            if args.pre:
                return
        # read existing inputs
        inputs = xr.open_dataset(args.inputs)
        parent = xr.DataArray(args.outputs.parent)
        outdir, _ = xr.broadcast(parent, inputs)
        # with the `--cluster` argument, prepare to process a subset of inputs
        # in subdirectories, defined by the dimension(s) given with cluster
        if args.cluster:
            parent = xr.DataArray(args.outputs.with_suffix(''))
            outdir, _ = xr.broadcast(parent, inputs)
            coordinates = split_cluster(args.cluster)
            try:
                outdir = reduce(paths_by_cluster, coordinates, outdir)
            except KeyError as cause:
                exception = Exception(
                    '`--cluster` value(s) must be dimensions of inputs'
                    )
                raise exception from cause
            outdir = outdir.isel(coordinates)
            inputs = inputs.isel(coordinates)
        # with the `--post` argument, combine existing RT outputs and return
        if args.post:
            paths = np.unique(outdir)
            dataset = xr.open_mfdataset(
                paths=[i / args.outputs.name for i in paths],
                combine='nested',
                concat_dim=outdir.dims[-len(paths.shape):],
                )
            dataset.to_netcdf(args.outputs)
            return
        # execute the RT simulations in a temp directory then copy to outputs
        for key, value in groupby(dataset=inputs, groups=outdir):
            self.rtsos(value, key / args.outputs.name)

    def rtsos(self, inputs: xr.Dataset, outputs: Path) -> None:
        # within a temporary directory, write the rtsos input files and store
        # outputs from each rtsos calculation, run as a subprocess
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            outdir = outputs.parent
            outdir.mkdir(parents=True, exist_ok=True)
            # iterate over all coordinate combinations
            datasets = []
            shape = tuple(inputs.dims.values())
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
                subprocess.run(args=[self.program, tmpdir / infile], check=True)
                # expect no output if instructed to only calculate Mie tables
                name = P.MIE_TABLE_CAL.__name__
                if name in one_input and one_input[name] == 1:
                    continue
                # lazy read for outfile metadata
                # FIXME use netCDF4-python see Unidata/netCDF4-python#1226
                one_output = xr.open_dataset(tmpdir / outfile, engine='h5netcdf')
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
                        if item in ['MONOCHROMATIC_FLAG', 'OCEAN_RAMAN_FLAG', 'OCEAN_FCHLA_FLAG', 'OCEAN_FCDOM_FLAG']:
                            raise Exception('zhai-rt#2')
                        raise ValueError('Inputs/outputs are not as expected.')
                # combine coords from one_input with variables and coords
                # from one_output, and store for concatenation across each_input
                one_output = xr.merge((one_input, one_output))
                datasets.append(one_output)
            if datasets:
                # write the concatenated datasets to the outputs directory, with
                # length one coordinates returned to scalars
                return xr.combine_by_coords(datasets).to_netcdf(path=outputs)

    def infile(self, path: Path, dataset: xr.Dataset) -> Path:
        '''Write parameters to a text file, and return its path.'''
        lines = []
        for item in self.params:
            param = dataset[item]
            name = param.attrs.get('name', item)
            desc = param.attrs.get('description', '')
            lines.append(
                f'{param.values:<24} # {name}: {desc}'
                )
        outfile = Path(tokenize(dataset)).with_suffix('.outfile')
        lines += [f'{path / outfile}', '']
        infile = outfile.with_suffix('.infile.txt')
        with (path / infile).open('w') as stream:
            stream.write('\n'.join(lines))
        return infile, outfile.with_suffix('.outfile.h5')
