from bot import settings
from bot.models import Session, User
from datetime import datetime
from pyproj import Geod
import csv
import os
import os.path
import requests

session = Session()


def edit_json_api():
    """Функция получающая JSON информацию с API, и возвращающая требуюмую
    информацию в нормальном виде для рабты представленных функций бота"""

    result = requests.get(settings.ROCKET_LAUNCH_API).json()['result']

    launch_info = []

    for item in result:
        name_mission = item['name']
        provider = item['provider']['name']
        vehicle = item['vehicle']['name']
        location = item['pad']['location']['name']
        start_time = item['win_open']

        if start_time is not None:
            start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%MZ')
        else:
            start_time = 'Неизвестно'

        message = {'name_mission': name_mission, 'provider': provider,
                   'vehicle': vehicle, 'location': location,
                   'start_time': start_time}

        launch_info.append(message)

    return launch_info


def make_message(query):
    """Функция формирующая сообщение после нажатия инлайновой кнопки"""

    launch = edit_json_api()

    for item in launch:
        if query == item['name_mission']:
            name_mission = item['name_mission']
            provider = item['provider']
            vehicle = item['vehicle']
            location = item['location']
            start_time = item['start_time']

    filename = os.path.join('images', f'{vehicle}.jpg')
    image = os.path.abspath(filename)

    text = f'Название миссии - {name_mission}\n' \
           f'Поставщик - {provider}\n' \
           f'Ракето-носитель - {vehicle}\n' \
           f'Место пуска - {location}\n' \
           f'Время пуска - {start_time}\n'

    return text, image


def find_near_pad_location(my_point):
    """Функция расчитывающая растояние и азимут к ближайшему космодрому"""

    filename = os.path.join('resources', 'pad_location.csv')
    pad_location = os.path.abspath(filename)

    my_lat = my_point['latitude']
    my_long = my_point['longitude']

    distance = None

    with open(pad_location, encoding="utf-8") as file:
        reader = csv.reader(file)

        for row in reader:
            pad_lat = row[2]
            pad_long = row[3]

            # расчет прямого, обратного азимута и дистанции(в метрах)
            forward_a, back_a, length = Geod(ellps='WGS84'). \
                inv(my_long, my_lat, pad_long, pad_lat)

            if distance is None or length <= distance:
                distance = length
                pad_name = row[1]
                azimuth = forward_a

    route = formatted_coordinate(distance=distance, pad_name=pad_name,
                                 azimuth=azimuth)

    return route


def formatted_coordinate(distance, pad_name, azimuth):
    """Функция преобразующая полученные расчеты функции
    find_near_pad_location() в информацию для формирования сообщения"""

    # преобразование азимута в направление
    direction = {'северном': (-22.5, 22.5),
                 'северо-восточном': (22.5, 67.5),
                 'восточном': (67.5, 112.5),
                 'юго-восточном': (112.5, 157.5),
                 'западном': (-112.5, -67.5),
                 'северо-западном': (-67.5, -22.5,),
                 'юго-западном': (-157.5, -112.5)}

    azimuth = round(azimuth, 1)

    if azimuth >= 157.5 or azimuth <= -157.5:
        azimuth = 'южном'
    else:
        for name, coordinate in direction.items():

            if coordinate[0] <= azimuth < coordinate[1]:
                azimuth = name
                break

    # преобразование (м -> км)
    KM = 1000
    distance = round((distance / KM), 1)

    route = {'pad_name': pad_name, 'distance': distance, 'azimuth': azimuth}

    return route


def add_database(telegram_id):
    """Функция добавляющая пользователя телеграм в базу данных бота.

    Это нуждо чтобы отслеживать подписки пользователей на бота"""

    user_info = User(telegram_id=telegram_id, sub_status=False)
    session.add(user_info)
    session.commit()


def subscribe_database(telegram_id):
    """Функция меняющая статус пользователя в базе данных на подписаного"""

    user_info = session.query(User).filter_by(telegram_id=telegram_id).first()

    if user_info.sub_status is True:
        return False
    else:
        user_info.sub_status = True
        session.commit()
        return True


def unsubscribe_database(telegram_id):
    """Функция меняющая статус пользователя в базе данных на отподписаного"""

    user_info = session.query(User).filter_by(telegram_id=telegram_id).first()

    if user_info.sub_status is False:
        return False
    else:
        user_info.sub_status = False
        session.commit()
        return True
