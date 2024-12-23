from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import *

import asyncio
import json
import os

# Глобальные переменные для хранения сообщений чата и списка онлайн-пользователей
chat_msgs = []
online_users = set()
muted_users = set()  # Список пользователей, которым запрещено отправлять сообщения
admins = {
    "Лыков": "52472862",

    "Алейников" : "GG25SGAG37G6O7DD8G9HDWE",
    "Алейников Рома" : "GG25SGAG37G6O7DD8G9HDWE",
    "Алейников Роман" : "GG25SGAG37G6O7DD8G9HDWE",
    "Рома Алейников" : "GG25SGAG37G6O7DD8G9HDWE",
    "Роман Алейников" : "GG25SGAG37G6O7DD8G9HDWE",
    "Forest" : "GG25SGAG37G6O7DD8G9HDWE",
    
    "Ильченко" : "1452",
    "Наставник" : "PKTi03"
}  # Список админов с их паролями

# Словарь для хранения паролей обычных участников
participants = {
    "mentor": "mentorpass"  # Новый участник с паролем
}

MAX_MSG_COUNT = 100  # Ограничение на количество сообщений, чтобы чат не перегружался
MSG_FILE = "chat_history.json"  # Имя файла для сохранения истории чата

# Функция для загрузки сообщений из файла при перезапуске сервера
def load_messages():
    global chat_msgs
    if os.path.exists(MSG_FILE):
        with open(MSG_FILE, 'r', encoding='utf-8') as f:
            chat_msgs = json.load(f)

# Функция для сохранения сообщений в файл после каждого обновления чата
def save_messages():
    global chat_msgs
    with open(MSG_FILE, 'w', encoding='utf-8') as f:
        json.dump(chat_msgs, f)

# Админская панель для управления чатом и пользователями
async def admin_actions(nicname, msg_box):
    global chat_msgs
    while True:
        # Выводим панель админских действий с выбором доступных операций
        action = await actions('⚙️ Админ-панель', buttons=['Мьют/Размьют пользователя', 'Очистить чат', 'Удалить сообщение', 'Закрыть панель'])

        # Действие мьют/размьют пользователя
        if action == 'Мьют/Размьют пользователя':
            target_user = await input("Введите имя пользователя для мьюта/размьюта", required=True)
            if target_user in online_users:
                if target_user in muted_users:
                    muted_users.remove(target_user)  # Если пользователь уже замьючен, размьютим
                    chat_msgs.append(('🎃', f"Пользователь `{target_user}` размьючен админом `{nicname}`!"))
                    msg_box.append(put_markdown(f"🎃 Пользователь `{target_user}` размьючен админом `{nicname}`!"))
                else:
                    muted_users.add(target_user)  # Иначе мьютим
                    chat_msgs.append(('🎃', f"Пользователь `{target_user}` замьючен админом `{nicname}`!"))
                    msg_box.append(put_markdown(f"🎃 Пользователь `{target_user}` замьючен админом `{nicname}`!"))
            else:
                toast("Пользователь не найден!", color="error")

        # Очистка чата
        elif action == 'Очистить чат':
            chat_msgs.clear()  # Полная очистка сообщений
            msg_box.reset()  # Очищаем отображаемые сообщения
            chat_msgs.append(('🎃', f"Чат был очищен админом `{nicname}`!"))
            msg_box.append(put_markdown(f"🎃 Чат был очищен админом `{nicname}`!"))
            save_messages()  # Сохраняем изменения

        # Удаление конкретного сообщения по его индексу
        elif action == 'Удалить сообщение':
            target_idx = await input("Введите индекс сообщения для удаления (начиная с 0)", type=NUMBER, required=True)
            if 0 <= target_idx < len(chat_msgs):
                deleted_msg = chat_msgs.pop(target_idx)
                msg_box.clear()  # Обновляем чат после удаления
                for m in chat_msgs:
                    msg_box.append(put_markdown(f"`{m[0]}`: {m[1]}"))
                toast(f"Сообщение от `{deleted_msg[0]}` удалено!", color="success")
            else:
                toast("Неверный индекс сообщения!", color="error")

        elif action == 'Закрыть панель':
            break

    save_messages()

# Основная функция чата
async def main():
    global chat_msgs

    # Приветственное сообщение при входе в чат
    put_markdown('📚 Добро пожаловать в чат созданный группой ИСП9-kh11!!!')

    # Загружаем сохраненные сообщения из файла (если чат был уже запущен ранее)
    load_messages()

    # Контейнер для сообщений, который будет отображаться пользователям
    msg_box = output()

    # Прокручиваемое окно для сообщений
    put_scrollable(msg_box, height=300, keep_bottom=True)

    # Переменная для отслеживания выхода пользователя
    user_exit = False
    last_nicname = None

    while True:
        # Если пользователь вышел из чата, предлагаем перезайти с тем же ником
        if user_exit:
            action = await actions('Вы вышли из чата. Что вы хотите сделать?', buttons=['Перезайти', 'Закрыть'])
            if action == 'Перезайти':
                nicname = last_nicname  # Восстанавливаем прошлое имя
                user_exit = False
            else:
                break
        else:
            # Просим пользователя ввести никнейм и проверяем, не занят ли он
            nicname = await input("Войдите в чат", required=True, placeholder="Ваше имя", 
                                  validate=lambda n: "Это имя уже занято" if n in online_users or n == '🎃' else None)

            # Проверка на наставника
            if nicname in participants:
                participant_password = await input("Введите пароль для Наставника", type=PASSWORD, required=True)
                if participant_password == participants[nicname]:
                    # Успешный вход как наставник, добавляем пользователя в онлайн
                    online_users.add(nicname)
                else:
                    toast("Неверный пароль!", color="error")
                    continue

            # Если не наставник, проверяем права админа
            is_admin = False
            if nicname in admins:
                admin_password = await input("Введите пароль для админа", type=PASSWORD, required=True)
                if admin_password == admins[nicname]:
                    is_admin = True
                    nicname = f"[Админ] {nicname}"  # Помечаем как админа
                else:
                    toast("Неверный пароль!", color="error")
                    continue

            # Добавляем пользователя в список онлайн
            online_users.add(nicname)

            # Сообщаем всем, что новый пользователь присоединился
            chat_msgs.append(('🎃', f"{nicname} присоединился к беседе!"))
            msg_box.append(put_markdown(f'`{nicname}` присоединился к беседе!'))

            # Запускаем задачу обновления сообщений для текущего пользователя
            refresh_task = run_async(refresh_msg(nicname, msg_box))

            # Отображаем все прошлые сообщения чата
            for m in chat_msgs:
                msg_box.append(put_markdown(f"`{m[0]}`: {m[1]}"))

            # Если это админ, запускаем админскую панель
            if is_admin:
                run_async(admin_actions(nicname, msg_box))
                put_buttons(['Открыть админ-панель'], onclick=lambda _: run_async(admin_actions(nicname, msg_box)))

            # Основной цикл для ввода сообщений
            while True:
                # Получаем данные от пользователя
                data = await input_group('✉ Новое сообщение', [
                    input(placeholder="Текст сообщения", name="msg"), 
                    actions(name="cmd", buttons=["Отправить", {'label': "Выйти из чата", 'type': "cancel"}])
                ])

                # Если пользователь вышел
                if data is None:
                    user_exit = True
                    last_nicname = nicname
                    break

                # Если отправили сообщение
                if data['cmd'] == "Отправить":
                    # Проверяем наличие текста в сообщении
                    if not data['msg']:
                        toast("Введите текст сообщения!", color="error")
                        continue

                    # Если пользователь замьючен, он не может отправить сообщение
                    if nicname in muted_users:
                        toast("Вы замьючены и не можете отправлять сообщения!", color="error")
                        continue

                    # Добавляем сообщение пользователя в чат
                    msg_box.append(put_markdown(f"`{nicname}`: {data['msg']}"))
                    chat_msgs.append((nicname, data['msg']))

                    # Сохраняем обновления
                    save_messages()

            # Завершаем обновление сообщений для этого пользователя
            refresh_task.close()

            # Удаляем пользователя из списка онлайн
            online_users.remove(nicname)

            # Сообщаем всем, что пользователь покинул чат
            toast("Вы вышли из чата!")
            msg_box.append(put_markdown(f"🎃 Пользователь {nicname} покинул чат!"))
            chat_msgs.append(('🎃', f"Пользователь {nicname} покинул чат!"))

            # Сохраняем обновления
            save_messages()

# Функция для периодического обновления сообщений в чате
async def refresh_msg(nickname, msg_box):
    global chat_msgs
    last_idx = len(chat_msgs)  # Индекс последнего сообщения, которое видел пользователь

    while True:
        await asyncio.sleep(1)  # Интервал обновления

        # Выводим новые сообщения
        for m in chat_msgs[last_idx:]:
            if m[0] != nickname:  # Не показываем свои сообщения
                msg_box.append(put_markdown(f"`{m[0]}`: {m[1]}"))

        # Проверка на количество сообщений
        if len(chat_msgs) > MAX_MSG_COUNT:
            chat_msgs = chat_msgs[len(chat_msgs) // 2:]

        last_idx = len(chat_msgs)  # Обновляем индекс последнего сообщения

# Запуск веб-сервера PyWebIO
if __name__ == '__main__':
    start_server(main, debug=True, port=8080, cdn=False)
