import json

import requests
from vk_parser import VkTokens
from data.auth_data.auth_vk import access_token1, access_token2, headers

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
        req = req.get(url=url_post, headers=headers)
        with open('last_post.json', 'w', encoding='UTF-8') as file:
            file.write(req.text)
        post_data = {}


        for post in req.json()['response']['items']:
            try:
                if post['is_pinned']:
                    continue
            except KeyError:
                pass
            post_data['text'] = post['text']
            post_data['photo'] = []
            post_data['video'] = []
            for item in post['attachments']:
                if item['type'] == 'photo':
                    post_data['photo'].append(item['photo']['sizes'][4]['url'])
                elif item['type'] == 'video':
                    post_data['video'].append(f'https://vk.com/video{item["video"]["owner_id"]}_{item["video"]["id"]}')
        print(post_data)
        with open('post_data.json', 'w', encoding='UTF-8') as file:
            json.dump(post_data, file, indent=4, ensure_ascii=False)


def main():
    auth_data = VkTokens(access_token1)
    print(auth_data)
    last_post = ImportLastPost('-69452999', auth_data)
    last_post.get_last_post()


if __name__ == '__main__':
    main()
