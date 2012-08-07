#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import logging

class cmp:
	"""compare values from given menu and return things to modify"""

	def __init__(self, version):
		self.vsersion = version
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
		order = ()
		self.log.debug('entering default method')
		#get all ids
		all_ids = [dict.get('.id') for dict in present if dict.get('.id')]
		self.log.debug('all ids = {0}'.format(all_ids))
		#get all default ids if present
		def_ids = [dict.get('.id') for dict in present if dict.get('default')]
		self.log.debug('default ids = {0}'.format(def_ids))

		self.log.debug('present rules (before filtering out dynamic) = {0}'.format(present))
		#filter out dynamic rules
		present = [dict for dict in present if not dict.get('dynamic')]
		self.log.debug('present rules (after filtering out dynamic) = {0}'.format(present))
		# empty rules under menu level means delete everything
		if not wanted:
			return ([], [], all_ids, order)

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
		#all_ids - save_ids gives ids to remove from current menu level
		dellist = set(all_ids) - set(save_ids) - set(def_ids)
		return (addlist, setlist, dellist, order)

	def __uniqKeyNoOrder(self, wanted, present, key, offset=0, mng_def=False):
		"""
		may have default entries, they are not removable
		key is unique
		no .id menu levels can not be handeled by this method

		key (str) is uniqie key name
		offset (mixed). if int, treat first number of offset as default. if 'all' treat all found as default
		mng_def (bool) pass to 'shift' default entries
		"""
		self.log.debug('entering __uniqKeyNoOrder method')

		if isinstance(offset, int):
			#find all .ids from rules where default key is set to True, or first offset if given
			def_ids = [dic.get('.id') for dic in present if dic.get('default')] or [dic.get('.id') for dic in present[:offset]]
		else:
			#treat all found ids as default, not removable
			def_ids = [dic.get('.id') for dic in present]
		self.log.debug('default_ids = {0}'.format(def_ids))

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

		self.log.debug('shifting default entries')

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

	def _snmp_community(self, wanted, present):
		"""snmp community name must be unique"""
		self.log.debug('entering _snmp_community method')
		addlist, setlist, dellist = self.__uniqKeyNoOrder(wanted, present, 'name', mng_def=True)
		return (addlist, setlist, dellist, ())

	def _ip_service(self, wanted, present):
		"""snmp community name must be unique"""
		addlist, setlist, dellist = self.__uniqKeyNoOrder(wanted, present, 'name', offset='all')
		return ([], setlist, [], ())

	def _user(self, wanted, present):
		"""user name must be unique"""
		self.log.debug('entering _user method')
		addlist, setlist, dellist = self.__uniqKeyNoOrder(wanted, present, 'name')
		#mikrotik will not allow remving of last user with full permissions
		#add possible first
		return (addlist, setlist, dellist, ('ADD', 'SET', 'DEL'))

	def _user_group(self, wanted, present):
		"""
		group names must be uniqie
		policy can be split into list to ease up comparison
		by default first 3 groups are not removable
		"""
		self.log.debug('entering _user_group method')
		#convert present and wanted to split policy into list
		present = list(dict((k,(v.split(',') if k == 'policy' else v)) for (k,v) in inner.items()) for inner in present)
		wanted = list(dict((k,(v.split(',') if k == 'policy' else v)) for (k,v) in inner.items()) for inner in wanted)

		addlist, setlist, dellist = self.__uniqKeyNoOrder(wanted, present, 'name', offset=3)

		#convert back to original form
		addlist = list(dict((k,(','.join(v) if k == 'policy' else v)) for (k,v) in inner.items()) for inner in addlist)
		setlist = list(dict((k,(','.join(v) if k == 'policy' else v)) for (k,v) in inner.items()) for inner in setlist)

		return (addlist, setlist, dellist, ())
