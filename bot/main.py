from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

from bot import settings
from bot.handlers import handlers_functions

from logging.handlers import RotatingFileHandler


log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logFile = 'bot.log'

my_handler = RotatingFileHandler(logFile, maxBytes=10240)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)

app_log = logging.getLogger('root')
app_log.setLevel(logging.INFO)

app_log.addHandler(my_handler)

PROXY = {'proxy_url': settings.PROXY_URL,
         'urllib3_proxy_kwargs': {'username': settings.PROXY_USERNAME,
                                  'password': settings.PROXY_PASSWORD}}


def main():
    updater = Updater(settings.TOKEN, use_context=True, request_kwargs=PROXY)

    # создание диспечера
    dp = updater.dispatcher

    # обработчик команд
    start_handler = CommandHandler('start', handlers_functions.start_bot)
    dp.add_handler(start_handler)
    # dp.add_handler(CommandHandler('guess', guess_number))
    # dp.add_handler(CommandHandler('cat', send_cat_picture))

    # обработчик кнопок
    dp.add_handler(MessageHandler(Filters.regex(
        '^(Список ближайших пяти пусков ракето-носителей)$'),
        handlers_functions.rocket_launch))
    dp.add_handler(MessageHandler(Filters.location,
                                  handlers_functions.user_coordinates))

    # обработчик любых сообщений, обрабатывает только текст
    # dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    # частые обращения за обновлением
    updater.start_polling()

    # постоянная работа пока не отключат бота
    updater.idle()