# Library-Bot
Телеграм бот для скачивания книг с различных сайтов

# Использованные технологии
- <b>python 3.8+</b>
- <b>mysql 8.0+</b>
- Библиотеки для python3: <b>aiogram, mysql-connector-python, aiohttp, bs4, asyncio, lxml, getpass, time, shutil, os, json, fpdf2, re, datetime, aiofiles</b>

# Установка
<b>ПЕРЕД НИЖЕПЕРЕЧИСЛЕННЫМИ ДЕЙСТВИЯМИ САМО-СОБОЙ РАЗУМЕЕТСЯ НАЛИЧИЕ СОЗДАННОГО ВАМИ ТЕЛЕГРАМ БОТА</b>

1. Устанавливаем python 3.8+ с оф. сайта с пунктом <b>ADD PYTHON TO PATH</b>. Устанавливаем все необходимые библиотеки - для этого переходим в директорию с файлами бота и пишем в консоле <b>pip3 install -r requirements.txt</b> (должен быть pip)
2. Устанавливаем mysql server на сервер/пк для бота.  Создаем пользователя с полными правами
3. Создем базу данный с названием, которое позднее впишем в начальную настройку. Команда: <b>CREATE DATABASE {название бд} CHARSET = 'utf8mb4';</b>
4. Развертываем дамп базы данных командой <b>mysql -u {ваш логин} -p {то же название бд, что и в прошлой команде} < db.sql</b>
5. Запускаем файл main.py, если вы впервые запускаете этого бота вас попросят ввести данные от mysql сервера и от вашего заранее созданного бота. Вводим данные
6. Бот запущен, наслаждаемся жизнью :)
