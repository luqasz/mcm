#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from getpass import getpass

from librouteros import LoginError, connect, ConnError

from args import get_arguments
from iodevices import StaticConfig, RouterOsAPIDevice
from adapters import SlaveAdapter, MasterAdapter
from configurators import Configurator
from loggers import setup as setup_logging
from datastructures import make_cmdpath





def mk_slave(user, host):
    api = connect(host=host, user=user, pw=getpass())
    iodevice = RouterOsAPIDevice(api=api)
    slave = SlaveAdapter(device=iodevice)
    return slave


def mk_master(config):
    iodevice = StaticConfig(data=config)
    master = MasterAdapter(device=iodevice)
    return master


def mk_paths(data):
    paths = []
    for path in data['paths']:
        CmdPath = make_cmdpath(path=path['path'], strategy=path['strategy'])
        paths.append(CmdPath)
    return paths


if __name__ == '__main__':
    args = get_arguments()
    mainlog = setup_logging(verbosity=args.verbose)
    master = mk_master(config=args.config['paths'])

    try:
        paths = mk_paths(data=args.config)
        slave = mk_slave(user=args.username, host=args.host)
    except KeyError as path:
        mainlog.error('Could not find path specification for {}'.format(path))
        exit(1)
    except ConnError as error:
        mainlog.error('Could not connect: {}'.format(error))
        exit(1)
    except LoginError as error:
        mainlog.error('Failed to login: {}'.format(error))
        exit(1)

    configurator = Configurator(master=master, slave=slave)
    configurator.run(paths=paths)
