import json

import requests
from backend.settings import headers, API_V_INST
from data.auth_data.auth_instagram import id_acc_instagram


class InstagramAPI:
    def __init__(self):
        with open('inst_token.txt') as file:
            self.access_token = file.read()
        self.endpoint = {
            'main_url': 'https://graph.facebook.com',
            'vers': '/' + API_V_INST,
            'id': '/' + id_acc_instagram,
            'media': '/media',
            'get_com_data': '/me/accounts',
            'check_post_limit': '/content_publishing_limit',
            'post_container': '/media_publish'
        }
        self.endpoint['com'] = self.endpoint['main_url'] + self.endpoint['vers'] + self.endpoint['id']
        self.id_container = None

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
        url = self.endpoint['com'] + self.endpoint['media']
        params = {
            'access_token': self.access_token
        }
        req = requests.get(url=url, params=params, headers=headers)
        print(req.json(), 'Количество оставшихся запросов на сегодня')

    def check_post_limit(self):
        url = self.endpoint['com'] + self.endpoint['check_post_limit']
        params = {
            'access_token': self.access_token
        }
        req = requests.get(url=url, params=params, headers=headers)
        print(req.json())

    def create_single_container(self, text, photo):
        url = self.endpoint['com'] + self.endpoint['media']
        params = {
            'image_url': photo,
            'caption': text,
            'access_token': self.access_token,
        }
        req = requests.post(url=url, params=params, headers=headers)
        print(req.json(), 'Контейнер получен')
        self.id_container = req.json()['id']

    def post_media_single(self):
        url = self.endpoint['com'] + self.endpoint['post_container']
        params = {
            'creation_id': self.id_container,
            'access_token': self.access_token,
        }
        req = requests.post(url=url, params=params, headers=headers)
        print(req.json(), 'Пост опубликован')

    # def post_media_multi(self):  # карусель не собирает готовые контейнеры, не работает, оставил на потом...
    #     url = self.endpoint['com'] + self.endpoint['media']
    #     with open('post_data.json', encoding='utf-8') as file:
    #         vk_post = json.loads(file.read())
    #     print(vk_post)
    #     params = {
    #         'is_carousel_item': True,
    #         'access_token': self.access_token,
    #     }
    #     media_id_list = []
    #     for image in vk_post['photo']:
    #         params = {
    #             'image_url': image,
    #             'is_carousel_item': 'true',
    #             'access_token': self.access_token,
    #         }
    #         req = requests.post(url=url, params=params, headers=headers)
    #         print(req.url)
    #         print(req.json())
    #         if req.json().get('id'):
    #             media_id_list.append(req.json()['id'])
    #
    #     print(media_id_list)
    #     print(len(media_id_list))
    #     children = '%'.join(media_id_list)
    #     # params = {}
    #     params = {
    #         'caption': 'Primer',
    #         'media_type': 'CAROUSEL',
    #         'children': '%'.join(media_id_list),
    #         # 'children': media_id_list[0],
    #         'access_token': self.access_token,
    #     }
    #     req = requests.post(url=url, params=params, headers=headers)
    #     print(req.url)
    #     print(req.json())
    #


def main():
    with open('post_data.json', encoding='utf-8') as file:
        vk_post = json.loads(file.read())
    print(vk_post)

    inst_obj = InstagramAPI()
    inst_obj.check_post_limit()
    inst_obj.create_single_container(vk_post['text'], vk_post['photo'][0])
    inst_obj.post_media_single()


if __name__ == '__main__':
    main()
