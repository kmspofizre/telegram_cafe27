import logging


from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ShippingQueryHandler, PreCheckoutQueryHandler
from telegram.ext import CallbackQueryHandler
from telegram import LabeledPrice, ShippingQuery, ShippingOption, PreCheckoutQuery, SuccessfulPayment
from handlers import start, text_handler, callback_hand, location_hand


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)


logger = logging.getLogger(__name__)


TOKEN = '5412543523:AAEiLUcXgspy4bqUyKFCkC7lmsdjIzvskAE'


def main():
    update = Updater(TOKEN)
    dp = update.dispatcher
    start_handler = CommandHandler('start', start)
    text_handler1 = MessageHandler(Filters.text, text_handler)
    location_handler = MessageHandler(Filters.location, location_hand)
    callback_handler = CallbackQueryHandler(callback_hand)
    dp.add_handler(start_handler)
    dp.add_handler(text_handler1)
    dp.add_handler(callback_handler)
    dp.add_handler(location_handler)
    update.start_polling()
    update.idle()


if __name__ == '__main__':
    main()