# -*- coding: UTF-8 -*-

from datastructures import make_cmdpath


class JsonParser:


    def __init__(self, parsed):
        self.parsed = parsed


    def __iter__(self):
        paths = []
        for path in self.parsed['paths']:
            CmdPath = make_cmdpath(path=path['path'], strategy=path['strategy'])
            paths.append((CmdPath, path['rules']))

        return iter(paths)

