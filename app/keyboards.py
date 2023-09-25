import aiogram
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardBuilder, ReplyKeyboardMarkup, KeyboardButton
import asyncio
import texts
from start_sett import connect_to_mysql
from load_data import mysql_settings


login = mysql_settings['login']
password = mysql_settings['password']
host = mysql_settings['host']
port = mysql_settings['port']
db_name = mysql_settings['db_name']

VALIDATE = {'validate': True, 'typing': False}
VALIDATE_WITH_TYPING = {'validate': True, 'typing': True}


def __temp():
    return connect_to_mysql(host, login=login, password=password, db_name=db_name)


async def connect_to_db():
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, __temp)
    return result


async def start_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=texts.REGISTRATION_BUTTON, callback_data='start'))
    return keyboard


async def main_keyboard():
    markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=texts.PARSE_BUTTON), KeyboardButton(text=texts.PROFILE_BUTTON), KeyboardButton(text=texts.SETTINGS_BUTTON)], [KeyboardButton(text=texts.ABOUT_BOT_BUTTON)]], resize_keyboard=True, one_time_keyboard=True)
    return markup


async def back_keyboard():
    markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=texts.BACK_BUTTON_TEXT)]], resize_keyboard=True, one_time_keyboard=True)
    return markup


async def settings_temp_keyboard():
    markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=texts.SETTINGS_TEMP_ANSWER_SET), KeyboardButton(text=texts.SETTINGS_TEMP_ANSWER_CLEAR)], [KeyboardButton(text=texts.BACK_BUTTON_TEXT)]], resize_keyboard=True, one_time_keyboard=True)
    return markup


async def set_settings_question_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=texts.WANNA_SET_FONT, callback_data='set font'), InlineKeyboardButton(text=texts.WANNA_SET_FORMAT, callback_data='set format'))
    return keyboard.adjust(1)


async def set_font_keyboard():
    mydb = await connect_to_db()
    cursor = mydb.cursor(buffered=True)
    get_all_fonts = "SELECT font_name FROM fonts"
    cursor.execute(get_all_fonts)
    all_fonts = [i[0] for i in cursor.fetchall()]

    temp = []
    keyboard = InlineKeyboardBuilder()
    for font_name in all_fonts:
        keyboard.add(InlineKeyboardButton(text=font_name, callback_data=f'set font to {font_name}'))
        temp.append(2)
    keyboard.add(InlineKeyboardButton(text=texts.BACK_BUTTON_TEXT, callback_data='back to set_font_menu'))

    temp = temp[:len(all_fonts)//2]
    if len(all_fonts)%2 != 0:
        temp.append(1)
        temp.append(1)
    else:
        temp.append(1)
    return keyboard.adjust(*temp)


async def set_format_keyboard():
    mydb = await connect_to_db()
    cursor = mydb.cursor(buffered=True)

    get_all_formates = "SELECT format_name FROM formates"
    cursor.execute(get_all_formates)
    all_formates = [i[0] for i in cursor.fetchall()]

    temp = []
    keyboard = InlineKeyboardBuilder()
    for format_name in all_formates:
        if format_name.lower() != 'all':
            keyboard.add(InlineKeyboardButton(text=f'.{format_name}', callback_data=f'set format to {format_name}'))
        else:
            keyboard.add(InlineKeyboardButton(text='Все', callback_data=f'set format to {format_name}'))
        temp.append(2)
    keyboard.add(InlineKeyboardButton(text=texts.BACK_BUTTON_TEXT, callback_data='back to set_format_menu'))

    temp = temp[:len(all_formates)//2]
    if len(all_formates)%2 != 0:
        temp.append(1)
        temp.append(1)
    else:
        temp.append(1)
    return keyboard.adjust(*temp)


async def are_u_sure_clear_settings_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Да', callback_data='access clear settings'), InlineKeyboardButton(text='Нет', callback_data='denied clear settings'))
    return keyboard
