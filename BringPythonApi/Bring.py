from typing import Optional, Union, List, Dict

import requests
from requests import Response
from urllib3 import encode_multipart_formdata

from BringPythonApi.Exceptions import InvalidUser, InvalidEmail, RequestFailed, InvalidCredentials
from BringPythonApi.Item import Item
from BringPythonApi.User import User


class Bring(object):
	API_URL: str = 'https://api.getbring.com/rest/v2'
	API_KEY: str = 'cof4Nc6D8saplXjE3h3HXqHH8m7VU2i1Gs0g85Sp'

	def __init__(self, email: str, password: str):
		self._translations = dict()
		self._email = email
		self._password = password
		self._user: Optional[User] = None
		self._userItems: List = list()
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
			self.loadCatalog()
			self.loadArticles()
			self.loadUserItemDetails()
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

	def getListUsers(self) -> List:
		try:
			req = requests.get(
				url=f'{self.API_URL}/bringlists/{self._user.bringListUUID}/users',
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

	def loadUserItemDetails(self):
		try:
			req = requests.get(
				url=f'{self.API_URL}/bringlists/{self._user.bringListUUID}/details',
				headers=self._headers
			)
			if req.status_code != 200:
				raise RequestFailed('Failed getting user item details')

			data = req.json()
			for itemData in data:
				self._userItems.append(Item(**itemData))
		except:
			raise

	@property
	def userItems(self) -> List[Item]:
		return self._userItems

	@property
	def userItemsById(self) -> Dict[str, Item]:
		return {item.itemId: item for item in self._userItems}

	@property
	def userItemsByUuid(self) -> Dict[str, Item]:
		return {item.uuid: item for item in self._userItems}

	def changeUserListLanguage(self, languageCode: str) -> bool:
		try:
			req = requests.post(
				url=f'{self.API_URL}/bringusersettings/{self._user.uuid}/{self._user.bringListUUID}/listArticleLanguage',
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
		if not newPassword:
			raise RequestFailed('Cannot change password to empty string')
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

	def purchase(self, item: str, detail: Union[str, int]) -> Response:
		return requests.put(
			url=f'{self.API_URL}/bringlists/{self._user.bringListUUID}',
			headers=self._headers,
			data={
				'uuid':          self._user.bringListUUID,
				'purchase':      item,
				'specification': detail
			}
		)

	def remove(self, item: str, detail: Union[str, int]) -> Response:
		return requests.put(
			url=f'{self.API_URL}/bringlists/{self._user.bringListUUID}',
			headers=self._headers,
			data={
				'uuid':          self._user.bringListUUID,
				'remove':        item,
				'specification': detail
			}
		)

	def getItemStatistic(self, itemName: str) -> Response:
		return requests.get(
			url=f'{self.API_URL}/bringstatistics/history/list/{self._user.bringListUUID}/{itemName}',
			headers=self._headers
		)

	def getUserProfilePicture(self) -> Response:
		return requests.get(
			url=f'{self.API_URL}/bringusers/profilepictures/{self._user.publicUuid}',
			headers=self._headers
		)

	def addToRecentItems(self, item: str, detail: Union[str, int]) -> Response:
		return requests.put(
			url=f'{self.API_URL}/bringlists/{self._user.bringListUUID}',
			headers=self._headers,
			data={
				'uuid':          self._user.bringListUUID,
				'recently':      item,
				'specification': detail
			}
		)

	def emptyPurchaseList(self):
		try:
			items = self.getShoppingList()
			for item in items['purchase']:
				self.remove(item=item['name'], detail=item['specification'])
		except:
			raise

	def getShoppingList(self, translate: bool = False, translatedTo: str = None) -> Dict:
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
			url=f'{self.API_URL}/bringlists/{self._user.bringListUUID}',
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


	def changeItemCategory(self, newCategory: str, itemId: Optional[str] = '', itemUuid: Optional[str] = '') -> Response:
		if not itemId and not itemUuid:
			raise RequestFailed('Must specify either itemId or itemUuid')

		if newCategory not in self._user.listSectionOrder:
			raise RequestFailed(f'The specified category does not exist: Existing categories are {self._user.listSectionOrder}')

		if itemId:
			item = self.userItemsById.get(itemId, None)
			if not item:
				raise RequestFailed(f'Cannot find itemId "{itemId}"')
			uuid = item.uuid
		else:
			if not itemUuid in self.userItemsByUuid.keys():
				raise RequestFailed(f'Cannot find itemUuid "{itemUuid}"')
			uuid = itemUuid

		return requests.put(
			url=f'{self.API_URL}/bringlistitemdetails/{uuid}/usersection',
			headers=self._headers,
			data={
				'userSectionId': newCategory
			}
		)

	def getItemDetails(self, itemId: str) -> Response:
		headers = self._headers.copy()
		headers['content-type'] = 'multipart/form-data'
		payload = {
			'itemId': itemId,
			'listUuid': self._user.bringListUUID
		}

		return requests.post(
			url=f'{self.API_URL}/bringlistitemdetails',
			headers=headers,
			files={
				'itemId': itemId,
				'listUuid': self.user.bringListUUID
			}
		)

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


if __name__ == '__main__':
	try:
		bring = Bring(email='', password='')
	except Exception as e:
		print(f'Failed login: {e}')

