import json

import requests
from backend.settings import headers
from data.auth_data.auth_instagram import id_acc_instagram, id_page_facebook, client_id_app, secret_id_app

with open('inst_token.txt') as file:
    access_token = file.read()

url_1 = 'https://graph.facebook.com/v13.0/me/accounts'
params_url_1 = {
    'access_token': access_token
}

req = requests.get(url=url_1, params=params_url_1, headers=headers)
print(req.text)
with open('token.json', 'w', encoding='UTF-8') as file:
    json.dump(req.json(), file, indent=4, ensure_ascii=False)
