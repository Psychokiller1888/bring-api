from typing import Optional, Union

import requests
from requests import Response

from BringPythonApi.Exceptions import InvalidUser, InvalidEmail, RequestFailed, InvalidCredentials
from BringPythonApi.User import User


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
				raise RequestFailed()
			data = req.json()
			if not data['emailValid']:
				raise InvalidEmail()
			elif not data['userExists']:
				raise InvalidUser()
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
				raise InvalidCredentials()
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
			return True
		except:
			raise


	def purchase(self, item: str, detail: Union[str, int]) -> Response:
		return requests.put(
			url=f'{self.API_URL}/bringlists/{self._user.bringListUUID}',
			headers=self._headers,
			data={
				'uuid': self._user.bringListUUID,
				'purchase': item,
				'specification': detail
			}
		)


	def remove(self, item: str, detail: Union[str, int]) -> Response:
		return requests.put(
			url=f'{self.API_URL}/bringlists/{self._user.bringListUUID}',
			headers=self._headers,
			data={
				'uuid': self._user.bringListUUID,
				'remove': item,
				'specification': detail
			}
		)


	def addToRecentItems(self, item: str, detail: Union[str, int]) -> Response:
		return requests.put(
			url=f'{self.API_URL}/bringlists/{self._user.bringListUUID}',
			headers=self._headers,
			data={
				'uuid': self._user.bringListUUID,
				'recently': item,
				'specification': detail
			}
		)


	def emptyPurchaseList(self):
		req = self.getShoppingList()
		if req.status_code != 200:
			raise RequestFailed

		for item in req.json()['purchase']:
			self.remove(item=item['name'], detail=item['specification'])


	def getShoppingList(self) -> Response:
		return requests.get(
			url=f'{self.API_URL}/bringlists/{self._user.bringListUUID}',
			headers=self._headers
		)

if __name__ == '__main__':
	try:
		bring = Bring(email='laurentchervet@bluewin.ch', password='SOqMil')
		bring.emptyPurchaseList()
	except Exception as e:
		print(f'Failed login: {e}')
