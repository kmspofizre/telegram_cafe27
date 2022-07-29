import telegram.error
from telegram.ext import CommandHandler, MessageHandler, Filters, ShippingQueryHandler, PreCheckoutQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo
import json
from data import db_session
from data.users import User
from data.restaurant_types import RestaurantTypes
from data.blacklist import Blacklist
from data.restaurants import Restaurant
from data.scores import Scores
from data.payments import Payment
import datetime
from keyboards import main_menu_keyboard, card_inline_keyboard_del_ru, \
    card_inline_keyboard_del_en, \
    main_menu_keyboard_en, geoposition_keyboard, \
    geoposition_keyboard_en, rate_keyboard, personal_account_vip_ru, \
    personal_account_default_ru, personal_account_vip_en, \
    personal_account_default_en, info_keyboard_ru, info_keyboard_en, single_vip_keyboard_ru, single_vip_keyboard_en

from templates import card_html_with_score_ru, card_html_without_score_ru, \
    card_short_html, card_html_with_score_en, card_html_without_score_en, card_short_html_en
from distance import lonlat_distance
from payment import vip_price

db_session.global_init("db/cafe27.db")
db_sess = db_session.create_session()

vid_ext = tuple('.mp4')
ph_ext = tuple(['.jpg', '.jpeg', '.png'])

P_TOKEN = "381764678:TEST:40489"


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


def choose_restaurant_type(callback_data, user_tgid, user_tlg, context):
    user = db_sess.query(User).filter(User.telegram_id == user_tgid).one()
    user_fav = list(map(int, user.favourite.split(', ')))
    restaurant_type_id = int(callback_data[1])
    page = context.chat_data['page']
    chosen_restaurants = db_sess.query(Restaurant).filter(Restaurant.confirmed).all()
    chosen_restaurants = list(filter(lambda x: restaurant_type_id in map(int, x.type.split(', ')), chosen_restaurants))
    all_restaurants = chosen_restaurants
    chosen_restaurants = chosen_restaurants[5 * (page - 1):5 * page]
    to_send = list()
    for restaurant in chosen_restaurants:
        d = dict()

        if len(restaurant.description) > 100:
            description = restaurant.description[:100].split()
            description = ' '.join(description[:len(description) - 1])
            description_en = restaurant.description_en[:100].split()
            description_en = ' '.join(description_en[:len(description_en) - 1])
        else:
            description = restaurant.description
            description_en = restaurant.description_en
        try:
            user_language = context.chat_data['language']
            if user_language == 'ru':
                html_short = card_short_html.substitute(name=restaurant.name,
                                                        description=description,
                                                        average_price=restaurant.average_price)
            else:
                html_short = card_short_html_en.substitute(name=restaurant.name_en,
                                                           description=description_en,
                                                           average_price=restaurant.average_price)
        except KeyError:
            if user_tlg.language_code == 'ru':
                html_short = card_short_html.substitute(name=restaurant.name,
                                                        description=description,
                                                        average_price=restaurant.average_price)
            else:
                html_short = card_short_html_en.substitute(name=restaurant.name_en,
                                                           description=description_en,
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
        d['html_short'] = html_short
        d['media'] = media
        d['favourite'] = restaurant.id in user_fav
        d['owner_link'] = db_sess.query(User).filter(User.id == restaurant.owner).one().user_link
        d['vip_owner'] = restaurant.vip_owner
        to_send.append(d)

    return to_send, all_restaurants


def add_to_favourite(user_tg, restaurant, message, chat, context, media_message, json_data, dm):
    user = db_sess.query(User).filter(User.telegram_id == user_tg.id).one()
    favourite = user.favourite.split(', ')
    favourite.append(str(restaurant))
    user.favourite = ', '.join(favourite)
    language_code = user_tg.language_code
    try:
        user_language = context.chat_data['language']
        if user_language == 'ru':
            fav_button, tlg_button, describe, rate = card_inline_keyboard_del_ru('del', dm)
            text = json_data['messages']['ru']['actions']
        else:
            fav_button, tlg_button, describe, rate = card_inline_keyboard_del_en('del', dm)
            text = json_data['messages']['en']['actions']
    except KeyError:
        if language_code == 'ru':
            fav_button, tlg_button, describe, rate = card_inline_keyboard_del_ru('del', dm)
            text = json_data['messages']['ru']['actions']
        else:
            fav_button, tlg_button, describe, rate = card_inline_keyboard_del_en('del', dm)
            text = json_data['messages']['en']['actions']
    fav_button.callback_data = f"delfav_{restaurant}_{media_message}_{dm}"
    chosen_restaurant = db_sess.query(Restaurant).filter(Restaurant.id == restaurant).one()
    try:
        chosen_restaurant.in_favourite += 1
    except TypeError:
        chosen_restaurant.in_favourite = 1
    restaurant_owner = db_sess.query(User).filter(User.id == chosen_restaurant.owner).one().user_link
    tlg_button.url = restaurant_owner
    describe.callback_data = f"des_{restaurant}_{media_message}_{dm}"
    rate.callback_data = f"rate_{restaurant}_{media_message}_{dm}"
    inl_keyboard = InlineKeyboardMarkup([[describe, tlg_button],
                                         [fav_button],
                                         [rate]])
    context.bot.editMessageText(chat_id=chat, message_id=message, text=text, reply_markup=inl_keyboard)
    db_sess.commit()


def del_from_favourite(user_tg, restaurant, message, chat, context, media_message, json_data, dm):
    user = db_sess.query(User).filter(User.telegram_id == user_tg.id).one()
    favourite = user.favourite.split(', ')
    favourite.remove(str(restaurant))
    user.favourite = ', '.join(favourite)
    language_code = user_tg.language_code
    try:
        user_language = context.chat_data['language']
        if user_language == 'ru':
            fav_button, tlg_button, describe, rate = card_inline_keyboard_del_ru('add', dm)
            text = json_data['messages']['ru']['actions']
        else:
            fav_button, tlg_button, describe, rate = card_inline_keyboard_del_en('add', dm)
            text = json_data['messages']['en']['actions']
    except KeyError:
        if language_code == 'ru':
            fav_button, tlg_button, describe, rate = card_inline_keyboard_del_ru('add', dm)
            text = json_data['messages']['ru']['actions']
        else:
            fav_button, tlg_button, describe, rate = card_inline_keyboard_del_en('add', dm)
            text = json_data['messages']['en']['actions']
    fav_button.callback_data = f"addfav_{restaurant}_{media_message}_{dm}"
    chosen_restaurant = db_sess.query(Restaurant).filter(Restaurant.id == restaurant).one()
    try:
        chosen_restaurant.in_favourite -= 1
    except TypeError:
        chosen_restaurant.in_favourite = 0
    restaurant_owner = db_sess.query(User).filter(User.id == chosen_restaurant.owner).one().user_link
    tlg_button.url = restaurant_owner
    describe.callback_data = f"des_{restaurant}_{media_message}_{dm}"
    rate.callback_data = f"rate_{restaurant}_{media_message}_{dm}"
    inl_keyboard = InlineKeyboardMarkup([[describe, tlg_button],
                                         [fav_button],
                                         [rate]])
    context.bot.editMessageText(chat_id=chat, message_id=message, text=text, reply_markup=inl_keyboard)
    db_sess.commit()


def show_full_description(restaurant, message, chat, context, language, message_with_buttons, json_data, user_tgid,
                          redact=False):
    restaurant = db_sess.query(Restaurant).filter(Restaurant.id == int(restaurant)).one()
    if restaurant.number_of_scores == 0 or restaurant.number_of_scores == None:
        description = restaurant.description
        description_en = restaurant.description_en
        try:
            user_language = context.chat_data['language']
            if user_language == 'ru':
                html_long = card_html_without_score_ru.substitute(name=restaurant.name,
                                                                  description=description,
                                                                  working_hours=restaurant.working_hours,
                                                                  working_days=restaurant.working_days,
                                                                  average_price=restaurant.average_price)
            else:
                html_long = card_html_without_score_en.substitute(name=restaurant.name_en,
                                                                  description=description_en,
                                                                  working_hours=restaurant.working_hours,
                                                                  working_days=restaurant.working_days_en,
                                                                  average_price=restaurant.average_price)
        except KeyError:
            if language == 'ru':
                html_long = card_html_without_score_ru.substitute(name=restaurant.name,
                                                                  description=description,
                                                                  working_hours=restaurant.working_hours,
                                                                  working_days=restaurant.working_days,
                                                                  average_price=restaurant.average_price)
            else:
                html_long = card_html_without_score_en.substitute(name=restaurant.name_en,
                                                                  description=description_en,
                                                                  working_hours=restaurant.working_hours,
                                                                  working_days=restaurant.working_days_en,
                                                                  average_price=restaurant.average_price)
    else:
        description = restaurant.description
        description_en = restaurant.description_en
        try:
            user_language = context.chat_data['language']
            if user_language == 'ru':
                html_long = card_html_with_score_ru.substitute(name=restaurant.name,
                                                               description=description,
                                                               working_hours=restaurant.working_hours,
                                                               working_days=restaurant.working_days,
                                                               average_price=restaurant.average_price,
                                                               average_score=restaurant.score,
                                                               number_of_scores=restaurant.number_of_scores)
            else:
                html_long = card_html_with_score_en.substitute(name=restaurant.name_en,
                                                               description=description_en,
                                                               working_hours=restaurant.working_hours,
                                                               working_days=restaurant.working_days_en,
                                                               average_price=restaurant.average_price,
                                                               average_score=restaurant.score,
                                                               number_of_scores=restaurant.number_of_scores)
        except KeyError:
            if language == 'ru':
                html_long = card_html_with_score_ru.substitute(name=restaurant.name,
                                                               description=description,
                                                               working_hours=restaurant.working_hours,
                                                               working_days=restaurant.working_days,
                                                               average_price=restaurant.average_price,
                                                               average_score=restaurant.score,
                                                               number_of_scores=restaurant.number_of_scores)
            else:
                html_long = card_html_with_score_en.substitute(name=restaurant.name_en,
                                                               description=description_en,
                                                               working_hours=restaurant.working_hours,
                                                               working_days=restaurant.working_days_en,
                                                               average_price=restaurant.average_price,
                                                               average_score=restaurant.score,
                                                               number_of_scores=restaurant.number_of_scores)
    media_vid = list(map(lambda x: InputMediaVideo(open(x, 'rb')), filter(lambda y: y.endswith(vid_ext),
                                                                          restaurant.media.split(';'))))
    media_ph = list(map(lambda x: InputMediaPhoto(open(x, 'rb')), filter(lambda y: y.endswith(ph_ext),
                                                                         restaurant.media.split(';'))))
    media = list()
    media.extend(media_vid)
    media.extend(media_ph)
    media[0].caption = html_long
    media[0].parse_mode = 'HTML'
    user = db_sess.query(User).filter(User.telegram_id == user_tgid).one()
    user_fav = list(map(int, user.favourite.split(', ')))
    fav = restaurant.id in user_fav
    if fav:
        fav = 'del'
    else:
        fav = 'add'
    try:
        user_language = context.chat_data['language']
        if user_language == 'ru':
            fav_button, tlg_button, describe, rate = card_inline_keyboard_del_ru(fav, 'min')
            text = json_data['messages']['ru']['actions']
            text1 = json_data['messages']['ru']['distance']
            keyboard = geoposition_keyboard
        else:
            fav_button, tlg_button, describe, rate = card_inline_keyboard_del_en(fav, 'min')
            text = json_data['messages']['en']['actions']
            text1 = json_data['messages']['en']['distance']
            keyboard = geoposition_keyboard_en
    except KeyError:
        if language == 'ru':
            fav_button, tlg_button, describe, rate = card_inline_keyboard_del_ru(fav, 'min')
            text = json_data['messages']['ru']['actions']
            text1 = json_data['messages']['ru']['distance']
            keyboard = geoposition_keyboard
        else:
            fav_button, tlg_button, describe, rate = card_inline_keyboard_del_en(fav, 'min')
            text = json_data['messages']['en']['actions']
            text1 = json_data['messages']['en']['distance']
            keyboard = geoposition_keyboard_en
    restaurant_owner = db_sess.query(User).filter(User.id == restaurant.owner).one().user_link
    tlg_button.url = restaurant_owner
    rate.callback_data = f"rate_{restaurant.id}_{message}_min"
    if fav == 'add':
        fav_button.callback_data = f"addfav_{restaurant.id}_{message}_min"
    else:
        fav_button.callback_data = f"delfav_{restaurant.id}_{message}_min"

    describe.callback_data = f"des_{restaurant.id}_{message}_min"
    inl_keyboard = InlineKeyboardMarkup([[describe, tlg_button],
                                         [fav_button],
                                         [rate]])
    try:
        restaurant.requested += 1
    except TypeError:
        restaurant.requested = 1
    context.chat_data['place_location'] = restaurant.coordinates
    context.bot.editMessageMedia(chat_id=chat, message_id=message, media=media[0])
    context.bot.editMessageText(chat_id=chat, message_id=message_with_buttons.message_id,
                                text=text, reply_markup=inl_keyboard)
    if not redact:
        context.bot.sendMessage(chat_id=chat, text=text1, reply_markup=keyboard)


def show_short_description(user_tg, context, rest, message, text_message_id, json_data, chat):
    user = db_sess.query(User).filter(User.telegram_id == user_tg.id).one()
    user_fav = list(map(int, user.favourite.split(', ')))
    fav = int(rest) in user_fav
    print(user_fav, int(rest), fav)
    if fav:
        fav = 'del'
    else:
        fav = 'add'
    restaurant = db_sess.query(Restaurant).filter(Restaurant.id == int(rest)).one()
    if len(restaurant.description) > 100:
        description = restaurant.description[:100].split()
        description = ' '.join(description[:len(description) - 1])
        description_en = restaurant.description_en[:100].split()
        description_en = ' '.join(description_en[:len(description_en) - 1])
    else:
        description = restaurant.description
        description_en = restaurant.description_en
    try:
        user_language = context.chat_data['language']
        if user_language == 'ru':
            fav_button, tlg_button, describe, rate = card_inline_keyboard_del_ru(fav, 'des')
            text = json_data['messages']['ru']['actions']
            text1 = json_data['messages']['ru']['back']
            keyboard = main_menu_keyboard
            html_short = card_short_html.substitute(name=restaurant.name,
                                                    description=description,
                                                    average_price=restaurant.average_price)
        else:
            fav_button, tlg_button, describe, rate = card_inline_keyboard_del_en(fav, 'des')
            text = json_data['messages']['en']['actions']
            text1 = json_data['messages']['en']['back']
            keyboard = main_menu_keyboard_en
            html_short = card_short_html.substitute(name=restaurant.name_en,
                                                    description=description_en,
                                                    average_price=restaurant.average_price)
    except KeyError:
        if user_tg.language_code == 'ru':
            fav_button, tlg_button, describe, rate = card_inline_keyboard_del_ru(fav, 'des')
            text = json_data['messages']['ru']['actions']
            text1 = json_data['messages']['ru']['back']
            keyboard = main_menu_keyboard
            html_short = card_short_html.substitute(name=restaurant.name,
                                                    description=description,
                                                    average_price=restaurant.average_price)
        else:
            fav_button, tlg_button, describe, rate = card_inline_keyboard_del_en(fav, 'des')
            text = json_data['messages']['en']['actions']
            text1 = json_data['messages']['en']['back']
            keyboard = main_menu_keyboard_en
            html_short = card_short_html.substitute(name=restaurant.name_en,
                                                    description=description_en,
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
    tlg_button.url = user.user_link
    rate.callback_data = f"rate_{restaurant.id}_{message}_des"
    if fav == 'add':
        fav_button.callback_data = f"addfav_{restaurant.id}_{message}_des"
    else:
        fav_button.callback_data = f"delfav_{restaurant.id}_{message}_des"

    describe.callback_data = f"des_{restaurant.id}_{message}_des"
    inl_keyboard = InlineKeyboardMarkup([[describe, tlg_button],
                                         [fav_button],
                                         [rate]])
    context.bot.editMessageMedia(chat_id=chat, message_id=message, media=media[0])
    context.bot.editMessageText(chat_id=chat, message_id=text_message_id,
                                text=text, reply_markup=inl_keyboard)
    context.bot.sendMessage(chat_id=chat, text=text1, reply_markup=keyboard)


def start(update, context):
    in_blacklist = db_sess.query(Blacklist).filter(Blacklist.telegram_id == update.message.from_user.id).all()
    if not in_blacklist:
        user = db_sess.query(User).filter(User.telegram_id == update.message.from_user.id).all()
        try:
            user_language = context.chat_data['language']
            if user_language == 'ru':
                markup = main_menu_keyboard
            else:
                markup = main_menu_keyboard_en
        except KeyError:
            if update.message.from_user.language_code == 'ru':
                markup = main_menu_keyboard
            else:
                markup = main_menu_keyboard_en

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
        update.message.reply_text(get_message_from_json(update.message.from_user.language_code, context, "greeting"),
                                  reply_markup=markup)


def show_favourite(user_tg, context):
    user = db_sess.query(User).filter(User.telegram_id == user_tg.id).one()
    language = user_tg.language_code
    favourite = list(map(int, user.favourite.split(', ')))
    chosen_restaurants = db_sess.query(Restaurant).filter(Restaurant.id.in_(favourite)).all()
    to_send = list()
    for restaurant in chosen_restaurants:
        d = dict()

        if len(restaurant.description) > 100:
            description = restaurant.description[:100].split()
            description = ' '.join(description[:len(description) - 1])
            description_en = restaurant.description_en[:100].split()
            description_en = ' '.join(description_en[:len(description_en) - 1])
        else:
            description = restaurant.description
            description_en = restaurant.description_en
        try:
            user_language = context.chat_data['language']
            if user_language == 'ru':
                html_short = card_short_html.substitute(name=restaurant.name,
                                                        description=description,
                                                        average_price=restaurant.average_price)
            else:
                html_short = card_short_html_en.substitute(name=restaurant.name_en,
                                                           description=description_en,
                                                           average_price=restaurant.average_price)
        except KeyError:
            if language == 'ru':
                html_short = card_short_html.substitute(name=restaurant.name,
                                                        description=description,
                                                        average_price=restaurant.average_price)
            else:
                html_short = card_short_html_en.substitute(name=restaurant.name_en,
                                                           description=description_en,
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
        d['html_short'] = html_short
        d['media'] = media
        d['favourite'] = True
        d['owner_link'] = db_sess.query(User).filter(User.id == restaurant.owner).one().user_link
        d['vip_owner'] = restaurant.vip_owner
        to_send.append(d)

    return to_send


def text_handler(update, context):
    with open('json/messages.json') as json_messages:
        json_messages_data = json.load(json_messages)
    in_blacklist = db_sess.query(Blacklist).filter(Blacklist.telegram_id == update.message.from_user.id).all()
    if not in_blacklist:
        user = db_sess.query(User).filter(User.telegram_id == update.message.from_user.id).one()
        vip_user = user.is_vip
        if update.message.text in ('Каталог 📖', 'Catalog 📖'):
            try:
                user_language = context.chat_data['language']
                if user_language == 'ru':
                    if vip_user:
                        restaurant_types = list(
                            map(lambda x: InlineKeyboardButton(text=x.type_name, callback_data=f"rt_{x.id}"),
                                db_sess.query(RestaurantTypes).all()))
                    else:
                        restaurant_types = list(
                            map(lambda x: InlineKeyboardButton(text=x.type_name, callback_data=f"rt_{x.id}"),
                                db_sess.query(RestaurantTypes).filter(RestaurantTypes.only_vip == 0).all()))
                    text = json_messages_data['messages']['ru']['places']
                else:
                    if vip_user:
                        restaurant_types = list(
                            map(lambda x: InlineKeyboardButton(text=x.type_name_en, callback_data=f"rt_{x.id}"),
                                db_sess.query(RestaurantTypes).all()))
                    else:
                        restaurant_types = list(
                            map(lambda x: InlineKeyboardButton(text=x.type_name_en, callback_data=f"rt_{x.id}"),
                                db_sess.query(RestaurantTypes).filter(RestaurantTypes.only_vip == 0).all()))
                    text = json_messages_data['messages']['en']['places']
            except KeyError:
                if update.message.from_user.language_code == 'ru':
                    if vip_user:
                        restaurant_types = list(
                            map(lambda x: InlineKeyboardButton(text=x.type_name, callback_data=f"rt_{x.id}"),
                                db_sess.query(RestaurantTypes).all()))
                    else:
                        restaurant_types = list(
                            map(lambda x: InlineKeyboardButton(text=x.type_name, callback_data=f"rt_{x.id}"),
                                db_sess.query(RestaurantTypes).filter(RestaurantTypes.only_vip == 0).all()))
                    text = json_messages_data['messages']['ru']['places']
                else:
                    if vip_user:
                        restaurant_types = list(
                            map(lambda x: InlineKeyboardButton(text=x.type_name_en, callback_data=f"rt_{x.id}"),
                                db_sess.query(RestaurantTypes).all()))
                    else:
                        restaurant_types = list(
                            map(lambda x: InlineKeyboardButton(text=x.type_name_en, callback_data=f"rt_{x.id}"),
                                db_sess.query(RestaurantTypes).filter(RestaurantTypes.only_vip == 0).all()))
                    text = json_messages_data['messages']['en']['places']

            buttons = InlineKeyboardMarkup(
                [restaurant_types[2 * i:2 * (i + 1)] for i in range(len(restaurant_types) // 2 + 1)])
            update.message.reply_text(text, reply_markup=buttons)

        elif update.message.text == '🔙':
            try:
                user_language = context.chat_data['language']
                if user_language == 'ru':
                    update.message.reply_text(json_messages_data['messages']['ru']['back'],
                                              reply_markup=main_menu_keyboard)
                elif user_language == 'en':
                    update.message.reply_text(json_messages_data['messages']['en']['back'],
                                              reply_markup=main_menu_keyboard_en)
            except KeyError:
                if update.message.from_user.language_code == 'ru':
                    update.message.reply_text(json_messages_data['messages']['ru']['back'],
                                              reply_markup=main_menu_keyboard)
                else:
                    update.message.reply_text(json_messages_data['messages']['en']['back'],
                                              reply_markup=main_menu_keyboard_en)
        elif update.message.text in ('Избранное ❤️', 'Favourite ❤️'):
            to_show = show_favourite(update.message.from_user, context)
            for elem in to_show:
                try:
                    user_language = context.chat_data['language']
                    if user_language == 'ru':
                        fav_button, tlg_button, describe, rate = card_inline_keyboard_del_ru('del', 'des')
                        text = json_messages_data['messages']['ru']['actions']
                    else:
                        fav_button, tlg_button, describe, rate = card_inline_keyboard_del_en('del', 'des')
                        text = json_messages_data['messages']['en']['actions']
                except KeyError:
                    if update.message.from_user.language_code == 'ru':
                        fav_button, tlg_button, describe, rate = card_inline_keyboard_del_ru('del', 'des')
                        text = json_messages_data['messages']['ru']['actions']
                    else:
                        fav_button, tlg_button, describe, rate = card_inline_keyboard_del_en('del', 'des')
                        text = json_messages_data['messages']['en']['actions']
                fav_button_call = f"delfav_{elem['id']}"
                media_message = context.bot.send_media_group(update.message.from_user.id,
                                                             media=elem['media'])
                tlg_button.url = elem['owner_link']
                rate.callback_data = f"rate_{elem['id']}_{media_message[0].message_id}_des"
                fav_button.callback_data = fav_button_call + f'_{media_message[0].message_id}_des'
                describe.callback_data = f"des_{elem['id']}_{media_message[0].message_id}_des"
                inl_keyboard = InlineKeyboardMarkup([[describe, tlg_button],
                                                     [fav_button],
                                                     [rate]])
                context.bot.sendMessage(update.message.from_user.id, text=text, reply_markup=inl_keyboard)
            if not bool(to_show):
                try:
                    user_language = context.chat_data['language']
                    if user_language == 'ru':
                        text = json_messages_data['messages']['ru']['favourite_empty']
                    else:
                        text = json_messages_data['messages']['en']['favourite_empty']
                except KeyError:
                    if update.message.from_user.language_code == 'ru':
                        text = json_messages_data['messages']['ru']['favourite_empty']
                    else:
                        text = json_messages_data['messages']['en']['favourite_empty']
                update.message.reply_text(text)
        elif update.message.text in ('Личный кабинет 👤', 'Personal account 👤'):
            is_vip = db_sess.query(User).filter(User.telegram_id == update.message.from_user.id).one().is_vip
            try:
                user_language = context.chat_data['language']
                if user_language == 'ru':
                    text = json_messages_data['messages']['ru']['personal_account']
                    if is_vip:
                        markup = personal_account_vip_ru
                    else:
                        markup = personal_account_default_ru
                else:
                    text = json_messages_data['messages']['en']['personal_account']
                    if is_vip:
                        markup = personal_account_vip_en
                    else:
                        markup = personal_account_default_en
            except KeyError:
                if update.message.from_user.language_code == 'ru':
                    text = json_messages_data['messages']['ru']['personal_account']
                    if is_vip:
                        markup = personal_account_vip_ru
                    else:
                        markup = personal_account_default_ru
                else:
                    text = json_messages_data['messages']['en']['personal_account']
                    if is_vip:
                        markup = personal_account_vip_en
                    else:
                        markup = personal_account_default_en
            update.message.reply_text(text, reply_markup=markup)
        elif update.message.text == 'ENG 🇬🇧':
            context.chat_data['language'] = 'en'
            is_vip = db_sess.query(User).filter(User.telegram_id == update.message.from_user.id).one().is_vip
            if is_vip:
                update.message.reply_text(
                    get_message_from_json(update.message.from_user.language_code, context, "greeting"),
                    reply_markup=personal_account_vip_en)
            else:
                update.message.reply_text(
                    get_message_from_json(update.message.from_user.language_code, context, "greeting"),
                    reply_markup=personal_account_default_en)
        elif update.message.text == 'RUS 🇷🇺':
            context.chat_data['language'] = 'ru'
            is_vip = db_sess.query(User).filter(User.telegram_id == update.message.from_user.id).one().is_vip
            if is_vip:
                update.message.reply_text(
                    get_message_from_json(update.message.from_user.language_code, context, "greeting"),
                    reply_markup=personal_account_vip_ru)
            else:
                update.message.reply_text(
                    get_message_from_json(update.message.from_user.language_code, context, "greeting"),
                    reply_markup=personal_account_default_ru)
        elif update.message.text in ('Инфо ℹ️', 'Info ℹ️'):
            try:
                user_language = context.chat_data['language']
                if user_language == 'ru':
                    text = json_messages_data['messages']['ru']['info']
                    keyboard = info_keyboard_ru
                else:
                    text = json_messages_data['messages']['en']['info']
                    keyboard = info_keyboard_en
            except KeyError:
                if update.message.from_user.language_code == 'ru':
                    text = json_messages_data['messages']['ru']['info']
                    keyboard = info_keyboard_ru
                else:
                    text = json_messages_data['messages']['en']['info']
                    keyboard = info_keyboard_en
            update.message.reply_text(text, reply_markup=keyboard)
        elif update.message.text in ('Become VIP 💵', 'Стать VIP 💵'):
            try:
                user_language = context.chat_data['language']
                if user_language == 'ru':
                    text = json_messages_data['messages']['ru']['VIP_advantage']
                    keyboard = single_vip_keyboard_ru
                else:
                    text = json_messages_data['messages']['en']['VIP_advantage']
                    keyboard = single_vip_keyboard_en
            except KeyError:
                if update.message.from_user.language_code == 'ru':
                    text = json_messages_data['messages']['ru']['VIP_advantage']
                    keyboard = single_vip_keyboard_ru
                else:
                    text = json_messages_data['messages']['en']['VIP_advantage']
                    keyboard = single_vip_keyboard_en
            update.message.reply_text(text, reply_markup=keyboard)
        elif update.message.text == 'VIP 👑':
            try:
                user_language = context.chat_data['language']
                if user_language == 'ru':
                    text = json_messages_data['messages']['ru']['VIP_advantage']
                else:
                    text = json_messages_data['messages']['en']['VIP_advantage']
            except KeyError:
                if update.message.from_user.language_code == 'ru':
                    text = json_messages_data['messages']['ru']['VIP_advantage']
                else:
                    text = json_messages_data['messages']['en']['VIP_advantage']
            update.message.reply_text(text)


def location_hand(update, context):
    with open('json/messages.json') as json_messages:
        json_messages_data = json.load(json_messages)
    user_location = update.message.location
    user_location = user_location['latitude'], user_location['longitude']
    restaurant_location = tuple(map(lambda x: float(x), context.chat_data['place_location'].split(', ')))
    try:
        user_language = context.chat_data['language']
        if user_language == 'ru':
            message = json_messages_data['messages']['ru']['distance_to_object']
        else:
            message = json_messages_data['messages']['en']['distance_to_object']
    except KeyError:
        if update.message.from_user.language_code == 'ru':
            message = json_messages_data['messages']['ru']['distance_to_object']
        else:
            message = json_messages_data['messages']['en']['distance_to_object']
    distance = int(lonlat_distance(user_location, restaurant_location)) / 1000
    update.message.reply_text(text=f"{message}{distance} km")


def rate_restaurant_short(user_tg, context, rest, message, text_message_id, json_data, chat):
    restaurant = db_sess.query(Restaurant).filter(Restaurant.id == int(rest)).one()
    try:
        user_language = context.chat_data['language']
        if user_language == 'ru':
            text = json_data['messages']['ru']['rate']
        else:
            text = json_data['messages']['en']['rate']
    except KeyError:
        if user_tg.language_code == 'ru':
            text = json_data['messages']['ru']['rate']
        else:
            text = json_data['messages']['en']['tate']
    rate_keybrd = rate_keyboard
    rate_keybrd[0][0].callback_data = f"rated_{restaurant.id}_{message}_des_1"
    rate_keybrd[1][0].callback_data = f"rated_{restaurant.id}_{message}_des_2"
    rate_keybrd[2][0].callback_data = f"rated_{restaurant.id}_{message}_des_3"
    rate_keybrd[3][0].callback_data = f"rated_{restaurant.id}_{message}_des_4"
    rate_keybrd[4][0].callback_data = f"rated_{restaurant.id}_{message}_des_5"
    inl_keyboard = InlineKeyboardMarkup(rate_keybrd)
    context.bot.editMessageText(chat_id=chat, message_id=text_message_id,
                                text=text, reply_markup=inl_keyboard)


def rate_restaurant_long(restaurant, message, chat, context, language, message_with_buttons, json_data):
    restaurant = db_sess.query(Restaurant).filter(Restaurant.id == int(restaurant)).one()
    try:
        user_language = context.chat_data['language']
        if user_language == 'ru':
            text = json_data['messages']['ru']['rate']
        else:
            text = json_data['messages']['en']['rate']
    except KeyError:
        if language == 'ru':
            text = json_data['messages']['ru']['rate']
        else:
            text = json_data['messages']['en']['tate']
    rate_keybrd = rate_keyboard
    rate_keybrd[0][0].callback_data = f"rated_{restaurant.id}_{message}_min_1"
    rate_keybrd[1][0].callback_data = f"rated_{restaurant.id}_{message}_min_2"
    rate_keybrd[2][0].callback_data = f"rated_{restaurant.id}_{message}_min_3"
    rate_keybrd[3][0].callback_data = f"rated_{restaurant.id}_{message}_min_4"
    rate_keybrd[4][0].callback_data = f"rated_{restaurant.id}_{message}_min_5"
    inl_keyboard = InlineKeyboardMarkup(rate_keybrd)
    try:
        context.bot.editMessageText(chat_id=chat, message_id=message_with_buttons.message_id,
                                    text=text, reply_markup=inl_keyboard)
    except telegram.error.BadRequest:
        context.bot.editMessageText(chat_id=chat, message_id=message_with_buttons.message_id,
                                    text=text + '.', reply_markup=inl_keyboard)


def change_inline(chat, message_id, user_tg, context, json_data, rest, message):
    user = db_sess.query(User).filter(User.telegram_id == user_tg.id).one()
    user_fav = list(map(int, user.favourite.split(', ')))
    fav = int(rest) in user_fav
    print(user_fav, int(rest), fav)
    if fav:
        fav = 'del'
    else:
        fav = 'add'
    restaurant = db_sess.query(Restaurant).filter(Restaurant.id == int(rest)).one()
    try:
        user_language = context.chat_data['language']
        if user_language == 'ru':
            fav_button, tlg_button, describe, rate = card_inline_keyboard_del_ru(fav, 'des')
            text = json_data['messages']['ru']['actions']

        else:
            fav_button, tlg_button, describe, rate = card_inline_keyboard_del_en(fav, 'des')
            text = json_data['messages']['en']['actions']
    except KeyError:
        if user_tg.language_code == 'ru':
            fav_button, tlg_button, describe, rate = card_inline_keyboard_del_ru(fav, 'des')
            text = json_data['messages']['ru']['actions']
        else:
            fav_button, tlg_button, describe, rate = card_inline_keyboard_del_en(fav, 'des')
            text = json_data['messages']['en']['actions']
    tlg_button.url = user.user_link
    rate.callback_data = f"rate_{restaurant.id}_{message}_des"
    if fav == 'add':
        fav_button.callback_data = f"addfav_{restaurant.id}_{message}_des"
    else:
        fav_button.callback_data = f"delfav_{restaurant.id}_{message}_des"

    describe.callback_data = f"des_{restaurant.id}_{message}_des"
    inl_keyboard = InlineKeyboardMarkup([[describe, tlg_button],
                                         [fav_button],
                                         [rate]])
    context.bot.editMessageText(chat_id=chat, message_id=message_id,
                                text=text, reply_markup=inl_keyboard)


def callback_hand(update, context):
    in_blacklist = db_sess.query(Blacklist).filter(Blacklist.telegram_id == update.callback_query.from_user.id).all()
    if not in_blacklist:
        with open('json/messages.json') as json_messages:
            json_messages_data = json.load(json_messages)
        data = update.callback_query.data.split('_')
        if data[0] == 'rt':
            if len(data) == 2:
                context.chat_data['page'] = 1
            else:
                context.chat_data['page'] = int(data[2])
            rests, all_rests = choose_restaurant_type(data, update.callback_query.from_user.id,
                                                      update.callback_query.from_user, context)
            vip_rests = list(filter(lambda x: x['vip_owner'], rests))
            not_vip_rests = list(filter(lambda x: not x['vip_owner'], rests))
            all_rests_vip = list(filter(lambda x: x.vip_owner, all_rests))
            all_rests_not_vip = list(filter(lambda x: not x.vip_owner, all_rests))
            all_rests = []
            all_rests.extend(all_rests_vip)
            all_rests.extend(all_rests_not_vip)
            rests = []
            rests.extend(vip_rests)
            rests.extend(not_vip_rests)

            for elem in rests:
                print(elem)
                if elem['favourite']:
                    try:
                        user_language = context.chat_data['language']
                        if user_language == 'ru':
                            fav_button, tlg_button, describe, rate = card_inline_keyboard_del_ru('del', 'des')
                            text = json_messages_data['messages']['ru']['actions']
                        else:
                            fav_button, tlg_button, describe, rate = card_inline_keyboard_del_en('del', 'des')
                            text = json_messages_data['messages']['en']['actions']
                    except KeyError:
                        if update.callback_query.from_user.language_code == 'ru':
                            fav_button, tlg_button, describe, rate = card_inline_keyboard_del_ru('del', 'des')
                            text = json_messages_data['messages']['ru']['actions']
                        else:
                            fav_button, tlg_button, describe, rate = card_inline_keyboard_del_en('del', 'des')
                            text = json_messages_data['messages']['en']['actions']
                    fav_button_call = f"delfav_{elem['id']}"

                else:
                    try:
                        user_language = context.chat_data['language']
                        if user_language == 'ru':
                            fav_button, tlg_button, describe, rate = card_inline_keyboard_del_ru('add', 'des')
                            text = json_messages_data['messages']['ru']['actions']
                        else:
                            fav_button, tlg_button, describe, rate = card_inline_keyboard_del_en('add', 'des')
                            text = json_messages_data['messages']['en']['actions']
                    except KeyError:
                        if update.callback_query.from_user.language_code == 'ru':
                            fav_button, tlg_button, describe, rate = card_inline_keyboard_del_ru('add', 'des')
                            text = json_messages_data['messages']['ru']['actions']
                        else:
                            fav_button, tlg_button, describe, rate = card_inline_keyboard_del_en('add', 'des')
                            text = json_messages_data['messages']['en']['actions']
                    fav_button_call = f"addfav_{elem['id']}"
                print(type(elem['media']))
                media_message = context.bot.send_media_group(update.callback_query.from_user.id,
                                                             media=elem['media'])
                tlg_button.url = elem['owner_link']
                rate.callback_data = f"rate_{elem['id']}_{media_message[0].message_id}_des"
                fav_button.callback_data = fav_button_call + f'_{media_message[0].message_id}_des'
                describe.callback_data = f"des_{elem['id']}_{media_message[0].message_id}_des"
                inl_keyboard = InlineKeyboardMarkup([[describe, tlg_button],
                                                     [fav_button],
                                                     [rate]])
                context.bot.sendMessage(update.callback_query.from_user.id, text=text, reply_markup=inl_keyboard)
            print(all_rests[5 * (context.chat_data['page'] - 1):5 * context.chat_data['page']])
            if bool(all_rests[5 * context.chat_data['page']:]):
                try:
                    user_language = context.chat_data['language']
                    if user_language == 'ru':
                        text1 = json_messages_data['messages']['ru']['show_more']
                        show_more_btn = InlineKeyboardMarkup([
                            [InlineKeyboardButton(text=text1,
                                                  callback_data=f"rt_{data[1]}_{context.chat_data['page'] + 1}")]])
                    else:
                        text1 = json_messages_data['messages']['en']['show_more']
                        show_more_btn = InlineKeyboardMarkup([
                            [InlineKeyboardButton(text=text1,
                                                  callback_data=f"rt_{data[1]}_{context.chat_data['page'] + 1}")]])
                except KeyError:
                    if update.callback_query.from_user.language_code == 'ru':
                        text1 = json_messages_data['messages']['ru']['show_more']
                        show_more_btn = InlineKeyboardMarkup([
                            [InlineKeyboardButton(text=text1,
                                                  callback_data=f"rt_{data[1]}_{context.chat_data['page'] + 1}")]])
                    else:
                        text1 = json_messages_data['messages']['en']['show_more']
                        show_more_btn = InlineKeyboardMarkup([
                            [InlineKeyboardButton(text=text1,
                                                  callback_data=f"rt_{data[1]}_{context.chat_data['page'] + 1}")]])
                context.bot.sendMessage(update.callback_query.from_user.id, text=text1, reply_markup=show_more_btn)
        elif data[0] == 'addfav':
            add_to_favourite(update.callback_query.from_user, data[1], update.callback_query.message.message_id,
                             update.callback_query.message.chat_id, context, data[2], json_messages_data, data[3])
            print(db_sess.query(User).filter(User.telegram_id == update.callback_query.from_user.id).one().favourite)
        elif data[0] == 'delfav':
            del_from_favourite(update.callback_query.from_user, data[1], update.callback_query.message.message_id,
                               update.callback_query.message.chat_id, context, data[2], json_messages_data, data[3])

            print(db_sess.query(User).filter(User.telegram_id == update.callback_query.from_user.id).one().favourite)
        elif data[0] == 'des' and data[3] == 'des':
            show_full_description(data[1], data[2],
                                  update.callback_query.message.chat_id,
                                  context, update.callback_query.from_user.language_code,
                                  update.callback_query.message, json_messages_data, update.callback_query.from_user.id)
        elif data[0] == 'des' and data[3] == 'min':
            show_short_description(update.callback_query.from_user, context, data[1], data[2],
                                   update.callback_query.message.message_id, json_messages_data,
                                   update.callback_query.message.chat_id)
        elif data[0] == 'rate':
            if data[3] == 'des':
                rate_restaurant_short(update.callback_query.from_user, context, data[1], data[2],
                                      update.callback_query.message.message_id, json_messages_data,
                                      update.callback_query.message.chat_id)
            elif data[3] == 'min':
                rate_restaurant_long(data[1], data[2],
                                     update.callback_query.message.chat_id,
                                     context, update.callback_query.from_user.language_code,
                                     update.callback_query.message, json_messages_data)
        elif data[0] == 'rated':
            rest = db_sess.query(Restaurant).filter(Restaurant.id == int(data[1])).one()
            user = db_sess.query(User).filter(User.telegram_id == update.callback_query.from_user.id).one()
            score_exists = db_sess.query(Scores).filter(Scores.place == rest.id,
                                                        Scores.user == user.id).all()
            print(bool(score_exists))
            if not bool(score_exists):
                try:
                    rest.number_of_scores += 1
                except TypeError:
                    rest.number_of_scores = 1
                try:
                    rest.total_score += int(data[4])
                except TypeError:
                    rest.total_score = int(data[4])

                rest.score = round(rest.total_score / rest.number_of_scores, 1)
                score = Scores(place=rest.id,
                               user=db_sess.query(User).filter(
                                   User.telegram_id == update.callback_query.from_user.id).one().id,
                               score=int(data[4]))
                db_sess.add(score)
                db_sess.commit()
            else:
                rest.total_score -= score_exists[0].score
                rest.total_score += int(data[4])
                score_exists[0].score = int(data[4])
                rest.score = round(rest.total_score / rest.number_of_scores, 1)
                db_sess.commit()
            if data[3] == 'des':
                change_inline(update.callback_query.message.chat_id,
                              update.callback_query.message.message_id, update.callback_query.from_user,
                              context, json_messages_data, data[1], data[2])
            elif data[3] == 'min':
                show_full_description(data[1], data[2],
                                      update.callback_query.message.chat_id,
                                      context, update.callback_query.from_user.language_code,
                                      update.callback_query.message, json_messages_data,
                                      update.callback_query.from_user.id, redact=True)
        elif data[0] == 'about':
            try:
                user_language = context.chat_data['language']
                if user_language == 'ru':
                    text = json_messages_data['messages']['ru']['about']
                else:
                    text = json_messages_data['messages']['en']['about']
            except KeyError:
                if update.callback_query.from_user.language_code == 'ru':
                    text = json_messages_data['messages']['ru']['about']
                else:
                    text = json_messages_data['messages']['en']['about']
            context.bot.sendMessage(update.callback_query.message.chat_id, text)
        elif data[0] == 'buyvip':
            if not db_sess.query(User).filter(User.telegram_id == update.callback_query.from_user.id).one().is_vip:
                try:
                    user_language = context.chat_data['language']
                    if user_language == 'ru':
                        title = 'VIP статус'
                        description = json_messages_data['messages']['ru']['VIP_advantage']
                        lan = 'ru'
                    else:
                        title = 'VIP status'
                        description = json_messages_data['messages']['en']['VIP_advantage']
                        lan = 'en'
                except KeyError:
                    if update.callback_query.from_user.language_code == 'ru':
                        title = 'VIP статус'
                        description = json_messages_data['messages']['ru']['VIP_advantage']
                        lan = 'ru'
                    else:
                        title = 'VIP status'
                        description = json_messages_data['messages']['en']['VIP_advantage']
                        lan = 'en'
                pay_message = context.bot.sendInvoice(update.callback_query.message.chat_id,
                                                      title=title,
                                                      description=description,
                                                      provider_token=P_TOKEN,
                                                      currency='rub',
                                                      need_email=True,
                                                      need_phone_number=True,
                                                      prices=[vip_price(lan)],
                                                      payload='VIP_invoice')
                context.chat_data['pay_message'] = pay_message.message_id
            else:
                try:
                    user_language = context.chat_data['language']
                    if user_language == 'ru':
                        text = json_messages_data['messages']['ru']['already_VIP']
                    else:
                        text = json_messages_data['messages']['en']['already_VIP']
                except KeyError:
                    if update.callback_query.from_user.language_code == 'ru':
                        text = json_messages_data['messages']['ru']['already_VIP']
                    else:
                        text = json_messages_data['messages']['en']['already_VIP']
                context.bot.sendMessage(update.callback_query.message.chat_id, text)


def checkout_process(update, context):
    context.bot.answerPreCheckoutQuery(
        update.pre_checkout_query.id,
        ok=True
    )


def successful_payment(update, context):
    with open('json/messages.json') as json_data:
        json_messages_data = json.load(json_data)
    try:
        user_language = context.chat_data['language']
        if user_language == 'ru':
            text = json_messages_data['messages']['ru']['successful_payment']
            keyboard = personal_account_vip_ru
        else:
            text = json_messages_data['messages']['en']['successful_payment']
            keyboard = personal_account_vip_en
    except KeyError:
        if update.message.from_user.language_code == 'ru':
            text = json_messages_data['messages']['ru']['successful_payment']
            keyboard = personal_account_vip_ru
        else:
            text = json_messages_data['messages']['en']['successful_payment']
            keyboard = personal_account_vip_en
    update.message.reply_text(f'{text} {update.message.successful_payment.total_amount / 100}'
                              f'{update.message.successful_payment.currency}', reply_markup=keyboard)
    user = db_sess.query(User).filter(User.telegram_id == update.message.from_user.id).one()
    user.is_vip = True
    new_payment = Payment(
        payment_name='VIP status',
        user=user.id,
        transaction_amount=update.message.successful_payment.total_amount / 100,
        email=update.message.successful_payment.order_info.email,
        phone=update.message.successful_payment.order_info.phone_number
    )
    db_sess.add(new_payment)
    context.bot.deleteMessage(update.message.chat_id, context.chat_data['pay_message'])
    db_sess.commit()
