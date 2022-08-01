import logging
from chat_bot_handlers import start, applications, confirm, reject, text_handler, blacklist, unban, translate, bot_help


from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)


logger = logging.getLogger(__name__)

TOKEN = '5441072240:AAF5mrQ6BfsMqrV7cee_G2lQNq6RuownURY'


def main():
    update = Updater(TOKEN)
    dp = update.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('applications', applications))
    dp.add_handler(CommandHandler('confirm', confirm,
                                  pass_args=True,

                                  pass_job_queue=True,

                                  pass_chat_data=True,

                                  pass_user_data=True
                                  ))
    dp.add_handler(CommandHandler('reject', reject,
                                  pass_args=True,

                                  pass_job_queue=True,

                                  pass_chat_data=True,

                                  pass_user_data=True
                                  ))
    dp.add_handler(CommandHandler('blacklist', blacklist,
                                  pass_args=True,

                                  pass_job_queue=True,

                                  pass_chat_data=True,

                                  pass_user_data=True
                                  ))
    dp.add_handler(CommandHandler('unban', unban))
    dp.add_handler(CommandHandler('translate', translate,
                                  pass_args=True,

                                  pass_job_queue=True,

                                  pass_chat_data=True,

                                  pass_user_data=True
                                  ))
    dp.add_handler(CommandHandler('help', bot_help))
    dp.add_handler(MessageHandler(Filters.text, text_handler))
    update.start_polling()
    update.idle()


if __name__ == '__main__':
    main()