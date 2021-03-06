import requests


class Request:
    def __init__(self, secret, api):
        self.secret = secret
        self.api = api

    def hello(self):
        response = requests.get(self.api + '/hello')
        return response.text

    def getUser(self, telegramId):
        response = requests.get(self.api + '/users/' + str(telegramId), headers={'x-api-key': self.secret})
        return response

    def postUser(self, telegramId, name, age, phone):
        response = requests.post(self.api + '/users',
                                 json={'name': name, 'telegramId': telegramId, 'phone': phone, 'age': age},
                                 headers={'x-api-key': self.secret, 'Content-Type': 'application/json'})
        return response.status_code

    def removeUser(self, telegramId):
        id = self.getUser(telegramId).json().get('user').get('id')
        response = requests.delete(self.api + '/users/' + str(id), headers={'x-api-key': self.secret})
        return response.status_code

    def changeUser(self, telegramId, name, age, phone):
        id = self.getUser(telegramId).json().get('user').get('id')
        response = requests.patch(self.api + '/users/' + str(id), json={'name': name, 'phone': phone, 'age': age},
                                  headers={'x-api-key': self.secret})
        return response.status_code

    def addBarCode(self, telegramId, barCode):
        id = self.getUser(telegramId).json().get('user').get('id')
        response = requests.patch(self.api + '/users/' + str(id), json={'qr': barCode},
                                  headers={'x-api-key': self.secret})
        return response.status_code

    def getEvents(self):
        response = requests.get(self.api + '/events/', headers={'x-api-key': self.secret})
        return response

    def getEventById(self, eventId):
        response = requests.get(self.api + '/events/' + str(eventId), headers={'x-api-key': self.secret})
        return response

    def getEventsUsers(self, eventId):
        id = self.getEventById(eventId).json().get('id')
        response = requests.get(self.api + '/events/' + str(id) + '/users', headers={'x-api-key': self.secret})
        return response

    def postUserOnEvent(self, telegramId, eventId):
        id = self.getUser(telegramId).json().get('user').get('id')
        response = requests.post(self.api + '/users-on-events?userId=' + str(id) + '&eventId=' + str(eventId),
                                 headers={'x-api-key': self.secret})
        return response.status_code

    def deleteUserOnEvent(self, telegramId, eventId):
        id = self.getUser(telegramId).json().get('user').get('id')
        response = requests.delete(self.api + '/users-on-events?userId=' + str(id) + '&eventId=' + str(eventId),
                                   headers={'x-api-key': self.secret})
        return response.status_code

    def getUsersEvents(self, telegramId):
        id = self.getUser(telegramId).json().get('user').get('id')
        response = requests.get(self.api + '/users/' + str(id) + '/events', headers={'x-api-key': self.secret})
        return response

    def getPlaceOfEvent(self, placeId):
        response = requests.get(self.api + '/place/' + str(placeId), headers={'x-api-key': self.secret})
        return response

