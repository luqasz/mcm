#!/usr/bin/python3 -B
# -*- coding: UTF-8 -*-

try:
	import rosapi
except ImportError as estr:
	exit(estr)

try:
	api = rosapi.rosapi()
	api.login('', '', '')
	adr = api.talk('/ip/service/print')
	if not adr:
		print(api.last_error)
	else:
		print(adr)
except rosapi.socket.error as estr:
	exit(estr.args[-1])
except KeyboardInterrupt:
	print('\r')
	exit('bye...')
except (rosapi.loginError, rosapi.writeError, rosapi.readError) as estr:
	exit(estr)
finally:
	api.disconnect()
