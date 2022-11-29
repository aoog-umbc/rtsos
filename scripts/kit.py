from argparse import ArgumentParser, Namespace
from functools import reduce
from pathlib import Path
from shutil import copy
from tempfile import TemporaryDirectory
from typing import Iterable
import os
import subprocess

from dask.base import tokenize
import xarray as xr
import numpy as np


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
        'comma-separated list of the dimensions by which inputs are split into '
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
    '''Compensate for xr.Dataset.groupby's inability to handle the edge case
    of zero-dimensional grouping.'''
    if dataset.dims:
        return dataset.groupby(groups)
    else:
        return ((groups.item(), dataset), )


class ZhaiRT:

    def __init__(
            self,
            program: str,
            params: tuple,
            defaults: xr.Dataset,
            dims: dict = {},
            ) -> None:
        self.program = program
        self.params = tuple(i.__name__ for i in params)
        self.defaults = defaults
        self.dims = dims

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
        # with the `--cluster` argument, prepare to process inputs/outputs
        # in subdirectories for each of the supplied dimensions
        if args.cluster:
            outdir = xr.DataArray(
                data=args.outputs.with_suffix(''),
                coords=inputs.coords,
                )
            coordinates = self.split_cluster(args.cluster)
            try:
                inputs = inputs.isel(coordinates)
            except ValueError as cause:
                exception = Exception(
                    '`--cluster` variables must be in `inputs.indexes`'
                    )
                raise exception from cause
            outdir = reduce(self.paths_by_cluster, coordinates, outdir)
            outdir = outdir.isel(coordinates)
        else:
            outdir = xr.DataArray(
                data=args.outputs.parent,
                coords=inputs.coords,
                )
        # with the `--post` argument, combine existing RT outputs and return
        if args.post:
            paths = np.unique(outdir)
            dataset = xr.open_mfdataset(
                paths=[i / args.outputs.name for i in paths],
                combine='nested',
                concat_dim=tuple(outdir.dims)[:len(paths.shape)],
            )
            dataset.to_netcdf(args.outputs)
            return
        # execute the RT simulations in a temp directory then copy to outputs
        for key, value in groupby(inputs, outdir):
            self.rtsos(value.unstack(), key / args.outputs.name)

    def rtsos(self, inputs: xr.Dataset, outputs: Path) -> None:
        # within a temporary directory, write the rtsos input files and store
        # outputs from each rtsos calculation, run as a subprocess
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            outdir = outputs.parent
            outdir.mkdir(parents=True, exist_ok=True)
            # TODO all these accessory files to be read from infile
            with (tmpdir / 'auxiliary_directory').open('w') as stream:
                path = Path(str(inputs['aux_dir'].data))
                inputs = inputs.drop_vars('aux_dir')
                stream.write(f'{path.absolute()}{os.sep}')
            with (tmpdir / 'gas_absorption_coeff_dir').open('w') as stream:
                path = Path(str(inputs['gas_abs_coef_dir'].data))
                inputs = inputs.drop_vars('gas_abs_coef_dir')
                stream.write(f'{path.absolute()}{os.sep}')
            try:
                instrument = inputs['instrument']
            except KeyError:
                instrument = 1
            if instrument == 1:
                filename = 'OCI_MIE_DIR.txt'
            elif instrument == 2:
                filename = 'MODIS_MIE_DIR.txt'
            elif instrument == 3:
                filename = 'SEAWIFS_MIE_DIR.txt'
            elif instrument == 4:
                filename = 'MISR_MIE_DIR.txt'
            else:
                raise
            with (tmpdir / filename).open('w') as stream:
                path = Path(str(inputs['mie_database_dir'].data))
                inputs = inputs.drop_vars('mie_database_dir')
                stream.write(f'{path.absolute()}{os.sep}')
            # iterate over all variable combinations
            datasets = []
            groups = xr.DataArray(coords=inputs.coords)
            groups.data = np.arange(groups.size).reshape(groups.shape)
            for _, one_input in groupby(inputs, groups):
                one_input = one_input.unstack().squeeze()
                # convert the now zero-dimensional dataset to a parameter file
                # that gets copied to the folder with the combined outputs
                infile, outfile = self.infile(tmpdir, one_input)
                copy(tmpdir / infile, outdir)
                # run RT as subprocess
                # TODO wrapper for Fortran subroutines
                subprocess.run(args=[self.program, infile], cwd=tmpdir)
                # lazy read for outfile metadata
                one_output = xr.open_dataset(tmpdir / outfile).squeeze()
                # add dimension names and missing coordinates
                one_output = one_output.swap_dims(self.dims)
                for item in self.dims.values():
                    if item not in one_output:
                        one_output.coords[item] = range(one_output.dims[item])
                # drop params duplicated in rt outputs
                for item in one_input.coords:
                    if item not in one_output:
                        continue
                    # TODO issue zhai-rt#2
                    if (not (one_output[item] == one_input[item]).all()) and (item not in ['MONOCHROMATIC_FLAG', 'OCEAN_RAMAN_FLAG', 'OCEAN_FCHLA_FLAG', 'OCEAN_FCDOM_FLAG']):
                        raise ValueError('Inputs/outputs are not as expected.')
                    # TODO Improve parameter name matching to catch duplicates
                    #      e.g. ATMOS_ZERO
                    one_output = one_output.drop_vars(item)
                # expand all scalar coords to allow `xr.combine_by_coords`
                one_input = one_input.expand_dims(tuple(one_input.coords))
                datasets.append(xr.merge((one_output, one_input)))
            # write the concatenated datasets to the outputs directory, with
            # length one coordinates returned to scalars
            xr.combine_by_coords(datasets).squeeze().to_netcdf(path=outputs)

    def infile(self, path: Path, dataset: xr.Dataset) -> Path:
        '''Write parameters to a text file, and return its path.'''
        lines = []
        for item in self.params:
            # TODO all these accessory files to be read from infile
            if item.endswith('_dir'): continue
            param = dataset[item]
            name = param.attrs.get('name', item)
            desc = param.attrs.get('description', '')
            lines.append(
                f'{param.values:<24} # {name}: {desc}'
                )
        outfile = Path(tokenize(dataset)).with_suffix('.outfile')
        lines += [f'{outfile}', '']
        infile = outfile.with_suffix('.infile.txt')
        with (path / infile).open('w') as stream:
            stream.write('\n'.join(lines))
        return infile, outfile.with_suffix('.outfile.h5')

    @staticmethod
    def split_cluster(arg: str) -> dict:
        ''''Split the comma separated elements of `arg`, which are key, value
        pairs for the returned dictionary, parsing the value for later use
        in xr.Dataset indexing.'''
        cluster = {}
        for item in arg.split(','):
            key, *value = item.split(':')
            value = tuple(int(i) for i in value)
            if len(value) == 0:
                cluster[key] = slice(None)
            elif len(value) == 1:
                cluster[key] = value[0]
            else:
                cluster[key] = slice(*value)
        return cluster

    @staticmethod
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
