from dataclasses import dataclass, field
from typing import Optional


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
