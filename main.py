from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import *
import asyncio
import json

from utils import load_messages, save_messages, refresh_msg, load_user
from admin import admin_actions
from config import chat_msgs, online_users, muted_users, USERS_BASE


#Получаем доступ к БД
with open(USERS_BASE, 'r', encoding='utf-8') as f:
    Users = json.load(f)

# Получение данных участников и администраторов
participants = {user["username"]: user["password"] for user in Users.get("Ussers", [])}
admins = {admin["username"]: admin["password"] for admin in Users.get("Admins", [])}

# Основная функция чата
async def main():
    global chat_msgs

    put_markdown('📚 Добро пожаловать в чат, созданный группой ИСП9-kh11!!!')

    load_messages()
    load_user()

    msg_box = output()
    put_scrollable(msg_box, height=300, keep_bottom=True)

    user_exit = False
    last_nicname = None

    while True:
        if user_exit:
            action = await actions('Вы вышли из чата. Что вы хотите сделать?', buttons=['Перезайти', 'Закрыть'])
            if action == 'Перезайти':
                nicname = last_nicname
                user_exit = False
            else:
                break
        else:
            # Проверяем, есть ли пользователь в базе данных
            nicname = await input("Войдите в чат", required=True, placeholder="Ваше имя", 
                                  validate=lambda n: "Имя не найдено в базе данных" if n not in participants and n not in admins else None)

            # Проверка на обычного участника
            if nicname in participants:
                participant_password = await input("Введите пароль участника", type=PASSWORD, required=True)
                if participant_password == participants[nicname]:
                    online_users.add(nicname)
                else:
                    toast("Неверный пароль!", color="error")
                    continue

            # Проверка на администратора
            elif nicname in admins:
                admin_password = await input("Введите пароль для админа", type=PASSWORD, required=True)
                if admin_password == admins[nicname]:
                    is_admin = True
                    nicname = f"[Админ] {nicname}"
                    online_users.add(nicname)
                else:
                    toast("Неверный пароль!", color="error")
                    continue

            chat_msgs.append(('🎃', f"{nicname} присоединился к беседе!"))
            msg_box.append(put_markdown(f'`{nicname}` присоединился к беседе!'))

            refresh_task = run_async(refresh_msg(nicname, msg_box))

            for m in chat_msgs:
                msg_box.append(put_markdown(f"`{m[0]}`: {m[1]}"))

            # Если пользователь администратор, открываем админ-панель
            if "Админ" in nicname:
                run_async(admin_actions(nicname, msg_box))
                put_buttons(['Открыть админ-панель'], onclick=lambda _: run_async(admin_actions(nicname, msg_box)))

            # Цикл отправки сообщений
            while True:
                data = await input_group('✉ Новое сообщение', [
                    input(placeholder="Текст сообщения", name="msg"), 
                    actions(name="cmd", buttons=["Отправить", {'label': "Выйти из чата", 'type': "cancel"}])
                ])

                if data is None:
                    user_exit = True
                    last_nicname = nicname
                    break

                if data['cmd'] == "Отправить":
                    if not data['msg']:
                        toast("Введите текст сообщения!", color="error")
                        continue

                    if nicname in muted_users:
                        toast("Вы замьючены и не можете отправлять сообщения!", color="error")
                        continue

                    msg_box.append(put_markdown(f"`{nicname}`: {data['msg']}"))
                    chat_msgs.append((nicname, data['msg']))
                    save_messages()

            refresh_task.close()

            online_users.remove(nicname)
            toast("Вы вышли из чата!")
            msg_box.append(put_markdown(f"🎃 Пользователь {nicname} покинул чат!"))
            chat_msgs.append(('🎃', f"Пользователь {nicname} покинул чат!"))
            save_messages()

if __name__ == '__main__':
    start_server(main, debug=True, port=8000, cdn=False)
