#!/usr/bin/python3 -B
# -*- coding: UTF-8 -*-

try:
	import rosApi, getpass, logging
except ImportError as estr:
	exit(estr)

logging.basicConfig(format='%(name)s/%(levelname)s:	%(message)s', level=logging.INFO)

try:
	api = rosApi.rosApi()
	user = input('Username:')
	pw = getpass.getpass()
	api.login('172.30.30.20', user, pw)
	print(api.talk('/ip/srvice/print'))
except rosapi.socket.error as estr:
	exit("socket error: {0}".format(estr.args[-1]))
except KeyboardInterrupt:
	print('\r')
	exit('bye...')
except (rosapi.loginError, rosapi.writeError, rosapi.readError) as estr:
	exit(estr)
finally:
	api.disconnect()

