class writeError(Exception):
	def __init__(self, msg):
		Exception.__init__(self, msg)

class readError(Exception):
	def __init__(self, msg):
		Exception.__init__(self, msg)

class cmdError(Exception):
	def __init__(self, msg):
		Exception.__init__(self, msg)

class apiError(Exception):
	def __init__(self, msg):
		Exception.__init__(self, msg)

class loginError(Exception):
	def __init__(self, msg):
		Exception.__init__(self, msg)

