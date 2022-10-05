from collections import OrderedDict
from tempfile import TemporaryDirectory
from pathlib import Path
from shutil import copy
import os
import subprocess

import xarray as xr
import numpy as np

from .kit import argv_parser, instrument_case, parameters, input_writer


def default_inputs(instrument, stack):
    # values written, in the order below, to the RT input file
    # each tuple below must hold
    # 1) a key defined in `kit.parameters`
    # 2) a zero or one dimensional Numpy array
    values = OrderedDict((
        (
            'instrument',
            # will be set from command line arguments
            np.array(instrument, dtype=np.int32)
        ),
        (
            'aerosol',
            np.arange(11, 21, dtype=np.int32)
        ),
        (
            'aerofmf',
            # intentionly set aerofmf to be bizarre as we don't need it in this work
            np.array(-1.0e12, dtype=np.float32)
        ),
        (
            'rh',
            np.array(
                [0.3, 0.5, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95],
                dtype=np.float32,
            )
        ),
        (
            # sigma will be used to calculate wndspd, it's not an input
            'sigma',
            np.array(
                [0, 0.1], # DEBUG
                # [0, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4],
                dtype=np.float32,
            )
        ),
        (
            'wndspd',
            # wndspd array will be calculated
            None
        ),
        (
            'theta0',
            # theta0 will be set to vary only when `df == 0`
            np.arange(0, 90, 2, dtype=np.float32)
        ),
        (
            'tau865',
            np.array(
                [0], # DEBUG
                # [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5],
                dtype=np.float32,
            )
        ),
        (
            'pressure_surface',
            np.array(1013, dtype=np.float32)
        ),
        (
            'H2O_COLUMN',
            np.array(1.4387, dtype=np.float32)
        ),
        (
            'OZONE_COLUMN',
            np.array(345.66, dtype=np.float32)
        ),
        (
            'iwhitecap',
            np.array(0, dtype=np.int32)
        ),
        (
            'I_SURFACE_ROUGHNESS_PARA',
            np.array(2, dtype=np.int32)
        ),
        (
            'df',
            np.array([1], dtype=np.int32) # DEBUG
            # np.array([0, 1], dtype=np.int32)
        ),
        (
            'I_SPHERICAL_SHELL_CORRECTION',
            np.array(0, dtype=np.int32)
        ),
        (
            'atmos_profile',
            np.array('afglus.dat')
        ),
    ))
    # calculate compound coordinate wndspd
    sigma = values.pop('sigma')
    surface = values['I_SURFACE_ROUGHNESS_PARA']
    if surface == 1:
        wndspd = (np.square(sigma)-0.003)/0.00512
    elif surface == 2:
        wndspd = (np.square(sigma))/0.00534
    wndspd[wndspd<0.0] = 0.0
    values['wndspd'] = wndspd
    # create an xarray.Dataset with inputs as coordinates
    dataset = xr.Dataset(
        coords={
            i: (i if values[i].shape else (), values[i], parameters[i])
            for i in values
        },
    )
    # remove independent theta0 and df dimensions
    dataset = dataset.stack({'theta0_df': ('theta0', 'df')})
    dataset = (
        dataset.where(
            # TODO confirm theta0 value for diffuse transmission
            ~np.logical_and(dataset['df']==1, dataset['theta0']!=0.),
            drop=True,
        )
        .reset_index('theta0_df')
    )
    # prepare to write netCDF file(s) of inputs into sub-directories
    dataset = dataset.stack(stack)
    return tuple(values.keys()), dataset


def main(argv=None):
    # parse command line arguments
    args = argv_parser.parse_args(argv)
    instrument = instrument_case(args.instrument)
    # build coordinates dataset and write it to netCDF(s) in subdirectories
    # for each value of the following coordinates
    subdir = ('aerosol', 'rh')
    order, inputs = default_inputs(instrument[0], {'subdir': subdir})
    if args.pre:
        # with the `--pre` command line argument, exit after writing inputs
        for _, inputs in inputs.groupby('subdir'):
            path = args.inputs
            for coordinate in subdir:
                # create a unique path that is in-sensitive to rounding
                value = inputs[coordinate].values.tobytes().hex()
                path = path / '_'.join((coordinate, value))
            path.mkdir(parents=True, exist_ok=True)
            inputs.drop_vars('subdir').to_netcdf(path=path / 'inputs.nc')
        return
    # run the RT model on inputs, in a temp directory, and write to outputs,
    # including RT infiles in the same directory as the combined h5 outfile
    # TODO recurse into args.inputs if a directory
    inputs = xr.open_dataset(args.inputs)
    inputs = inputs.stack({'singleton': tuple(inputs.dims.keys())})
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        outdir = args.outputs.parent
        outdir.mkdir(parents=True, exist_ok=True)
        # TODO all these accessory files should go away, write paths to infile
        with (tmpdir / 'auxiliary_directory').open('w') as stream:
            path = args.auxiliary_directory
            stream.write(f'{path.absolute()}{os.sep}')
        with (tmpdir / 'gas_absorption_coeff_dir').open('w') as stream:
            path = args.gas_absorption_coefficients_dir
            stream.write(f'{path.absolute()}{os.sep}')
        with (tmpdir / instrument[1]).open('w') as stream:
            path = args.mie_database_dir / instrument[2]
            stream.write(f'{path.absolute()}{os.sep}')
        for key, dataset in inputs.groupby('singleton'):
            # each zero dimensional dataset produces a single h5 output
            infile = f'{hash(key):x}.infile.txt'
            input_writer(tmpdir / infile, order, dataset)
            subprocess.run(
                args=['rtsos_GSFC_AC_LUT.exe', infile],
                cwd=tmpdir,
            )
            copy(tmpdir / infile, outdir)
        # each h5 output is concatenated and written to the outputs argument
        # TODO correct phony dim names
        outputs = xr.open_mfdataset(
            tmpdir.glob('*.outfile.h5'),
            concat_dim='subdir',
            combine='nested',
        )
        outputs.to_netcdf(args.outputs)
    # TODO compile results split across subdirs (use --post argument)
    # TODO recurse into args.inputs if a directory
    return
