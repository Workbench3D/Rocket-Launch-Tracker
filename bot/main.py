from bot.handlers.handlers_functions import *
from bot import settings
from logging.handlers import RotatingFileHandler
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater)
import logging


log_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logFile = 'bot.log'
my_handler = RotatingFileHandler(logFile, maxBytes=10240)
my_handler.setFormatter(log_formatter)
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
    dp.add_handler(CommandHandler('start', start_bot))

    # обработчик кнопок
    dp.add_handler(MessageHandler(Filters.regex(
        '^(Список ближайших пяти пусков ракето-носителей)$'),
        send_launch_buttons))
    # dp.add_handler(MessageHandler(Filters.regex(
    #     '^(Подписаться на получение уведомлений)$'), subscribe))
    # dp.add_handler(MessageHandler(Filters.regex(
    #     '^(Отписаться от получение уведомлений)$'), unsubscribe))
    dp.add_handler(MessageHandler(Filters.location, send_near_pad_location))

    dp.add_handler(CallbackQueryHandler(send_launch_info))

    # обработчик любых сообщений, обрабатывает только текст
    # dp.add_handler(MessageHandler(Filters.text, notification_timer))

    # частые обращения за обновлением
    updater.start_polling()

    # постоянная работа пока не отключат бота
    updater.idle()
