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

import operator
from distutils.version import LooseVersion

def vcmp(v1, v2, op):
	"""
	takes float | str v1, float | str v2, str op (operator can be gt, lt, ge, le, eq, ne)
	return bool
	compare v1 to v2 using op as comparison operator
	
	"""

	#cast versions to strings
	v1 = str(v1)
	v2 = str(v2)

	return getattr(operator, op)(LooseVersion(v1), LooseVersion(v2))

def typeCast(string):
	"""cast strings into possibly int, boollean"""
	try:
		ret = int(string)
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
	#put every value in ""
	log_str = ' '.join('{0}={1}'.format(k,('"{0}"'.format(v) if ' ' in str(v) else v)) for (k,v) in dictionary.items())
	return log_str
