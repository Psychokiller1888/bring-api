import json
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class User(object):
	publicUuid: str
	email: str
	name: str
	photoPath: str
	uuid: Optional[str] = ''
	bringListUUID: Optional[str] = ''
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


	def initSettings(self, data: dict):
		for userSetting in data.get('usersettings', dict()):
			setattr(self, userSetting['key'], userSetting['value'])
		for userSetting in data.get('userlistsettings', dict())[0].get('usersettings', dict()):
			try:
				value = json.loads(userSetting['value'])
			except:
				value = userSetting['value']

			setattr(self, userSetting['key'], value)
