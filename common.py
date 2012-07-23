#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from distutils.version import StrictVersion as vcmp

def opResult(v1, v2, op):
	"""
	takes float, float, str
	return bool
	compare v1 to v2 using op as comparison operator
	"""

	v1 = str(v1)
	v2 = str(v2)
	opmap = {'gt': vcmp(v1) > vcmp(v2), 'lt': vcmp(v1) < vcmp(v2), 'ge': vcmp(v1) >= vcmp(v2), 'le': vcmp(v1) <= vcmp(v2), 'eq': vcmp(v1) == vcmp(v2), 'ne': vcmp(v1) != vcmp(v2)}
	return opmap[op]
