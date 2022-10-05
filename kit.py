from argparse import ArgumentParser
from pathlib import Path


# command line arguments
argv_parser = ArgumentParser()
argv_parser.add_argument(
    '--pre',
    action='store_true',
    help='prepare RT inputs and exit',
)
argv_parser.add_argument(
    '--post',
    action='store_true',
    help='compile existing RT outputs into LUT',
)
argv_parser.add_argument(
    '--auxiliary_directory',
    default='data/RT/pwzrt/Data',
    type=Path,
    help='path required by RT',
)
argv_parser.add_argument(
    '--gas_absorption_coefficients_dir',
    default='data/RT/pwzrt/Gas_Absorption_Coefficients',
    type=Path,
    help='path required by RT',
)
argv_parser.add_argument(
    '--mie_database_dir',
    default='data/RT/pwzrt/Mie_Database',
    type=Path,
    help='path required by RT',
)
argv_parser.add_argument(
    'instrument',
    type=str,
    help='valid (case insensitive) choices: OCI, MODISa, SeaWiFS, MISR',
)
argv_parser.add_argument(
    'inputs',
    type=Path,
    help=(
        'path for RT input files (to read and/or write), or with `--post` RT '
        'output files'
    ),
)
argv_parser.add_argument(
    'outputs',
    nargs="?",
    type=Path,
    help=(
        'path for RT output files (not required with `--pre`), or '
        'with `--post` the LUT path'
    ),
)


# dictionary of valid parameters and their metadata
parameters = {
    'aerofmf': {
        'name': 'Aerosol Fine Mode Fraction',
        'description': 'only used when Aerosol Model is set to "-1"',
        },
    'aerosol': {
        'name': 'Aerosol Model',
        'description': (
            '1-10 is Shettle and Fenn, '
            '11-20 is Ahmad model, '
            '21 dust aerosol model'
        ),
    },
    'atmos_profile': {
        'description': (
            'valid atmosphere profiles are: afglus.dat, '
            'afglsw.dat, afglss.dat, or afglmw.dat'
        ),
    },
    'df': {
        'description': (
            'calculate regular reflectance (0) or '
            'diffuse transmittance (1)'
        ),
    },
    'instrument': {
        'description': 'numeric identifier of the instrument',
    },
    'iwhitecap': {
        'description': 'turn white cap calculation off (0) or on (1)',
    },
    'pressure_surface': {
        'name': 'surface pressure',
        'units': 'mb',
    },
    'rh': {
        'name': 'Relative Humidity',
    },
    'theta0': {
        'units': 'degrees',
    },
    'tau865': {},
    'wndspd': {
        'name': 'Wind Speed',
        'description': (
            'if `I_SURFACE_ROUGHNESS_PARA == 1`, inverse wind speed '
            'from SIGMA^2=0.003D0+0.00512D0*WNDSPD Cox & Munk 1954, '
            'else if `I_SURFACE_ROUGHNESS_PARA == 2` from Gordon & '
            'Wang 1992'
        ),
    },
    'H2O_COLUMN': {
        'description': 'water vapor in the whole column',
        'units': 'cm',
        'source': 'US standard atmosphere 1976',
    },
    'I_SURFACE_ROUGHNESS_PARA': {},
    'I_SPHERICAL_SHELL_CORRECTION': {
        'description': (
            'turn spherical shell correction off (0) or on (1)'
        ),
    },
    'OZONE_COLUMN': {
        'description': 'ozone in the whole column',
        'units': 'Dobson Unit',
        'source': 'US standard atmosphere 1976',
    },
}


def input_writer(path, key, value):
    lines = []
    for item in key:
        param = value[item]
        name = param.attrs.get('name', item)
        desc = param.attrs.get('description', '')
        lines.append(
            f'{param.values:<24}# {name}: {desc}'
        )
    outfile = path.with_suffix('').with_suffix('.outfile').name
    lines += [outfile, '']
    with path.open('w') as stream:
        stream.write('\n'.join(lines))


def instrument_case(name):
    lname = name.lower()
    if lname == 'oci' :
        return 1, 'OCI_MIE_DIR.txt', 'OCI_Mie_Database'
    elif lname == 'modisa' :
        return 2, 'MODIS_MIE_DIR.txt', 'MODIS_Mie_Database'
    elif lname == 'seawifs' :
        return 3, 'SEAWIFS_MIE_DIR.txt', 'SeaWifs_Mie_Database'
    elif lname == 'misr' :
        return 4, 'MISR_MIE_DIR.txt', 'Misr_Mie_Database'
    else:
        raise NotImplementedError(
            f'argument {name} for `instrument` is not recognized'
        )
