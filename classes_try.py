import requests
from datetime import datetime
from tqdm import tqdm
from time import sleep


class VkPhotos:
    def __init__(self):
        self.album_list = []
        self.album_count = 0

        # self.vk_token = 'ВВЕДИТЕ ТУТ ВАШ ТОКЕН ВК и скройте строки 13-15'

        with open("token_vk.txt") as f:
            # f.readline()  # добавить эту строчку чтообы считать коровина, убрать чтобы мой
            self.vk_token = f.read().split()[0]

        self.user_id = ''

        self.validate_error = ''

        self.wall, self.wall_count = [], 0
        self.profile, self.profile_count = [], 0

        self.error = ''

        # self.validate_user_id(self.user_id)
        # self.get_albums_list()  # на выходе - список с названиями альбомов пользователя, если они есть
        #
        # self.wall, self.wall_count = self.photos_get('wall')  # словари и лайки
        # self.profile, self.profile_count = self.photos_get('profile')
        # self.saved, self.saved_count = self.photos_get('saved')

    def validate_user_id(self, data):
        """
        эта функция проверяет, есть ли user_id в базе ВК, True - если есть, False - если нет
        и ещё она подменит screen_name на id если ввести именно screen_name
        """

        # data = self.user_id  # для тестирования чисто этой части
        if data:  # чтобы не ввели пустоту
            params = {
                'user_ids': data,
                'access_token': self.vk_token,
                'v': '5.126'
            }
            res = requests.get('https://api.vk.com/method/users.get', params=params)
            # print(res.json())

            if "error" in res.json():  # ошибка - неправильный id, такого пользователя нету ВК, неверный токен
                # print(res.json()['error']['error_msg']
                self.validate_error = res.json()['error']['error_msg']
                return False

            # print('Успешно введён id пользователя')
            try:
                int(data)
                self.user_id = data

            except ValueError:
                # print(res.json())
                self.user_id = res.json()['response'][0]['id']

            finally:
                print(res.json())

                if 'deactivated' in res.json()['response'][0]:
                    self.validate_error = 'Этот пользователь удалён'
                    return False

                if res.json()['response'][0]['is_closed'] and not res.json()['response'][0]['can_access_closed']:
                    self.validate_error = 'Этот пользователь для вас закрыт'
                    return False

                return True

        else:  # это если в поле введите id не ввести вообще ничего
            self.validate_error = 'Нужно что-то ввести'
            return False

    def get_albums_list(self):

        params = {
            'owner_id': self.user_id,
            'access_token': self.vk_token,
            'v': '5.126',
            'photo_sizes': True,

        }

        response = requests.get('https://api.vk.com/method/photos.getAlbums', params=params)

        if "error" in response.json():
            print(f"{response.json()['error']['error_msg']} для личного альбома")
            self.error = response.json()['error']['error_msg']  # распечатать ошибку потом в гуи

        else:
            print(response.json())
            self.album_count = response.json()['response']['count']

            for each in response.json()['response']['items']:
                self.album_list.append([each['title'], each['size'], each['id']])
                # создали список типа название альбома, количество фоток там, id альбома
            print(self.album_list)

    def photos_get(self, album_id, count=1000):

        links_list = []

        params = {
            'owner_id': self.user_id,
            'access_token': self.vk_token,
            'v': '5.126',
            'album_id': album_id,
            'photo_sizes': True,
            'extended': True,
            'count': count,
            'rev': 1
        }

        response = requests.get('https://api.vk.com/method/photos.get', params=params)

        if "error" in response.json():  # ошибка что пользователь закрыл фотки или удалён
            print(f"{response.json()['error']['error_msg']} для альбома {album_id}")
            self.error = response.json()['error']['error_msg']  # print error
        else:
            result = response.json()['response']['items']
            # print(response.json())

            for photo in result:
                links_dict = {}
                like = photo['likes']['count']
                link = photo['sizes'][-1]['url']

                # if link not in links_dict.values():  # чтобы две одинаковые фотки не заливать
                normal_date = datetime.utcfromtimestamp(int(photo["date"])).strftime('%Y-%m-%d_%H-%M-%S')
                # print(normal_date)
                links_dict[f'{like}_{str(normal_date)}'] = link
                links_list.append(links_dict)
            # photos_count = len(links_dict)
            print('альбом', links_list)
        return links_list, len(links_list)

    def execute_photos_get(self):
        self.wall, self.wall_count = self.photos_get('wall')  # словари и лайки
        self.profile, self.profile_count = self.photos_get('profile')
        # self.saved, self.saved_count = self.photos_get('saved')

    def execute_album_link(self, album_list_number: int):
        print('альбом_id', self.album_list[album_list_number][2])
        album_list = self.photos_get(self.album_list[album_list_number][2])[0]
        return album_list


class YandexUploader:
    def __init__(self):

        # self.ya_token = 'ВВЕДИТЕ ВАШ ЯНДЕКС ТОКЕН СЮДА и скройте следующие 3 строки'

        with open("token_vk.txt") as f:
            f.readline()
            f.readline()
            self.ya_token = f.read().split()[0]

        self.status = ''  # сообщение успеха загрузки

    def create_folder(self, user_id: str, album_id: str):
        """создаёт папку пользователя, альбома и ещё список names с файлами в этой папке"""

        names = []  # список всех доступных файлов в конкретной папке

        folder_name = f'user_{user_id}'  # создаём папку user_userid
        response = requests.put('https://cloud-api.yandex.net/v1/disk/resources',
                                params={'path': folder_name},
                                headers={'Authorization': f'OAuth {self.ya_token}'})

        if response.status_code in [201, 409]:  # если папка создалась (201) или уже есть (409)
            album_folder_name = f'user_{user_id}/{album_id}'  # создаём внутри папку альбома
            response = requests.put('https://cloud-api.yandex.net/v1/disk/resources',
                                    params={'path': album_folder_name},
                                    headers={'Authorization': f'OAuth {self.ya_token}'})

            if response.status_code in [201, 409]:  # если она создалась, тогда загружаем

                files = requests.get('https://cloud-api.yandex.net/v1/disk/resources/',
                                     params={'path': f'user_{user_id}/{album_id}'},
                                     headers={'Authorization': f'OAuth {self.ya_token}'})

                # print(files.json())

                if "error" not in files.json():
                    number = files.json()['_embedded']['items']
                    # print(len(number))
                    for each in number:
                        names.append(each['name'])
                print('доступные файлики в папке', names)
                return True, names

            else:  # это если она не создалась
                self.status = f"Ошибка яндекса - {response.json()['message']}"
                print(self.status)
                return False, names

        else:  # а это если ошибка на уровне целого пользователя
            self.status = f"Ошибка яндекса - {response.json()['message']}"
            print(self.status)
            return False, names

    def upload_all(self, user_id: str, photos_list: list, album_id: str):
        """загружаем все фоточки из photos_list на яндекс диск"""
        if photos_list:

            status, names = self.create_folder(user_id, album_id)

            if status:
                print("Начинаем загрузку")
                i = 0  # счетчик количества повторяющихся файлов

                for each in tqdm(photos_list):
                    for key, value in each.items():
                        if key not in names:
                            album_folder_name = f'user_{user_id}/{album_id}'
                            requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload',
                                          params={'path': f'{album_folder_name}/{key}', 'url': value},
                                          headers={'Authorization': f'OAuth {self.ya_token}'})
                        else:
                            # print('такой уже есть')
                            i += 1
                        sleep(0.33)

                if i == 0:
                    self.status = "Загрузка завершена"
                    # print("Загрузка завершена")
                else:
                    self.status = f'Загрузка завершена, {i} не загружено, так как они уже есть'
                    # print(f'Загрузка завершена, {i} не загружено, так как они уже есть')
                print(self.status)
                log(user_id, album_id, photos_list, i)  # ещё дополнительно создаём лог txt-файл

        else:  # а это если с пользователем ВК всё было ок, но у него нету фоточек
            print("У пользователя нет фоток или он закрытый")

    def upload_one(self, user_id: str, one: dict, album_id: str):
        """это загрузить одну фоточку из словаря one, вида {имя: ссылка}"""

        status, names = self.create_folder(user_id, album_id)
        # print("качаем одну фотку", user_id, album_id)

        if status:
            # print("Начинаем загрузку")
            i = 0

            for key, value in one.items():
                if key not in names:
                    album_folder_name = f'user_{user_id}/{album_id}'
                    requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload',
                                  params={'path': f'{album_folder_name}/{key}', 'url': value},
                                  headers={'Authorization': f'OAuth {self.ya_token}'})
                    self.status = "Загружено"
                else:
                    self.status = "Такой уже есть"
                    i = 1

            log(user_id, album_id, [1], i)


def log(user_id, album_id, photos_list, i):
    with open('current_time_log.txt', "a+", encoding='utf-8') as f:  # лог txt с дозаписью
        line = f'_user_id={user_id}_album={album_id}_____загружено_{len(photos_list) - i}_фоток\n'
        f.write(str(datetime.now().strftime('%Y-%d-%m___%H-%M-%S') + line))
        print('log_file updated')
