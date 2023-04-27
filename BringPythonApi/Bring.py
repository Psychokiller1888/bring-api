from dataclasses import dataclass, field
from typing import Optional

import requests

class RequestFailed(Exception):
	def __init__(self, message: Optional[str] = None):
		super().__init__(message)

class InvalidEmail(Exception):
	def __init__(self, message: Optional[str] = None):
		super().__init__(message)

class InvalidUser(Exception):
	def __init__(self, message: Optional[str] = None):
		super().__init__(message)

class Bring(object):

	API_URL: str = 'https://api.getbring.com/rest/v2'
	API_KEY: str = 'cof4Nc6D8saplXjE3h3HXqHH8m7VU2i1Gs0g85Sp'

	def __init__(self, email: str, password: str):
		self._email = email
		self._password = password
		self._user: Optional[User] = None
		self._headers = {
			'x-bring-api-key': self.API_KEY,
			'x-bring-client': 'webApp'
		}
		try:
			self.checkEmail(self._email)
			self._headers['Content-Type'] = 'application/x-www-form-urlencoded'
			self.login()
			self.getUserProfile()
			self.getUserData()
		except:
			raise


	def checkEmail(self, email: Optional[str] = None) -> bool:
		email = email or self._email
		try:
			req = requests.get(
				url=f'{self.API_URL}/bringauth/checkemail?email={email}',
				headers=self._headers
			)
			if req.status_code != 200:
				raise RequestFailed('URL not found')
			data = req.json()
			if not data['emailValid']:
				raise InvalidEmail('Invalid email')
			elif not data['userExists']:
				raise InvalidUser('Invalid user')
			else:
				return True
		except:
			raise

	def login(self) -> bool:
		try:
			req = requests.post(
				url=f'{self.API_URL}/bringauth',
				headers=self._headers,
				data={
					'email': self._email,
					'password': self._password
				}
			)
			if req.status_code != 200:
				raise RequestFailed('Email or password invalid')
			data = req.json()
			self._user = User(**data)
			self._headers['Authorization'] = f'{self._user.token_type} {self._user.access_token}'
			return True
		except:
			raise


	def getUserProfile(self) -> bool:
		try:
			req = requests.get(
				url=f'{self.API_URL}/bringusers/profiles/{self._user.publicUuid}',
				headers=self._headers
			)
			if req.status_code != 200:
				raise RequestFailed('Failed getting user profile')
			data = req.json()
			self._user.pushEnabled = data['pushEnabled']
			self._user.plusTryOut = data['plusTryOut']
			self._user.country = data['country']
			self._user.language = data['language']
			self._headers['x-bring-country'] = self._user.country
			return True
		except:
			raise


	def getUserData(self) -> bool:
		try:
			req = requests.get(
				url=f'{self.API_URL}/bringusers/{self._user.uuid}',
				headers=self._headers
			)
			if req.status_code != 200:
				raise RequestFailed('Failed getting user data')
			data = req.json()
			self._user.premiumConfiguration = data['premiumConfiguration']
			print(self._user)
			return True
		except:
			raise


@dataclass
class User(object):
	uuid: str
	publicUuid: str
	email: str
	name: str
	photoPath: str
	bringListUUID: str
	access_token: str
	refresh_token: str
	token_type: str
	expires_in: int
	pushEnabled: Optional[bool] = False
	plusTryOut: Optional[bool] = False
	country: Optional[str] = ''
	language: Optional[str] = 'en'
	premiumConfiguration: Optional[dict] = field(default_factory=dict)

if __name__ == '__main__':
	try:
		bring = Bring(email='laurentchervet@bluewin.ch', password='')
	except Exception as e:
		print(f'Failed login: {e}')
