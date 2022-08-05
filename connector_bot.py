import logging


from telegram.ext import Updater, MessageHandler, Filters
from data import db_session
from data.tasks import Task


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)


logger = logging.getLogger(__name__)

TOKEN = ''


db_session.global_init("db/cafe27.db")
db_sess = db_session.create_session()


def check_bd(context):
    tasks = db_sess.query(Task).filter(Task.in_work == 0).all()
    to_remove = []
    for elem in tasks:
        if elem.task_type.startswith('del'):
            context.bot.send_message('@mybotstes', f'{elem.task_type}')
            to_remove.append(elem.id)
        else:
            context.bot.send_message('@mybotstes', f'{elem.task_type}_{elem.item_id}')
            elem.in_work = True
    for elem in to_remove:
        db_sess.delete(elem)
    db_sess.commit()


def main():
    update = Updater(TOKEN)
    update.bot.get_updates(allowed_updates=['channel_post'])
    update.job_queue.run_repeating(check_bd, interval=5, first=1)
    update.start_polling()
    update.idle()


if __name__ == '__main__':
    main()