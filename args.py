# -*- coding: UTF-8 -*-

from argparse import ArgumentParser, ArgumentTypeError
from json import load as json_load

from static import __version__



class JsonFile:

    def __call__(self, file):
        try:
            with open(file, mode='rt', encoding='UTF-8', errors='strict') as fp:
                return json_load(fp)
        except (OSError, IOError) as error:
            msg = 'Can not open {!r}. {}'.format
            raise ArgumentTypeError(msg(file, error))
        except ValueError as error:
            msg = 'Error when parsing config file {!r}. {}'.format
            raise ArgumentTypeError(msg(file, error))



def get_arguments():
    argparser = ArgumentParser(description='Mikrotik Configuration Manager. Version {}'.format(__version__))
    argparser.add_argument('host', type=str, help='Host to connect to.')
    argparser.add_argument('config', type=JsonFile(), help='Configuration file.')
    argparser.add_argument('--username', '-u', type=str, help='Mikrotik API username.', required=True)
    argparser.add_argument('--version', '-V', action='version', version=str(__version__))
    argparser.add_argument('--verbose', '-v', default=0, action='count', help='Verbosity level. Can be supplied multiple times to increase verbosity.')
    argparser.add_argument('--dry-run', '-n', action='store_true', help='Perform a trial run without making any changes.')

    return argparser.parse_args()

