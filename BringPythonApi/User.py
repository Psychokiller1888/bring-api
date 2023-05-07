import json
from dataclasses import dataclass, field
from typing import Optional

from BringPythonApi.BringList import BringList


@dataclass
class User(object):
	publicUuid: str
	email: str
	name: str
	photoPath: str
	uuid: Optional[str] = ''
	bringListUUID: Optional[str] = ''  # This is returned by auth, seems to be the default list uuid
	pushEnabled: Optional[bool] = False
	plusTryOut: Optional[bool] = False
	access_token: Optional[str] = ''
	refresh_token: Optional[str] = ''
	token_type: Optional[str] = ''
	expires_in: Optional[str] = ''
	country: Optional[str] = ''
	language: Optional[str] = 'en'
	premiumConfiguration: Optional[dict] = field(default_factory=dict)
	userSettings: Optional[dict] = field(default_factory=dict)
	autoPush: Optional[str] = 'ON'
	defaultListUUID: Optional[str] = ''
	suggestedSpecifications: Optional[str] = 'ON'
	onboardClient: Optional[str] = 'webApp'
	purchaseStyle: Optional[str] = 'grouped'
	listSectionOrder: Optional[list] = field(default_factory=list)
	listArticleLanguage: Optional[str] = ''
	lists: Optional[list] = field(default_factory=list)

	def initSettings(self, data: dict):
		for userSetting in data.get('usersettings', dict()):
			setattr(self, userSetting['key'], userSetting['value'])
		for userSetting in data.get('userlistsettings', dict())[0].get('usersettings', dict()):
			try:
				value = json.loads(userSetting['value'])
			except:
				value = userSetting['value']

			setattr(self, userSetting['key'], value)

	def setLists(self, data: list):
		for entry in data:
			self.lists.append(BringList(**entry))

	def getDefaultList(self) -> Optional[BringList]:
		return self.listsByUuid.get(self.defaultListUUID, None)

	def getList(self, name: str = '', uuid: str = '') -> Optional[BringList]:
		if not name and not uuid:
			raise Exception('Cannot get list without either name or uuid')

		if uuid:
			return self.listsByUuid.get(uuid, None)
		else:
			return self.listsByName.get(name, None)

	@property
	def listsByUuid(self) -> dict:
		return {bringList.listUuid: bringList for bringList in self.lists}

	@property
	def listsByName(self) -> dict:
		return {bringList.name: bringList for bringList in self.lists}
