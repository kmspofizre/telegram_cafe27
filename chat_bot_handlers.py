import json
from telegram import InputMediaPhoto, InputMediaVideo
from data import db_session
from data.users import User
from data.restaurants import Restaurant
from data.restaurant_types import RestaurantTypes
from templates import card_for_moderator
from telegram import ChatPermissions
from data.blacklist import Blacklist
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


def text_handler(update, context):
    with open('json/messages.json') as json_messages:
        json_messages_data = json.load(json_messages)
    mes = update.message
    text = update.message.text
    bad_words = json_messages_data['ban_words']
    try:
        if context.chat_data[mes.from_user.id]['number'] == 5:
            context.chat_data[mes.from_user.id]['number'] = 0
        context.chat_data[mes.from_user.id]['mess'][context.chat_data[mes.from_user.id]['number']] = text
        context.chat_data[mes.from_user.id]['number'] += 1
        m = context.chat_data[mes.from_user.id]['mess']
        if m[0] == m[1] == m[2] == m[3] == m[4] and '' not in m:
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
            'mess': ['', '', '', '', ''],
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
