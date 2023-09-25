import aiogram
from aiogram import Router, types, F
from aiogram.types import FSInputFile
from aiogram.filters.command import Command
import texts
from start_sett import connect_to_mysql
from load_data import mysql_settings
import datetime
import keyboards
import re
from parse import bot_api_parse
from aiogram.dispatcher.flags import get_flag
from aiogram.utils.chat_action import ChatActionSender
from urllib.parse import urlparse
import asyncio


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


class MainMiddleWare(aiogram.BaseMiddleware):
    async def __call__(self, handler, event, data):
        mydb = await connect_to_db()
        cursor = mydb.cursor(buffered=True)

        use_lock = get_flag(data, 'validate')
        if use_lock:
            typing = get_flag(data, 'typing')
            if not typing:
                check_user = f"SELECT user_id FROM users WHERE LOWER(username) = LOWER('@{event.from_user.username}');"
                cursor.execute(check_user)
                r = cursor.fetchall()
                if r:
                    return await handler(event, data)
                await event.answer(texts.NOT_REGISTR_ERROR) if isinstance(event, aiogram.types.message.Message) else await data['bot'].send_message(event.from_user.id, texts.NOT_REGISTR_ERROR)
            else:
                check_user = f"SELECT user_id FROM users WHERE LOWER(username) = LOWER('@{event.from_user.username}');"
                cursor.execute(check_user)
                r = cursor.fetchall()
                if r:
                    async with ChatActionSender(bot=data['bot'], chat_id=event.chat.id, action='typing', initial_sleep=0.1):
                        return await handler(event, data)
                async with ChatActionSender(bot=data['bot'], chat_id=event.chat.id, action='typing', initial_sleep=0.1):
                    await event.answer(texts.NOT_REGISTR_ERROR) if isinstance(event, aiogram.types.message.Message) else await data['bot'].send_message(event.from_user.id, texts.NOT_REGISTR_ERROR)
        else:
            return await handler(event, data)


router = Router()
router.message.middleware(MainMiddleWare())
router.callback_query.middleware(MainMiddleWare())


@router.message(Command('start', 'go'))
async def start_message_handler(message: types.Message):
    mydb = await connect_to_db()
    cursor = mydb.cursor(buffered=True)

    check_user = f"SELECT user_id FROM users WHERE LOWER(username) = LOWER('@{message.from_user.username}');"
    cursor.execute(check_user)
    if cursor.fetchall():
        await message.answer(texts.USER_IN_DB_WARN_START)
    else:
        keyboard = await keyboards.start_keyboard()
        await message.answer(texts.START_TEXT, reply_markup=keyboard.as_markup())
    mydb.commit()


@router.callback_query(lambda call: call.data == 'start')
async def callback_handler(call: types.CallbackQuery, bot: aiogram.Bot):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

    mydb = await connect_to_db()
    cursor = mydb.cursor(buffered=True)

    check_user = f"SELECT user_id FROM users WHERE LOWER(username) = LOWER('@{call.from_user.username}');"
    cursor.execute(check_user)
    if cursor.fetchall():
        await bot.send_message(call.from_user.id, texts.USER_IN_DB_WARN_CALLBACK)
    else:
        create_user = f"""START TRANSACTION; INSERT INTO users (user_id, username, date_registration) VALUES ({int(call.from_user.id)}, '@{call.from_user.username}', '{datetime.datetime.now().strftime("%d.%m.%Y %X")}'); INSERT INTO users_locks (user_id, locked) VALUES ({int(call.from_user.id)}, False); INSERT INTO users_settings (user_id, font_id, format_id) VALUES ({int(call.from_user.id)}, 1, 9999); COMMIT;"""
        cursor.execute(create_user)

        await bot.send_sticker(call.from_user.id, FSInputFile('bot_data/start_sticker.webp'))

        keyboard = await keyboards.main_keyboard()
        await call.answer(texts.REGISTRATION_SUCCESS_CALLBACK)
        await bot.send_message(call.from_user.id, texts.REGISTRATION_SUCCESS, reply_markup=keyboard)


@router.message(F.text.lower() == texts.PARSE_BUTTON.lower(), flags=VALIDATE)
async def parse_button_handler(message: types.Message):
    mydb = await connect_to_db()
    cursor = mydb.cursor(buffered=True)

    get_available_list = "SELECT service_url FROM available_services"
    cursor.execute(get_available_list)
    available_list = [urlparse(i[0]).netloc for i in cursor.fetchall()]

    await message.answer(texts.GUIDE_TO_PARSE + '<b>Доступные на данный момент сервисы: ' + ', '.join(available_list) + '</b>', reply_markup=await keyboards.back_keyboard())


@router.message(F.text.lower() == texts.PROFILE_BUTTON.lower(), flags=VALIDATE)
async def profile_button_handler(message: types.Message):
    mydb = await connect_to_db()
    cursor = mydb.cursor(buffered=True)

    u_link = f'tg://user?id={message.from_user.id}'
    user_link = f'<a href="{u_link}">{message.from_user.first_name} {message.from_user.last_name}</a>'

    select_date_registr = f"SELECT date_registration FROM users WHERE username = '@{message.from_user.username}';"
    cursor.execute(select_date_registr)
    date_registration = cursor.fetchone()[0]

    get_user_font = f"SELECT font_name FROM users_settings INNER JOIN fonts ON users_settings.font_id = fonts.font_id WHERE user_id = '{message.from_user.id}';"
    cursor.execute(get_user_font)
    user_font = cursor.fetchone()[0]

    get_user_format = f"SELECT format_name FROM users_settings INNER JOIN formates ON users_settings.format_id = formates.format_id WHERE user_id = '{message.from_user.id}';"
    cursor.execute(get_user_format)
    user_format = cursor.fetchone()[0]
    if user_format.lower() == 'all':
        user_format = 'Все форматы'

    await message.answer(f'<b>{texts.TITLE_MESSAGE_PROFILE}</b>\n    {texts.USERNAME_MESSAGE_PROFILE} <b>{user_link}</b>\n    {texts.DATETIME_MESSAGE_PROFILE} <b>{date_registration}</b>\n\n    {texts.FONT_MESSAGE_PROFILE} <b>{user_font}</b>\n    {texts.FORMAT_MESSAGE_PROFILE} <b>{user_format}</b>', reply_markup=await keyboards.back_keyboard())


@router.message(F.func(lambda x: re.fullmatch(r'https://ilibrary\.ru.+', x.text)), flags=VALIDATE_WITH_TYPING)
async def ilibrary_parse_handler(message: types.Message, bot: aiogram.Bot):
    mydb = await connect_to_db()
    cursor = mydb.cursor(buffered=True)

    locked = f"SELECT locked FROM users_locks WHERE locked = True;"
    cursor.execute(locked)
    r = cursor.fetchall()

    if not r:
        lock = f"UPDATE users_locks INNER JOIN users ON users_locks.user_id = users.user_id SET locked = True WHERE users.user_id = {message.from_user.id};"
        cursor.execute(lock)
        mydb.commit()
        try:
            check_font = f"SELECT font_name FROM users_settings INNER JOIN fonts ON users_settings.font_id = fonts.font_id WHERE users_settings.user_id = {int(message.from_user.id)}"
            cursor.execute(check_font)
            user_font = cursor.fetchone()[0]

            check_formates = f"SELECT format_name FROM users_settings INNER JOIN formates ON users_settings.format_id = formates.format_id WHERE users_settings.user_id = {int(message.from_user.id)}"
            cursor.execute(check_formates)
            user_formate = cursor.fetchone()[0]

            await message.answer(texts.START_PARSING)
            await bot_api_parse(message.text, path_to_font__=f'bot_data/{user_font}.ttf', font_name__=user_font)
            await message.answer(texts.PARSING_ENDED_SUCCESS)

            if user_formate.lower() == 'all':
                await bot.send_document(message.from_user.id, FSInputFile('books/tgbot/book.pdf'))
                await bot.send_document(message.from_user.id, FSInputFile('books/tgbot/book.txt'))
            elif user_formate.lower() == 'pdf':
                await bot.send_document(message.from_user.id, FSInputFile('books/tgbot/book.pdf'))
            elif user_formate.lower() == 'txt':
                await bot.send_document(message.from_user.id, FSInputFile('books/tgbot/book.txt'))

        except Exception as e:
            print(e)
            await message.answer(texts.PARSING_ENDED_ERROR)
        unlock = f"UPDATE users_locks INNER JOIN users ON users_locks.user_id = users.user_id SET locked = False WHERE users.user_id = {message.from_user.id};"
        cursor.execute(unlock)
        mydb.commit()
    else:
        await message.answer(texts.DELAY_ERROR)

    mydb.commit()


@router.message(F.text.lower() == texts.BACK_BUTTON_TEXT.lower(), flags=VALIDATE)
async def back_message_handler(message: types.Message):
    await message.answer(texts.BACK_BUTTON_ANSWER, reply_markup=await keyboards.main_keyboard())


@router.message(F.text.lower() == texts.SETTINGS_BUTTON.lower(), flags=VALIDATE)
async def settings_message_handler(message: types.Message):
    await message.answer(texts.SETTINGS_QUESTION, reply_markup=await keyboards.settings_temp_keyboard())


@router.message(F.text.lower() == texts.SETTINGS_TEMP_ANSWER_SET.lower(), flags=VALIDATE)
async def send_settings_callback_handler(message: types.Message):
    keyboard = await keyboards.set_settings_question_keyboard()
    await message.answer(texts.SET_SETTINGS_QUESTION, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.lower() == 'set font', flags=VALIDATE)
async def set_font_chose_handler(call: types.CallbackQuery, bot: aiogram.Bot):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

    keyboard = await keyboards.set_font_keyboard()
    await bot.send_message(call.from_user.id, texts.SET_FONT_TEXT, reply_markup=keyboard.as_markup())


@router.callback_query(F.func(lambda x: re.fullmatch(r'set font to .+', x.data.lower())), flags=VALIDATE)
async def edit_font_handler(call: types.CallbackQuery, bot: aiogram.Bot):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

    mydb = await connect_to_db()
    cursor = mydb.cursor(buffered=True)

    font_name = call.data.lstrip("set font to ")
    set_font = f"UPDATE users_settings SET font_id = (SELECT font_id FROM fonts WHERE LOWER(font_name) = '{font_name.lower()}');"
    cursor.execute(set_font)
    mydb.commit()

    await bot.send_message(call.from_user.id, f'{texts.SET_FONT_SUCCESS} "{font_name}"')


@router.callback_query(F.data.lower() == 'set format')
async def set_format_chose_handler(call: types.CallbackQuery, bot: aiogram.Bot):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

    keyboard = await keyboards.set_format_keyboard()
    await bot.send_message(call.from_user.id, texts.SET_FORMAT_TEXT, reply_markup=keyboard.as_markup())


@router.callback_query(F.func(lambda x: re.fullmatch(r'set format to .+', x.data.lower())), flags=VALIDATE)
async def edit_format_handler(call: types.CallbackQuery, bot: aiogram.Bot):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

    mydb = await connect_to_db()
    cursor = mydb.cursor(buffered=True)

    format_name = call.data.lstrip('set format to ')
    set_format_name = f"UPDATE users_settings SET format_id = (SELECT format_id FROM formates WHERE format_name = '{format_name}');"
    cursor.execute(set_format_name)
    mydb.commit()

    if format_name.lower() != 'all':
        await bot.send_message(call.from_user.id, f'{texts.SET_FORMAT_SUCCESS} ".{format_name}"')
    else:
        await bot.send_message(call.from_user.id, f'{texts.SET_FORMAT_SUCCESS} "Все"')


@router.message(F.text.lower() == texts.SETTINGS_TEMP_ANSWER_CLEAR.lower(), flags=VALIDATE)
async def clear_settings_sure_handler(message: types.Message):
    keyboard = await keyboards.are_u_sure_clear_settings_keyboard()
    await message.answer(texts.ARE_U_SURE_ABOUT_CLEAR_SETTINGS_TEXT, reply_markup=keyboard.as_markup())


@router.callback_query(F.func(lambda x: re.fullmatch(r'(access|denied) clear settings', x.data.lower())), flags=VALIDATE)
async def clear_settings_sure_answer_handler(call: types.CallbackQuery, bot: aiogram.Bot):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

    answer = call.data.split(" clear settings")[0].strip()
    if answer.lower() == 'access':
        mydb = await connect_to_db()
        cursor = mydb.cursor(buffered=True)

        clear_settings = f"UPDATE users_settings SET font_id = 1, format_id = 9999 WHERE user_id = {call.from_user.id}"
        cursor.execute(clear_settings)
        mydb.commit()
        await bot.send_message(call.from_user.id, texts.CLEAR_SETTINGS_SUCCESS)
    else:
        await bot.send_message(call.from_user.id, texts.CLEAR_SETTINGS_DENIED)


@router.callback_query(F.func(lambda x: re.fullmatch(r'back to .+_menu', x.data.lower())), flags=VALIDATE)
async def back_to_menu_callback_query_handler(call: types.CallbackQuery, bot: aiogram.Bot):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

    back_to = call.data.lstrip('back to ').strip().lower()

    keyboard = await keyboards.set_settings_question_keyboard()
    await bot.send_message(call.from_user.id, texts.SETTINGS_QUESTION, reply_markup=keyboard.as_markup())


@router.message(F.text.lower() == texts.ABOUT_BOT_BUTTON.lower())
async def about_bot_handler(message: types.Message):
    await message.answer(texts.ABOUT_BOT_TEXT)
