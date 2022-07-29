import logging


from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, PreCheckoutQueryHandler
from telegram.ext import CallbackQueryHandler, ConversationHandler
from telegram import LabeledPrice, ShippingQuery, ShippingOption, PreCheckoutQuery, SuccessfulPayment
from handlers import start, text_handler, callback_hand, location_hand, checkout_process, successful_payment
from handlers import conversation_start, first_response, second_response,\
    third_response, fourth_response, fifth_response, sixth_response, seventh_response, eighth_response, ninth_response,\
    stop


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)


logger = logging.getLogger(__name__)


TOKEN = '5412543523:AAEiLUcXgspy4bqUyKFCkC7lmsdjIzvskAE'


restaurant_conversation = ConversationHandler(
    entry_points=[CommandHandler('conversationstart', conversation_start)],
    states={
        1: [MessageHandler(Filters.text & ~Filters.command, first_response)],

        2: [MessageHandler(Filters.text & ~Filters.command, second_response)],

        3: [MessageHandler(Filters.text & ~Filters.command, third_response)],

        4: [MessageHandler(Filters.text & ~Filters.command, fourth_response)],

        5: [MessageHandler(Filters.text & ~Filters.command, fifth_response)],

        6: [MessageHandler(Filters.text & ~Filters.command, sixth_response)],

        7: [MessageHandler(Filters.text & ~Filters.command, seventh_response)],

        8: [MessageHandler(Filters.text & ~Filters.command, eighth_response)],

        9: [MessageHandler(Filters.text & ~Filters.command, ninth_response)],

    },

    fallbacks=[CommandHandler('stop', stop)]
)


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
    dp.add_handler(PreCheckoutQueryHandler(checkout_process))
    dp.add_handler(MessageHandler(Filters.successful_payment, successful_payment))
    dp.add_handler(CommandHandler('conversationstart', conversation_start))
    dp.add_handler(restaurant_conversation)
    update.start_polling()
    update.idle()


if __name__ == '__main__':
    main()
