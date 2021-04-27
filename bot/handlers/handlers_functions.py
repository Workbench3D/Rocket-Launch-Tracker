from telegram import ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, \
    InlineKeyboardButton, InlineKeyboardMarkup, Location
import os
import os.path
from datetime import datetime

from bot.handlers.utils import find_near_pad_location, \
    send_processed_info_five_launch


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
            text = item['text']
            image = item['image']

    filename = os.path.join('images', f'{image}.jpg')
    image = os.path.abspath(filename)

    chat_id = update.effective_chat.id
    try:
        context.bot.send_photo(chat_id=chat_id, photo=open(image, 'rb'),
                               caption=text)
    except FileNotFoundError:
        context.bot.send_message(chat_id=chat_id, text=text)
