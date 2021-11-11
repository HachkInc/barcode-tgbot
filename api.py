import requests

class Request:
    def __init__(self, secret, api):
        self.secret = secret
        self.api = api

    def hello(self):
        response = requests.get(self.api + '/hello')
        return response.text

    def getUser(self, id):
        response = requests.get(self.api + '/users/' + str(id),  headers={'x-api-key': self.secret})
        return response.text