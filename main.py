import logging


from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, PreCheckoutQueryHandler
from telegram.ext import CallbackQueryHandler
from handlers import start, text_handler, callback_hand, location_hand, checkout_process, successful_payment
from handlers import restaurant_conversation, types_init
import json


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)


logger = logging.getLogger(__name__)


with open('json/messages.json') as json_d:
    json_keys_data = json.load(json_d)


TOKEN = json_keys_data['tokens']['main_bot_token']


def main():
    types_init()
    update = Updater(TOKEN)
    dp = update.dispatcher
    start_handler = CommandHandler('start', start)
    text_handler1 = MessageHandler(Filters.text, text_handler)
    location_handler = MessageHandler(Filters.location, location_hand)
    callback_handler = CallbackQueryHandler(callback_hand)
    dp.add_handler(restaurant_conversation)
    dp.add_handler(start_handler)
    dp.add_handler(text_handler1)
    dp.add_handler(callback_handler)
    dp.add_handler(location_handler)
    dp.add_handler(PreCheckoutQueryHandler(checkout_process))
    dp.add_handler(MessageHandler(Filters.successful_payment, successful_payment))

    update.start_polling()
    update.idle()


if __name__ == '__main__':
    main()
