import json
from telegram import InputMediaPhoto, InputMediaVideo
from data import db_session
from data.users import User
from data.restaurants import Restaurant
from data.restaurant_types import RestaurantTypes
from templates import card_for_moderator, post_template
from telegram import ChatPermissions
from data.blacklist import Blacklist
from data.posts import Posts
from data.polls import Poll
from data.banners import Banner
from data.tasks import Task
import datetime
import requests

db_session.global_init("db/cafe27.db")
db_sess = db_session.create_session()
vid_ext = tuple('.mp4')
ph_ext = tuple(['.jpg', '.jpeg', '.png'])
with open('json/messages.json') as json_d:
    json_keys_data = json.load(json_d)

folder_id = json_keys_data['API_keys']['folder_id']
translate_api_server = json_keys_data['API_keys']["translate_api_server"]
API_KEY = json_keys_data['API_keys']['translator']


def remove_job_if_exists(context):
    name = context.job.context[0]
    current_jobs = context.job_queue.get_jobs_by_name(name)

    for job in current_jobs:
        job.schedule_removal()
    task = db_sess.query(Task).filter(Task.task_type == context.job.context[2]).one()
    db_sess.delete(task)
    db_sess.commit()


def poll(context):
    with open('json/messages.json') as json_messages:
        json_messages_data = json.load(json_messages)
    job = context.job
    data = job.context.split('_')
    new_poll = db_sess.query(Poll).filter(Poll.id == data[1]).one()
    variants = new_poll.variants.split(';')
    number_of_variants = len(variants)
    header = new_poll.header
    is_anon = new_poll.is_anon
    mes_poll = context.bot.send_poll(json_messages_data['chat_id'], question=header,
                                     options=variants, is_anonymous=is_anon)
    rez = [0] * number_of_variants
    new_poll.answers = ';'.join(map(str, rez))
    new_poll.message_id = mes_poll.poll.id
    task = db_sess.query(Task).filter(Task.task_type == 'poll', Task.item_id == data[1]).all()[0]
    db_sess.delete(task)
    db_sess.commit()


def post(context):
    with open('json/messages.json') as json_messages:
        json_messages_data = json.load(json_messages)
    job = context.job
    data = job.context.split('_')
    new_post = db_sess.query(Posts).filter(Posts.id == data[1]).one()
    if new_post.media is not None:
        media = new_post.media.split(';')
    else:
        media = []
    temp = post_template.substitute(
        header=new_post.header,
        text=new_post.text
    )
    if bool(media) and media[0] != '':

        photo = list(map(lambda x: InputMediaPhoto(open(x, 'rb')), media))
        photo[0].caption = temp
        photo[0].parse_mode = 'HTML'
        context.bot.send_media_group(json_messages_data['chat_id'], media=photo)
    else:
        context.bot.sendMessage(json_messages_data['chat_id'], temp, parse_mode='HTML')
    task = db_sess.query(Task).filter(Task.task_type == 'post', Task.item_id == data[1]).all()[0]
    db_sess.delete(task)
    db_sess.commit()


def banner(context):
    with open('json/messages.json') as json_messages:
        json_messages_data = json.load(json_messages)
    job = context.job
    data = job.context.split('_')
    new_banner = db_sess.query(Banner).filter(Banner.id == data[1]).all()[0]
    if new_banner.image is not None:
        if new_banner.text is not None:
            context.bot.send_media_group(json_messages_data['chat_id'],
                                         media=[InputMediaPhoto(open(new_banner.image, 'rb'), caption=new_banner.text)])
        else:
            context.bot.send_media_group(json_messages_data['chat_id'],
                                         media=[InputMediaPhoto(open(new_banner.image, 'rb'))])
    else:
        if new_banner.text is not None:
            context.bot.sendMessage(json_messages_data['chat_id'], text=new_banner.text)
    task = db_sess.query(Task).filter(Task.task_type == 'banner', Task.item_id == data[1]).all()[0]
    db_sess.delete(task)
    db_sess.commit()


def poll_answer_handler(update, context):
    answer = update.poll_answer
    poll_id = answer.poll_id
    answered_poll = db_sess.query(Poll).filter(Poll.message_id == poll_id).all()
    if bool(answered_poll):
        if not bool(answer.option_ids):
            user = str(answer.user.id)
            user_answer = list(filter(lambda x: x.split(':')[0] == user, answered_poll[0].all_answers.split(';')))[0]
            answer_id = int(user_answer.split(':')[1])
            all_answers = answered_poll[0].all_answers.split(';')
            all_answers.remove(user_answer)
            if len(all_answers) != 0:
                answered_poll[0].all_answers = ';'.join(all_answers)
                answers = list(map(int, answered_poll[0].answers.split(';')))
                answers[answer_id] -= 1
                answered_poll[0].answers = ';'.join(map(str, answers))
            else:
                answers = list(map(int, answered_poll[0].answers.split(';')))
                answers[answer_id] -= 1
                answered_poll[0].answers = ';'.join(map(str, answers))
                answered_poll[0].all_answers = None
            db_sess.commit()
        else:
            if answered_poll[0].all_answers is not None:
                user = str(answer.user.id)
                new_answer = f"{user}:{answer.option_ids[0]}"
                answers = list(map(int, answered_poll[0].answers.split(';')))
                answers[answer.option_ids[0]] += 1
                answered_poll[0].answers = ';'.join(map(str, answers))
                all_answers = answered_poll[0].all_answers.split(';')
                all_answers.append(new_answer)
                answered_poll[0].all_answers = ';'.join(all_answers)
            else:
                user = str(answer.user.id)
                new_answer = f"{user}:{answer.option_ids[0]}"
                answers = list(map(int, answered_poll[0].answers.split(';')))
                answers[answer.option_ids[0]] += 1
                answered_poll[0].all_answers = new_answer
                answered_poll[0].answers = ';'.join(map(str, answers))
            db_sess.commit()


def text_handler(update, context):
    with open('json/messages.json') as json_messages:
        json_messages_data = json.load(json_messages)
    try:
        mes = update.message
        text = update.message.text
        bad_words = json_messages_data['ban_words']
        try:
            if context.chat_data[mes.from_user.id]['number'] == \
                    json_messages_data['punishments']['spam']['number_of_messages']:
                context.chat_data[mes.from_user.id]['number'] = 0
            context.chat_data[mes.from_user.id]['mess'][context.chat_data[mes.from_user.id]['number']] = text
            context.chat_data[mes.from_user.id]['number'] += 1
            m = context.chat_data[mes.from_user.id]['mess']
            if len(set(m)) == 1 and '' not in m:
                time_delta = datetime.timedelta(minutes=json_messages_data['punishments']['spam']['timeout'])
                timeout = datetime.datetime.now() + time_delta
                context.bot.restrict_chat_member(update.message.chat_id,
                                                 update.message.from_user.id,
                                                 until_date=timeout - datetime.timedelta(hours=3),
                                                 permissions=ChatPermissions(
                                                     can_send_messages=False,
                                                     can_send_media_messages=False,
                                                     can_send_other_messages=False,
                                                     can_add_web_page_previews=False)
                                                 )
                context.bot.delete_message(update.message.chat_id,
                                           update.message.message_id)
                context.bot.sendMessage(update.message.chat_id,
                                        f"{mes.from_user.first_name} was restricted for"
                                        f" {json_messages_data['punishments']['spam']['name']}")
                new_to_blacklist = Blacklist(
                    telegram_id=mes.from_user.id,
                    reason=json_messages_data['punishments']['spam']['name'],
                    name=update.message.from_user.first_name,
                    username=update.message.from_user.username
                )
                db_sess.add(new_to_blacklist)
                db_sess.commit()
                return
        except KeyError:
            context.chat_data[mes.from_user.id] = {
                'mess': [''] * json_messages_data['punishments']['spam']['number_of_messages'],
                'number': 0
            }
        for word in text.split():
            if word.lower() in bad_words:
                time_delta = datetime.timedelta(minutes=json_messages_data['punishments']['ban_words']['timeout'])
                timeout = datetime.datetime.now() + time_delta
                context.bot.restrict_chat_member(update.message.chat_id,
                                                 update.message.from_user.id,
                                                 until_date=timeout - datetime.timedelta(hours=3),
                                                 permissions=ChatPermissions(
                                                     can_send_messages=False,
                                                     can_send_media_messages=False,
                                                     can_send_other_messages=False,
                                                     can_add_web_page_previews=False)
                                                 )
                context.bot.delete_message(update.message.chat_id,
                                           update.message.message_id)
                context.bot.sendMessage(update.message.chat_id,
                                        f"{mes.from_user.first_name} was restricted for"
                                        f" {json_messages_data['punishments']['ban_words']['name']}")
                new_to_blacklist = Blacklist(
                    telegram_id=mes.from_user.id,
                    reason=json_messages_data['punishments']['ban_words']['name'],
                    name=update.message.from_user.first_name,
                    username=update.message.from_user.username
                )
                db_sess.add(new_to_blacklist)
                db_sess.commit()
                return
    except AttributeError:
        command = update.channel_post.text
        data = command.split('_')
        if data[0] == 'post':
            task_date = db_sess.query(Task).filter(Task.task_type == 'post', Task.item_id == data[1]).all()[0].datetime
            context.job_queue.run_once(post, task_date - datetime.timedelta(hours=3), context=f"post_{data[1]}",
                                       name=f"post_{data[1]}")
        elif data[0] == 'banner':
            command = update.channel_post.text
            data = command.split('_')
            task_date = db_sess.query(Task).filter(Task.task_type == 'banner',
                                                   Task.item_id == data[1]).all()[0].datetime
            context.job_queue.run_once(banner, task_date - datetime.timedelta(hours=3), context=f"banner_{data[1]}",
                                       name=f"banner_{data[1]}")
        elif data[0] == 'poll':
            task_date = db_sess.query(Task).filter(Task.task_type == 'poll',
                                                   Task.item_id == data[1]).all()[0].datetime
            context.job_queue.run_once(poll, task_date - datetime.timedelta(hours=3), context=f"poll_{data[1]}",
                                       name=f"poll_{data[1]}")
        elif data[0] == 'del' and data[1] != 'restaurant':
            context.job_queue.run_once(remove_job_if_exists,
                                       1,
                                       context=[f"{data[1]}_{data[2]}", context, f'del_{data[1]}_{data[2]}'],
                                       name=f"del_{data[1]}_{data[2]}")


def start(update, context):
    user = db_sess.query(User).filter(User.telegram_id == update.message.from_user.id).one()
    if user.moderator:
        context.bot.sendMessage(update.message.chat_id, """Я бот-помощник модератора.\n
        Вы можете посмотреть заявки на добавление заведения, команда /applications\n
        Одобрить заявку /confirm <id заведения>\n
        Отклонить и удалить заявку /reject <id заведения>\n
        Увидеть всех заблокированных пользователей /blacklist\n
        Удалить пользователя из черного списка - /unban <telegram_id пользователя>""")


def applications(update, context):
    user = db_sess.query(User).filter(User.telegram_id == update.message.from_user.id).one()
    if user.moderator:
        to_confirm = db_sess.query(Restaurant).filter(Restaurant.confirmed == 0).all()
        applications_to_view = []
        for restaurant in to_confirm:
            owner = db_sess.query(User).filter(User.id == restaurant.owner).one()
            owner_des = f"{owner.username} {owner.user_link}"
            types = db_sess.query(RestaurantTypes).all()
            ntypes = list(map(int, restaurant.type.split(', ')))
            types = ', '.join(list((map(lambda y: y.type_name, filter(lambda x: x.id in ntypes, types)))))
            html = card_for_moderator.substitute(name=restaurant.name,
                                                 description=restaurant.description,
                                                 average_price=restaurant.average_price,
                                                 address=restaurant.address,
                                                 id=restaurant.id,
                                                 working_hours=restaurant.working_hours,
                                                 phone=restaurant.phone,
                                                 owner=owner_des,
                                                 types=types
                                                 )
            media_vid = list(map(lambda x: InputMediaVideo(open(x, 'rb')), filter(lambda y: y.endswith(vid_ext),
                                                                                  restaurant.media.split(';'))))
            media_ph = list(map(lambda x: InputMediaPhoto(open(x, 'rb')), filter(lambda y: y.endswith(ph_ext),
                                                                                 restaurant.media.split(';'))))
            media = list()
            media.extend(media_vid)
            media.extend(media_ph)
            media[0].caption = html
            media[0].parse_mode = 'HTML'
            applications_to_view.append(media)
        for elem in applications_to_view:
            context.bot.send_media_group(update.message.chat_id, media=elem)


def confirm(update, context):
    user = db_sess.query(User).filter(User.telegram_id == update.message.from_user.id).one()
    if user.moderator:
        try:
            application_id = int(context.args[0])
            application = db_sess.query(Restaurant).filter(Restaurant.id == application_id,
                                                           Restaurant.confirmed == 0).all()
            if not bool(application):
                update.message.reply_text('Заявки с таким id нет')

                return

            application[0].confirmed = 1
            db_sess.commit()
            update.message.reply_text('Заявка подтверждена')

        except (IndexError, ValueError):

            update.message.reply_text('Использование: /confirm <id заведения>')


def reject(update, context):
    user = db_sess.query(User).filter(User.telegram_id == update.message.from_user.id).one()
    if user.moderator:
        try:
            application_id = int(context.args[0])
            application = db_sess.query(Restaurant).filter(Restaurant.id == application_id,
                                                           Restaurant.confirmed == 0).all()
            if not bool(application):
                update.message.reply_text('Заявки с таким id нет')

                return

            db_sess.delete(application[0])
            db_sess.commit()
            update.message.reply_text('Заявка отклонена')

        except (IndexError, ValueError):

            update.message.reply_text('Использование: /reject <id заведения>')


def blacklist(update, context):
    bl = db_sess.query(Blacklist).all()
    for elem in bl:
        context.bot.sendMessage(update.message.chat_id, f"tg_id - {elem.telegram_id}\n"
                                                        f"name - {elem.name}\n"
                                                        f"username - {elem.username}")
    if not bool(bl):
        update.message.reply_text('Черный список пуст')


def unban(update, context):
    user = db_sess.query(User).filter(User.telegram_id == update.message.from_user.id).one()
    if user.moderator:
        try:
            user_id = int(context.args[0])
            user1 = db_sess.query(Blacklist).filter(Blacklist.telegram_id == user_id).all()
            if not bool(user1):
                update.message.reply_text('В черном списке нет пользователя с таким Telegram id')

                return

            db_sess.delete(user1[0])
            db_sess.commit()
            update.message.reply_text('Юзер разблокирован')

        except (IndexError, ValueError):

            update.message.reply_text('Использование: /unban <telegram_id юзера>')


def translate(update, context):
    try:
        language = context.args[0]
        text = ' '.join(context.args[1:])
        body = {
            "targetLanguageCode": language,
            "texts": text,
            "folderId": folder_id,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Api-Key {0}".format(API_KEY)
        }
        response = requests.post(translate_api_server,
                                 json=body,
                                 headers=headers
                                 ).json()
        try:
            if response['code']:
                update.message.reply_text('Использование: /translate <язык, на который нужно перевести> <сообщение>')
        except KeyError:
            update.message.reply_text(response['translations'][0]['text'])

    except (IndexError, ValueError):

        update.message.reply_text('Использование: /translate <язык,'
                                  ' на который нужно перевести в формате двух букв> <сообщение>')


def link(update, context):
    user = db_sess.query(User).filter(User.telegram_id == update.message.from_user.id).one()
    if user.moderator:
        try:
            user_id = context.args[0]
            rest_id = context.args[1]
            new_user = db_sess.query(User).filter(User.id == user_id).all()

            if not bool(new_user):
                update.message.reply_text('Юзера с таким id нет')

                return
            new_rest = db_sess.query(Restaurant).filter(Restaurant.id == rest_id).all()
            if not bool(new_rest):
                update.message.reply_text('Ресторана с таким id нет')

                return
            new_rest[0].owner = new_user[0].id
            db_sess.commit()
            update.message.reply_text('Компания закреплена за пользователем')
        except (IndexError, ValueError):
            update.message.reply_text('Использование:\n'
                                      '/link <user_id> <restaurant_id>')


def bot_help(update, context):
    context.bot.sendMessage(update.message.chat_id, text="""Вы можете перевести сообщение командой /translate\n"
                                                         Использование: /translate <язык,
                                  на который нужно перевести в формате двух букв> <сообщение>""")
