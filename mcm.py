#!/usr/bin/python3
# -*- coding: UTF-8 -*-

try:
	import cfParser, configurator, logging, getpass
except ImportError as estr:
	exit(estr)

class moduleFilter(logging.Filter):
	def __init__(self, module):
		self.module = module

	def filter(self, record):
		#print(record.module)
		return not self.module == record.module

mainlog = logging.getLogger('mcm')
mainlog.setLevel(logging.INFO)
#formatter = logging.Formatter(fmt='%(asctime)s %(name)s: %(levelname)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
#ch.addFilter(moduleFilter('rosApi'))
mainlog.addHandler(ch)

host = ''
user = 'admin'
pw = getpass.getpass()

try:
	parser = cfParser.cfParser()
	profile = parser.parseProfile('test/rules.conf')[1]
	configer = configurator.configurator(profile)
	configer.login(host, user, pw)
	configer.gatherInfo()
	configer.configure()
except configurator.rosApi.socket.error as estr:
	mainlog.error("{0}: socket error: {1}".format(host, estr.args[-1]))
except (configurator.configError, configurator.rosApi.loginError, configurator.rosApi.cmdError) as estr:
	mainlog.error('{0}: {1}'.format(host, estr))
except cfParser.parseError as estr:
	mainlog.error(estr)
except KeyboardInterrupt:
	print('\r')
	exit('bye...')
finally:
	logging.shutdown()

