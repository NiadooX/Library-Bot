import aiogram
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
import asyncio
from load_data import bot_settings
from handlers import router
import aiohttp
import os
from parse import bot_api_parse
from start_sett import connect_to_mysql
from load_data import mysql_settings


login = mysql_settings['login']
password = mysql_settings['password']
host = mysql_settings['host']
port = mysql_settings['port']
db_name = mysql_settings['db_name']


def __temp():
    return connect_to_mysql(host, login=login, password=password, db_name=db_name)


async def connect_to_db():
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, __temp)
    return result


async def parse_bot_data():
    if not os.path.exists('bot_data/') or not os.path.exists('data/start_sticker.webp'):
        if not os.path.exists('bot_data/'):
            os.mkdir('bot_data/')
        sticker_url = 'https://tlgrm.ru/_/stickers/f48/f6d/f48f6d08-6536-3107-9473-ec8123a0946d/5.webp'
        async with aiohttp.request('GET', sticker_url) as sticker_page:
            r = await sticker_page.read()
            with open('bot_data/start_sticker.webp', 'wb') as f:
                f.write(r)


bot = Bot(token=bot_settings['token'], parse_mode=ParseMode.HTML)


async def main():
    mydb = await connect_to_db()
    cursor = mydb.cursor(buffered=True)
    start_sett = "UPDATE users_locks SET locked = False"
    cursor.execute(start_sett)
    mydb.commit()
    cursor.close()

    await parse_bot_data()

    dp = Dispatcher()
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())
