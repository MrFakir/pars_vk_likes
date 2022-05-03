import json
from pathlib import Path

import requests
from backend.settings import headers, API_V_INST, TEMP_USERS_DATA, PLACE_HOLDER
from data.auth_data.auth_instagram import id_acc_instagram


class InstagramAPI:
    def __init__(self, access_token):
        self.access_token = access_token
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
        self.post_limit = None

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
        print(req.json())

    def check_post_limit(self):
        url = self.endpoint['com'] + self.endpoint['check_post_limit']
        params = {
            'access_token': self.access_token
        }
        req = requests.get(url=url, params=params, headers=headers)
        print(req.json(), 'Количество оставшихся запросов на сегодня')
        self.post_limit = req.json()['data'][0]['quota_usage']

    def create_single_container(self, text, photo):
        url = self.endpoint['com'] + self.endpoint['media']
        params = {
            'image_url': photo,
            'caption': text,
            'access_token': self.access_token,
        }
        while True:
            req = requests.post(url=url, params=params, headers=headers)
            print(req.json(), 'Контейнер получен')
            # if item.get('is_pinned'):
            if req.json().get('error'):
                if req.json()['error']['message'] == 'The aspect ratio is not supported.':
                    # params['image_url'] = self.cut_image(params['image_url'])
                    params['image_url'] = PLACE_HOLDER
                    continue
                elif req.json()['error']['message'] == 'An unexpected error has occurred.' \
                                                       ' Please retry your request later.':
                    continue
            self.id_container = req.json()['id']
            break

    def post_media_single(self):
        url = self.endpoint['com'] + self.endpoint['post_container']
        params = {
            'creation_id': self.id_container,
            'access_token': self.access_token,
        }
        req = requests.post(url=url, params=params, headers=headers)
        print(req.json(), 'Пост опубликован')

    # def cut_image(self, img_url):
    #     req_img = requests.get(url=img_url, headers=headers)
    #     file_name = Path(TEMP_USERS_DATA, img_url.split('/')[-1].split('?')[0])
    #     with open(file_name, 'wb') as file:
    #         file.write(req_img.content)
    #     print(file_name)
    #     return str(file_name)

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


def call_post_instagram(access_token, vk_post):
    inst_obj = InstagramAPI(access_token)
    inst_obj.check_post_limit()
    if inst_obj.post_limit >= 25:
        return 'Превышен лимит'
    inst_obj.create_single_container(vk_post['text'], vk_post['photo'][0])
    inst_obj.post_media_single()
    return f'Пост {vk_post["text"]} опубликован'


def main():
    with open('post_data.json', encoding='utf-8') as file:
        vk_post = json.loads(file.read())
    print(vk_post)
    with open('inst_token.txt') as file:
        access_token = file.read()
    inst_obj = InstagramAPI(access_token)
    inst_obj.check_post_limit()
    inst_obj.create_single_container(vk_post['text'], vk_post['photo'][0])
    # inst_obj.post_media_single()


if __name__ == '__main__':
    main()
