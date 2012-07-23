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
		self.log = logging.getLogger('mcm.{0}'.format(self.__class__.__name__))

	def parseRules (self, fn):
		self.log.debug('parsing file {0}'.format(fn))
		try:
			tree = xml.parse(fn)
		except xml.ParseError as estr:
			raise parseError(estr)
		root_name = tree.getroot().tag
		tree_root = tree.getroot()
		if root_name != 'rules':
			raise parseError('no \'rules\' section found')

		menu_list = []
		#parse all menu tags
		for menu in list(tree_root):
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
					# to od try to convert below 2 to more easilly understandable form
				rule_list.append({'version': rule.get('version'), 'defs': defs_dict})
			menu_list.append({'version': menu.get('version'), 'level': menu.get('level'), 'action': menu.get('action'), 'rules': rule_list})
		if not menu_list:
			raise parseError('empty rules are not allowed')
		return menu_list

	def __typeCaster(self, string):
		"""cast strings into possibly float, int, boollean"""
		try:
			ret = int(string)
		except (ValueError, TypeError):
			try:
				ret = float(string)
			except (ValueError, TypeError):
				mapping = {'false': False, 'true': True, 'yes': True, 'no': False, 'True': True, 'False': False, None: ''}
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
		menu.set('version', menu.get('version', ''))
		if menu.get('version'):
			pattern = re.compile('^(gt|lt|le|ge|eq|ne){1}\d{1}\.\d{1,2}$')
			match = pattern.match(menu.get('version'))
			if not match:
				raise parseError('wrong value \'{0}\' in \'version\' attribute'.format(rule.get('version')))
		return menu

	def prepValidRule(self, rule):
		#set default version string
		rule.set('version', rule.get('version', ''))
		#check for valid entries in version list
		if rule.get('version'):
			pattern = re.compile('^(gt|lt|le|ge|eq|ne){1}\d{1}\.\d{1,2}$')
			match = pattern.match(rule.get('version'))
			if not match:
				raise parseError('wrong value \'{0}\' in \'version\' attribute'.format(rule.get('version')))
		return rule

