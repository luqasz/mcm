# -*- coding: UTF-8 -*-

from argparse import ArgumentParser, ArgumentTypeError
from json import load as json_load
from os import environ
from getpass import getpass

from mcm import __version__

EPILOG = '''
By default program will issue a password prompt.
If you don't want that, store it in MCM_HOST_PASSWORD environment variable.
'''


def get_password():
    try:
        return environ['MCM_HOST_PASSWORD']
    except KeyError:
        return getpass()


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
    argparser = ArgumentParser(prog='mcm', epilog=EPILOG, description='Mikrotik Configuration Manager. Version ' + str(__version__))
    argparser.add_argument('host', type=str, help='Host to connect to.')
    argparser.add_argument('config', type=JsonFile(), help='Configuration file.')
    argparser.add_argument('--username', '-u', type=str, help='Mikrotik API username.', required=True)
    argparser.add_argument('--version', '-V', action='version', version=str(__version__))
    argparser.add_argument('--verbose', '-v', default=0, action='count', help='Verbosity level. Can be supplied multiple times to increase verbosity.')
    argparser.add_argument('--dry-run', '-n', default=False, action='store_true', help='Do not perform any modification actions. Just simulate what could be done.')

    args = argparser.parse_args()
    args.password = get_password()
    return args
