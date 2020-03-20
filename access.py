import time
from datetime import datetime, timedelta
from splinter import Browser
import urllib
import requests

from ToSlogin import user_name, password, api_key

class ToS_Access():

    def __init__(self):

        self._update()

        self.path = {'executable_path': r"C:\Users\ghard\Documents\chromedriver.exe"}
        self.redirect_uri = 'http://localhost/test'
        self.endpoint = r'https://api.tdameritrade.com/v1/oauth2/token'
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    def Access(self):
        if datetime.now() < self.access_exp:
            pass
        elif datetime.now() > self.access_exp and datetime.now() < self.refresh_exp:
            grant = 'refresh_token'
            self._postRequest(grant=grant)
        elif datetime.now() > self.refresh_exp:
            grant = 'authorization_code'
            self._getURLcode()
            self._postRequest(grant=grant)

    def _getURLcode(self):
        browser = Browser('chrome', **self.path, headless = True)

        built_url = 'https://auth.tdameritrade.com/auth?response_type=code&redirect_uri={0}&client_id={1}%40AMER.OAUTHAP'.format(self.redirect_uri, api_key)

        browser.visit(built_url)

        payload = {'username': user_name, 'password': password}

        browser.find_by_id('username').first.fill(payload['username'])
        browser.find_by_id('password').first.fill(payload['password'])
        browser.find_by_id('accept').first.click()
        browser.find_by_id('accept').first.click()

        time.sleep(1)

        name = browser.url
        self.parse_url = urllib.parse.unquote(name.split('code=')[1])

        browser.quit()

    def _postRequest(self, grant):

        if grant == 'authroization_code':

            payload = {'grant_type': grant,
                    'access_type': 'offline',
                    'code': self.parse_url,
                    'client_id': api_key,
                    'redirect_uri': self.redirect_uri}
        
        else:
            payload = {'grant_type': 'refresh_token',
                    'refresh_token': self.refresh_tkn,
                    'access_type': 'offline',
                    'client_id': api_key}

        authReply = requests.post(self.endpoint, headers = self.headers, data = payload)
        content = authReply.json()

        content['refresh_token_expires_in'] = datetime.now() + timedelta(seconds = content['refresh_token_expires_in'])

        content['expires_in'] = datetime.now() +timedelta(seconds = content['expires_in'])

        with open('ToS_token.txt', 'r+') as file:
            file.truncate(0)

            for line in content.values():
                file.writelines(str(line)+'\n')
        
        self._update()
    
    def _update(self):

        with open('ToS_token.txt', 'r+') as file:
            self.lines = file.readlines()

        self.access_tkn = self.lines[0].strip('\n')
        self.refresh_tkn = self.lines[1].strip('\n')
        self.access_exp = datetime.strptime(self.lines[3].strip('\n'), '%Y-%m-%d %H:%M:%S.%f')
        self.refresh_exp = datetime.strptime(self.lines[4].strip('\n'), '%Y-%m-%d %H:%M:%S.%f')

if __name__ == '__main__':
    test = ToS_Access()

    # test.Access()
    # test._getURLcode()
    test._postRequest(grant='refresh_token')
    # test._postRequest(grant='authorization_code')