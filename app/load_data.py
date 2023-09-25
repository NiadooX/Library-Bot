import json
from start_sett import set_settings


set_settings()
with open('config.json', 'r', encoding='utf-8') as f:
    file = json.load(f)
    bot_settings = file['bot']
    mysql_settings = file['mysql']