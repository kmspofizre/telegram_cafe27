import logging
from chat_bot_handlers import start, applications, confirm, reject,\
    text_handler, blacklist, unban, translate, bot_help, link, poll_answer_handler
import json


from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, PollAnswerHandler


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)


logger = logging.getLogger(__name__)

with open('json/messages.json') as json_d:
    json_keys_data = json.load(json_d)


TOKEN = json_keys_data['tokens']['chat_bot_token']


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
    dp.add_handler(CommandHandler('link', link,
                                  pass_args=True,

                                  pass_job_queue=True,

                                  pass_chat_data=True,

                                  pass_user_data=True
                                  ))
    dp.add_handler(MessageHandler(Filters.text, text_handler))
    dp.add_handler(PollAnswerHandler(poll_answer_handler))
    update.bot.get_updates(allowed_updates=['channel_post', 'message', 'poll_answer'])
    update.start_polling()
    update.idle()


if __name__ == '__main__':
    main()