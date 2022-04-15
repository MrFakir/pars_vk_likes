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

    def __init__(self, *tokens):
        self.tokens_tuple = tokens
        self.check_auth(self.tokens_tuple)

    def check_auth(self, tokens_tuple):
        """
        проверка токена
        tokens_tuple: param tokens_tuple: токен пользователя, tuple
        """
        if self.tokens_tuple:
            auth_error_list = []
            tokens_list = []
            for token in tokens_tuple:
                while True:
                    token_number = tokens_tuple.index(token) + 1
                    print(f'Проверяю токен номер {token_number}')
                    check_auth_url = f'https://api.vk.com/method/wall.get?count=1&access_token={token}&v=5.131'
                    req = requests.Session()
                    req = req.get(url=check_auth_url, headers=headers)
                    if 'error' in req.text[0:9]:
                        result = json.loads(req.text)
                        code_error, print_error = self.vk_errors(result)
                        print(f'Токен номер {token_number} не сработал, код ошибки {code_error}')
                        print('Текст ошибки')
                        print(print_error)
                        print()
                        if code_error == 5:
                            auth_error_list.append(token_number)
                            break
                        else:
                            print('Ждем 3 сек и продолжаем...')
                            time.sleep(3)
                            continue
                    else:
                        print(f'Токен номер {token_number} ок.')
                        print()
                        tokens_list.append(token)
                        break
            if auth_error_list:
                print(f'Токены под номерами {auth_error_list} не прошли проверку авторизации, желаете продолжить?')
                while True:
                    input_exit = input('y - продолжить, n - выход ').lower()
                    if input_exit == 'y':
                        break
                    elif input_exit == 'n':
                        sys.exit(0)
            self.tokens_tuple = tuple(tokens_list)
            print('Проверка токенов завершена, кортеж токенов переопределён')
        else:
            raise ValueError("Необходимо передать токены, при создании объекта класса")

    def vk_errors(self, result):
        error_code = result['error']['error_code']
        with open('json_data/vk_api_errors.json', encoding='utf-8') as file:
            vk_api_errors = json.load(file)
        return error_code, vk_api_errors[str(error_code)]

    def get_post_id(self, group_id):
        post_id_list = []
        tasks = []

        async def get_post_list(group_id, token, get_post_list_off_set):
            post_id_list_post_list = []
            url_post_list = f'https://api.vk.com/method/wall.get?owner_id={group_id}&' \
                            f'offset={str(get_post_list_off_set)}&count=100&offset={str(get_post_list_off_set)}' \
                            f'&access_token={token}&v=5.131'
            async with aiohttp.ClientSession() as session:
                req_post_list = await session.get(url=url_post_list, headers=headers)
                result_post_list = json.loads(await req_post_list.text())
                while True:
                    try:
                        for item in result_post_list['response']['items']:
                            post_id_list_post_list.append(item['id'])
                        break
                    except KeyError:
                        print('Возникла ошибка')
                        error_code_post_list, error_text_error_code_post_list = self.vk_errors(result_post_list)
                        if error_code_post_list == 5:
                            print('Произошла ошибка авторизации, используемый токен более не действителен')
                            print('Работа приложения завершена, все данные потеряны :)')
                            sys.exit(0)
                        else:
                            print(f'Код ошибки {error_code_post_list}')
                            print(error_text_error_code_post_list)
                            print('Ждем пару секунд и пробуем ещё раз')

            await asyncio.sleep(1)
            print('...', end='')
            nonlocal post_id_list
            post_id_list += post_id_list_post_list

        async def tasks_for_posts_id(group_id):
            nonlocal tasks
            print('Получаем количество постов:', end=' ')
            url_count = f'https://api.vk.com/method/wall.get?owner_id={group_id}' \
                        f'&count=1&access_token={self.tokens_tuple[0]}&v=5.131'
            req_count = requests.Session()
            req_count = req_count.get(url=url_count, headers=headers)
            result_count = json.loads(req_count.text)
            print(result_count['response']['count'])
            print('Получаем посты...', end='')
            count_iterations = result_count['response']['count'] // 100 + 1
            post_id_off_set = 0
            post_id_k = 0
            while post_id_k <= count_iterations:
                for token in self.tokens_tuple:
                    for page in range(1, 4):
                        task = asyncio.create_task(get_post_list(group_id, token, post_id_off_set))
                        tasks.append(task)
                        post_id_off_set += 100
                        post_id_k += 1
                await asyncio.gather(*tasks)

        asyncio.run(tasks_for_posts_id(group_id=group_id))
        print('ок')
        print('Посты получены.')
        with open(f'{group_id}_id_posts.json', 'w') as file:
            json.dump(post_id_list, file, indent=4, ensure_ascii=False)
        return post_id_list


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
        # with open(f'json_data/posts_of_{group_id_local}.json') as file:
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
    # -157081760
    error_token = access_token2 + '123'
    # item = LegalVKParser(token=access_token2)
    item = LegalVKParser(access_token2, access_token4)
    # item.get_post_id(group_id=-193834404)
    item.get_post_id(group_id=-157081760)
    # item.get_post_id(group_id=-170301568)
    # item.get_likes_from_group('-193834404')
    # item.start_pars()


if __name__ == '__main__':
    main()
