from pywebio.input import *
from pywebio.output import *
from config import chat_msgs, online_users, muted_users,admin_users
from utils import save_messages

async def admin_actions(nicname, msg_box):
    while True:
        action = await actions('⚙️ Админ-панель', buttons=['Бан/Разбанен пользователя', 'Очистить чат', 'Удалить сообщение', 'Закрыть панель'])

        if action == 'Бан/Разбан пользователя':
            target_user = await input("Введите имя пользователя для мьюта/размьюта", required=True)
            if target_user in online_users and not admin_users:
                if target_user in muted_users:
                    muted_users.remove(target_user)
                    chat_msgs.append(('🎃', f"Пользователь `{target_user}` разбанен админом `{nicname}`!"))
                    msg_box.append(put_markdown(f"🎃 Пользователь `{target_user}` разбанен админом `{nicname}`!"))
                else:
                    muted_users.add(target_user)
                    chat_msgs.append(('🎃', f"Пользователь `{target_user}` забанен админом `{nicname}`!"))
                    msg_box.append(put_markdown(f"🎃 Пользователь `{target_user}` забанен админом `{nicname}`!"))
            else:
                toast("Пользователь не найден!", color="error")

        elif action == 'Очистить чат':
            chat_msgs.clear()
            msg_box.reset()
            chat_msgs.append(('🎃', f"Чат был очищен админом `{nicname}`!"))
            msg_box.append(put_markdown(f"🎃 Чат был очищен админом `{nicname}`!"))
            save_messages()

        elif action == 'Удалить сообщение':
            target_idx = await input("Введите индекс сообщения для удаления (начиная с 0)", type=NUMBER, required=True)
            if 0 <= target_idx < len(chat_msgs):
                deleted_msg = chat_msgs.pop(target_idx)
                msg_box.reset()
                for m in chat_msgs:
                    msg_box.append(put_markdown(f"`{m[0]}`: {m[1]}"))
                toast(f"Сообщение от `{deleted_msg[0]}` удалено!", color="success")
            else:
                toast("Неверный индекс сообщения!", color="error")

        elif action == 'Закрыть панель':
            break

    save_messages()
