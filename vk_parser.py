import datetime
import json
import sys
import time
import aiohttp
import asyncio
import requests
from data.auth_data.auth_vk import access_token1, access_token2, headers
from settings import *


# from progress.bar import IncrementalBar


class VkTokens:

    def __init__(self, *args):  # объявляем конструктор класса
        self.tokens_tuple = args  # принимаем произвольное количество токенов, всё это будет кортежем
        self.check_auth(self.tokens_tuple)  # и проверяем их на работоспособность

    def check_auth(self, tokens_tuple):  # проверка токенов
        """
        проверка токена
        tokens_tuple: param tokens_tuple: токен пользователя, tuple
        """
        if self.tokens_tuple:  # если токены переданы
            auth_error_list = []  # объявляем лист, в который будут записываться индексы не рабочих токенов
            tokens_list = []  # ну и новый лист для рабочих токенов
            for token in tokens_tuple:  # перебираем токены
                while True:  # запускаем бесконечный цикл на случай не удачных авторизаций не по 5 ошибке
                    token_number = tokens_tuple.index(token) + 1  # получаем индекс текущего
                    print(f'Проверяю токен номер {token_number}')  # пользовательский вывод
                    check_auth_url = f'https://api.vk.com/method/wall.get?count=1&access_token={token}&v=5.131'
                    # ссылка на проверку текущий авторизации, просто пытаемся получить первую запись со своей страницы
                    req = requests.Session()  # открываем обычную синхронную сессию
                    req = req.get(url=check_auth_url, headers=headers)  # ну и запрашиваем данных
                    if 'error' in req.text[0:9]:  # если видим ошибку
                        result = json.loads(req.text)  # парсим всё полученное в словарь
                        code_error, print_error = self.vk_errors(result)  # и получаем текст и код ошибки (об этом ниже)
                        print(f'Токен номер {token_number} не сработал, код ошибки {code_error}')  # сообщаем
                        print('Текст ошибки')
                        print(print_error)  # также
                        print()
                        if code_error == 5:  # и вот если ошибка 5, не удачная авторизация добавляем номер текущего
                            # токена в список "битых" токенов
                            auth_error_list.append(token_number)
                            break  # и прерываем цикл
                        else:
                            print('Ждем 3 сек и продолжаем...')
                            time.sleep(3)  # если ошибка не 5 (например, превышение количества запросов)
                            # отдыхаем 3 сек и пробуем ещё раз
                            # если в токине будет ошибка написания, то он выбивает 5 ошибку, поэтому на тестах
                            # зацикливание исключено, но доработаю ещё на ручное прерывание
                            continue
                    else:
                        print(f'Токен номер {token_number} ок.')  # сообщаем об успешности проверки токена
                        print()
                        tokens_list.append(token)  # и добавляем токен в новый список для переопределения листа
                        break  # также прерываем цикл
            if auth_error_list:  # если в списке битых токенов хоть что-нибудь есть
                print(f'Токены под номерами {auth_error_list} не прошли проверку авторизации, желаете продолжить?')
                while True:  # запрашиваем ввод пользователя, продолжать или нет, т.к. не все токены прошли проверку
                    input_exit = input('y - продолжить, n - выход ').lower()
                    if input_exit == 'y':
                        break
                    elif input_exit == 'n':
                        sys.exit(0)
            self.tokens_tuple = tuple(tokens_list)  # переопределяем список и записываем обратно в свойство класса
            print('Проверка токенов завершена, кортеж токенов переопределён')
        else:
            raise ValueError("Необходимо передать токены, при создании объекта класса")
            # исключение на случай если при создании экземпляра класса не было передано ни одного токена

    @staticmethod
    def vk_errors(result):  # получение текста ошибки по коду ошибки
        error_code = result['error']['error_code']  # раз метод вызван, то точно ошибка и смело получаем её код
        path = Path(DATA_JSON_DIR, 'vk_api_errors.json')
        with open(path, encoding='utf-8') as file:
            vk_api_errors = json.load(file)  # парсим из файла подготовленный словарь ошибок в вк
        return error_code, vk_api_errors[str(error_code)]  # и по нему возвращаем текст и код ошибки


class GetVkPosts:
    def __init__(self, auth_data, group_id, save_in_file=False, limit=0):
        self.auth_data = auth_data
        self.group_id = group_id
        self.post_id_list = []
        self.global_break = 0
        self.unix_time_limit = 0
        self.save_in_file = save_in_file
        self.limit = limit

    def get_post_id(self):
        """
        Получение списка ID постов из группы в вк
        :return:
        """
        self.post_id_list = []
        self.global_break = 0
        if self.limit:
            self.create_limit()

        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(self.tasks_for_posts_id())  # основной запуск всего этого дела

        print('ок')
        print('Посты получены.')
        if self.limit:
            print(f'Новое количество постов: {len(self.post_id_list)}')
        self.post_id_list.sort(reverse=True)  # сортируем список, чтобы начинать с последних постов
        if self.save_in_file:
            with open(f'{self.group_id}_id_posts.json', 'w') as file:  # записываем всё в файл
                json.dump(self.post_id_list, file, indent=4, ensure_ascii=False)

    def create_limit(self):
        self.unix_time_limit = self.limit * 60 * 60 * 24 * 30


    async def get_post_list(self, token, get_post_list_off_set):
        """
        Асинх метод получения списка постов
        :param token:
        :param get_post_list_off_set:
        """

        post_id_list_post_list = []  # внутренний лист для записи id постов
        url_post_list = f'https://api.vk.com/method/wall.get?owner_id={self.group_id}&' \
                        f'offset={str(get_post_list_off_set)}&count=100&offset={str(get_post_list_off_set)}' \
                        f'&access_token={token}&v=5.131'  # формируем ссылку
        while True:  # обрабатываем получение данных бесконечным циклом для повторных попыток
            async with aiohttp.ClientSession() as session:  # асинхронно открываем сессию
                req_post_list = await session.get(url=url_post_list, headers=headers)  # запрашиваем данные
                result_post_list = json.loads(await req_post_list.text())  # парсим их в словарь

                try:  # открываем try, для обработки словаря
                    for item in result_post_list['response']['items']:
                        try:
                            if item['is_pinned']:  # проверка закрепленного поста, если старый, он сбивает алгоритм
                                continue
                        except KeyError:
                            pass

                        if item['date'] <= self.unix_time_limit:
                            self.global_break = 1
                            break
                        post_id_list_post_list.append((item['id'], item['date']))
                        # если такие поля есть, значит мы спокойно получаем id поста и идём дальше завершая цикл
                    break
                except KeyError:  # если такого поля нет
                    print('Возникла ошибка')
                    error_code_post_list, error_text_error_code_post_list = self.auth_data.vk_errors(result_post_list)
                    # логично полагать, что значит ошибка и мы прогоняем её через функцию обработки ошибок
                    if error_code_post_list == 5:  # а если ошибка авторизации то завершаем работу (ПЕРЕДЕЛАТЬ)
                        print('Произошла ошибка авторизации, используемый токен более не действителен')
                        print('Работа приложения завершена, все данные потеряны :)')
                        sys.exit(0)  # выход
                    else:
                        print(f'Код ошибки {error_code_post_list}')  # если это не ошибка авторизации
                        print(error_text_error_code_post_list)  # распечатываем данные и пробуем ещё
                        print('Ждем пару секунд и пробуем ещё раз')
                        await asyncio.sleep(1)

        print('.', end='')  # пользовательская загрузка для прогресса
        self.post_id_list += post_id_list_post_list
        self.post_id_list.sort(reverse=True)

    async def tasks_for_posts_id(self):
        """
        Внутренняя асинх функция для формирования списка тасков для асинх потока
        """
        tasks = []  # создаем список для тасков
        print('Получаем количество постов:', end=' ')
        url_count = f'https://api.vk.com/method/wall.get?owner_id={self.group_id}' \
                    f'&count=2&access_token={self.auth_data.tokens_tuple[0]}&v=5.131'
        # формируем url для получения количества постов
        req_count = requests.Session()  # запрашиваем первую запись в которой указано количество
        req_count = req_count.get(url=url_count, headers=headers)
        result_count_and_date = json.loads(req_count.text)  # парсим в словарь
        print(result_count_and_date['response']['count'])  # выводим количество постов
        if self.unix_time_limit:
            print(f'Установлен лимит "{self.limit}"')
            self.unix_time_limit = result_count_and_date['response']['items'][1]['date'] - self.unix_time_limit
        print('Получаем посты..', end='')
        # если лимит установлен, то берем время последнего поста и вычитаем наш лимит, чтобы получить
        # время для последнего поста с последнего поста
        count_iterations = result_count_and_date['response']['count'] // 100 + 1  # считаем количество итераций
        post_id_off_set = 0  # объявляем (и обнуляем смещение)
        post_id_k = 0  # а эт чтоб по циклу двигаться

        # progress = [i for i in range(0, count_iterations)]
        # bar = IncrementalBar('Прогресс', max=len(progress))
        while post_id_k <= count_iterations:  # поехали
            # bar.next()
            if self.global_break == 1:
                break
            for token in self.auth_data.tokens_tuple:  # перебираем все имеющиеся токены, чтобы запустить парсинг
                if self.global_break == 1:
                    break
                for page in range(1, 4):  # каждый токен получает по три страницы (ограничения вк)
                    if self.global_break == 1:
                        break
                    task = asyncio.create_task(self.get_post_list(token, post_id_off_set))
                    tasks.append(task)
                    post_id_off_set += 100  # смещаем оффсет
                    post_id_k += 1  # и счетчик
            await asyncio.gather(*tasks)  # ну и когда задачи сформированы, ждём их выполнения
            await asyncio.sleep(.5)
        # bar.finish()


class GetVkLikes:

    def __init__(self, auth_data, group_data, save_in_file=False, cache=False, limit=0):
        self.auth_data = auth_data
        self.group_data = group_data
        self.save_in_file = save_in_file
        self.cache = cache
        self.limit = limit
        self.unix_time_limit = None

    def create_limit(self):
        self.unix_time_limit = self.limit * 60 * 60 * 24 * 30
        self.unix_time_limit = self.group_data.post_id_list[0][1] - self.unix_time_limit
        self.group_data.post_id_list = [i for i in self.group_data.post_id_list if i[1] > self.unix_time_limit]

    def get_likes_from_group(self):
        """
        Метод получения списка лайков с группы
        """
        print('Группа номер:', self.group_data.group_id)
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(self.create_tasks_for_get_likes_from_group())
        # наконец запускаем всё это дело

    async def get_likes_of_post(self, post_id, page_k, local_access_token):
        """
        Внутренний асинх метод получения лайков с поста
        :param page_k:
        :param post_id: id поста
        :param local_access_token: токен
        """
        print('Работаем с постом', page_k + 1)  # показываем номер поста на котором работаем

        k = 1  # объявляем счетчик
        count_iter = 99  # ставим большое количество итераций для первой прогонки цикла
        off_set = 0  # обнуляем значение смещения страниц на лайках, за раз можем получить только 100
        user_likes_list = []  # внутренний список для парса лайков с поста
        while k <= count_iter:  # открываем цикл
            # формируем url
            url = f'https://api.vk.com/method/likes.getList?type=post&owner_id={self.group_data.group_id}&' \
                  f'offset={str(off_set)}&item_id={post_id}&access_token={local_access_token}&v=5.131'
            off_set += 100  # сразу "сдвигаем" offset на 100
            while True:
                async with aiohttp.ClientSession() as session:  # открываем асинхронную сессию
                    req = await session.get(url=url, headers=headers)  # получаем данные
                    result = json.loads(await req.text())  # переводим всё в словарь
                    try:
                        for item in result['response']['items']:  # перебираем словарь
                            user_likes_list.append(item)  # пополняем лист с лайками данными из словаря
                        all_likes = result['response']["count"]  # смотрим количество лайков на посте
                        count_iter = all_likes // 100 + 1  # обновляем количество итераций для цикла (лайки динамичные,
                        # могут меняться, поэтому было принято решение обновлять количество итераций цикла динамически
                        # во время его работы (поэтому мы использовали "while", а не "for")
                        k += 1  # увеличиваем счетчик для выхода из цикла
                        await asyncio.sleep(.5)  # засыпаем на секунду, чтобы не было превышения
                        # лимита запросов между offset и прерываем бесконечный цикл запросов
                        break
                    except KeyError:
                        print('Ошибка поста', page_k + 1)
                        await asyncio.sleep(1)
                        continue
        with open(f'{self.group_data.group_id}.json') as file:
            local_list_for_file = json.load(file)  # открываем файл с лайками и парсим всё в переменную, списком

        local_list_for_file += user_likes_list  # пополняем список новообретенными лайками
        local_set = set(local_list_for_file)  # переводим список в множество, для исключения повторений
        local_list_for_file = list(local_set)  # возвращаем всё в список
        with open(self.group_data.group_id + '.json', 'w') as file:
            json.dump(local_list_for_file, file, indent=4, ensure_ascii=False)  # и переписываем файл
        print(f'Пост {page_k + 1} готов')  # собственно пост готов

    async def create_tasks_for_get_likes_from_group(self):
        """
        Формирование тасков для получения постов
        """
        with open(self.group_data.group_id + '.json', 'w') as file:
            json.dump([], file, indent=4, ensure_ascii=False)  # создаем пустой файл для до записи
        tasks = []
        k = 1  # объявляем счетчик для итераций
        post_k = 0  # объявляем счетчик для перемещения по списку постов
        if self.limit:
            self.create_limit()
        number_of_iterations = len(self.group_data.post_id_list) // (len(self.auth_data.tokens_tuple) * 3)
        # считаем количество итераций
        while k <= number_of_iterations:  # открываем цикл
            for token in self.auth_data.tokens_tuple:  # перемещаемся по списку доступных токенов для авторизации
                for page in range(post_k, post_k + 3):
                    # формируем таски на асинхронный парсинг, по 3 за раз (ограничение вк)
                    tasks.append(asyncio.create_task(self.get_likes_of_post(self.group_data.post_id_list[page][0],
                                                                            page, token)))
                post_k += 3  # раз три записали, три и прибавляем
            await asyncio.gather(*tasks)  # пишем всё это дело в цикл асинх
            await asyncio.sleep(.5)
            k += 1  # увеличиваем счетчик итераций внешнего цикла
        number_of_iterations = len(self.group_data.post_id_list) % (len(self.auth_data.tokens_tuple) * 3)
        # получаем количество итераций
        # для оставшихся постов
        k = 1  # обновляем счетчик для нового цикла
        while k <= number_of_iterations:  # запускаем цикл получения последних постов
            await self.get_likes_of_post(self.group_data.post_id_list[post_k][0], post_k,
                                         self.auth_data.tokens_tuple[0])
            # уже синхронно друг за другом получаем посты, но используем await т.к. находимся в асинх методе
            post_k += 1  # увеличиваем номер поста
            k += 1  # ну и счётчик цикла



def call_get_vk_post(auth_data, group_id, limit=0):
    try:
        limit = int(limit)
    except ValueError:
        limit = 0
    obj_auth = VkTokens(*auth_data)
    obj_main = GetVkPosts(auth_data=obj_auth, group_id=group_id, limit=limit)
    obj_main.get_post_id()
    return obj_main.post_id_list


def main():
    # asyncio.run(start_main())

    # group_name1 = '-170301568'
    # group_name = '-159519198'
    # -193834404
    # -157081760
    # error_token = access_token2 + '123'
    # item = LegalVKParser(token=access_token2)
    # pass
    print(datetime.datetime.now())
    auth_tokens = VkTokens(access_token1, access_token2)
    get_group = GetVkPosts(group_id='-69452999', auth_data=auth_tokens)
    get_group.get_post_id()
    get_like = GetVkLikes(auth_data=auth_tokens, group_data=get_group, limit=0)
    get_like.get_likes_from_group()
    print(datetime.datetime.now())
    # get_group.group_id = '-159519198'
    # get_group.get_post_id()

    # item.get_post_id(group_id=-193834404)
    # item.get_post_id(group_id=-157081760)
    # item.get_post_id(group_id=-170301568)
    # item.get_likes_from_group('-193834404')
    # item.get_likes_from_group('-157081760')
    # item.get_likes_from_group('-170301568')
    # item.get_likes_from_group('-69452999')
    # item.start_pars()


if __name__ == '__main__':
    # pass
    main()
