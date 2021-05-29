from bot.handlers.utils import *
from datetime import datetime
from telegram import (ReplyKeyboardMarkup, KeyboardButton,
                      InlineKeyboardButton, InlineKeyboardMarkup)
import random



def get_keyboard():
    """Команда реализующая отрображение клавиатуры, срабатывающая
    после отправки команды /start"""

    my_keyboard = ReplyKeyboardMarkup([
        [KeyboardButton('Ближайший космодром', request_location=True)],
        ['Список ближайших пяти пусков ракето-носителей']
        # ['Подписаться на получение уведомлений',
        #  'Отписаться от получение уведомлений']
    ], resize_keyboard=True)
    return my_keyboard


def start_bot(update, context):
    """Функция срабатывающая при отправки команды /start, отправляющая
    сообщение и запускающая функцию добавления пользователя телеграм
    в базу данных бота"""

    DAY = 60 * 60 * 24
    add_database(update.message.from_user.id)
    chat_id = update.message.chat_id
    context.job_queue.run_repeating(notification, interval=DAY, context=chat_id)

    text = ('Добро пожаловать в Rocket Launch Tracker!\n\n'
            'Бот предназначен для отслеживания пусков '
            'ракета-носителей разных стран.\n\n'
            'Чем помочь?')
    update.message.reply_text(text=text, reply_markup=get_keyboard())


def send_near_pad_location(update, context):
    """Функция формирующая и отправляющая сообщение с информацией о
    ближайшем космодроме от пользователя телеграм"""

    route = find_near_pad_location(update.message.location)
    pad_name = route['pad_name']
    distance = route['distance']
    azimuth = route['azimuth']

    text = f'Ближайший космодром {pad_name}\n' \
           f'расположен на растоянии {distance} км,\n' \
           f'на {azimuth} напровлении!'
    update.message.reply_text(text=text, reply_markup=get_keyboard())


def send_launch_buttons(update, context):
    """Функция формирующая 5 инлайновых кнопок с краткой информацией
    о предстоящих пусках"""

    launch = edit_json_api()

    inline_list = []

    for item in launch:
        name_mission = item['name_mission']
        inline_button = [InlineKeyboardButton(
            text=name_mission, callback_data=name_mission)]
        inline_list.append(inline_button)

    inline_keyboard = InlineKeyboardMarkup(inline_list)

    text = 'Названия миссии ближайших пяти пусков ракето-носителей'
    update.message.reply_text(text=text, reply_markup=inline_keyboard)


def send_launch_info(update, context):
    """Отправка сообщения в чат бота после нажатия инлайновой кнопки"""

    query = update.callback_query
    query.answer()
    query = query.data
    chat_id = update.effective_chat.id

    text, image = make_message(query)

    try:
        context.bot.send_photo(chat_id=chat_id, photo=open(image, 'rb'),
                               caption=text)
    except FileNotFoundError:
        context.bot.send_message(chat_id=chat_id, text=text)


# def subscribe(update, context):
#     """Функция меняющая статус подписки на True если пользователь
#     телеграм был неподписан, или отправляющая сообщение что
#     пользователь уже подписан на рассылку"""
#
#     status = subscribe_database(update.message.from_user.id)
#
#     if status is False:
#         text = 'Вы уже подписаны на уведомления бота!'
#     else:
#         text = 'Вы подписалить на уведомления бота!'
#
#     update.message.reply_text(text=text, reply_markup=get_keyboard())


# def unsubscribe(update, context):
#     """Функция меняющая статус подписки на False если пользователь
#     телеграм был подписан, или отправляющая сообщение что
#     пользователь и так отподписан от рассылки"""
#
#     status = unsubscribe_database(update.message.from_user.id)
#
#     if status is False:
#         text = 'Вы уже отписаны от уведомлений бота!'
#     else:
#         text = 'Вы отписались от уведомлений бота!'
#
#     update.message.reply_text(text=text, reply_markup=get_keyboard())


def notification(context):
    """Функция уведомляющая за сутки о ближайшем пуске"""

    DAY = 60 * 60 * 24
    now_time = round(datetime.utcnow().timestamp())
    start_time, text = near_start_launch()
    start_time = start_time.timestamp()
    delta_time = start_time - now_time

    if delta_time <= DAY:
        job = context.job

        text, image = notification_message()

        try:
            context.bot.send_photo(job.context, photo=open(image, 'rb'),
                                   caption=text)
        except FileNotFoundError:
            context.bot.send_message(job.context, text=text)


# команда генерации юзеров для тестирования БД
# def random_user(update, context):
#     for i in range(100):
#         telegram_id = random.randrange(1000000000)
#         sub_status = random.randint(0, 1)
#         if sub_status == 1:
#             sub_status = True
#         else:
#             sub_status = False
#         generate_person = User(telegram_id=telegram_id, sub_status=sub_status)
#         s = Session()
#         s.add(generate_person)
#         s.commit()
