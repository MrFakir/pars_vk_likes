import json
import time

from backend.vk.last_vk_post import call_get_last_post, ImportLastPost
from backend.instagram.post_instagram import call_post_instagram, InstagramAPI
from backend.vk.vk_parser import VkTokens
from backend.instagram.inst_token import InstToken

from data.auth_data.auth_vk import access_token1 as vk_token
from data.auth_data.auth_instagram import access_token as insta_token


class AutoPostingFromVK:
    def __init__(self, status, auth_data_vk, group_id, access_token_inst):
        self.vk_token = auth_data_vk
        self.insta_token = access_token_inst
        self.status = status
        self.set_status(status)

        self.group_id = group_id

        self.check_tokens()

    def check_tokens(self):
        self.vk_token = VkTokens(vk_token)
        self.insta_token = InstToken(insta_token)
        # проверку авторизации дописать!

    @staticmethod
    def set_status(status):
        status = {'status': status}
        with open('publish_status.json', 'w', encoding='UTF-8') as file:
            json.dump(status, file, indent=4, ensure_ascii=False)

    def get_status(self):
        with open('publish_status.json') as file:
            status = json.loads(file.read())
        self.status = status['status']
        return status['status']

    def parser_from_vk(self):
        post_id = None
        while self.get_status():
            print('слушаю группу')
            post_obj = ImportLastPost(auth_data=self.vk_token, group_id=self.group_id)
            post_obj.get_last_post()
            if post_obj.post_data['id'] == post_id:
                time.sleep(1)
                print('Продолжаю слушать, новых постов нет.')
                continue
            insta_object = InstagramAPI(self.insta_token.access_token)
            insta_object.check_post_limit()
            if insta_object.post_limit >= 25:
                return 'Превышен лимит'
            print(post_obj.post_data)
            insta_object.create_single_container(post_obj.post_data['text'], post_obj.post_data['photo'][0])
            insta_object.post_media_single()
            print(f'Пост опубликован')
            post_id = post_obj.post_data['id']
            time.sleep(1)


def call_parser_from_vk(auth_data_vk, access_token_inst, group_id, status=False):
    parser = AutoPostingFromVK(status=status, auth_data_vk=auth_data_vk,
                               access_token_inst=access_token_inst, group_id=group_id)
    parser.parser_from_vk()


def main():
    parser = AutoPostingFromVK(status=True, auth_data_vk=vk_token,
                               access_token_inst=insta_token, group_id='-69452999')
    parser.parser_from_vk()


if __name__ == '__main__':
    main()
