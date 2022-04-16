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

    def __init__(self, *tokens):  # объявляем конструктор класса
        self.tokens_tuple = tokens  # принимаем произвольное количество токенов, всё это будет кортежем
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
                    req = requests.Session()  # откарываем обычную синхронную сессию
                    req = req.get(url=check_auth_url, headers=headers)  # ну и запрашиваем данных
                    if 'error' in req.text[0:9]:  # если видим ошибку
                        result = json.loads(req.text)  # парсим всё полученное в словарь
                        code_error, print_error = self.vk_errors(result)  # и получаем текст и код ошибки (об этом ниже)
                        print(f'Токен номер {token_number} не сработал, код ошибки {code_error}')  # сообщаем
                        print('Текст ошибки')
                        print(print_error)  # также
                        print()
                        if code_error == 5:  # и вот если ошибка 5, не удачная авторизацияЮ добовляем номер текущего
                            # токена в список "битых" токенов
                            auth_error_list.append(token_number)
                            break  # и прерываем цикл
                        else:
                            print('Ждем 3 сек и продолжаем...')
                            time.sleep(3)  # если ошибка не 5 (может с инетом беда или превышено количество запросов)
                            # отдыхаем 3 сек и пробуем ещё раз
                            # если в токине будет ошибка написания, то он полюбому выбивает 5 ошибку, поэтому на тестах
                            # зацикливание исключено, но доработаю ещё на ручное прерывание
                            continue
                    else:
                        print(f'Токен номер {token_number} ок.')  # сообщаем об успешности проверки токена
                        print()
                        tokens_list.append(token)  # и добавляем токен в новый список для переопределение листа
                        break  # также прерываем цикл
            if auth_error_list:  # если в списке битых токенов хоть чтонибудь есть
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
        with open('json_data/vk_api_errors.json', encoding='utf-8') as file:
            vk_api_errors = json.load(file)  # парсим из файла подготовленный словарь ошибок в вк
        return error_code, vk_api_errors[str(error_code)]  # и по нему возвращаем текст и код ошибки

    def get_post_id(self, group_id):
        """
        Получение списка ID постов из группы в вк
        :param group_id:
        :return:
        """
        post_id_list = []

        async def get_post_list(group_id, token, get_post_list_off_set):
            """
            Внутряняя асинх функция получения списка постов
            :param group_id:
            :param token:
            :param get_post_list_off_set:
            :return:
            """
            post_id_list_post_list = []  # внутренний лист для записи лайков из поста
            url_post_list = f'https://api.vk.com/method/wall.get?owner_id={group_id}&' \
                            f'offset={str(get_post_list_off_set)}&count=100&offset={str(get_post_list_off_set)}' \
                            f'&access_token={token}&v=5.131'  # формируем ссылку
            async with aiohttp.ClientSession() as session:  # асинхронно открываем сессию
                req_post_list = await session.get(url=url_post_list, headers=headers)  # запарашиваем данные
                result_post_list = json.loads(await req_post_list.text())  # парсим их в словарь
                while True:  # обробатываем полученные данные бесконечных циклом для повторных попыток (ОШИБКА)
                    try:  # открываем try, для обработки слловаря
                        for item in result_post_list['response']['items']:
                            post_id_list_post_list.append(item['id'])
                            # если такие поля есть, значит мы спокойно получаем id поста и идём дальше завершая цикл
                        break
                    except KeyError:  # если такого поля нет
                        print('Возникла ошибка')
                        error_code_post_list, error_text_error_code_post_list = self.vk_errors(result_post_list)
                        # логично пологать, что значит ошибка и мы прогоняем её через функцию обработки ошибок
                        if error_code_post_list == 5:  # а если ошибка авторизации то завершаем работу (ПЕРЕДЕЛАТЬ)
                            print('Произошла ошибка авторизации, используемый токен более не действителен')
                            print('Работа приложения завершена, все данные потеряны :)')
                            sys.exit(0)  # выход
                        else:
                            print(f'Код ошибки {error_code_post_list}')  # если это не ошибка авторизации
                            print(error_text_error_code_post_list)  # распечатываем данные и пробуем ещё
                            print('Ждем пару секунд и пробуем ещё раз')

            await asyncio.sleep(1)  # спим, чтоб не превышать количество запросов
            print('...', end='')  # пользовательская загрузка для прогресса
            nonlocal post_id_list  # берем лист из внешней функции и пополняем его итоговым списком постов
            post_id_list += post_id_list_post_list

        async def tasks_for_posts_id(group_id):
            """
            Внутренняя асинх функция для формирования списка тасков для асинх потока
            :param group_id:
            :return:
            """
            tasks = []  # очищаем список тасков (малоли что там было)
            print('Получаем количество постов:', end=' ')
            url_count = f'https://api.vk.com/method/wall.get?owner_id={group_id}' \
                        f'&count=1&access_token={self.tokens_tuple[0]}&v=5.131'
            # формируем url для получения количества постов
            req_count = requests.Session()  # обычных реквестом запрашиваем первую запись в которой указано количество
            req_count = req_count.get(url=url_count, headers=headers)
            result_count = json.loads(req_count.text)
            print(result_count['response']['count'])  # парсим в словарь
            print('Получаем посты...', end='')
            count_iterations = result_count['response']['count'] // 100 + 1  # считаем количество итераций
            post_id_off_set = 0  # объявялем (и обнуляем смещение)
            post_id_k = 0  # а эт чтоб по циклу двигаться
            while post_id_k <= count_iterations:  # поехали
                for token in self.tokens_tuple:  # перебираем все имеющиеся токены чтобы запустить парсинг
                    for page in range(1, 4):  # каждый токен получает по три страницы (ограничения вк)
                        task = asyncio.create_task(get_post_list(group_id, token, post_id_off_set))
                        tasks.append(task)
                        post_id_off_set += 100  # смещаем оффсет
                        post_id_k += 1  # и счетчик
                await asyncio.gather(*tasks)  # ну и когда задачи сформированы, ждём их выполнения

        asyncio.run(tasks_for_posts_id(group_id=group_id))  # основной запуск всего этого дела
        print('ок')
        print('Посты получены.')
        with open(f'{group_id}_id_posts.json', 'w') as file:  # записываем всё в файл
            json.dump(post_id_list, file, indent=4, ensure_ascii=False)
        return post_id_list  # а эт передача листа для дальнейшей работы

    def get_likes_from_group(self, group_id):
        """
        Метод получения списка лайков с группы
        :param group_id:
        :return:
        """
        print('Группа номер:', group_id)
        posts_list_local = self.get_post_id(group_id)

        async def get_likes_of_post(group_id, post_id, page_k, local_access_token):
            """
            Внутренний асинх метод получения лайков с поста
            :param page_k:
            :param group_id: id группы
            :param post_id: id поста
            :param local_access_token: токен
            :return:
            """
            print('Работаем с постом', page_k + 1)  # показываем номер поста на котором работаем

            k = 0  # объявляем счетчик
            count_iter = 99  # ставим большое количество итераций для первой прогонки цикла
            off_set = 0  # обнуляем значение смещения страниц на лайках, за раз можем получить только 100
            user_likes_list = []  # внутренний список для парса лайков с поста
            while k <= count_iter:  # открываем цикл
                # формируем url
                url = f'https://api.vk.com/method/likes.getList?type=post&owner_id={group_id}&' \
                      f'offset={str(off_set)}&item_id={post_id}&access_token={local_access_token}&v=5.131'
                off_set += 100  # сразу "сдвигаем" offset на 100
                async with aiohttp.ClientSession() as session:  # открываем асинхронную сессию
                    req = await session.get(url=url, headers=headers)  # получаем данные
                    result = json.loads(await req.text())  # переводим всё в словарь
                    for item in result['response']['items']:  # перебираем словарь
                        user_likes_list.append(item)  # пополняем лист с лайками данными из словаря
                    all_likes = result['response']["count"]  # смотрим количество постов
                    count_iter = all_likes // 100 + 1  # обновляем количество итераций для цикла (лайки динамичные, и
                    # могут меняться, поэтому было принято решение обновлять количество итераций цикла динамически
                    # во время его работы (поэтому мы использовали "while", а не "for"
                    k += 1  # увеличиваем счетчик для выхода из цикла
                    await asyncio.sleep(1)  # засыпаем на секунду, чтобы не было превышения
                    # лимита запросов между offset

            with open(f'{group_id}.json') as file:
                local_list_for_file = json.load(file)  # открываем файл с лайками и парсим всё в переменную, списком

            local_list_for_file += user_likes_list  # пополняем список новообретенными лайками
            local_set = set(local_list_for_file)  # переводим список в множество, для исключения повторений
            local_list_for_file = list(local_set)  # возвращаем всё в список
            with open(group_id + '.json', 'w') as file:
                json.dump(local_list_for_file, file, indent=4, ensure_ascii=False)  # и переписываем файл
            print(f'Пост {page_k + 1} готов')  # собственно пост готов
            await asyncio.sleep(2)  # засыпаем между постами

        async def create_tasks_for_get_likes_from_group(group_id, posts_list_local):
            """
            Формирование тасков для получения постов
            :param group_id: id группы
            :param posts_list_local: список
            :return:
            """
            group_id_local = group_id  #
            with open(group_id_local + '.json', 'w') as file:
                json.dump([], file, indent=4, ensure_ascii=False)  # создаем пустой файл для дозаписи
            tasks = []
            k = 1  # обьявляем счетчик для итераций
            post_k = 0  # объявляем счетчик для перемещения по списку постов
            number_of_iterations = len(posts_list_local) // 6  # считаем количество итераций (требует обновления)
            while k <= number_of_iterations:  # открываем цикл
                for token in self.tokens_tuple:  # перемещаемся по списку доступных токенов для авторизации
                    for page in range(post_k, post_k + 3):
                        # формируем таски на асинхронный парсинг, по 3 за раз (ограничение вк)
                        tasks.append(asyncio.create_task(get_likes_of_post(group_id_local,
                                                                           posts_list_local[page], page, token)))
                    post_k += 3  # раз три записали, три и прибавляем
                await asyncio.gather(*tasks)  # пишем всё это дело в цикл асинх
                k += 1  # увеличиваем счетчик итераций внешнего цикла
            number_of_iterations = len(posts_list_local) % 6  # получаем количество итераций для оставшихся постов
            k = 1  # обновляем счетчик для нового цикла
            while k <= number_of_iterations:  # запускаем цикл получения последних 5(или менее) постов (требует обновления)
                await get_likes_of_post(group_id_local, posts_list_local[post_k], post_k, self.tokens_tuple[0])
                # уже синхронно друг за другом получаем посты, но используем await т.к. находимся в асинх методе
                post_k += 1  # увеличиваем номер поста
                k += 1  # ну и счётчик цикла

        asyncio.run(create_tasks_for_get_likes_from_group(group_id, posts_list_local))
        # наконец запускаем всё это дело


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
    # item.get_post_id(group_id=-157081760)
    # item.get_post_id(group_id=-170301568)
    # item.get_likes_from_group('-193834404')
    # item.get_likes_from_group('-157081760')
    item.get_likes_from_group('-69452999')
    # item.start_pars()


if __name__ == '__main__':
    main()
