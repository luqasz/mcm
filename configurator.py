#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import rosApi, logging, common, menucmp
from copy import deepcopy

class configError(Exception):
	def __init__(self, msg):
		Exception.__init__(self, msg)

class configurator:
	"""
	configure mikrotik
	"""

	def __init__(self):
		self.log = logging.getLogger('mcm.{0}'.format(self.__class__.__name__))
		self.api = rosApi.rosApi()

	def login(self, host, user, pw):
		self.api.login(host, user, pw)
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
		self.log.info('version: {0}'.format(self.version))
		return

	def prepRules(self, rules):
		"""once remote version is known filter and prepare rules"""
		cp_rules = deepcopy(rules)
		for menu in rules:
			menuindex = cp_rules.index(menu)
			if menu.get('version'):
				menu_version = float(menu['version'][2:])
				menu_op = menu['version'][:2]
				if not common.opResult(self.version, menu_version, menu_op):
					cp_rules.remove(menu)
					continue
			for rule in menu['rules']:
				if rule.get('version'):
					rule_version = float(rule['version'][2:])
					rule_op = rule['version'][:2]
					if not common.opResult(self.version, rule_version, rule_op):
						cp_rules[menuindex]['rules'].remove(rule)
		#return modified rules
		return cp_rules

	def configure(self, rules):
		"""
		begin configuring remote device
		takes rules (list).
		"""
		cmp = menucmp.cmp(self.version)
		for menu in rules:
			self.log.debug('entering menu level {0}'.format(menu['level']))
			try:
				#get all rules from menu level from remote device
				present_rules = self.api.talk(menu['level'] + '/print')
			except rosApi.cmdError as estr:
				self.log.error('error while reading rules: {0}'.format(estr))
				continue
			cmp_menu_level = menu['level'].replace('/', '_').replace('-', '_')
			wanted = [dic['defs'] for dic in menu['rules']]
			#pick approprieate method for specific menu level. if not found pick default
			addlist, setlist, dellist, action_order = getattr(cmp, cmp_menu_level, cmp.default)(wanted, present_rules)

			self.log.debug('addlist={0}'.format(addlist))
			self.log.debug('setlist={0}'.format(setlist))
			self.log.debug('dellist={0}'.format(dellist))

			if action_order:
				for action in action_order:
					if action == 'ADD':
						self.__addEntry(menu['level'], addlist)
					elif action == 'DEL':
						self.__removeIds(menu['level'], dellist)
					elif action == 'SET':
						self.__updateEntry(menu['level'], setlist)
			else:
				self.__removeIds(menu['level'], dellist)
				self.__updateEntry(menu['level'], setlist)
				self.__addEntry(menu['level'], addlist)
		return

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

	def __updateEntry(self, menu_level, setlist):
		for set in setlist:
			try:
				if menu_level == '/user' and 'password' in set:
					log_str = ' '.join('{0}="{1}"'.format(k,'***' if k == 'password' else v) for (k,v) in set.items())
				else:
					log_str = ' '.join('{0}="{1}"'.format(k,v) for (k,v) in set.items())
				self.log.info('{0}/set {1}'.format(menu_level, log_str))
				self.api.talk('{0}/set'.format(menu_level), set)
			except rosApi.cmdError as estr:
				self.log.error(estr)
		return

	def __addEntry(self, menu_level, addlist):
		for set in addlist:
			try:
				if menu_level == '/user' and 'password' in set:
					log_str = ' '.join('{0}="{1}"'.format(k,'***' if k == 'password' else v) for (k,v) in set.items())
				else:
					log_str = ' '.join('{0}="{1}"'.format(k,v) for (k,v) in set.items())
				self.log.info('{0}/add {1}'.format(menu_level, log_str))
				self.api.talk('{0}/add'.format(menu_level), set)
			except rosApi.cmdError as estr:
				self.log.error(estr)
		return

	def __del__(self):
		self.api.disconnect()


