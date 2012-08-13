#!/usr/bin/python3
# -*- coding: UTF-8 -*-

try:
	import cfParser, configurator, logging, argparse
	from sys import stdout
	import xml.etree.ElementTree as xml
except ImportError as estr:
	exit(estr)

argParser = argparse.ArgumentParser(description='configure mikrotik via api')
argParser.add_argument('host', type=str, help="host to with to connect. may be fqdn, ipv4 or ipv6 address")
argParser.add_argument('-c', '--config', type=str, required=True, help="file with rules")
argParser.add_argument('-u', '--user', type=str, required=True, help="username")
argParser.add_argument('-P', '--password', type=str, required=True, help="password")
argParser.add_argument('-p', '--port', type=int, default=8728, help="port to connect to (default 8728)")
argParser.add_argument('-v', '--verbose', action='count', default=0, help="more times specified, more verbose")
args = argParser.parse_args()

class moduleFilter(logging.Filter):
	"""filter that will filter out all messages that belong to specified module name"""
	def __init__(self, module):
		self.module = module

	def filter(self, record):
		return not self.module == record.module

class hostAppend(logging.Filter):
	"""append host to message"""
	def __init__(self, host):
		self.host = host

	def filter(self, record):
		if 'configurator' in record.name:
			record.msg = '{0}: {1}'.format(self.host, record.msg)
		return True

mainlog = logging.getLogger('mcm')
console = logging.StreamHandler(stdout)

if args.verbose == 1:
	mainlog.setLevel(logging.INFO)
	formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
elif args.verbose >= 2:
	mainlog.setLevel(logging.DEBUG)
	formatter = logging.Formatter(fmt='%(asctime)s %(name)s %(levelname)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
else:
	mainlog.setLevel(logging.WARNING)
	formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

console.setFormatter(formatter)

if args.verbose < 3:
	console.addFilter(moduleFilter('rosApi'))

mainlog.addHandler(console)

try:
	parser = cfParser.cfParser()
	rules = parser.parseRules(args.config)
	configer = configurator.configurator()
	filter = hostAppend(args.host)
	console.addFilter(filter)
	configer.login(args.host, args.user, args.password)
	configer.gatherInfo()
	rules = configer.prepRules(rules)
	configer.configure(rules)
except configurator.rosApi.socket.error as estr:
	mainlog.error("{0}: socket error: {1}".format(args.host, estr))
except (configurator.configError, configurator.rosApi.loginError, configurator.rosApi.cmdError) as estr:
	mainlog.error('{0}: {1}'.format(args.host, estr))
except cfParser.parseError as estr:
	mainlog.error('{0}: {1}'.format(args.config, estr))
except IOError as estr:
	mainlog.error(estr)
except KeyboardInterrupt:
	exit(1)
finally:
	console.removeFilter(filter)
	logging.shutdown()

