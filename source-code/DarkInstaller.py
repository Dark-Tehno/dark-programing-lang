import os
import shutil
import requests
import zipfile
import io
import sys
import uuid


def install(mod_name):
    url = f'https://psv449.pythonanywhere.com/install/{mod_name}/'

    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        file_url = data['file']

        file_response = requests.get(file_url)
        file_response.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(file_response.content)) as zip_file:
            zip_file.extractall(f'mods/{mod_name}')

        print('Модификация успешно скачана')
        description = data['description']
        print(f'Описание:\n{description}')
    except requests.exceptions.HTTPError as err:
        print('HTTP error occurred:', err)
    except requests.exceptions.RequestException as err:
        print('Error occurred:', err)
    except zipfile.BadZipFile:
        print('Ошибка: файл не является корректным zip-архивом.')
    except Exception as e:
        print('Произошла ошибка:', e)

def uninstall(mod_name):
    mod_path = f'mods/{mod_name}'

    try:
        if os.path.exists(mod_path):
            shutil.rmtree(mod_path)
            print('Модификация успешно удалена:', mod_name)
        else:
            print('Ошибка: Модификация не найдена:', mod_name)
    except Exception as e:
        print('Произошла ошибка при удалении модификация:', e)

def add_mod(mod_name, mod_description, mod_file):
    try:
        url = 'https://psv449.pythonanywhere.com/add/'
        files = {
            'file': open(mod_file, 'rb')
        }
        data = {
            'name': mod_name,
            'description': open(mod_description, 'r')
        }

        response = requests.post(url, files=files, data=data)

        response_data = response.json()

        if response.status_code == 201:
            print("Модификация успешно добавлена:")
            print(f"Название: {response_data['mod'].get('name', 'Не указано')}")
            print(f"Описание: {response_data['mod'].get('description', 'Не указано')}")
            print(f"Файл: {response_data['mod'].get('file', 'Не указано')}")
            print(f"Токен: {response_data['token']}")
        else:
            print("Ошибка при добавлении модификации:")
            print(response_data.get('error', 'Неизвестная ошибка'))
    except Exception as e:
        print("Ошибка при добавлении модификации:", e)
def edit(token, description, file, name=None):
    try:
        try:
            uuid_obj = uuid.UUID(token)
            if uuid_obj.version != 4:
                raise ValueError("Токен не является UUID версии 4.")
        except ValueError as e:
            print(f"Ошибка: {e}")
            return

        url = f'https://psv449.pythonanywhere.com/edit/'
        files = {
            'file': open(file, 'rb')
        }
        if name is not None:
            data = {
                'token': token,
                'description': open(description, 'r'),
                'name': name
            }
        else:
            data = {
                'token': token,
                'description': open(description, 'r')
            }

        response = requests.put(url, files=files, data=data)

        response_data = response.json()
        if response.status_code != 200:
            print('Ошибка:', response_data['error'])
        else:
            print("Результат редактирования модификации:")
            print(f"Название: {response_data.get('name', 'Не указано')}")
            print(f"Описание: {response_data.get('description', 'Не указано')}")
            print(f"Файл: {response_data.get('file', 'Не указано')}")
            print(f"Токен: {response_data.get('token', 'Не указано')}")
    except Exception as e:
        print("Ошибка при редактировании модификации:", e)


args = sys.argv

if len(args) < 2:
    print("Недостаточно аргументов")
    sys.exit(1)
else:
    if args[1] == 'install':
        if len(args) != 3:
            print("Неверное число аргументов")
            sys.exit(1)
        else:
            mod_name = args[2]
            install(mod_name)
    elif args[1] == 'uninstall':
        if len(args) != 3:
            print("Неверное число аргументов")
            sys.exit(1)
        else:
            mod_name = args[2]
            uninstall(mod_name)
    elif args[1] == 'upload':
        if len(args) != 5:
            print("Неверное число аргументов")
            sys.exit(1)
        else:
            mod_name = args[2]
            mod_description = args[3]
            mod_file = args[4]
            add_mod(mod_name, mod_description, mod_file)
    elif args[1] == 'edit':
        if len(args) < 5 or len(args) > 6:
            print("Неверное число аргументов")
            sys.exit(1)
        else:
            token = args[2]
            description = args[3]
            file = args[4]
            name = args[5] if len(args) == 6 else None
            edit(token, description, file, name)
    else:
        print("Неправильный аргумент. Используйте install, uninstall, upload или edit")
