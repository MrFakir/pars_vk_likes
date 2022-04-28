import json

import requests
from backend.settings import headers, API_V_INST
from data.auth_data.auth_instagram import id_acc_instagram, id_page_facebook, client_id_app, secret_id_app


class InstagramAPI:
    def __init__(self):
        with open('inst_token.txt') as file:
            self.access_token = file.read()

    def get_com_data(self):
        url = f'https://graph.facebook.com/{API_V_INST}/me/accounts'
        params = {
            'access_token': self.access_token
        }

        req = requests.get(url=url, params=params, headers=headers)
        print(req.text)
        with open('token_com_data.json', 'w', encoding='UTF-8') as file:
            json.dump(req.json(), file, indent=4, ensure_ascii=False)

    def get_media(self):
        url = f'https://graph.facebook.com/{API_V_INST}/{id_acc_instagram}/media'
        params = {
            'access_token': self.access_token
        }
        req = requests.get(url=url, params=params, headers=headers)
        print(req.json())


def main():
    inst_obj = InstagramAPI()
    inst_obj.get_media()


if __name__ == '__main__':
    main()
