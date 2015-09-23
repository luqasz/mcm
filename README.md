[![Build Status](https://travis-ci.org/luqasz/mcm.svg)](https://travis-ci.org/luqasz/mcm)

### This is beta version

This software is still under developement. Things may change. There are still some command path specifications missing. If you see an error `Could not find path specification for ...`, please cntact author or create an issue with exact error message.

### Mikrotik Configuration Manager

MCM is a radically simple automation system. It handles configuration management and multiple devices orchestration. For more information [read this](https://github.com/luqasz/mcm/wiki).

### Requirements

* python3
* All config files must be utf-8 encoded

### Usage

`./mcm.py -u USERNAME IP_ADDRESS CONFIG_FILE`

By default program will issue a password prompt. If you don't want that, store it in `MCM_HOST_PASSWORD` environment variable.

For more help run `./mcm.py --help`

### [Developement](DEVELOP.md)
