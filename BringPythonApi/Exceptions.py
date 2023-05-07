from typing import Optional


class RequestFailed(Exception):
	def __init__(self, message: Optional[str] = None):
		if not message:
			message = 'Request failed'
		super().__init__(message)


class InvalidEmail(Exception):
	def __init__(self, message: Optional[str] = None):
		if not message:
			message = 'Invalid email'
		super().__init__(message)


class InvalidUser(Exception):
	def __init__(self, message: Optional[str] = None):
		if not message:
			message = 'Invalid user'
		super().__init__(message)


class InvalidCredentials(Exception):
	def __init__(self, message: Optional[str] = None):
		if not message:
			message = 'Invalid credentials'
		super().__init__(message)
