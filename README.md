## Bring Python API

This is an unofficial python API for Bring! the shopping list service, based on their webapi. Some endpoints might be missing, this is solely based on traffic capture while using the web app.


### API doc
You'll find the API documentation on this page: https://psychokiller1888.github.io/bring-api/

Please note that sme endpoints might be missing

### Insomnia repository
Import the repository in your Insomnia app: https://github.com/Psychokiller1888/bring-api/tree/master

### Usage

- Import the package in your project
- Create a Bring instance by passing your login and password to use the API:

```python
from BringPythonApi.Bring import Bring

try:
    bring = Bring(email='foo@bar.com', password='foobar')
except Exception as e:
    print(f'Error logging in: {e}')
else:
    # Add an item to your default list
    bring.purchase(item='Milk', detail='3 liters')
    
    # Remove 1 cat food from your default list
    bring.remove(item='Cat food', detail=1)
    
    # Empty your list called "My work list". If no name provided, defaults to you default list
    bring.emptyPurchaseList(listUuid=bring.user.getList(name='My work list'))

    # Change the default list language
    bring.changeUserListLanguage(languageCode='en-US')

    # Change the account password
    bring.changeUserPassword(newPassword='myNewPassword')

    # Get stats for Cat food
    bring.getItemStatistic(itemName='Cat food')

    # Get profile picture
    bring.getUserProfilePicture()

    # Add item to recent list
    bring.addToRecentItems(item='Milk', detail='2 liters')
    
    # Get my work shopping list
    bring.getShoppingList(listUuid=bring.user.getList(name='Work list'))
    
    # Move cucumber to another category
    bring.changeItemCategory(newCategory='Eigene Artikel')
```
