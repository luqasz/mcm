#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from distutils.version import StrictVersion

def vcmp(v1, v2, op):
	"""
	takes float, float, str
	return bool
	compare v1 to v2 using op as comparison operator
	"""

	v1 = str(v1)
	v2 = str(v2)
	opmap = {'==': 'eq', '>': 'gt', '<': 'lt', '>=': 'ge', '<=': 'le', '!=': 'ne'}
	op = opmap.get(op, op)

	result_map = {'gt': StrictVersion(v1) > StrictVersion(v2), 'lt': StrictVersion(v1) < StrictVersion(v2), 'ge': StrictVersion(v1) >= StrictVersion(v2), 'le': StrictVersion(v1) <= StrictVersion(v2), 'eq': StrictVersion(v1) == StrictVersion(v2), 'ne': StrictVersion(v1) != StrictVersion(v2)}

	return result_map[op]

def typeCast(string):
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

def dictStr (dictionary):
	"""
	convert dictionary to string ready for logging. key="value"
	replace 'password' key value when updaing password for users
	map bollean to more human readable form
	"""
	mapping = {True:'yes', False:'no'}
	#map bollean to more human readable form
	dictionary = dict((k, mapping.get(v, v)) for (k,v) in dictionary.items())
	#replace password value with '***' in dictionary if present
	if 'password' in dictionary:
		dictionary = dict((k,'***' if k == 'password' else v) for (k,v) in dictionary.items())

	log_str = ' '.join('{0}={1}'.format(k,('"{0}"'.format(v) if ' ' in v else v)) for (k,v) in dictionary.items())
	return log_str
