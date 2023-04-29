import json
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Item(object):
	uuid: str
	itemId: str
	listUuid: str
	userIconItemId: str
	userSectionId: str
	assignedTo: str
	imageUrl: str
