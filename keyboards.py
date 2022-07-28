from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
import json

main_menu_keyboard = ReplyKeyboardMarkup([
    [KeyboardButton(text='Каталог 📖'),
     KeyboardButton(text='Личный кабинет 👤')],
    [KeyboardButton(text='Инфо ℹ️'),
     KeyboardButton(text='Избранное ❤️')]
], resize_keyboard=True, input_field_placeholder='Главное меню 🧭')

main_menu_keyboard_en = ReplyKeyboardMarkup([
    [KeyboardButton(text='Catalog 📖'),
     KeyboardButton(text='Personal account 👤')],
    [KeyboardButton(text='Info ℹ️'),
     KeyboardButton(text='Favourite ❤️')]
], resize_keyboard=True, input_field_placeholder='Main menu 🧭')

geoposition_keyboard = ReplyKeyboardMarkup([
    [KeyboardButton(text='🔙'),
     KeyboardButton(text='Расстояние 👣', request_location=True)]], resize_keyboard=True,
    input_field_placeholder='')

geoposition_keyboard_en = ReplyKeyboardMarkup([
    [KeyboardButton(text='🔙'),
     KeyboardButton(text='Distance 👣', request_location=True)]], resize_keyboard=True,
    input_field_placeholder='')

personal_account_default_ru = ReplyKeyboardMarkup([
    [KeyboardButton(text='ENG 🇬🇧'), KeyboardButton(text='Добавить заведение ➕')],
    [KeyboardButton(text='Мои заведения'), KeyboardButton(text='Стать VIP 💵')],
    [KeyboardButton(text='🔙')]
], resize_keyboard=True, input_field_placeholder='Личный кабинет')

personal_account_vip_ru = ReplyKeyboardMarkup([
    [KeyboardButton(text='ENG 🇬🇧'), KeyboardButton(text='Добавить заведение ➕')],
    [KeyboardButton(text='Мои заведения'), KeyboardButton(text='VIP 👑')],
    [KeyboardButton(text='🔙')]
], resize_keyboard=True, input_field_placeholder='Личный кабинет')

personal_account_default_en = ReplyKeyboardMarkup([
    [KeyboardButton(text='RUS 🇷🇺'), KeyboardButton(text='Add restaurant ➕')],
    [KeyboardButton(text='My restaurants'), KeyboardButton(text='Become VIP 💵')],
    [KeyboardButton(text='🔙')]
], resize_keyboard=True, input_field_placeholder='Personal account')

personal_account_vip_en = ReplyKeyboardMarkup([
    [KeyboardButton(text='RUS 🇷🇺'), KeyboardButton(text='Add restaurant ➕')],
    [KeyboardButton(text='My restaurants'), KeyboardButton(text='VIP 👑')],
    [KeyboardButton(text='🔙')]
], resize_keyboard=True, input_field_placeholder='Personal account')

rate_keyboard = [[InlineKeyboardButton(text='⭐️')],
                 [InlineKeyboardButton(text='⭐⭐')],
                 [InlineKeyboardButton(text='⭐⭐⭐')],
                 [InlineKeyboardButton(text='⭐⭐⭐⭐')],
                 [InlineKeyboardButton(text='⭐⭐⭐⭐⭐')]]


info_keyboard_ru = InlineKeyboardMarkup([
    [InlineKeyboardButton(text='Чат 💬', url='https://t.me/+9dpfvhkdyiJmNjYy'),
     InlineKeyboardButton(text='Канал 📺', url='https://t.me/zverochannel')],
    [InlineKeyboardButton(text='О проекте ℹ️', callback_data='about')],
     [InlineKeyboardButton(text='Связь с модератором 📞', url='https://t.me/Kmspofizre')]
])


info_keyboard_en = InlineKeyboardMarkup([
    [InlineKeyboardButton(text='Chat 💬', url='https://t.me/+9dpfvhkdyiJmNjYy'),
     InlineKeyboardButton(text='Channel 📺', url='https://t.me/zverochannel')],
    [InlineKeyboardButton(text='About us ℹ️', callback_data='about')],
     [InlineKeyboardButton(text='Contact moderator 📞', url='https://t.me/Kmspofizre')]
])


single_vip_keyboard_ru = InlineKeyboardMarkup([
    [InlineKeyboardButton(text='Купить VIP статус', callback_data='buyvip')]
])


single_vip_keyboard_en = InlineKeyboardMarkup([
    [InlineKeyboardButton(text='Buy VIP status', callback_data='buyvip')]
])


def card_inline_keyboard_del_ru(add_del, des_min):
    with open('json/messages.json') as json_messages:
        json_messages_data = json.load(json_messages)
    if add_del == 'del':
        favourite_ru = InlineKeyboardButton(text=json_messages_data['messages']['ru']['delete_from_favourite'])
    else:
        favourite_ru = InlineKeyboardButton(text=json_messages_data['messages']['ru']['add_to_favourite'])
    if des_min == 'des':
        description = InlineKeyboardButton(text=json_messages_data['messages']['ru']['description'])
    else:
        description = InlineKeyboardButton(text=json_messages_data['messages']['ru']['minimize'])
    contact_ru = InlineKeyboardButton(text=json_messages_data['messages']['ru']['contact'])
    rate = InlineKeyboardButton(text=json_messages_data['messages']['ru']['rate'])
    return favourite_ru, contact_ru, description, rate


def card_inline_keyboard_del_en(add_del, des_min):
    with open('json/messages.json') as json_messages:
        json_messages_data = json.load(json_messages)
    if add_del == 'del':
        favourite_ru = InlineKeyboardButton(text=json_messages_data['messages']['en']['delete_from_favourite'])
    else:
        favourite_ru = InlineKeyboardButton(text=json_messages_data['messages']['en']['add_to_favourite'])
    if des_min == 'des':
        description = InlineKeyboardButton(text=json_messages_data['messages']['en']['description'])
    else:
        description = InlineKeyboardButton(text=json_messages_data['messages']['en']['minimize'])
    contact_ru = InlineKeyboardButton(text=json_messages_data['messages']['en']['contact'])

    rate = InlineKeyboardButton(text=json_messages_data['messages']['ru']['rate'])
    return favourite_ru, contact_ru, description, rate
