# -*- coding: UTF-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import xml.etree.ElementTree as xml
import re
import logging
from copy import deepcopy

from common import typeCast, vcmp

class parseError(Exception):
	def __init__(self, msg):
		Exception.__init__(self, msg)

def parseRules (fn):
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
		checkKeys(menu, ['level'], ['level', 'action', 'version'])
		menu = prepValidMenu(menu)
		rule_list = []
		#for every rule tag under menu
		for rule in list(menu):
			checkKeys(rule, [], ['version'])
			rule = prepValidRule(rule)
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
				defs_dict[defs.tag] = typeCast(value)
				# to od try to convert below 2 to more easilly understandable form
			rule_list.append({'version': rule.get('version'), 'defs': defs_dict})
		menu_list.append({'version': menu.get('version'), 'level': menu.get('level'), 'action': menu.get('action'), 'rules': rule_list})
	if not menu_list:
		raise parseError('empty rules are not allowed')
	return menu_list

def checkKeys(tag, mandatory=[], allowed=[]):
	"""check for mandatory and allowed keys in given element"""
	if mandatory:
		result = list(set(mandatory) - set(tag.keys()))
		if result:
			raise parseError('could not find \'{0}\' attribute in <{1}> tag'.format(result[0], tag.tag))
	if allowed:
		result = list(set(tag.keys()) - set(allowed))
		if result:
			raise parseError('unknown attribute \'{0}\' in <{1}> tag'.format(result[0], tag.tag))

def prepValidMenu(menu):
	#check for valid value of level
	pattern = re.compile('^(/[a-zA-Z]+)([/][-a-zA-Z]+)*$')
	match = pattern.match(menu.get('level'))
	if not match:
		raise parseError('invalid value of \'level\' attribute \'{0}\''.format(menu.get('level')))
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

def prepValidRule(rule):
	#set default version string
	rule.set('version', rule.get('version', ''))
	#check for valid entries in version list
	if rule.get('version'):
		pattern = re.compile('^(gt|lt|le|ge|eq|ne){1}\d{1}\.\d{1,2}$')
		match = pattern.match(rule.get('version'))
		if not match:
			raise parseError('wrong value \'{0}\' in \'version\' attribute'.format(rule.get('version')))
	return rule

def prepRules(rules, version):
	"""filter and prepare rules"""
	cp_rules = deepcopy(rules)
	for menu in rules:
		menuindex = cp_rules.index(menu)
		if menu.get('version'):
			menu_version = menu['version'][2:]
			menu_op = menu['version'][:2]
			if not vcmp(version, menu_version, menu_op):
				cp_rules.remove(menu)
				continue
		for rule in menu['rules']:
			if rule.get('version'):
				rule_version = rule['version'][2:]
				rule_op = rule['version'][:2]
				if not vcmp(version, rule_version, rule_op):
					cp_rules[menuindex]['rules'].remove(rule)
		#remove menu witch have been stripped out of rules
		if not cp_rules[menuindex]['rules'] and menu['rules']:
			del cp_rules[menuindex]
	#return modified rules
	return cp_rules

