import json

import requests
from vk_parser import VkTokens
from data.auth_data.auth_vk import access_token1, access_token2, headers
from settings import *


class ImportLastPost:
    def __init__(self, group_id, auth_data):
        self.group_id = group_id
        self.auth_data = auth_data

    def get_last_post(self):
        # url_post = f'https://api.vk.com/method/wall.get?owner_id={self.group_id}&' \
        #                 f'offset={str(get_post_list_off_set)}&count=100&offset={str(get_post_list_off_set)}' \
        #                 f'&access_token={token}&v=5.131'  # формируем ссылку
        url_post = f'https://api.vk.com/method/wall.get?owner_id={self.group_id}' \
                   f'&count=2&access_token={self.auth_data.tokens_tuple[0]}&v=5.131'  # формируем ссылку
        req = requests.Session()
        req_post_data = req.get(url=url_post, headers=headers)
        with open('last_post.json', 'w', encoding='UTF-8') as file:
            file.write(req_post_data.text)
        post_data = {}
        for post in req_post_data.json()['response']['items']:
            if post.get('is_pinned'):
                continue
            post_data['text'] = post['text']
            post_data['photo'] = []
            post_data['video'] = []
            for item in post['attachments']:
                if item['type'] == 'photo':
                    post_data['photo'].append(self.get_image(item['photo']['sizes'][4]['url']))
                elif item['type'] == 'video':
                    post_data['video'].append(f'https://vk.com/video{item["video"]["owner_id"]}_{item["video"]["id"]}')
        print(post_data)
        with open('post_data.json', 'w', encoding='UTF-8') as file:
            json.dump(post_data, file, indent=4, ensure_ascii=False)

    def get_image(self, url):
        req = requests.Session()
        req_img = req.get(url=url, headers=headers)
        file_name = Path(TEMP_USERS_DATA, url.split('/')[-1].split('?')[0])
        with open(file_name, 'wb') as file:
            file.write(req_img.content)
        return str(file_name)


def main():
    auth_data = VkTokens(access_token1)
    print(auth_data)
    last_post = ImportLastPost('-69452999', auth_data)
    last_post.get_last_post()


if __name__ == '__main__':
    main()
