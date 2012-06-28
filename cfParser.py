#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import xml.etree.ElementTree as xml
import re, logging

class parseError(Exception):
	def __init__(self, msg):
		self.msg = msg
		Exception.__init__(self, msg)

class cfParser:
	"""
	parse given configuration file
	"""
	def __init__(self):
		self.log = logging.getLogger('mcm.cfParser')

	def parseProfile(self, fn):
		"""
		parse profile file.
		fn = filename with relative path
		returns dictionary with {profile_name: profile_dict}
		"""
		self.log.debug('parsing file {0}'.format(fn))
		tree = xml.parse(fn)
		root_name = tree.getroot().tag
		tree_root = tree.getroot()
		if root_name != 'profile':
			raise parseError('root tag must be named \'profile\'')
		self.checkKeys(tree_root, ['name'], ['name'])
		profile_name = tree_root.get('name')
		if not profile_name:
			raise parseError('profile name must be given')

		profile = {}
		for elem in tree_root:
			if elem.tag == 'rules':
				profile['rules'] = self.parseRules(elem)
		if not profile:
			raise parseError('empty profiles are not allowed')
		return (profile_name, profile)

	def parseRules (self, rules):
		#map strings to bollean types
		menu_list = []
		#parse all menu tags
		for menu in list(rules):
			self.checkKeys(menu, ['level'], ['level', 'action', 'version'])
			menu = self.prepValidMenu(menu)
			rule_list = []
			#for every rule tag under menu
			for rule in list(menu):
				self.checkKeys(rule, [], ['version'])
				rule = self.prepValidRule(rule)
				#check if rule is empty
				if not list(rule):
					raise parseError('no rule definitions found under \'{0}\' menu level'.format(menu.get('level')))
				defs_dict = {}
				for defs in list(rule):
					#strip whitechars from begin and end
					if defs.text:
						value = defs.text.strip()
					else:
						value = defs.text
					#populate dictionary
					defs_dict[defs.tag] = self.__typeCaster(value)
				rule_list.append({'version': rule.get('version'), 'defs': defs_dict})
			menu_list.append({'level': menu.get('level'), 'action': menu.get('action'), 'rules': rule_list})
		return menu_list

	def __typeCaster(self, string):
		"""cast strings into possibly float, int, boollean"""
		try:
			ret = int(string)
		except ValueError:
			try:
				ret = float(string)
			except ValueError:
				mapping = {'false': False, 'true': True, 'yes': True, 'no': False, 'True': True, 'False': False}
				ret = mapping.get(string, string)
		return ret

	def checkKeys(self, tag, mandatory=[], allowed=[]):
		"""check for mandatory and allowed keys in given element"""
		if mandatory:
			result = list(set(mandatory) - set(tag.keys()))
			if result:
				raise parseError('could not find \'{0}\' attribute in <{1}> tag'.format(result[0], tag.tag))
		if allowed:
			result = list(set(tag.keys()) - set(allowed))
			if result:
				raise parseError('unknown attribute \'{0}\' in <{1}> tag'.format(result[0], tag.tag))

	def prepValidMenu(self, menu):
		#check for valid value of level
		pattern = re.compile('^(/[a-zA-Z]+)([/][a-zA-Z]+)*$')
		match = pattern.match(menu.get('level'))
		if not match:
			raise parseError('invalid value of \'level\' attribute')
		#set default action value if it doesn't exist'
		menu.set('action', menu.get('action', 'overwrite'))
		#check for valid action values
		if menu.get('action') not in ['append', 'overwrite']:
			raise parseError('unknown value \'{0}\' of \'action\' attribute'.format(menu.get('action')))
		menu.set('version', menu.get('version'))
		if menu.get('version'):
			pattern = re.compile('^([!=<>]{1})\d{1}\.\d{1,2}$')
			match = pattern.match(menu.get('version'))
			if not match:
				raise parseError('wrong value \'{0}\' in \'version\' attribute'.format(rule.get('version')))
		return menu

	def prepValidRule(self, rule):
		#set default version string
		rule.set('version', rule.get('version', ''))
		#check for valid entries in version list
		if rule.get('version'):
			pattern = re.compile('^([!=<>]{1})\d{1}\.\d{1,2}$')
			match = pattern.match(rule.get('version'))
			if not match:
				raise parseError('wrong value \'{0}\' in \'version\' attribute'.format(rule.get('version')))
		return rule

