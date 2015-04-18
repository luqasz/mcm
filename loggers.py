# -*- coding: UTF-8 -*-

from sys import stdout
import logging

def setup(verbosity):

    mainlog = logging.getLogger('mcm')
    console = logging.StreamHandler(stdout)

    if verbosity == 1:
        mainlog.setLevel(logging.INFO)
    elif verbosity >= 1:
        mainlog.setLevel(logging.DEBUG)
    else:
        mainlog.setLevel(logging.WARNING)

    formatter = logging.Formatter(fmt='{levelname} {message}', datefmt='%d/%m/%Y %H:%M:%S', style='{')
    console.setFormatter(formatter)
    mainlog.addHandler(console)
