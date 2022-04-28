import json

import requests
from backend.settings import API_V_INST
from data.auth_data.auth_instagram import id_acc_instagram, id_page_facebook, client_id_app, secret_id_app

token_from_web = ''


class InstToken:
    def __init__(self):
        self.api_v = API_V_INST

    def get_long_token(self):
        params = {
            'grant_type': 'fb_exchange_token',
            'client_id': client_id_app,
            'client_secret': secret_id_app,
            'fb_exchange_token': token_from_web
        }

        url = f'https://graph.facebook.com/{self.api_v}/oauth/access_token'

        data = requests.get(url, params)
        long_lived_token = json.loads(data.content)
        print(long_lived_token)
        access_token = long_lived_token['access_token']
        with open('inst_token.txt', 'w') as file:
            file.write(access_token)

    def check_token(self):
        with open('inst_token.txt') as file:
            access_token = file.read()
        params = {
            'input_token': access_token,
            'access_token': access_token,
        }

        url = f'https://graph.facebook.com/{self.api_v}/debug_token'

        data = requests.get(url=url, params=params)
        print(data.json())


def main():
    token_obj = InstToken()
    token_obj.check_token()


if __name__ == '__main__':
    main()