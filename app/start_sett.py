import os
import json
from getpass import getpass
import time
import mysql.connector


def set_settings():
    must_start = False
    if not os.path.exists('config.json'):
        must_start = True
    else:
        with open('config.json', 'r', encoding='utf-8') as conf:
            r = json.load(conf)
        if 'bot' in list(r.keys()) and 'mysql' in list(r.keys()):
            for category in r.keys():
                must_start = not all(map(lambda x: len(str(x)) > 0, r[category].values()))
                if must_start is True:
                    break
        else:
            must_start = True

    if must_start:
        print('[INFO] Привет, давай выполним первичную настройку бота! Вставляй данные корректно, иначе бот будет выдавать ошибки!')
        time.sleep(0.1)
        bot_token = input('\t[+] Введите токен бота: ').split()
        mysql_login = input('\t[+] Введите логин пользователя mysql: ').split()
        mysql_password = getpass(prompt='\t[+] Введите пароль для пользователя mysql с прошлого шага. (Если доступ к бд осуществляется без пароля, пожалуйста, добавьте пароль): ').split()
        mysql_host = input('\t[+] Введите хост с работающим mysql server (для локального сервера укажите - "localhost"): ').split()
        mysql_host_port = input('\t[+] Введите порт хоста с работающим mysql server: ').split()
        mysql_db_name = input('\t[+] Введите название базы данных для бота (Читайте руководство на GitHub): ').split()
        mydict = {"bot": {"token": bot_token[0]}, "mysql": {"login": mysql_login[0], "password": mysql_password[0], "host": mysql_host[0], "port": mysql_host_port[0], "db_name": mysql_db_name[0]}}
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(mydict, f, indent=4, ensure_ascii=False)
        print('[INFO] Первичная настройка успешно окончена! Если вы ошиблись в данных, то просто удалите конфигурационный файл "config.json" и заново запустите бота для новой настройки. Удачного использования!')

"""Connection to mysql server part"""

def connect_to_mysql(host='localhost', port='3306', *, login, password, db_name):
    db_session = mysql.connector.connect(
        host = host,
        port = port,
        user = login,
        password = password,
        database = db_name,
        charset = 'utf8mb4'
    )
    return db_session
