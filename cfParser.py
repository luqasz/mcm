#!/usr/bin/python3 -B
# -*- coding: UTF-8 -*-

import xml.etree.ElementTree as xml
import re

class parseError(Exception):
	def __init__(self, msg):
		self.msg = msg
		Exception.__init__(self, msg)

class cfParser:
	"""
	parse given configuration file
	"""

	def parseProfile(self, fp):
		"""
		parse profile file.
		fp = file pointer or filename with relative path
		"""
		tree = xml.parse(fp)
		if tree.getroot().tag != 'profile':
			raise parseError('root tag must be named \'profile\'')
		self.check_keys(['name'], tree.getroot())
		self.check_mand_keys(['name'], tree.getroot())
		prof_name = tree.getroot().get('name')
		if not prof_name:
			raise parseError('profile name must be given')

		profile = {}
		for elem in tree.getroot():
			if elem.tag == 'rules':
				profile['rules'] = self.parseRules(elem)
			elif elem.tag == 'packages':
				profile['packages'] = self.parsePackages(elem)
		if not profile:
			raise parseError('empty profiles are not allowed')
		return profile

	def parseRules (self, rules):
		#map strings to bollean types
		mapping = {'false': False, 'true': True, 'yes': True, 'no': False}
		menu_list = []
		#parse all menu tags
		for menu in list(rules):
			self.check_mand_keys(['level'], menu)
			self.check_keys(['level', 'action', 'version'], menu)
			menu = self.prep_valid_menu(menu)
			rule_list = []
			#for every rule tag under menu
			for rule in list(menu):
				self.check_keys(['version'], rule)
				rule = self.prep_valid_rule(rule)
				#check if rule is empty
				if not list(rule):
					raise parseError('no rule definitions found')
				defs_dict = {}
				for defs in list(rule):
					#strip whitechars from begin and end
					value = defs.text.strip()
					#populate dictionary
					defs_dict[defs.tag] = mapping.get(value, value)
				rule_list.append({'version': rule.get('version'), 'defs': defs_dict})
			menu_list.append({'level': menu.get('level'), 'action': menu.get('action'), 'rules': rule_list})
		return menu_list

	def parsePackages(self, packages):
		return

	def check_mand_keys(self, keys, tag):
		"""
		check obligatory keys
		takes: list, tag
		"""
		result = list(set(keys) - set(tag.keys()))
		if result:
			raise parseError('could not find \'{0}\' attribute in <{1}> tag'.format(result[0], tag.tag))

	def check_keys(self, keys, tag):
		"""
		check unknown keys
		takes: list, tag
		"""
		result = list(set(tag.keys()) - set(keys))
		if result:
			raise parseError('unknown attribute \'{0}\' in <{1}> tag'.format(result[0], tag.tag))

	def prep_valid_menu(self, menu):
		#check for valid value of level
		pattern = re.compile('^(/[a-zA-Z]+)([/][a-zA-Z]+)*$')
		match = pattern.match(menu.get('level'))
		if not match:
			raise parseError('invalid value of \'level\' attribute')
		#set default action value if it doesn't exist'
		menu.set('action', menu.get('action', 'remove-rest'))
		#check for valid action values
		if menu.get('action') not in ['remove-rest', 'append']:
			raise parseError('unknown value \'{0}\' of \'action\' attribute'.format(menu.get('action')))
		return menu

	def prep_valid_rule(self, rule):
		#set default version string
		rule.set('version', rule.get('version', ''))
		#check for valid entries in version list
		if rule.get('version'):
			pattern = re.compile('^([!=+-]{1})\d{1}\.\d{1,2}$')
			match = pattern.match(rule.get('version'))
			if not match:
				raise parseError('wrong value \'{0}\' in \'version\' attribute'.format(rule.get('version')))
		return rule

