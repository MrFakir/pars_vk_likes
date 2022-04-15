import json
import sys
import time
import aiohttp
import asyncio
import requests
# import shutil
from data.auth_data.auth_vk import access_token4, access_token2, headers



class LegalVKParser:
    tasks = []

    def __init__(self, tokens_tuple=None, token=None, token3=None, token4=None):
        self.tokens_tuple = tokens_tuple

        self.access_token = token
        self.access_token3 = token3
        self.access_token4 = token4
        self.check_auth(self.access_token)

    def check_auth(self, token):
        """
        проверка токена
        :param token: токен пользователя, str
        """
        if self.access_token:
            check_auth_url = f'https://api.vk.com/method/wall.get?count=1&access_token={token}&v=5.131'
            req = requests.Session()
            req = req.get(url=check_auth_url, headers=headers)
            if 'error' in req.text[0:9]:
                result = json.loads(req.text)
                code_error, print_error = self.vk_errors(result)
                print(code_error)
                print(print_error)
                if code_error == 5:
                    sys.exit(0)

    def vk_errors(self, result):
        error_code = result['error']['error_code']
        with open('json_data/vk_api_errors.json', encoding='utf-8') as file:
            vk_api_errors = json.load(file)
        return error_code, vk_api_errors[str(error_code)]

    def get_post_id(self, group_id):
        print('Получаем количество постов:', end='')
        k = 0
        off_set = 0
        posts_list = []
        k_iter = 99
        error_auth = 0
        while k <= k_iter:
            url = f'https://api.vk.com/method/wall.get?owner_id={group_id}&offset={str(off_set)}' \
                  f'&count={100}&offset={str(off_set)}&access_token={self.access_token3}&v=5.131'
            # print(url)
            off_set += 100
            req = requests.Session()
            req = req.get(url=url, headers=headers)
            result = json.loads(req.text)
            try:
                if result['error']:
                    print()
                    error_code, error_text = self.vk_errors(result)
                    if error_code == 5:
                        print(error_text)
                        print('Завершение работы текущего токена')
                        return
                        # error_auth += 1
                        # if error_auth == 5:
                        #     print('Ошибка авторизации, закрываем программу')
                        #     sys.exit()
                    print(error_code)
                    print(error_text)
                    print('Пробуем ещё раз')
                    time.sleep(4)
                    continue
            except KeyError:
                print('...', end='')
            for i in result['response']['items']:
                posts_list.append(i['id'])
            all_post = result['response']["count"]
            k_iter = all_post // 100 + 1
            k += 1
            # time.sleep(1)
        print('Количество постов получено.')
        with open('json_data/posts.json', 'w') as file:
            json.dump(posts_list, file, indent=4, ensure_ascii=False)
        return posts_list

    async def get_likes_of_post(self, group_id, post_id, local_access_token):
        k = 0
        k_iter = 99
        off_set = 0
        user_likes_list = []
        while k <= k_iter:
            url = f'https://api.vk.com/method/likes.getList?type=post&owner_id={group_id}&' \
                  f'offset={str(off_set)}&item_id={post_id}&access_token={local_access_token}&v=5.131'
            off_set += 100
            async with aiohttp.ClientSession() as session:
                req = await session.get(url=url, headers=headers)
                result = json.loads(await req.text())
                for i in result['response']['items']:
                    user_likes_list.append(i)
                all_likes = result['response']["count"]
                k_iter = all_likes // 100 + 1
                k += 1
                await asyncio.sleep(1)

        await asyncio.sleep(2)
        return user_likes_list

    async def common_parser_group(self, group_id, posts_list, page_k, local_access_token):
        print('Работаем с постом', page_k + 1)
        local_likes_list = await self.get_likes_of_post(group_id, posts_list[page_k], local_access_token)

        with open(group_id + '.json') as file:
            local_list_for_file = json.load(file)

        local_list_for_file += local_likes_list
        local_set = set(local_list_for_file)
        local_list_for_file = list(local_set)
        with open(group_id + '.json', 'w') as file:
            json.dump(local_list_for_file, file, indent=4, ensure_ascii=False)
        print(f'Пост {page_k + 1} готов')
        page_k += 1

    async def create_task1(self, group_id_local, posts_list_local, page, local_access_token):
        task = asyncio.create_task(self.common_parser_group(group_id_local, posts_list_local, page, local_access_token))
        self.tasks.append(task)

    async def create_tasks_for_get_likes_from_group(self, group_id):
        group_id_local = group_id
        # group_id_local = '-159519198'
        print('Группа номер:', group_id_local)
        posts_list_local = self.get_post_id(group_id_local)
        # print(posts_list_local)
        #
        # with open('json_data/posts.json') as file:
        #     posts_list_local = json.load(file)
        # print(posts_list_local)

        print('Всего постов:', len(posts_list_local))
        local_list_for_file = []
        with open(group_id_local + '.json', 'w') as file:
            json.dump(local_list_for_file, file, indent=4, ensure_ascii=False)
        # tasks = []
        k = 1
        page_k = 0
        number_of_iterations = len(posts_list_local) // 6
        while k <= number_of_iterations:
            for page in range(page_k, page_k + 3):
                await self.create_task1(group_id_local, posts_list_local, page, self.access_token3)
            for page in range(page_k + 3, page_k + 6):
                await self.create_task1(group_id_local, posts_list_local, page, self.access_token4)
            await asyncio.gather(*self.tasks)
            k += 1
            page_k += 6
        k = 1
        number_of_iterations = len(posts_list_local) % 6
        while k <= number_of_iterations:
            for page in range(page_k, page_k + 1):
                await self.create_task1(group_id_local, posts_list_local, self.tasks, self.access_token3)
            await asyncio.gather(*self.tasks)
            page_k += 1
            k += 1

    def get_likes_from_group(self, group_id):
        asyncio.run(self.create_tasks_for_get_likes_from_group(group_id))


def main():
    # asyncio.run(start_main())

    group_name1 = '-170301568'
    group_name = '-159519198'
    # -193834404
    error_token = access_token2 + '123'
    # item = LegalVKParser(token=access_token2)
    item = LegalVKParser(token3=access_token2, token4=access_token4)
    # item.get_post_id(group_id=group_name)
    item.get_likes_from_group('-193834404')
    # item.start_pars()


if __name__ == '__main__':
    main()
