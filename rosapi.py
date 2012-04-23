#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from time import time
import binascii, socket, hashlib

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

class rosapi:
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

	def login(self, address, username, password, port=8728, saddr=0, sport=0):
		"""
		login to RouterOS via api
		takes:
			(string) address = may be fqdn or ip/ipv6 address
			(string) username = username to login
			(string) password = password to login
			(int) port = port to witch to login. defaults to 8728
			(int) saddr = source address defaults to 0
			(int) sport = source port defaults to 0
		returns:
			(bool) True when logged in successfully
		exceptions:
			loginError. raised when failed to log in
		"""
		self.sock = socket.create_connection((address, port), self.sock_timeout, (str(saddr), sport))
		self.write('/login')
		response = self.read(parse=False)
		#check for valid response.
		#response must contain !done (as frst reply word), =ret=37 characters long response hash (as second reply word)
		if len(response) != 2 or len(response[1]) != 37:
			raise loginError('did not receive challenge response')
		chal = binascii.unhexlify((response[1].split('=')[2].encode('UTF-8')))
		md = hashlib.md5()
		md.update(b'\x00' + password.encode('UTF-8') + chal)
		self.write('/login', False)
		self.write('=name=' + username, False)
		self.write('=response=00' + binascii.hexlify(md.digest()).decode('UTF-8'))
		response = self.read(parse=False)
		#check if logged in successfully
		if response[0] != '!done':
			raise loginError('wrong username and/or password')
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
		#write level and if attrs is empty pass True to self.write, else False
		self.write(level, not bool(attrs))
		if attrs:
			count = len(attrs)
			i = 0
			if isinstance(attrs, dict):
				for name, value in attrs.items():
					i += 1
					last = (i == count)
					#write name and value (if bool is present convert to api equivalent) and cast it as string
					self.write('=' + name + '=' + str(mapping.get(value, value)), last)
			if isinstance(attrs, list):
				for string in attrs:
					i += 1
					last = (i == count)
					self.write(str(string), last)
		return self.read(read_timeout=read_timeout)

	def encodeLen(self, length):
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

	def write(self, string, end=True):
		"""
		takes:
			(mixed) string to write
			(bool) end. True = send sentence end, False = wait for more data to write
		returns:
			(bool) True on success
		exceptions:
			writeError. raised when failed to send all bytes to socket
		"""
		length = len(string)
		#send encoded string length
		self.sock.send(bytes(self.encodeLen(length), 'UTF-8'))
		#send the string itself
		result = self.sock.send(bytes(string, 'UTF-8'))
		if result < length:
			raise writeError('error while writing to socket. ' + result + '/' + length + ' bytes sent')
		#if end is set to bool(true) send ending character chr(0), if not send empty string.
		end = chr(0) if end else ''
		self.sock.send(bytes(end, 'UTF-8'))
		return True

	def read(self, read_timeout=None, parse=True):
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
				if len(retword) != LENGTH:
					raise readError('error while reading from socket. ' + len(retword) + '/' + LENGTH + ' bytes received')
				response.append(retword)
			#make a note when got !done. this marks end of transmission
			if retword == '!done':
				received_done = True
			#if we are not logged in (during initial login) and there is no more bytes to read, break the loop.
			#if we have received !done and we are logged in and no more bytes to read, break the loop
			if (not self.logged and not LENGTH) or (self.logged and not LENGTH and received_done):
				break
		if parse:
			response = self.parse_response(response)
		return response

	def parse_response(self, response=[]):
		"""
		takes:
			(list) response. response to be parsed
		returns:
			(list) on no error occurence. in list every data reply is a dictionary with key value pair
			(bool) False on error occurence from routeros. self.last_error contains all error messages from routeros
		exceptions:
			none
		"""
		parsed_response = []
		mapping = {'true': True, 'false': False}
		self.last_error = []
		is_error = False
		index = -1
		for word in response:
			if word == '!done':
				break
			elif word == '!re':
				index += 1
				parsed_response.append({})
			elif word == '!trap':
				is_error = True
			elif parsed_response:
				#strip first = char from word. then split it with first occurence of '='
				word = word.lstrip('=').split('=',1)
				parsed_response[index][word[0]] = mapping.get(word[1], word[1])
			elif is_error:
				self.last_error.append(word[1:])
		if self.last_error:
			sep = ', '
			self.last_error = sep.join(last_error)
			return False
		elif len(parsed_response) == 0:
			return True
		elif parsed_response:
			return parsed_response

	def disconnect(self):
		"""
		takes:
			none
		returns:
			(bool) True
		exceptions:
			none
		"""
		#send /quit and close socket if socket still exists
		if self.sock and self.logged:
			self.sock.send(bytes(self.encodeLen(5), 'UTF-8'))
			self.sock.send(bytes('/quit', 'UTF-8'))
			self.sock.send(bytes(chr(0), 'UTF-8'))
			self.sock.close()
		self.logged = False
		return True


