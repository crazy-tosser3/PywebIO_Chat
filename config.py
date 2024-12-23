import os

#Переменные для хранения информации о пользователях
chat_msgs = []
online_users = set()
muted_users = set()
admin_users = set()

#Техническая информация
MAX_MSG_COUNT = 100
MSG_FILE = os.path.join("JSON", "chat_history.json")
USERS_BASE = os.path.join("JSON", "users.json")
Users = dict()