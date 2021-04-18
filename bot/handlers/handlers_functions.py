from telegram import ReplyKeyboardMarkup, KeyboardButton
import os
import os.path

from bot.handlers.utils import haversine, five_launch


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
def user_coordinates(update, context):
    distance = haversine(update.message.location)
    update.message.reply_text(f'Растояние до космодрома {distance} км!',
                              reply_markup=get_keyboard())


# команда получения данных по пяти пускам
def rocket_launch(update, context):
    launch = five_launch()
    for item in launch:
        text = item['text']
        filename = f'images/{item["image"]}.jpg'
        image = os.path.abspath(filename)

        chat_id = update.effective_chat.id
        context.bot.send_photo(chat_id=chat_id, photo=open(image, 'rb'),
                               caption=text, reply_markup=get_keyboard())
