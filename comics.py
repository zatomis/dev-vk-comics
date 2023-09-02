import os
import requests
from environs import Env
from random import randint

API_VERSION_VK = 5.131
VK_URL_API = "https://api.vk.com/method/"


class VkError(Exception):

    def __init__(self, error_code, error_message):
        self.error_code = error_code
        self.error_message = error_message
        super().__init__(f'VK API error: {self.error_code}: {self.error_message}')


def check_vk_errors(response):
    if 'error' in response:
        raise VkError(response['error']['error_code'], response['error']['error_msg'])


def get_upload_url(group_id, token, version):
    """ Возвращает адрес сервера для загрузки фотографии на стену пользователя или сообщества.
        :param group_id: id группы
        :param token: ваш токен
        :param version: версия api vk
        :return: upload_url - адрес
    """
    server_params = {
        'access_token': token,
        'v': version,
        'group_id': group_id,
    }
    server_response = requests.get(
        f'{VK_URL_API}photos.getWallUploadServer',
        params=server_params,
    )
    server_response.raise_for_status()
    upload_settings = server_response.json()
    check_vk_errors(upload_settings)
    return upload_settings['response']['upload_url']


def upload_image(url, image):
    """
        :param url: адрес для загрузки фото
        :param image: картинка формата: JPG, PNG, GIF.
        :return: параметры server, photo, vk_hash,
    """
    with open(image, 'rb') as comics_img:
        payload = {
            'photo': comics_img,
        }
        response = requests.post(url, files=payload)
    response.raise_for_status()
    upload_response = response.json()
    return upload_response['server'], upload_response['photo'], upload_response['hash']


def save_on_server(group_id, token, version, server, photo, vk_hash):
    """ Сохраняет фотографии после успешной загрузки на URI, полученный методом photos.getWallUploadServer.
        :param group_id: id группы
        :param token: токен
        :param version: версия api вк
        :param server:
        :param photo:
        :param vk_hash:
        :return: owner_id, id
    """
    params = {
        'access_token': token,
        'v': version,
        'server': server,
        'photo': photo,
        'hash': vk_hash,
        'group_id': group_id,
    }
    response = requests.get(f"{VK_URL_API}photos.saveWallPhoto", params=params)
    response.raise_for_status()
    upload_settings = response.json()
    check_vk_errors(upload_settings)
    response = upload_settings['response'][0]
    return response['owner_id'], response['id']


def post_on_the_wall(group_id, token, version, owner_id, photo_id, message):
    """ Позволяет создать запись на стене, опубликовать существующую запись.
        :param group_id: id группы вк
        :param token: токен
        :param version: версия api вк
        :param owner_id: id владельца фото
        :param photo_id: id фото
        :param message: сообщения на стене
    """
    photo = f"photo{owner_id}_{photo_id}"
    params = {
        'access_token': token,
        'v': version,
        'owner_id': -int(group_id),
        'from_group': 1,
        'attachments': photo,
        'message': message,
        'close_comments': 0,
    }
    response = requests.get(f"{VK_URL_API}wall.post", params=params)
    response.raise_for_status()
    upload_settings = response.json()
    check_vk_errors(upload_settings)
    return upload_settings


def download_photo(url_image, name_image):
    """
        :param url_image: url картинки
        :param name_image: имя для картинки
    """
    response = requests.get(url_image)
    response.raise_for_status()
    with open(f"{name_image}", 'wb') as file:
        file.write(response.content)


def download_random_comic():
    url = f"https://xkcd.com/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    picture_number = randint(0, response.json()['num'])
    url = f"https://xkcd.com/{picture_number}/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    rnd_comic = response.json()
    message = rnd_comic['alt']
    picture_file_name = f"{picture_number}.png"
    url_image = rnd_comic['img']
    return message, picture_file_name, url_image


if __name__ == '__main__':
    env = Env()
    env.read_env()
    vk_token = env.str("VK_ACCESS_TOKEN")
    vk_group_id = env.str("VK_GROUP_ID")
    message, picture_file_name, url_image = download_random_comic()
    download_photo(url_image, picture_file_name)
    try:
        upload_url = get_upload_url(vk_group_id, vk_token, API_VERSION_VK)
        server, photo, vk_hash = upload_image(upload_url, picture_file_name)
        owner_id, photo_id = save_on_server(
            vk_group_id,
            vk_token,
            API_VERSION_VK,
            server,
            photo,
            vk_hash
        )
        post_on_the_wall(
            vk_group_id,
            vk_token,
            API_VERSION_VK,
            owner_id,
            photo_id,
            message,
        )
    finally:
        os.remove(picture_file_name)
