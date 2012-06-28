#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from time import time
import binascii, socket, hashlib, logging

class writeError(Exception):
	def __init__(self, msg):
		self.msg = msg
		Exception.__init__(self, msg)

class readError(Exception):
	def __init__(self, msg):
		self.msg = msg
		Exception.__init__(self, msg)

class loginError(Exception):
	def __init__(self, msg):
		self.msg = msg
		Exception.__init__(self, msg)

class cmdError(Exception):
	def __init__(self, msg):
		self.msg = msg
		Exception.__init__(self, msg)

class addHostname(logging.Filter):
	def __init__(self, host):
		self.host = host
	def filter(self, record):
		record.msg = '{0}: {1}'.format(self.host, record.msg)
		return True

class rosApi:
	"""
	RouterOS API implementation.

	This class can throw exceptions:
		socket.error -> socket errors that mey be raised from socket operations
		Exception -> various predefined exceptions. see class methods for more info

	no support for .tag.
	"""
	def __init__(self, read_timeout=15, sock_timeout=10):
		"""
		takes:
		(int) sock_timeout = socket timeout (in seconds). defaults to 20
		(int) read_timeout = data read timeout (in seconds). defaults to 30. protection not to wait forever for data. may be set to 0 to disable protection.
		"""
		self.read_timeout = read_timeout
		self.sock_timeout = sock_timeout
		self.sock = None
		self.logged = False
		self.log = logging.getLogger('mcm.configurator.rosApi')

	def login(self, address, username, password='', port=8728):
		"""
		login to RouterOS via api
		takes:
			(string) address = may be fqdn or ip/ipv6 address
			(string) username = username to login
			(string) password = password to login
			(int) port = port to witch to login. defaults to 8728
		returns:
			(bool) True when logged in successfully
		exceptions:
			loginError. raised when failed to log in
		"""
		self.log.addFilter(addHostname(address))
		self.sock = socket.create_connection((address, port), self.sock_timeout)
		self.__write('/login')
		response = self.__read(parse=False)
		#check for valid response.
		#response must contain !done (as frst reply word), =ret=37 characters long response hash (as second reply word)
		if len(response) != 2 or len(response[1]) != 37:
			raise loginError('did not receive challenge response')
		chal = binascii.unhexlify((response[1].split('=')[2].encode('UTF-8')))
		md = hashlib.md5()
		md.update(b'\x00' + password.encode('UTF-8') + chal)
		self.__write('/login', False)
		self.__write('=name=' + username, False)
		self.__write('=response=00' + binascii.hexlify(md.digest()).decode('UTF-8'))
		response = self.__read(parse=False)
		#check if logged in successfully
		if response[0] != '!done':
			raise loginError('could not log in. wrong username and/or password')
		self.logged = True
		return True

	def talk(self, level, attrs={}, read_timeout=None):
		"""
		this is a shortcut (wrapper) not to use write(), read() methods one after another. simply "talk" with RouterOS.
		takes:
			(string) level. eg /ip/address/print
			(dict) or (list) attrs default {}.
				dictionary with attribute -> value. every key value pair will be passed to api in form of =name=value
				list if order matters. eg. querry, every element in list is a word in api
			(int) read_timeout defaults to self.read_timeout.
		returns:
			returns parsed response from self.read()
		exceptions:
			loginError. raised when not logged in
		"""
		if not self.logged:
			raise loginError('not logged in')
		#map bollean types to string equivalents in routeros api
		mapping = {False: 'false', True: 'true'}
		read_timeout = read_timeout or self.read_timeout
		#write level and if attrs is empty pass True to self.__write, else False
		self.level = level
		self.__write(level, not bool(attrs))
		if attrs:
			count = len(attrs)
			i = 0
			if isinstance(attrs, dict):
				for name, value in attrs.items():
					i += 1
					last = (i == count)
					#write name and value (if bool is present convert to api equivalent) cast rest as string
					self.__write('={0}={1}'.format(name, str(mapping.get(value, value))), last)
			if isinstance(attrs, list):
				for string in attrs:
					i += 1
					last = (i == count)
					self.__write(str(string), last)
		return self.__read(read_timeout=read_timeout)

	def __encodeLen(self, length):
		"""
		takes:
			(int) length of a string as parameter
		returns:
			(mixed) encoded legth
		"""
		if length < 0x80:
			length = chr(length)
		elif (length < 0x4000):
			length |= 0x8000
			length = chr((length >> 8) & 0xFF) + chr(length & 0xFF)
		elif (length < 0x200000):
			length |= 0xC00000
			length = chr((length >> 16) & 0xFF) + chr((length >> 8) & 0xFF) + chr(length & 0xFF)
		elif (length < 0x10000000):
			length |= 0xE0000000
			length = chr((length >> 24) & 0xFF) + chr((length >> 16) & 0xFF) + chr((length >> 8) & 0xFF) + chr(length & 0xFF)
		elif (length >= 0x10000000):
			length = chr(0xF0) + chr((length >> 24) & 0xFF) + chr((length >> 16) & 0xFF) + chr((length >> 8) & 0xFF) + chr(length & 0xFF)
		return length

	def __write(self, string, end=True):
		"""
		takes:
			(mixed) string to write
			(bool) end. True = send sentence end, False = wait for more data to write
		returns:
			(bool) True on success
		exceptions:
			writeError. raised when failed to send all bytes to socket
		"""
		#strip all whitechars from begining and end
		string = string.strip()
		length = len(string)
		#send encoded string length
		self.sock.send(bytes(self.__encodeLen(length), 'UTF-8'))
		#send the string itself
		result = self.sock.send(bytes(string, 'UTF-8'))
		self.log.debug('<<< {0}'.format(string))
		if result < length:
			raise writeError('error while writing to socket. {0}/{1} bytes sent'.format(result, length))
		#if end is set to bool(true) send ending character chr(0), if not send empty string.
		end = chr(0) if end else ''
		self.sock.send(bytes(end, 'UTF-8'))
		return True

	def __read(self, read_timeout=None, parse=True):
		"""
		takes:
			(bool) parse. whether to parse the response or not
			(int) read_timeout. data read timeout, defaults to self.read_timeout
		returns:
			(list) response. parsed or not depending on parse=
		exceptions:
			readError. raised when timeout is reached or failed to read all expected bytes from socket
		"""
		read_timeout = read_timeout or self.read_timeout
		response = []
		received_done = False
		timeout = time() + read_timeout
		while True:
			if (read_timeout > 0) and (time() > timeout):
				raise readError('timeout reached while reading data')
			#read encoded length
			BYTE = ord(self.sock.recv(1))
			LENGTH = 0
			if (BYTE & 128):
				if ((BYTE & 192) == 128):
						LENGTH = ((BYTE & 63) << 8) + ord(self.sock.recv(1))
				else:
					if ((BYTE & 224) == 192):
						LENGTH = ((BYTE & 31) << 8) + ord(self.sock.recv(1))
						LENGTH = (LENGTH << 8) + ord(self.sock.recv(1))
					else:
						if ((BYTE & 240) == 224):
							LENGTH = ((BYTE & 15) << 8) + ord(self.sock.recv(1))
							LENGTH = (LENGTH << 8) + ord(self.sock.recv(1))
							LENGTH = (LENGTH << 8) + ord(self.sock.recv(1))
						else:
							LENGTH = ord(self.sock.recv(1))
							LENGTH = (LENGTH << 8) + ord(self.sock.recv(1))
							LENGTH = (LENGTH << 8) + ord(self.sock.recv(1))
							LENGTH = (LENGTH << 8) + ord(self.sock.recv(1))
			else:
				LENGTH = BYTE
			retword = ''
			retlen = 0
			if LENGTH > 0:
				while retlen < LENGTH:
					#read as many data as we decoded previously
					string = self.sock.recv(LENGTH - retlen)
					retlen = len(string)
					retword += string.decode('UTF-8', 'replace')
				self.log.debug('>>> {0}'.format(retword))
				if len(retword) != LENGTH:
					raise readError('error while reading from socket. {0}/{1} bytes received'.format(len(retword), LENGTH))
				response.append(retword)
			#make a note when got !done. this marks end of transmission
			if retword == '!done':
				received_done = True
			#if we are not logged in (during initial login) and there is no more bytes to read, break the loop.
			#if we have received !done and we are logged in and no more bytes to read, break the loop
			if (not self.logged and not LENGTH) or (self.logged and not LENGTH and received_done):
				break
		if parse:
			response = self.__parseResponse(response)
		return response

	def __parseResponse(self, response=[]):
		"""
		takes:
			(list) response. response to be parsed
		returns:
			(list) or (bool) True on no error occurence. in list every data reply is a dictionary with key value pair
			(bool) False on error occurence from routeros. warning is emmited.
		exceptions:
			none
		"""
		parsed_response = []
		mapping = {'true': True, 'false': False}
		index = -1
		for word in response:
			if word in ['!trap', '!re']:
				index += 1
				parsed_response.append({})
			elif word == '!done' or word == '!fatal':
				break
			else:
				#split word by second occurence of '='
				word = word.split('=',2)
				parsed_response[index][word[1]] = self.__typeCaster(word[2])
		if '!trap' in response:
			msg = ', '.join(' '.join('{0}="{1}"'.format(k,v) for (k,v) in inner.items()) for inner in parsed_response)
			raise cmdError('{0} {1}'.format(self.level, msg))
		return parsed_response

	def __typeCaster(self, string):
		"""cast strings into possibly float, int, boollean"""
		try:
			ret = int(string)
		except ValueError:
			try:
				ret = float(string)
			except ValueError:
				mapping = {'true': True, 'false': False}
				ret = mapping.get(string, string)
		return ret

	def __del__(self):
		"""if forgot to disconnect manually do it when destroying class"""
		self.disconnect()

	def disconnect(self):
		"""
		takes:
			none
		returns:
			(bool) True
		exceptions:
			none
		"""
		#send /quit and close socket
		if self.logged and self.sock:
			self.sock.send(bytes(self.__encodeLen(5), 'UTF-8'))
			self.sock.send(bytes('/quit', 'UTF-8'))
			self.sock.send(bytes(chr(0), 'UTF-8'))
		if self.sock:
			self.sock.close()
		self.logged = False
		return True


