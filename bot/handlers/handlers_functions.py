from telegram import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardButton, InlineKeyboardMarkup
import os
import os.path
from datetime import datetime
from bot.models import Session, User

from bot.handlers.utils import find_near_pad_location, \
    send_processed_info_five_launch
import random
import asyncio

session = Session()


# клавиатура
def get_keyboard():
    my_keyboard = ReplyKeyboardMarkup([
        [KeyboardButton('Ближайший космодром', request_location=True)],
        ['Список ближайших пяти пусков ракето-носителей'],
        ['Подписаться на получение уведомлений',
         'Отписаться от получение уведомлений']
    ], resize_keyboard=True)
    return my_keyboard


# функция запуска старта в боте
def start_bot(update, context):
    text = 'Добро пожаловать в Rocket Launch Tracker!\n\n' \
           'Бот предназначен для отслеживания пусков ' \
           'ракета-носителей разных стран.\n\n' \
           'Чем помочь?'
    user_id = update.message.from_user.id
    user_info = User(user_id=user_id, sub_status=False)
    session.add(user_info)
    session.commit()
    update.message.reply_text(text, reply_markup=get_keyboard())


# команда получения геокоординат
def send_near_pad_location(update, context):
    route = find_near_pad_location(update.message.location)
    pad_name = route['pad_name']
    distance = route['distance']
    azimuth = route['azimuth']
    text = f'Ближайший космодром {pad_name}\n' \
           f'расположен на растоянии {distance} км,\n' \
           f'на {azimuth} напровлении!'
    update.message.reply_text(text=text, reply_markup=get_keyboard())


# команда получения данных и представлении в виде кнопок по пяти пускам
def send_launch_buttons(update, context):
    launch = send_processed_info_five_launch()

    inline_list = []
    for item in launch:
        callback_data = item['name_mission']
        name_mission = item['name_mission']
        inline_button = [InlineKeyboardButton(
            text=name_mission, callback_data=callback_data)]
        inline_list.append(inline_button)
    inline_keyboard = InlineKeyboardMarkup(inline_list)
    text = 'Названия миссии ближайших пяти пусков ракето-носителей'
    update.message.reply_text(text=text, reply_markup=inline_keyboard)


def send_launch_info(update, context):
    query = update.callback_query
    query.answer()
    launch = send_processed_info_five_launch()
    text = str()
    image = str()
    for item in launch:
        if query.data == item['name_mission']:
            name_mission = item['name_mission']
            provider = item['provider']
            image = item['image']
            location = item['location']
            start_time = item['start_time']
            text = f'Название миссии - {name_mission}\n' \
                   f'Поставщик - {provider}\n' \
                   f'Ракето-носитель - {image}\n' \
                   f'Место пуска - {location}\n' \
                   f'Время пуска - {start_time}\n'

    filename = os.path.join('images', f'{image}.jpg')
    image = os.path.abspath(filename)

    chat_id = update.effective_chat.id
    try:
        context.bot.send_photo(chat_id=chat_id, photo=open(image, 'rb'),
                               caption=text)
    except FileNotFoundError:
        context.bot.send_message(chat_id=chat_id, text=text)


def subscription(update, context):
    user_id = update.message.from_user.id
    user_info = session.query(User).filter_by(user_id=user_id).first()
    if user_info.sub_status is True:
        text = 'Вы уже подписаны на уведомления бота!'
        update.message.reply_text(text, reply_markup=get_keyboard())
    else:
        user_info.sub_status = True
        session.commit()
        text = 'Вы подписалить на уведомления бота!'
        update.message.reply_text(text, reply_markup=get_keyboard())


# def unsubscribe(update, context):
#     user_id = update.message.from_user.id
#     user_info = session.query(User).filter_by(user_id=user_id).first()
#     if user_info.sub_status is False:
#         text = 'Вы уже отписаны от уведомлений бота!'
#         update.message.reply_text(text, reply_markup=get_keyboard())
#     else:
#         user_info.sub_status = False
#         session.commit()
#         text = 'Вы отписались от уведомлений бота!'
#         update.message.reply_text(text, reply_markup=get_keyboard())


# команда генерации юзеров для тестирования БД
# def random_user(update, context):
#     for i in range(100):
#         user_id = random.randrange(1000000000)
#         sub_status = random.randint(0, 1)
#         if sub_status == 1:
#             sub_status = True
#         else:
#             sub_status = False
#         generate_person = User(user_id=user_id, sub_status=sub_status)
#         s = Session()
#         s.add(generate_person)
#         s.commit()


def unsubscribe(update, context):
    async def main_loop():
        DAY = 86400  # время секунд в одних сутках

        while True:
            start_time, text = None, None
            launch = send_processed_info_five_launch()
            for item in launch:
                start_time = item['start_time']
                name_mission = item['name_mission']
                provider = item['provider']
                image = item['image']
                location = item['location']
                text = f'Название миссии - {name_mission}\n' \
                       f'Поставщик - {provider}\n' \
                       f'Ракето-носитель - {image}\n' \
                       f'Место пуска - {location}\n' \
                       f'Время пуска - {start_time}\n'
                if start_time is None:
                    continue
                break
            # start_time = '2021-05-03T19:01Z'
            # start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%MZ')
            start_time_sec = start_time.timestamp()
            now_time_user = datetime.utcnow().isoformat(' ', 'seconds')
            now_time_user = datetime.strptime(now_time_user, '%Y-%m-%d %H:%M:%S')
            now_time_user_sec = now_time_user.timestamp()
            delta_time = start_time_sec - now_time_user_sec
            if delta_time > DAY:
                await asyncio.sleep(5)
                print('lol')
                # await asyncio.sleep(DAY)
            else:
                await asyncio.sleep(10)
                # await asyncio.sleep(delta_time)
                update.message.reply_text(text=text, reply_markup=get_keyboard())

    asyncio.run(main_loop())
