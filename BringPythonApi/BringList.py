from dataclasses import dataclass, field
from typing import Optional

from BringPythonApi.Item import Item


@dataclass
class BringList(object):
	listUuid: str
	name: Optional[str] = ''
	theme: Optional[str] = ''
	items: Optional[list] = field(default_factory=list)

	def setItems(self, data: list):
		for itemData in data:
			self.items.append(Item(**itemData))
