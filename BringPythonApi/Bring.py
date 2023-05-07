from typing import Optional, Union, List, Dict

import requests
from requests import Response
from urllib3 import encode_multipart_formdata

from BringPythonApi.Exceptions import InvalidUser, InvalidEmail, RequestFailed, InvalidCredentials
from BringPythonApi.User import User


class Bring(object):
	API_URL: str = 'https://api.getbring.com/rest/v2'
	API_KEY: str = 'cof4Nc6D8saplXjE3h3HXqHH8m7VU2i1Gs0g85Sp'
	BOUNDARY: str = '----------BRING-PYTHON-API--'

	def __init__(self, email: str, password: str):
		self._translations = dict()
		self._email = email
		self._password = password
		self._user: Optional[User] = None
		self._headers = {
			'content-type':    'application/x-www-form-urlencoded; charset=UTF-8',
			'x-bring-api-key': self.API_KEY,
			'x-bring-client':  'webApp'
		}
		try:
			self.checkEmail(self._email)
			self.login()
			self.getUserProfile()
			self.getUserData()
			self.getUserSettings()
			self.getUserLists()
			self.loadUserListsDetails()
			self.loadCatalog()
			self.loadArticles()
		except:
			raise

	@property
	def user(self) -> User:
		return self._user

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
					'email':    self._email,
					'password': self._password
				}
			)
			if req.status_code != 200:
				raise InvalidCredentials()
			data = req.json()
			self._user = User(**data)
			self._headers['Authorization'] = f'{self._user.token_type} {self._user.access_token}'
			self._headers['cookie'] = f'refresh_token={self._user.refresh_token}'
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

	def getUserLists(self) -> bool:
		try:
			req = requests.get(
				url=f'{self.API_URL}/bringusers/{self._user.uuid}/lists',
				headers=self._headers
			)
			if req.status_code != 200:
				raise RequestFailed('Failed getting user lists')
			self._user.setLists(req.json()['lists'])
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

	def getListUsers(self, listUuid: Optional[str] = '') -> List:
		try:
			if not listUuid:
				listUuid = self._user.defaultListUUID

			req = requests.get(
				url=f'{self.API_URL}/bringlists/{listUuid}/users',
				headers=self._headers
			)
			if req.status_code != 200:
				raise RequestFailed('Failed getting list users')
			data = req.json()
			ret = list()
			for userData in data['users']:
				ret.append(User(**userData))
			return ret
		except:
			raise

	def getUserSettings(self) -> bool:
		try:
			req = requests.get(
				url=f'{self.API_URL}/bringusersettings/{self._user.uuid}',
				headers=self._headers
			)
			if req.status_code != 200:
				raise RequestFailed('Failed getting user settings')
			self._user.initSettings(req.json())
			return True
		except:
			raise

	def loadUserListsDetails(self):
		try:
			for listUuid, bringList in self._user.listsByUuid.items():
				req = requests.get(
					url=f'{self.API_URL}/bringlists/{listUuid}/details',
					headers=self._headers
				)
				if req.status_code != 200:
					raise RequestFailed(f'Failed getting user list details for list {listUuid}')

				bringList.setItems(req.json())
		except:
			raise

	def loadCatalog(self, locale: str = None):
		locale = locale or self._user.listArticleLanguage
		data = self._getWebData(url='catalog', locale=locale)
		for section in data['catalog']['sections']:
			self._translations[locale]['sections'][section['sectionId']] = section['name']
			for item in section['items']:
				self._translations[locale]['items'][item['itemId']] = item['name']

	def loadArticles(self, locale: str = None):
		locale = locale or self._user.listArticleLanguage
		data = self._getWebData(url='articles', locale=locale)
		for itemId, name in data.items():
			self._translations[locale]['items'][itemId] = name

	def _getWebData(self, url: str, locale: str) -> Dict:
		req = requests.get(
			url=f'https://web.getbring.com/locale/{url}.{locale}.json',
			headers=self._headers
		)
		if req.status_code != 200:
			raise RequestFailed(f'Failed getting "{url}" web data')

		self._translations.setdefault(locale, dict())
		self._translations[locale].setdefault('sections', dict())
		self._translations[locale].setdefault('items', dict())

		return req.json()

	def changeUserListLanguage(self, languageCode: str, listUuid: Optional[str] = '') -> bool:
		"""
		Changes a list's language

		:param languageCode: The standard country-language code
		:param listUuid: The list to change the language
		:returns Requests.Response
		"""
		try:
			if not listUuid:
				listUuid = self._user.defaultListUUID

			req = requests.post(
				url=f'{self.API_URL}/bringusersettings/{self._user.uuid}/{listUuid}/listArticleLanguage',
				headers=self._headers,
				data={
					'value': languageCode
				}
			)
			if req.status_code != 200:
				raise RequestFailed('Failed changing user language')

			self._user.listArticleLanguage = languageCode
			return True
		except:
			raise

	def changeUserPassword(self, newPassword: str) -> bool:
		"""
		Changes the account password

		:param newPassword: The new password
		:returns Requests.Response
		"""
		if not newPassword:
			raise RequestFailed('Cannot change password to empty')
		try:
			req = requests.post(
				url=f'{self.API_URL}/bringusers/{self._user.uuid}/password',
				headers=self._headers,
				data={
					'password': newPassword
				}
			)
			if req.status_code != 200:
				raise RequestFailed('Failed changing user password')

			return True
		except:
			raise

	def purchase(self, item: str, detail: Union[str, int], listUuid: Optional[str] = '') -> Response:
		"""
		Puts an item in your purchase list

		:param item: The item name you wish to buy
		:param detail: The amount or any detail to write with the item
		:param listUuid: The list to add to
		:returns Requests.Response
		"""
		if not listUuid:
			listUuid = self._user.defaultListUUID

		return requests.put(
			url=f'{self.API_URL}/bringlists/{listUuid}',
			headers=self._headers,
			data={
				'uuid':          self._user.bringListUUID,
				'purchase':      item,
				'specification': detail
			}
		)

	def remove(self, item: str, detail: Optional[Union[str, int]] = 9999999, listUuid: Optional[str] = '') -> Response:
		"""
		Remove an item from a list. If no list provided, removes from your default list

		:param item: The item name you wish to remove
		:param detail: The amount you want to remove
		:param listUuid: The list to remove from
		:returns Requests.Response
		"""
		if not listUuid:
			listUuid = self._user.defaultListUUID

		return requests.put(
			url=f'{self.API_URL}/bringlists/{listUuid}',
			headers=self._headers,
			data={
				'uuid':          self._user.bringListUUID,
				'remove':        item,
				'specification': detail
			}
		)

	def getItemStatistic(self, itemName: str, listUuid: Optional[str] = '') -> Response:
		"""
		Returns the specified item's statistics

		:param itemName: The item name
		:param listUuid: The list to take the item from
		:returns Requests.Response
		"""
		if not listUuid:
			listUuid = self._user.defaultListUUID

		return requests.get(
			url=f'{self.API_URL}/bringstatistics/history/list/{listUuid}/{itemName}',
			headers=self._headers
		)

	def getUserProfilePicture(self) -> Response:
		"""
		Returns the user profile picture

		:returns Requests.Response
		"""
		return requests.get(
			url=f'{self.API_URL}/bringusers/profilepictures/{self._user.publicUuid}',
			headers=self._headers
		)

	def addToRecentItems(self, item: str, detail: Union[str, int], listUuid: Optional[str] = '') -> Response:
		"""
		Adds an item to the recent items list

		:param item: The item name you wish to add
		:param detail: The amount or any detail you want to add
		:param listUuid: The list to add to
		:returns Requests.Response
		"""
		if not listUuid:
			listUuid = self._user.defaultListUUID

		return requests.put(
			url=f'{self.API_URL}/bringlists/{listUuid}',
			headers=self._headers,
			data={
				'uuid':          self._user.bringListUUID,
				'recently':      item,
				'specification': detail
			}
		)

	def emptyPurchaseList(self, listUuid: Optional[str] = ''):
		"""
		Empties a shopping list
		:param listUuid: The list to empty
		:returns Requests.Response
		"""
		if not listUuid:
			listUuid = self._user.defaultListUUID

		try:
			items = self.getShoppingList(listUuid=listUuid)
			for item in items['purchase']:
				self.remove(item=item['name'], detail=item['specification'], listUuid=listUuid)
		except:
			raise

	def getShoppingList(self, listUuid: Optional[str] = '', translate: bool = False, translatedTo: str = None) -> Dict:
		"""
		Returns a shopping list, translated if required

		:param listUuid: The list to remove from
		:param translate: Whether to translate the items or not
		:param translatedTo: The standard country-language code to translate to, example "fr-CH"
		:returns Dictionary of items, in two categories "purchased" and "recently"
		"""
		if not listUuid:
			listUuid = self._user.defaultListUUID

		if translatedTo:
			translate = True

		if translate:
			translatedTo = translatedTo or self._user.listArticleLanguage
		else:
			translatedTo = 'de-CH'

		if translatedTo not in self._translations.keys():
			self.loadCatalog(locale=translatedTo)
			self.loadArticles(locale=translatedTo)

		req = requests.get(
			url=f'{self.API_URL}/bringlists/{listUuid}',
			headers=self._headers
		)

		if req.status_code != 200:
			raise RequestFailed('Failed getting shopping list')

		items = req.json()
		ret = dict()
		ret['purchase'] = list()
		ret['recently'] = list()
		for item in items['purchase']:
			ret['purchase'].append({
				'name':          self._translations[translatedTo]['items'].get(item['name'], item['name']) if translate else item['name'],
				'specification': item['specification']
			})

		for item in items['recently']:
			ret['recently'].append({
				'name':          self._translations[translatedTo]['items'].get(item['name'], item['name']) if translate else item['name'],
				'specification': item['specification']
			})

		return ret

	def changeItemCategory(self, newCategory: str, itemUuid: str) -> Response:
		"""
		Changes the specified item's category

		:param newCategory: The __existing__ category name to move the item to
		:param itemUuid: The item uuid to move
		:returns Requests.Response
		"""
		if newCategory not in self._user.listSectionOrder:
			raise RequestFailed(f'The specified category does not exist: Existing categories are {self._user.listSectionOrder}')

		return requests.put(
			url=f'{self.API_URL}/bringlistitemdetails/{itemUuid}/usersection',
			headers=self._headers,
			data={
				'userSectionId': newCategory
			}
		)

	def createNewList(self, listName: str, theme: Optional[str] = 'ch.publisheria.bring.theme.home') -> Response:
		"""
		Creates a new list on your account

		:param listName: The name of the new list
		:param theme: Used by the web app as a background
		:returns Requests.Response
		"""

		response = requests.post(
			url=f'{self.API_URL}/bringusers/{self.user.uuid}/lists',
			headers=self._headers,
			data={
				'name': listName,
				'theme': theme
			}
		)

		if response.status_code == 200:
			self.user.setLists(data=[{'listUuid': response.json()['bringListUUID'], 'name': listName, 'theme': theme}])

		return response

	def getItemDetails(self, itemId: str, listUuid: Optional[str] = '') -> Response:
		if not listUuid:
			listUuid = self._user.defaultListUUID

		headers = self._headers.copy()

		payload = {
			'itemId':   itemId,
			'listUuid': listUuid
		}

		payload, contentType = encode_multipart_formdata(payload, boundary=self.BOUNDARY)
		headers['Content-Type'] = contentType

		print(headers)

		# payload = f'{self.BOUNDARY}\n'
		# for item, value in content.items():
		# 	payload += f'Content-Disposition: form-data; name="{item}";\n\n'
		# 	payload += f'{value}\n'
		# 	payload += f'{self.BOUNDARY}\n'

		return requests.request(
			method='POST',
			url=f'{self.API_URL}/bringlistitemdetails',
			data=payload,
			headers=headers
		)

	def sendMagicLink(self, email: Optional[str] = '') -> Response:
		"""
		If logging via a browser, you may login with a magic link instead of a password

		:param email: The email address of the account
		:returns Requests.Response
		"""
		if not email and not self._user:
			raise RequestFailed('Cannot request magic link without user or email')

		if not email:
			email = self._user.email

		headers = self._headers.copy()
		headers.pop('x-bring-country', None)
		headers.pop('x-bring-user-uuid', None)
		headers.pop('x-bring-api-key', None)

		return requests.post(
			url=f'{self.API_URL}/bringauth/magiclink',
			headers=headers,
			data={
				'email': email
			}
		)
