from telegram import ReplyKeyboardMarkup, KeyboardButton


main_menu_keyboard = ReplyKeyboardMarkup([
    [KeyboardButton(text='Каталог 📖'),
     KeyboardButton(text='Личный кабинет 👤')],
    [KeyboardButton(text='Инфо ℹ️'),
     KeyboardButton(text='Избранное ❤️')]
], resize_keyboard=True, input_field_placeholder='Главное меню 🧭')
