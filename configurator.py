#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import logging
import rosapi
from time import time, localtime, strftime

from common import vcmp, dictStr
import menuspec

class configError(Exception):
	def init(self, msg):
		Exception.init(self, msg)

class configurator:
	"""
	configure mikrotik
	"""

	def __init__(self, host, user, pw):
		self.log = logging.getLogger('mcm.{0}'.format(self.__class__.__name__))
		self.run_time = None
		self.api = rosapi.login(host, user, pw)
		self.run_time = time()
		self.gatherInfo()

	def gatherInfo(self):
		"""get basic information from remote device"""
		resource = self.api.talk('/system/resource/print')[0]
		self.version = resource.get('version')

		try:
			float(self.version)
		except ValueError:
			raise configError('unknown/unsupported version number: {0}'.format(self.version))
		return

	def configure(self, rules):
		"""
		begin configuring remote device
		takes rules (list).
		"""
		cmp = comparison(self.version)
		for menu in rules:
			self.log.debug('entering menu level {0}'.format(menu['level']))
			try:
				#get all rules from menu level from remote device
				present_rules = self.api.talk('{0}/print'.format(menu['level']))
			except rosapi.cmdError as estr:
				self.log.error('error while reading {0}: {1}'.format(menu['level'], estr))
				continue

			wanted = [dic['defs'] for dic in menu['rules']]
			#pick approprieate method for specific menu level. if not found pick default
			addlist, setlist, dellist, action_order = cmp.compare(wanted, present_rules, menu['level'])

			self.log.debug('addlist={0}'.format(addlist))
			self.log.debug('setlist={0}'.format(setlist))
			self.log.debug('dellist={0}'.format(dellist))

			for action in action_order:
				if action == 'ADD':
					self.addEntry(menu['level'], addlist)
				elif action == 'DEL':
					self.removeIds(menu['level'], dellist)
				elif action == 'SET':
					self.updateEntry(menu['level'], setlist)

		return

	def removeIds(self, menu_level, idlist):
		"""remove all ids in given menu level"""
		if idlist:
			idlist = ','.join(str(x) for x in idlist)
			try:
				# maybe some more human readable form instead of mikrotiks .ids
				self.log.info('{0}/remove .id={1}'.format(menu_level, idlist))
				self.api.talk('{0}/remove'.format(menu_level), {'.id': idlist})
			except rosapi.cmdError as estr:
				self.log.error('{0}/remove .id={1}: {2}'.format(menu_level, idlist, estr))
		return

	def updateEntry(self, menu_level, setlist):
		for dictionary in setlist:
			log_str = dictStr(dictionary)
			try:
				self.log.info('{0}/set {1}'.format(menu_level, log_str))
				self.api.talk('{0}/set'.format(menu_level), dictionary)
			except rosapi.cmdError as estr:
				self.log.error('{0}/set {1}: {2}'.format(menu_level, log_str, estr))
		return

	def addEntry(self, menu_level, addlist):
		for dictionary in addlist:
			log_str = dictStr(dictionary)
			try:
				self.log.info('{0}/add {1}'.format(menu_level, log_str))
				self.api.talk('{0}/add'.format(menu_level), dictionary)
			except rosapi.cmdError as estr:
				self.log.error('{0}/add {1}: {2}'.format(menu_level, log_str, estr))
		return

	def __del__(self):
		if self.run_time:
			run_time = strftime('%M minutes %S seconds', localtime(time() - self.run_time))
			self.log.info('finished configuration run in {0}'.format(run_time))





class comparison:
	"""
	class that holds various comparison methods for different menus
	"""

	def __init__(self, version):
		self.version = version
		self.log = logging.getLogger('mcm.configurator.{0}'.format(self.__class__.__name__))

	def diffElem(self, wanted, present):
		"""
		compare 2 dictionaries in wanted and present
		if any value in present and wanted is a list compare it also
		return (dict) all key value pairs from wanted with are not present in present
		"""
		try:
			difference = dict(set(wanted.items())-set(present.items()))
		#case when at least one value is not hashable
		except TypeError:
			#first retrieve non list values and keys from both wanted and present
			no_list_wanted = dict((k,v) for (k,v) in wanted.items() if not isinstance(v,list))
			no_list_present = dict((k,v) for (k,v) in present.items() if not isinstance(v,list))
			difference = dict(set(iter(no_list_wanted.items()))-set(iter(no_list_present.items())))
			#search and compare list type values
			for k,v in wanted.items():
				if isinstance(v,list):
					cmp_value = present.get(k, [])
					dif = list(set(v) - set(cmp_value))
					#update only those with are not empty
					if dif:
						difference.update({k:dif})

		self.log.debug('difference={0}'.format(difference))
		return difference


	def default(self, wanted, present):
		"""
		default fallback function if could not find any menu level specific.
		compare every wanted rule with present one. if present is not found add it. if it has anything set it. remove rest
		crude but simple
		"""

		#get all ids
		all_ids = [dict.get('.id') for dict in present if dict.get('.id')]
		self.log.debug('all ids = {0}'.format(all_ids))
		#get all default ids
		def_ids = [dict.get('.id') for dict in present if dict.get('default')]
		self.log.debug('default ids = {0}'.format(def_ids))
		#get all dynamic .ids
		dyn_ids = [dict.get('.id') for dict in present if dict.get('dynamic')]
		self.log.debug('dynamic ids = {0}'.format(def_ids))

		#prevent removing dynamic and default .ids
		dellist = set(all_ids) - set(def_ids) - set(dyn_ids)

		if not wanted:
			return ([], [], dellist)

		#filter out dynamic rules
		self.log.debug('present rules (before filtering out dynamic) = {0}'.format(present))
		present = [dict for dict in present if not dict.get('dynamic')]
		self.log.debug('present rules (after filtering out dynamic) = {0}'.format(present))

		#filter out default rules
		self.log.debug('present rules (before filtering out default) = {0}'.format(present))
		present = [dict for dict in present if not dict.get('default')]
		self.log.debug('present rules (after filtering out default) = {0}'.format(present))

		save_ids = []
		addlist = []
		setlist = []
		index = 0

		for wanted_rule in wanted:
			#get n-th rule from present_rules
			try:
				present_rule = present[index]
			except IndexError:
				present_rule = {}
			self.log.debug('wanted rule: {0}'.format(wanted_rule))
			self.log.debug('present rule: {0}'.format(present_rule))
			if not present_rule:
				addlist.append(wanted_rule)
			else:
				#check for difference
				difference = self.diffElem(wanted_rule, present_rule)
				if difference:
					if '.id' in present_rule:
						difference['.id'] = present_rule['.id']
					setlist.append(difference)
				save_ids.append(present_rule.get('.id'))
			index += 1

		dellist = set(dellist) - set(save_ids)
		return (addlist, setlist, dellist)


	def uniqKeyNoOrder(self, wanted, present, key, offset=0, mng_def=False):
		"""
		may have default entries, they are not removable
		key is unique
		no .id menu levels can not be handeled by this method

		key (str) is uniqie key name
		offset (int). treat first number of offset as default
		mng_def (bool) pass to 'shift' default entries
		"""

		if offset:
			#find all .ids from rules where default key is set to True, or first offset if given
			def_ids = [dic.get('.id') for dic in present[:offset]]
		else:
			#treat all found ids as default, not removable
			def_ids = [dic.get('.id') for dic in present if dic.get('default')]
		self.log.debug('default_ids = {0}'.format(def_ids))

		#filter out dynamic rules
		self.log.debug('present rules (before filtering out dynamic) = {0}'.format(present))
		present = [dict for dict in present if not dict.get('dynamic')]
		self.log.debug('present rules (after filtering out dynamic) = {0}'.format(present))

		#get all .ids from present
		all_ids = [dict.get('.id') for dict in present]
		self.log.debug('all_ids = {0}'.format(all_ids))
		if not wanted:
			dellist = set(all_ids) - set(def_ids)
			if def_ids and not dellist:
				self.log.warning('can not remove default entry/entries')
			return ([], [], dellist)

		addlist = []
		setlist = []
		save_ids = []

		#for every wanted rule search for a unique key if present in present and return rule from present
		for wanted_rule in wanted:
			#look for unique key from wanted_rule in present rules
			try:
				setitem = [dic for dic in present if dic.get(key) == wanted_rule[key]][0]
			except IndexError:
				setitem = {}

			self.log.debug('setitem = {0}'.format(setitem))
			self.log.debug('wanted_rule = {0}'.format(wanted_rule))

			if setitem:
				difference = self.diffElem(wanted_rule, setitem)
				if difference:
					#add .id key value to difference
					difference['.id'] = setitem['.id']
					setlist.append(difference)
				#add found setitems .id to save_ids
				save_ids.append(setitem['.id'])
			else:
				#if could not find same unique key name add it to add list
				addlist.append(wanted_rule)
		dellist = set(all_ids) - set(def_ids) - set(save_ids)

		if not mng_def:
			return(addlist, setlist, dellist)

		self.log.debug('updating default entries')

		#if default entries should be managed then 'shift' them. do not leave entries with are not present in rules
		for id in set(def_ids) - set(save_ids):
			#return dictionary where id is found
			setitem = [dic for dic in present if dic.get('.id') == id][0]
			if addlist:
				cmpitem = addlist.pop()
			elif setlist:
				cmpitem_setlist = setlist.pop()
				cmpitem = [dic for dic in present if dic.get('.id') == cmpitem_setlist['.id']][0]
				cmpitem.update(cmpitem_setlist)
				try:
					del cmpitem['default']
				except KeyError:
					pass
				save_ids.remove(cmpitem_setlist['.id'])
			else:
				cmpitem = present.pop()
				try:
					del cmpitem['default']
				except KeyError:
					pass
				save_ids.remove(cmpitem['.id'])

			self.log.debug('cmpitem = {0}'.format(cmpitem))
			self.log.debug('setitem = {0}'.format(setitem))

			difference = self.diffElem(cmpitem, setitem)
			if difference:
				difference['.id'] = setitem['.id']
				setlist.append(difference)
				save_ids.append(setitem['.id'])
		dellist = set(all_ids) - set(def_ids) - set(save_ids)
		return(addlist, setlist, dellist)

	def convAttr (self, lst, attr, char, direction):

		"""
		lst is nested list with dictionaries
		attr. key name to split its value by char
		direction. True to split. False to join
		"""
		if direction:
			lst = list(dict((k,(v.split(char) if k == attr else v)) for (k,v) in inner.items()) for inner in lst)
		else:
			lst = list(dict((k,(char.join(v) if k == attr else v)) for (k,v) in inner.items()) for inner in lst)

		return lst

	def compare (self, wanted, present, menu_level):

		menu_level = menu_level.replace('/', '_').replace('-', '_')
		menu_attrs = getattr(menuspec.default, menu_level, {})
		if not menu_attrs:
			addlist, setlist, dellist = self.default(wanted, present)
			return (addlist, setlist, dellist, ('ADD', 'SET', 'DEL'))
		else:
			lst_attr = menu_attrs.pop('lst_attr', None)
			ADD = menu_attrs.pop('ADD', True)
			SET = menu_attrs.pop('SET', True)
			DEL = menu_attrs.pop('DEL', True)
			key = menu_attrs.pop('key', None)
			mod_ord = menu_attrs.pop('mod_ord', ('ADD', 'SET', 'DEL'))
			if lst_attr:
				wanted = self.convAttr(wanted, lst_attr[0], lst_attr[1], True)
				present = self.convAttr(present, lst_attr[0], lst_attr[1], True)
			if key:
				addlist, setlist, dellist = self.uniqKeyNoOrder(wanted, present, key, **menu_attrs)
			if lst_attr:
				addlist = self.convAttr(addlist, lst_attr[0], lst_attr[1], False)
				setlist = self.convAttr(setlist, lst_attr[0], lst_attr[1], False)

			addlist = addlist if ADD else []
			setlist = setlist if SET else []
			dellist = dellist if DEL else []

			return (addlist, setlist, dellist, mod_ord)


