import requests

import time

from pprint import pprint

class VK_api:
    def __init__(self, token_vk):
        self.token = token_vk
        self.params = {
            'access_token': self.token,
            'v': '5.131'
        }
        self.url = 'https://api.vk.com/method/'

    def get_photos(self, owner_id, count=5):
        global result_dict
        result_dict = {}
        last_size_list = []
        url_photos = self.url + 'photos.get'
        params_photos = {
            'count': count,
            'owner_id': owner_id,
            'extended': 1,
            'album_id': 'profile'
        }
        res = requests.get(url_photos, params={**self.params, **params_photos})
        if res.status_code >= 300:
            print(f"Ошибка в запросе: {res.text}")
            return  
        res = res.json()
        if 'errors' in res:
            print(f"Сервер ответил ошибкой: {res['errors']}")
            return 
        for photo_item in res['response']['items']:
            filename = photo_item['likes']['count']
            last_size_list.append(photo_item['sizes'][-1])
            for dict in enumerate(last_size_list):
                intermediate_dict = {}
                dict = last_size_list[-1]
                intermediate_dict['filenameandpath'] = f'{filename}.jpg'
                intermediate_dict['url'] = dict['url']
                intermediate_dict['size'] = dict['type']
                result_dict[f'file_name_{len(last_size_list)}'] = intermediate_dict
                break
        with open('file_information.json', 'w', encoding='utf-8') as file:
            file.write(str(result_dict).replace("\'", "\""))
        return YaPeople.upload(result_dict)

class YandexDisk:
    def __init__(self, token_ya):
        self.token = token_ya
        self.headers = {
                'Content-Type': 'application/json',
                'Authorization': f'OAuth {self.token}'
            }

    def create_folder(self, name_folder):
        global new_folder
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        new_folder = name_folder
        params = {
            'path': name_folder
        }
        res = requests.put(url, params=params, headers=self.headers).json()

    def upload(self, dict):
        counter = 0
        quantity_file = len(dict)
        for dict_ in dict.values():
            url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
            params_upload = {
                'path': f'{new_folder}/{dict_["filenameandpath"]}',
                'url': dict_['url'],
                }
            upload = requests.post(url=url, params=params_upload, headers=self.headers)
            for percent in range(100):
                progress = f'[{(percent // 10) * "#"}{(10 - (percent // 10)) * "O"}] {percent} {counter}/{quantity_file}'
                print(progress, end='\r')
                time.sleep(0.01)
            counter += 1

    def get_result(self, folder_name):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {
            'path': f'{folder_name}'
        }
        res = requests.get(url, params=params, headers=self.headers).json()
        with open('final_disk.json', 'w', encoding='utf-8') as file:
            file.write(str(res).replace("\'", "\""))

if __name__ == '__main__':
    folder_name = 'backup'
    token_ya = input('Токен из полигона: ')
    token_vk = input('Введите токен из ВК: ')
    owner_id = input('Введите id пользователя: ')
    YaPeople = YandexDisk(token_ya)
    photo = VK_api(token_vk)
    YaPeople.create_folder(folder_name)
    photo.get_photos(owner_id)
    YaPeople.get_result(folder_name)