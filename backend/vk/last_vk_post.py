import json

import requests
from backend.vk.vk_parser import VkTokens
from data.auth_data.auth_vk import access_token1, headers
from backend.settings import *


class ImportLastPost:
    def __init__(self, group_id, auth_data, debug=False):
        self.group_id = group_id
        self.auth_data = auth_data
        self.post_data = {}
        self.debug = debug

    def get_last_post(self):
        url_post = f'https://api.vk.com/method/wall.get'  # формируем ссылку
        params = {
            'owner_id': self.group_id,
            'count': 2,
            'access_token': self.auth_data.tokens_tuple[0],
            'v': 5.131,
        }
        req = requests.Session()
        req_post_data = req.get(url=url_post, params=params, headers=headers)
        if self.debug:
            with open('last_post.json', 'w', encoding='UTF-8') as file:
                file.write(req_post_data.text)
        for post in req_post_data.json()['response']['items']:
            if post.get('is_pinned'):
                continue
            self.post_data['text'] = post['text']
            self.post_data['photo'] = []
            self.post_data['video'] = []
            for item in post['attachments']:
                if item['type'] == 'photo':
                    self.post_data['photo'].append(item['photo']['sizes'][4]['url'])
                    # self.post_data['photo'].append(self.get_image(item['photo']['sizes'][4]['url']))
                elif item['type'] == 'video':
                    self.post_data['video'].append(f'https://vk.com/video'
                                                   f'{item["video"]["owner_id"]}_{item["video"]["id"]}')
        if self.debug:
            with open('post_data.json', 'w', encoding='UTF-8') as file:
                json.dump(self.post_data, file, indent=4, ensure_ascii=False)

    @staticmethod
    def get_image(url):
        req = requests.Session()
        req_img = req.get(url=url, headers=headers)
        file_name = Path(TEMP_USERS_DATA, url.split('/')[-1].split('?')[0])
        with open(file_name, 'wb') as file:
            file.write(req_img.content)
        return str(file_name)

    # def get_video(self):
    #     url1 = f'https://api.vk.com/method/video.get?owner_id={self.group_id}' \
    #            f'&videos=-69452999_456239018&count=2&access_token={self.auth_data.tokens_tuple[0]}&v=5.131'
    #     url = f'https://api.vk.com/method/video.get?owner_id={self.group_id}' \
    #           f'&access_token={self.auth_data.tokens_tuple[0]}&v=5.131'
    #     # формируем ссылку
    #     print(url)
    #     req = requests.Session()
    #     req1 = req.get(url=url, headers=headers)
    #     with open('post_data.json', 'w', encoding='UTF-8') as file:
    #         json.dump(req1.json(), file, indent=4, ensure_ascii=False)
    #     # url = 'https://vk.com/video_ext.php?oid=-69452999&id=168257843&hash=38632f896c07b7d7&_
    #     _ref=vk.api&api_hash=1651086326ce51e69a0dde2f0687_G4YTEOJYHE2DMNI'
    #     # req_video = req.get(url=url, headers=headers)
    #     # print(url)
    #     #
    #     # with open('123123.txt', 'wb') as file:
    #     #     file.write(req_video.content)


def call_get_last_post(auth_data, group_id):
    obj_auth = VkTokens(*auth_data)
    obj_main = ImportLastPost(group_id, obj_auth)
    obj_main.get_last_post()
    return obj_main.post_data


def main():
    auth_data = VkTokens(access_token1)
    last_post = ImportLastPost('-69452999', auth_data, debug=True)
    last_post.get_last_post()
    print(last_post.post_data)


if __name__ == '__main__':
    main()
