from telegram.ext import CommandHandler, MessageHandler, Filters, ShippingQueryHandler, PreCheckoutQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo
import json
from data import db_session
from data.users import User
from data.restaurant_types import RestaurantTypes
from data.blacklist import Blacklist
from data.restaurants import Restaurant
from data.scores import Scores
import datetime
from keyboards import main_menu_keyboard
from templates import card_html_with_score, card_html_without_score, card_short_html

db_session.global_init("db/cafe27.db")
db_sess = db_session.create_session()

vid_ext = tuple('.mp4')
ph_ext = tuple(['.jpg', '.jpeg', '.png'])


def get_message_from_json(language, context, message_type):
    with open('json/messages.json') as json_messages:
        json_messages_data = json.load(json_messages)
    try:
        user_language = context.chat_data['language']
        if user_language == 'ru':
            return json_messages_data['messages']['ru'][message_type]
        elif user_language == 'en':
            return json_messages_data['messages']['en'][message_type]
    except KeyError:
        if language == 'ru':
            return json_messages_data['messages']['ru'][message_type]
        else:
            return json_messages_data['messages']['en'][message_type]


def choose_restaurant_type(callback_data, user_tgid):
    user = db_sess.query(User).filter(User.telegram_id == user_tgid).all()[0]
    user_fav = list(map(int, user.favourite.split(', ')))
    restaurant_type_id = int(callback_data[1])
    chosen_restaurants = db_sess.query(Restaurant).filter(Restaurant.type == restaurant_type_id,
                                                          Restaurant.confirmed).all()
    to_send = list()
    for restaurant in chosen_restaurants:
        d = dict()
        if restaurant.number_of_scores == 0:
            if len(restaurant.description) > 100:
                description = restaurant.description[:100].split()
                description = ' '.join(description[:len(description) - 1])
            else:
                description = restaurant.description
            html_long = card_html_without_score.substitute(name=restaurant.name,
                                                           description=description,
                                                           working_hours=restaurant.working_hours,
                                                           working_days=restaurant.working_days,
                                                           average_price=restaurant.average_price)
        else:
            if len(restaurant.description) > 100:
                description = restaurant.description[:100].split()
                description = ' '.join(description[:len(description) - 1])
            else:
                description = restaurant.description
            html_long = card_html_with_score.substitute(name=restaurant.name,
                                                        description=description,
                                                        working_hours=restaurant.working_hours,
                                                        working_days=restaurant.working_days,
                                                        average_price=restaurant.average_price,
                                                        average_score=restaurant.score,
                                                        number_of_scores=restaurant.number_of_scores)
        html_short = card_short_html.substitute(name=restaurant.name,
                                                description=description,
                                                average_price=restaurant.average_price)
        media_vid = list(map(lambda x: InputMediaVideo(open(x, 'rb')), filter(lambda y: y.endswith(vid_ext),
                                                                              restaurant.media.split(';'))))
        media_ph = list(map(lambda x: InputMediaPhoto(open(x, 'rb')), filter(lambda y: y.endswith(ph_ext),
                                                                             restaurant.media.split(';'))))
        media = list()
        media.extend(media_vid)
        media.extend(media_ph)
        media[0].caption = html_short
        media[0].parse_mode = 'HTML'
        d['id'] = restaurant.id
        d['html_long'] = html_long
        d['html_short'] = html_short
        d['media'] = media
        d['favourite'] = restaurant.id in user_fav
        d['owner_link'] = db_sess.query(User).filter(User.id == restaurant.owner).all()[0].user_link
        try:
            d['score'] = db_sess.query(Scores).filter(Scores.user == user.id,
                                                      Scores.restaurant == restaurant.id).all()[0].score
        except Exception:
            d['score'] = None
        to_send.append(d)

    return to_send


def start(update, context):
    in_blacklist = db_sess.query(Blacklist).filter(Blacklist.telegram_id == update.message.from_user.id).all()
    if not in_blacklist:
        user = db_sess.query(User).filter(User.telegram_id == update.message.from_user.id).all()
        markup = main_menu_keyboard
        if not user:
            new_user = User(
                telegram_id=update.message.from_user.id,
                username=update.message.from_user.username,
                date_of_appearance=datetime.date.today(),
                name=update.message.from_user.full_name,
                user_link=update.message.from_user.link
            )
            db_sess.add(new_user)
            db_sess.commit()
        else:
            if user[0].is_vip:
                markup = main_menu_keyboard
        update.message.reply_text(get_message_from_json(update.message.from_user.language_code, context, "greeting"),
                                  reply_markup=markup)


def text_handler(update, context):
    in_blacklist = db_sess.query(Blacklist).filter(Blacklist.telegram_id == update.message.from_user.id).all()
    if not in_blacklist:
        if update.message.text == 'Каталог 📖':
            restaurant_types = list(map(lambda x: InlineKeyboardButton(text=x.type_name, callback_data=f"rt_{x.id}"),
                                        db_sess.query(RestaurantTypes).all()))
            buttons = InlineKeyboardMarkup(
                [restaurant_types[2 * i:2 * (i + 1)] for i in range(len(restaurant_types) // 2 + 1)])
            update.message.reply_text('Заведения по категориям:', reply_markup=buttons)


def callback_hand(update, context):
    in_blacklist = db_sess.query(Blacklist).filter(Blacklist.telegram_id == update.callback_query.from_user.id).all()
    if not in_blacklist:
        data = update.callback_query.data.split('_')
        if data[0] == 'rt':
            rests = choose_restaurant_type(data, update.callback_query.from_user.id)
            for elem in rests:
                print(elem)
                if elem['favourite']:
                    fav_button = InlineKeyboardButton(text='Удалить из избранного 💔',
                                                      callback_data=
                                                      f"delfav_{update.callback_query.from_user.id}_{elem['id']}")
                else:
                    fav_button = InlineKeyboardButton(text='Добавить в избранное ❤️',
                                                      callback_data=
                                                      f"addfav_{update.callback_query.from_user.id}_{elem['id']}")
                tlg_button = InlineKeyboardButton(text='Связаться ☎️', url=elem['owner_link'])
                describe = InlineKeyboardButton(text='Подробнее', callback_data=f"des_{elem['id']}")
                inl_keyboard = InlineKeyboardMarkup([[fav_button, tlg_button],
                                                     [describe]])
                context.bot.send_media_group(update.callback_query.from_user.id,
                                             media=elem['media'], )
                context.bot.sendMessage(update.callback_query.from_user.id, text='Действия:', reply_markup=inl_keyboard)



