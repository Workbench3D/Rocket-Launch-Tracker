from bot import settings
from pyproj import Geod
import os
import os.path
import requests
import csv


def send_processed_info_five_launch():
    result = requests.get(settings.ROCKET_LAUNCH_API).json()['result']

    launch = []

    for item in result:
        name_mission = str(item['name'])
        provider = str(item['provider']['name'])
        vehicle = str(item['vehicle']['name'])
        location = str(item['pad']['location']['name'])
        win_open = str(item['win_open'])

        text = f'Название миссии - {name_mission}\n' \
               f'Поставщик - {provider}\n' \
               f'Ракето-носитель - {vehicle}\n' \
               f'Место пуска - {location}\n' \
               f'Время пуска - {win_open}\n'

        message = {'image': vehicle, 'name_mission': name_mission,
                   'text': text}
        launch.append(message)

    return launch


def find_near_pad_location(my_point):
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
            forward_a, back_a, length = Geod(ellps='WGS84').\
                inv(my_long, my_lat, pad_long, pad_lat)

            if distance is None or length <= distance:
                distance = length
                pad_name = row[1]
                azimuth = forward_a

    route = formatted_coordinate(distance=distance, pad_name=pad_name,
                              azimuth=azimuth)

    return route


# функция обрабатывающая данный по геолокации
def formatted_coordinate(distance, pad_name, azimuth):

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
    distance = round((distance/KM), 1)

    route = {'pad_name': pad_name, 'distance': distance, 'azimuth': azimuth}

    return route
