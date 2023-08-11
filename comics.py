import os
import requests
from environs import Env
from random import randint

API_VERSION_VK = 5.131


def get_upload_url(url, group_id, token, version):
    """ Возвращает адрес сервера для загрузки фотографии на стену пользователя или сообщества.
        :param url: url vk
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
        f'{url}photos.getWallUploadServer',
        params=server_params,
    )
    server_response.raise_for_status()
    return server_response.json()['response']['upload_url']


def upload_image(url, image):
    """
        :param url: адрес для загрузки фото
        :param image: картинка формата: JPG, PNG, GIF.
        :return: параметры server, photo, vk_hash,
    """
    payload = {
        'photo': image,
    }
    upload_response = requests.post(url, files=payload)
    upload_response.raise_for_status()
    return upload_response.json()['server'], upload_response.json()['photo'], upload_response.json()['hash']


def save_on_server(url, group_id, token, version, server, photo, vk_hash):
    """ Сохраняет фотографии после успешной загрузки на URI, полученный методом photos.getWallUploadServer.
        :param url: url vk
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
    response = requests.get(f"{url}photos.saveWallPhoto", params=params)
    response.raise_for_status()
    response = response.json()['response'][0]
    return response['owner_id'], response['id']


def post_on_the_wall(url, group_id, token, version, owner_id, photo_id, message, copyright):
    """ Позволяет создать запись на стене, опубликовать существующую запись.
        :param url: vk url
        :param group_id: id группы вк
        :param token: токен
        :param version: версия api вк
        :param owner_id: id владельца фото
        :param photo_id: id фото
        :param message: сообщения на стене
        :param copyright: сообщение для copyright
    """
    photo = f"photo{owner_id}_{photo_id}"
    params = {
        'access_token': token,
        'v': version,
        'owner_id': 0-int(group_id),
        'from_group': 1,
        'attachments': photo,
        'message': message,
        'close_comments': 0,
        'copyright': copyright,
    }
    response = requests.get(f"{url}wall.post", params=params)
    response.raise_for_status()
    return response.json()


def save_photo(url_image, name_image, path_image):
    """
        :param url_image: url картинки
        :param name_image: имя для картинки
        :param path_image: путь сохранения
    """
    os.makedirs(path_image, exist_ok=True)
    response = requests.get(url_image)
    response.raise_for_status()
    with open(f"{path_image}{os.sep}{name_image}", 'wb') as file:
        file.write(response.content)


if __name__ == '__main__':
    env = Env()
    env.read_env()
    vk_client_id = env.str("VK_CLIENT_ID")
    vk_token = env.str("ACCESS_TOKEN")
    vk_group_id = env.str("GROUP_ID")
    vk_url_api = "https://api.vk.com/method/"
    url = f"https://xkcd.com/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    picture_number = randint(0, response.json()['num'])
    url = f"https://xkcd.com/{picture_number}/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    message = response.json()['alt']
    picture_file_name = f"{picture_number}.png"
    save_photo(url_image=response.json()['img'], name_image=picture_file_name, path_image=os.getcwd())
    upload_url = get_upload_url(vk_url_api, vk_group_id, vk_token, API_VERSION_VK)
    with open(picture_file_name, 'rb') as comics_img:
        server, photo, vk_hash = upload_image(upload_url, comics_img)
        owner_id, photo_id = save_on_server(
            url=vk_url_api,
            group_id=vk_group_id,
            token=vk_token,
            version=API_VERSION_VK,
            server=server,
            photo=photo,
            vk_hash=vk_hash
        )
        post_on_the_wall(
            url=vk_url_api,
            group_id=vk_group_id,
            token=vk_token,
            version=API_VERSION_VK,
            owner_id=owner_id,
            photo_id=photo_id,
            message=message,
            copyright=url
        )
    os.remove(comics_img.name)
