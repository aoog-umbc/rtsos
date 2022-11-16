from argparse import ArgumentParser
from pathlib import Path
from tempfile import TemporaryDirectory
from shutil import copy
import os
import subprocess

from dask.base import tokenize
import xarray as xr


cli = ArgumentParser()
cli.add_argument(
    '--pre',
    action='store_true',
    help='prepare RT inputs and exit',
    )
cli.add_argument(
    '--post',
    action='store_true',
    help='compile existing RT outputs into LUT',
    )
cli.add_argument(
    '--cluster',
    type=str,
    help=(
        'comma-separated list of the dimensions by which inputs are split into '
        'subdirectories'
        ),
    )
cli.add_argument(
    'inputs',
    type=Path,
    help=(
        'path for RT input files (to read and/or write), or with `--post` '
        ' the RT output files to be post-processed'
        ),
    )
cli.add_argument(
    'outputs',
    nargs="?",
    type=Path,
    help=(
        'path for RT output files (not required with `--pre`), or '
        'with `--post` the LUT path'
        ),
    )


class ZhaiRT:

    def __init__(
            self,
            program: str,
            params: tuple,
            defaults: xr.Dataset,
            phony_dims: dict = None,
            ) -> None:
        self.program = program
        self.params = tuple(i.__name__ for i in params)
        self.defaults = defaults
        self.phony_dims = phony_dims

    def execute(self, args) -> None:
        # with the `--pre` command line argument, write inputs and exit
        if args.pre:
            # build coordinates dataset and write it to netCDF(s)
            path = args.inputs
            path.parent.mkdir(parents=True, exist_ok=True)
            self.defaults.to_netcdf(path=path)
            return
        elif args.post:
            # TODO compile results split across subdirs (use --post argument)
            return
        # group outputs by the `--cluster` dimensions when writing, and
        # ineracts with outputs path to select inputs
        inputs = xr.open_dataset(args.inputs)
        if args.cluster:
            # TODO rethink the current need to match cluster and outputs
            subdir = tuple(args.cluster.split(','))
            path = args.outputs.parent
            coordinates = {}
            # extract coordinate indices from `--cluster` and `args.outputs`
            for item in path.parts[-len(subdir):]:
                key, value = item.rsplit('_', maxsplit=1)
                coordinates[key] = int(value)
                try:
                    inputs.dims[key]
                except KeyError as cause:
                    exception = ValueError(
                        '`--cluster` and `outputs` do not match'
                        )
                    raise exception from cause
            # restrict inputs to extracted coordinates
            inputs = inputs.isel(coordinates)
        # run the RT model on inputs (in a temp directory),
        # and write to output path from command line args
        self.rtsos(inputs, args.outputs)

    def rtsos(self, inputs, outputs) -> None:
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
            # flatten dataset for iteration over all variable combinations
            stack = tuple(inputs.dims.keys())
            if stack:
                inputs = inputs.stack({'_flattened': tuple(inputs.dims)})
            else:
                inputs = (
                    inputs
                    .reset_coords()
                    .expand_dims('_flattened')
                    .set_coords(list(inputs.variables))
                    )
            # run RT for each combination of variables
            for _, coordinates in inputs.groupby('_flattened'):
                # convert the (now) zero dimensional dataset to a parameter file
                # that gets copied to the folder with the combined outputs
                infile, outfile = self.infile(tmpdir, coordinates)
                copy(infile, outdir)
                # run RT as subprocess
                subprocess.run(args=[self.program, infile], cwd=tmpdir)
                # TODO wrap Fortran to call the program directly
                variables = xr.open_dataset(outfile).squeeze()
                # replace dimension names with meaningful values and make coords
                dataset = (
                    variables
                    .set_coords(tuple(
                        i for i in self.phony_dims.values() if i in variables
                        ))
                    .rename(self.phony_dims)
                    )
                # add coordinates to simulation outputs where missing
                for item in coordinates:
                    if item not in dataset.variables:
                        continue

                    # FIXME drop '_flattened' ?
                dataset = xr.merge((dataset, coordinates))

            # write the concatenated h5 outfiles to the outputs directory
            # FIXME order not known for merge with inputs
            outfiles = xr.open_mfdataset(
                tmpdir.glob('*.outfile.h5'),
                concat_dim='_flattened',
                combine='nested',
                )
            outfiles.to_netcdf(outputs)

    def infile(self, path: Path, dataset: xr.Dataset) -> Path:
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
        outfile = (path / tokenize(dataset)).with_suffix('.outfile')
        lines += [outfile.name, '']
        infile = outfile.with_suffix('.infile.txt')
        with infile.open('w') as stream:
            stream.write('\n'.join(lines))
        return infile, outfile.with_suffix('.outfile.h5')
