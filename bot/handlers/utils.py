from math import pi, sqrt, sin, cos, atan2
import os
import os.path
import requests


def haversine(pos1):
    filename = f'resources/pad_location.csv'
    pad_location = os.path.abspath(filename)

    pos2 = {'longitude': 63.30778, 'latitude': 45.96611}

    degree_to_rad = float(pi / 180.0)

    lat1 = pos1['latitude']
    long1 = pos1['longitude']

    lat2 = pos2['latitude']
    long2 = pos2['longitude']

    d_lat = (lat2 - lat1) * degree_to_rad
    d_long = (long2 - long1) * degree_to_rad

    a = pow(sin(d_lat / 2), 2) + cos(lat1 * degree_to_rad) * \
        cos(lat2 * degree_to_rad) * pow(sin(d_long / 2), 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    km = round((6367 * c), 1)

    return km


def five_launch():
    url = 'https://fdo.rocketlaunch.live/json/launches/next/5'
    r = requests.get(url)
    result = r.json()['result']

    launch = []

    for item in result:
        name = str(item['name'])
        provider = str(item['provider']['name'])
        vehicle = str(item['vehicle']['name'])
        location = str(item['pad']['location']['name'])
        win_open = str(item['win_open'])

        text = f'Название миссии - {name}\n' \
               f'Поставщик - {provider}\n' \
               f'Ракето-носитель - {vehicle}\n' \
               f'Место пуска - {location}\n' \
               f'Время пуска - {win_open}\n'

        message = {'image': vehicle, 'text': text}
        launch.append(message)

    return launch
