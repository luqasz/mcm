#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import rosApi, logging

class configError(Exception):
	def __init__(self, msg):
		self.msg = msg
		Exception.__init__(self, msg)

class addHostname(logging.Filter):
	def __init__(self, host):
		self.host = host
	def filter(self, record):
		record.msg = '{0}: {1}'.format(self.host, record.msg)
		return True

class configurator:
	"""
	configure mikrotik
	"""

	def __init__(self, profile):
		self.log = logging.getLogger('mcm.configurator')
		self.api = rosApi.rosApi()
		self.profile = profile

	def login(self, host, user, pw):

		self.api.login(host, user, pw)
		self.log.addFilter(addHostname(host))
		self.log.info('logged in')

	def gatherInfo(self):
		"""get basic information from remote device"""
		resource = self.api.talk('/system/resource/print')[0]
		self.version = resource.get('version')
		if not self.version:
			raise configError('could not retreive version number')
		try:
			self.version = float(self.version)
		except ValueError:
			raise configError('unknown/unsupported version number: {0}'.format(self.version))
		self.log.info('remote version is: {0}'.format(self.version))
		return



	def configure(self):
		"""begin configuring remote device"""
		for menu in self.profile['rules']:
			try:
				present_rules = self.api.talk(menu['level'] + '/print')
			except rosApi.cmdError as estr:
				self.log.error('error while reading rules: {0}'.format(estr))
			self.log.debug('remote rules for {0} are: {1}'.format(menu['level'], present_rules))
			self.log.debug('retreiving all .ids from {0}'.format(menu['level']))
			#get all ids in current menu level
			remote_ids = (dict.get('.id') for dict in (listelem for listelem in present_rules))
			#filter of None types from remote_ids
			remote_ids = list(filter(None, remote_ids))
			self.log.debug('.ids for {0} are: {1}'.format(menu['level'], remote_ids))
			#reset save ids
			self.log.debug('reseting saved .ids')
			save_ids = []
			# empty rules under menu level means delete everything
			if not menu['rules']:
				self.__removeIds(menu['level'], remote_ids)
			else:
				for wanted_rule in menu['rules']:
					#get current index
					wanted_rule_index = menu['rules'].index(wanted_rule)
					#get n-th rule from present_rules
					try:
						present_rule = present_rules[wanted_rule_index]
					except IndexError:
						present_rule = {}
					self.log.debug('present rule {0}'.format(present_rule))
					self.log.debug('wanted rule {0}'.format(wanted_rule['defs']))
					self.__updateEntry(menu['level'], present_rule, wanted_rule['defs'])
					#get id from present_rule
					save_ids.append(present_rule.get('.id'))
				#filter of None entries in save_ids list
				save_ids = list(filter(None, save_ids))
				#remote_ids - save_ids gives ids to remove from current menu level
				self.__removeIds(menu['level'], (set(remote_ids) - set(save_ids)))


	def __removeIds(self, menu_level, idlist):
		"""remove all ids in given menu level"""
		if idlist:
			idlist = ','.join(str(x) for x in idlist)
			try:
				# maybe some more human readable form instead of mikrotiks .ids
				self.log.info('{0}/remove .id={1}'.format(menu_level, idlist))
				self.api.talk('{0}/remove'.format(menu_level), {'.id': idlist})
			except rosApi.cmdError as estr:
				self.log.error(estr)
		return

	def __updateEntry(self, menu_level, present, wanted):
		"""to do: maybe add some function to check waether something have been done on remote device. sometimes doing something doesn't do what we want and do not return any error"""
		difference = dict(set(iter(wanted.items()))-set(iter(present.items())))
		self.log.debug('difference: {0}'.format(difference))
		if not difference:
			return
		#add wanted rule to menu if present is empty
		if not present:
			try:
				wanted_str = ' '.join('{0}="{1}"'.format(k,v) for (k,v) in difference.items())
				self.log.info('{0}/add {1}'.format(menu_level, wanted_str))
				self.api.talk('{0}/add'.format(menu_level), difference)
			except rosApi.cmdError as estr:
				self.log.error(estr)
		#update present rule with difference
		else:
			#if there is .id key in present rule add it to difference dict.
			#if there is no .id then it is no .id section eg. /system/clock
			if '.id' in present:
				difference['.id'] = present['.id']
			try:
				wanted_str = ' '.join('{0}="{1}"'.format(k,v) for (k,v) in difference.items())
				self.log.info('{0}/set {1}'.format(menu_level, wanted_str))
				self.api.talk('{0}/set'.format(menu_level), difference)
			except rosApi.cmdError as estr:
				self.log.error(estr)
		return

	def disconnect(self):
		self.api.disconnect()
		if self.api.logged:
			self.log.info('discnnected')
		return

	def __del__(self):
		self.disconnect()


