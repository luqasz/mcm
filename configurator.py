#!/usr/bin/python3 -B
# -*- coding: UTF-8 -*-

#~ compare dicts
#~ a = {'x': 1, 'y': 2}
#~ b = {'y': 2, 'x': 1}
#~ dict(set(iter(a.items()))-set(iter(b.items())))

#lista z sekcjami menu: wartocsia kazdego wpisu jest slownik
#	atrybuty z xmla
#	klucz rules > sekcje rule: wartosc lista. wartoscia kazdego wpisu z listy jest slownik
#		atrybuty z xmla dla rule
#		defs >: slownik z definicjami rulesa
#			slownik (wartosci maja byc mapowane na bolean)

import rosApi

class configurator:
	"""
	configure mikrotik
	"""

	def __init__(self, api):
		self.api = api

	def configure(self, config):

